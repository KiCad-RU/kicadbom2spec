#!/usr/bin/env python2
# -*-    Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4    -*-
### BEGIN LICENSE
# Copyright (C) 2018 Baranovskiy Konstantin (baranovskiykonstantin@gmail.com)
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

import argparse
import codecs
import inspect
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from operator import itemgetter
from ConfigParser import SafeConfigParser

import wx
import wx.grid

from odf.opendocument import __version__ as odfpy_version

EXEC_PATH = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import gui
from complist import *
from controls import *
from kicadsch import *

# Set default encoding
reload(sys)
sys.setdefaultencoding('utf-8')

# Global
VERSION = ''
DEFAULT_SETTINGS_FILE_NAME = 'settings.ini'
DEFAULT_LOGGING_FILE_NAME = 'log.txt'
SETTINGS_SEPARATOR = ';;;'
ID_RECENT = 2000


class Window(gui.MainFrame):
    """
    Graphical user interface for kicadbom2spec.

    """

    def __init__(self, parent):
        """
        Initialize main window.

        """
        gui.MainFrame.__init__(self, parent)

        # FIXME: temporary fix for wx bug (https://trac.wxwidgets.org/ticket/16440)
        bugDialog = wx.Dialog(self)
        bugDialog.SetSize(wx.Size(1, 1))
        bugDialog.Bind(wx.EVT_IDLE, lambda event: bugDialog.Destroy())
        bugDialog.Show()

        # Events
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_toolbar)
        self.splitter_main.Bind(wx.EVT_SIZE, self.on_splitter_size_changed)
        self.splitter_main.Bind(wx.EVT_MAXIMIZE, self.on_splitter_size_changed)
        self.splitter_main.Bind(
            wx.EVT_SPLITTER_SASH_POS_CHANGED,
            self.on_splitter_sash_changed
            )
        self.comp_fields_panel_grid.Bind(
            wx.EVT_CONTEXT_MENU,
            self.on_comp_fields_panel_grid_popup
            )
        self.comp_fields_panel_grid.Bind(
            wx.grid.EVT_GRID_CELL_RIGHT_CLICK,
            self.on_comp_fields_panel_grid_popup
            )
        self.comp_fields_panel_grid.Bind(
            wx.grid.EVT_GRID_RANGE_SELECT,
            self.on_comp_fields_panel_grid_select
            )

        # Variables
        self.schematic_file = ''
        self.library_file = ''
        self.complist_file = ''
        self.schematics = []
        self.library = None
        self.saved = True
        self.not_found = False
        self.buffer = []
        self.settings_file = ''

        # GUI
        self.toolbar.InsertStretchableSpace(
                self.toolbar.GetToolPos(gui.ID_COMP_FIELDS_PANEL)
                )
        self.toolbar.Realize()
        self.splitter_main.Initialize(self.panel_components)
        self.init_grid()

        # Default settings
        self.show_need_adjust_mark = False
        self.auto_groups_dict = {}
        self.values_dict = {
            u'группа':[],
            u'марка':[],
            u'значение':[],
            u'класс точности':[],
            u'тип':[],
            u'стандарт':[],
            u'примечание':[]
            }
        self.separators_dict = {
            u'марка':['',''],
            u'значение':['',''],
            u'класс точности':['',''],
            u'тип':['',''],
            u'стандарт':['','']
            }
        self.aliases_dict = {
            u'группа':u'Группа',
            u'марка':u'Марка',
            u'значение':u'',
            u'класс точности':u'Класс точности',
            u'тип':u'Тип',
            u'стандарт':u'Стандарт',
            u'примечание':u'Примечание'
            }
        self.stamp_dict = {
            u'decimal_num':u'',
            u'developer':u'',
            u'verifier':u'',
            u'inspector':u'',
            u'approver':u'',
            u'comp':u'',
            u'title':u''
            }
        self.group_names_dict = {}

        if sys.platform == 'win32':
            icon = wx.Icon('bitmaps/icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)

            self.config_path = os.path.join(
                    os.environ['APPDATA'],
                    'kicadbom2spec'
                    )
        else:
            icon = wx.Icon('bitmaps/icon.xpm', wx.BITMAP_TYPE_XPM)
            self.SetIcon(icon)

            self.config_path = os.path.join(
                    os.path.expanduser('~/.config'),
                    'kicadbom2spec'
                    )

        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)

        # Logging
        logging.basicConfig(
                filename=os.path.join(
                    self.config_path,
                    DEFAULT_LOGGING_FILE_NAME
                    ),
                level=logging.INFO,
                format='\n%(asctime)s %(levelname)s: %(message)s',
                datefmt='%Y.%m.%d %H:%M:%S'
                )

        # Settings
        self.settings_file = os.path.join(
                self.config_path,
                DEFAULT_SETTINGS_FILE_NAME
                )

        if not os.path.exists(self.settings_file):
            shutil.copy2(DEFAULT_SETTINGS_FILE_NAME, self.settings_file)

        self.load_settings(self.settings_file)

    def load_settings(self, settings_file_name=DEFAULT_SETTINGS_FILE_NAME, select=False):
        """
        Loads settings from configuration file.

        """
        if os.path.isfile(settings_file_name):
            if not select:
                # Load settings from file
                self.settings = SafeConfigParser()
                self.settings.readfp(codecs.open(
                    settings_file_name,
                    'r',
                    encoding='utf-8'
                    ))

                if self.settings.has_section('window'):
                    x, y = self.GetPosition()
                    width, height = self.GetClientSize()
                    if self.settings.has_option('window', 'x'):
                        x = self.settings.getint('window', 'x')
                    if self.settings.has_option('window', 'y'):
                        y = self.settings.getint('window', 'y')
                    self.SetPosition(wx.Point(x, y))

                    if self.settings.has_option('window', 'width'):
                        width = self.settings.getint('window', 'width')
                    if self.settings.has_option('window', 'height'):
                        height = self.settings.getint('window', 'height')
                    self.SetClientSize(wx.Size(width, height))
                    if self.settings.has_option('window', 'maximized'):
                        if self.settings.getint('window', 'maximized'):
                            self.Maximize()

                if self.settings.has_section('column sizes'):
                    if hasattr(self, 'grid'):
                        for col in self.settings.options('column sizes'):
                            col_size = self.settings.getint('column sizes', col)
                            self.grid.SetColSize(int(col), col_size)

                # Settings from section 'comp fields panel' loads
                # in 'splitter_mainOnIdle' event handler

                if self.settings.has_section('values'):
                    for item in self.values_dict.keys():
                        if self.settings.has_option('values', item):
                            values_list = self.settings.get('values', item)
                            values_list = values_list.split(SETTINGS_SEPARATOR)
                            if values_list != ['']:
                                self.values_dict[item] = values_list

                if self.settings.has_section('group names singular') and \
                        self.settings.has_section('group names plural'):
                    for name in self.settings.options('group names singular'):
                        if self.settings.has_option('group names plural', name):
                            singular = self.settings.get('group names singular', name)
                            plural = self.settings.get('group names plural', name)
                            self.group_names_dict[plural] = singular

                if self.settings.has_section('general'):
                    if self.settings.has_option('general', 'space as dot'):
                        self.grid.space_as_dot = self.settings.getboolean('general', 'space as dot')
                    if self.settings.has_option('general', 'show need adjust mark'):
                        self.show_need_adjust_mark = self.settings.getboolean('general', 'show need adjust mark')

                if self.settings.has_section('auto filling groups'):
                    for param in self.settings.options('auto filling groups'):
                        value = self.settings.get('auto filling groups', param)
                        self.auto_groups_dict[param.upper()] = value

                if self.settings.has_section('prefixes'):
                    for item in self.separators_dict.keys():
                        if self.settings.has_option('prefixes', item):
                            self.separators_dict[item][0] = self.settings.get('prefixes', item)[1:-1]

                if self.settings.has_section('suffixes'):
                    for item in self.separators_dict.keys():
                        if self.settings.has_option('suffixes', item):
                            self.separators_dict[item][1] = self.settings.get('suffixes', item)[1:-1]

                if self.settings.has_section('aliases'):
                    for item in self.aliases_dict.keys():
                        if self.settings.has_option('aliases', item):
                            alias_value = self.settings.get('aliases', item)
                            # Empty alias - default value
                            if alias_value != '':
                                self.aliases_dict[item] = self.settings.get('aliases', item)

                if self.settings.has_section('recent sch'):
                    recent_files = []
                    for recent in self.settings.options('recent sch'):
                        recent_files.append(self.settings.get('recent sch', recent))
                    self.build_recent_menu(recent_files, 'sch')

                if self.settings.has_section('recent lib'):
                    recent_files = []
                    for recent in self.settings.options('recent lib'):
                        recent_files.append(self.settings.get('recent lib', recent))
                    self.build_recent_menu(recent_files, 'lib')
            else:
            # Select settings for importing
                import_settings= {
                    'size_position':False,
                    'column_sizes':False,
                    'comp_fields_panel':False,
                    'general':False,
                    'values':False,
                    'auto_filling_groups':False,
                    'separators':False,
                    'aliases':False,
                    'group_names':False,
                    'complist':False,
                    'recent_sch':False,
                    'recent_lib':False
                    }
                # Load settings from file
                temp_settings = SafeConfigParser()
                temp_settings.readfp(codecs.open(
                    settings_file_name,
                    'r',
                    encoding='utf-8'
                    ))

                selector = gui.SettingsSelector(self)
                selector.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
                if temp_settings.has_section('window'):
                    selector.checkbox_size_position.SetValue(True)
                else:
                    selector.checkbox_size_position.Hide()
                if temp_settings.has_section('column sizes'):
                    selector.checkbox_column_sizes.SetValue(True)
                else:
                    selector.checkbox_column_sizes.Hide()
                if temp_settings.has_section('comp fields panel'):
                    selector.checkbox_comp_fields_panel.SetValue(True)
                else:
                    selector.checkbox_comp_fields_panel.Hide()
                if temp_settings.has_section('general'):
                    selector.checkbox_general.SetValue(True)
                else:
                    selector.checkbox_general.Hide()
                if temp_settings.has_section('values'):
                    selector.checkbox_values.SetValue(True)
                else:
                    selector.checkbox_values.Hide()
                if temp_settings.has_section('auto filling groups'):
                    selector.checkbox_auto_filling_groups.SetValue(True)
                else:
                    selector.checkbox_auto_filling_groups.Hide()
                if temp_settings.has_section('prefixes') or \
                       temp_settings.has_section('suffixes'):
                    selector.checkbox_separators.SetValue(True)
                else:
                    selector.checkbox_separators.Hide()
                if temp_settings.has_section('aliases'):
                    selector.checkbox_aliases.SetValue(True)
                else:
                    selector.checkbox_aliases.Hide()
                if temp_settings.has_section('group names singular') and \
                        temp_settings.has_section('group names plural'):
                    selector.checkbox_group_names.SetValue(True)
                else:
                    selector.checkbox_group_names.Hide()
                if temp_settings.has_section('complist'):
                    selector.checkbox_complist.SetValue(True)
                else:
                    selector.checkbox_complist.Hide()
                if temp_settings.has_section('recent sch'):
                    selector.checkbox_recent_sch.SetValue(True)
                else:
                    selector.checkbox_recent_sch.Hide()
                if temp_settings.has_section('recent lib'):
                    selector.checkbox_recent_lib.SetValue(True)
                else:
                    selector.checkbox_recent_lib.Hide()
                selector.Layout()
                selector.Fit()
                selector.CentreOnParent()
                selector.dialog_buttonOK.SetFocus()
                result = selector.ShowModal()
                if result == wx.ID_OK:
                    for key in import_settings.keys():
                        import_settings[key] = getattr(selector, 'checkbox_' + key).IsChecked()
                    if import_settings['size_position']:
                        if temp_settings.has_option('window', 'x') and \
                            temp_settings.has_option('window', 'y'):
                            x = temp_settings.getint('window', 'x')
                            y = temp_settings.getint('window', 'y')
                            self.SetPosition(wx.Point(x, y))
                        if temp_settings.has_option('window', 'width') and \
                            temp_settings.has_option('window', 'height'):
                            width = temp_settings.getint('window', 'width')
                            height = temp_settings.getint('window', 'height')
                            self.SetClientSize(wx.Size(width, height))
                        if temp_settings.has_option('window', 'maximized'):
                            if temp_settings.getint('window', 'maximized'):
                                self.Maximize()
                        if temp_settings.has_option('window', 'editor width'):
                            if not self.settings.has_section('window'):
                                self.settings.add_section('window')
                            self.settings.set(
                                'window',
                                'editor width',
                                str(temp_settings.getint('window', 'editor width')),
                                )
                    if import_settings['column_sizes']:
                        if hasattr(self, 'grid'):
                            for col in temp_settings.options('column sizes'):
                                col_size = temp_settings.getint('column sizes', col)
                                self.grid.SetColSize(int(col), col_size)
                    if import_settings['comp_fields_panel']:
                        if temp_settings.has_option('comp fields panel', 'width'):
                            width = temp_settings.getint('comp fields panel', 'width')
                            if not self.settings.has_section('comp fields panel'):
                                self.settings.add_section('comp fields panel')
                            self.settings.set('comp fields panel', 'width', str(width))
                            self.splitter_main.SetSashPosition(width)
                        if temp_settings.has_option('comp fields panel', 'show'):
                            if temp_settings.getboolean('comp fields panel', 'show'):
                                self.show_comp_fields_panel()
                            else:
                                self.hide_comp_fields_panel()
                        else:
                            self.hide_comp_fields_panel()
                        if temp_settings.has_option('comp fields panel', 'name width'):
                            width = temp_settings.getint('comp fields panel', 'name width')
                            self.comp_fields_panel_grid.SetColSize(0, width)
                        if temp_settings.has_option('comp fields panel', 'value width'):
                            width = temp_settings.getint('comp fields panel', 'value width')
                            self.comp_fields_panel_grid.SetColSize(1, width)
                    if import_settings['general']:
                        if temp_settings.has_option('general', 'space as dot'):
                            self.grid.space_as_dot = temp_settings.getboolean('general', 'space as dot')
                        if temp_settings.has_option('general', 'show need adjust mark'):
                            self.show_need_adjust_mark = temp_settings.getboolean('general', 'show need adjust mark')
                    if import_settings['values']:
                        for item in self.values_dict.keys():
                            if temp_settings.has_option('values', item):
                                values_list = temp_settings.get('values', item)
                                values_list = values_list.split(SETTINGS_SEPARATOR)
                                if values_list != ['']:
                                    self.values_dict[item] = values_list
                    if import_settings['auto_filling_groups']:
                        if not self.settings.has_section('auto filling groups'):
                            self.settings.add_section('auto filling groups')
                        for param in temp_settings.options('auto filling groups'):
                            value = temp_settings.get('auto filling groups', param)
                            self.auto_groups_dict[param.upper()] = value
                    if import_settings['separators']:
                        if not self.settings.has_section('prefixes'):
                            self.settings.add_section('prefixes')
                        if temp_settings.has_section('prefixes'):
                            for item in self.separators_dict.keys():
                                if temp_settings.has_option('prefixes', item):
                                    self.separators_dict[item][0] = temp_settings.get('prefixes', item)[1:-1]
                        if not self.settings.has_section('suffixes'):
                            self.settings.add_section('suffixes')
                        if temp_settings.has_section('suffixes'):
                            for item in self.separators_dict.keys():
                                if temp_settings.has_option('suffixes', item):
                                    self.separators_dict[item][1] = temp_settings.get('suffixes', item)[1:-1]
                    if import_settings['aliases']:
                        if not self.settings.has_section('aliases'):
                            self.settings.add_section('aliases')
                        for item in self.aliases_dict.keys():
                            if temp_settings.has_option('aliases', item):
                                alias_value = temp_settings.get('aliases', item)
                                # Empty alias - default value
                                if alias_value != '':
                                    self.aliases_dict[item] = alias_value
                    if import_settings['group_names']:
                        self.group_names_dict = {}
                        for name in temp_settings.options('group names singular'):
                            if temp_settings.has_option('group names plural', name):
                                singular = temp_settings.get('group names singular', name)
                                plural = temp_settings.get('group names plural', name)
                                self.group_names_dict[plural] = singular
                    if import_settings['complist']:
                        if not self.settings.has_section('complist'):
                            self.settings.add_section('complist')
                        for param in temp_settings.options('complist'):
                            value = temp_settings.get('complist', param)
                            self.settings.set('complist', param, value)
                    if import_settings['recent_sch']:
                        recent_files = []
                        for recent in temp_settings.options('recent sch'):
                            recent_files.append(temp_settings.get('recent sch', recent))
                        self.build_recent_menu(recent_files, 'sch')
                    if import_settings['recent_lib']:
                        recent_files = []
                        for recent in temp_settings.options('recent lib'):
                            recent_files.append(temp_settings.get('recent lib', recent))
                        self.build_recent_menu(recent_files, 'lib')

    def save_settings(self, settings_file_name=DEFAULT_SETTINGS_FILE_NAME):
        """
        Save settings to configuration file.

        """
        if not self.settings.has_section('window'):
            self.settings.add_section('window')
        if self.IsMaximized():
            self.settings.set('window', 'maximized', '1')
        else:
            self.settings.set('window', 'maximized', '0')
            x, y = self.GetPosition()
            width, height = self.GetClientSize()
            self.settings.set('window', 'x', str(x))
            self.settings.set('window', 'y', str(y))
            self.settings.set('window', 'width', str(width))
            self.settings.set('window', 'height', str(height))

        if not self.settings.has_section('column sizes'):
            self.settings.add_section('column sizes')
        for col in range(self.grid.GetNumberCols()):
            col_size = self.grid.GetColSize(col)
            self.settings.set('column sizes', str(col), str(col_size))

        if not self.settings.has_section('comp fields panel'):
            self.settings.add_section('comp fields panel')
        width = self.comp_fields_panel_grid.GetColSize(0)
        self.settings.set('comp fields panel', 'name width', str(width))
        width = self.comp_fields_panel_grid.GetColSize(1)
        self.settings.set('comp fields panel', 'value width', str(width))
        if self.splitter_main.IsSplit():
            self.settings.set('comp fields panel', 'show', '1')
            width = self.splitter_main.GetSashPosition() - self.splitter_main.GetSize().GetWidth()
            self.settings.set('comp fields panel', 'width', str(width))
        else:
            self.settings.set('comp fields panel', 'show', '0')

        if not self.settings.has_section('values'):
            self.settings.add_section('values')
        for field in self.values_dict.keys():
            field_values = SETTINGS_SEPARATOR.join(self.values_dict[field])
            field_values = field_values.replace('%', '%%')
            self.settings.set('values', field, field_values)

        self.settings.remove_section('auto filling groups')
        if self.auto_groups_dict:
            if not self.settings.has_section('auto filling groups'):
                self.settings.add_section('auto filling groups')
            for suffix, value in self.auto_groups_dict.items():
                self.settings.set('auto filling groups', suffix, value)

        if not self.settings.has_section('prefixes'):
            self.settings.add_section('prefixes')
        for field, separators in self.separators_dict.items():
            self.settings.set('prefixes', field, '"%s"' % separators[0])

        if not self.settings.has_section('suffixes'):
            self.settings.add_section('suffixes')
        for field, separators in self.separators_dict.items():
            self.settings.set('suffixes', field, '"%s"' % separators[1])

        if not self.settings.has_section('aliases'):
            self.settings.add_section('aliases')
        for field, alias in self.aliases_dict.items():
            if field.capitalize() == alias and field != u'значение':
                # Default value stored as empty string
                self.settings.set('aliases', field, '')
            else:
                self.settings.set('aliases', field, alias)


        self.settings.remove_section('group names singular')
        self.settings.add_section('group names singular')
        self.settings.remove_section('group names plural')
        self.settings.add_section('group names plural')
        for i, names in enumerate(self.group_names_dict.items()):
                self.settings.set('group names singular', str(i), names[1])
                self.settings.set('group names plural', str(i), names[0])

        if not self.settings.has_section('general'):
            self.settings.add_section('general')
        self.settings.set( 'general', 'space as dot', str(self.grid.space_as_dot))
        self.settings.set( 'general', 'show need adjust mark', str(self.show_need_adjust_mark))

        self.settings.remove_section('recent sch')
        if self.submenu_recent_sch.GetMenuItemCount() > 0:
            self.settings.add_section('recent sch')
            for index, menuitem in enumerate(self.submenu_recent_sch.GetMenuItems()):
                self.settings.set(
                        'recent sch',
                        str(index),
                        menuitem.GetItemLabel()
                        )

        self.settings.remove_section('recent lib')
        if self.submenu_recent_lib.GetMenuItemCount() > 0:
            self.settings.add_section('recent lib')
            for index, menuitem in enumerate(self.submenu_recent_lib.GetMenuItems()):
                self.settings.set(
                        'recent lib',
                        str(index),
                        menuitem.GetItemLabel()
                        )

        self.settings.write(codecs.open(settings_file_name, 'w', encoding='utf-8'))

    def init_grid(self):
        """
        Initialize the grid for the components.

        """
        # Save grid options
        if hasattr(self, 'grid'):
            if not self.settings.has_section('column sizes'):
                self.settings.add_section('column sizes')
            for col in range(self.grid.GetNumberCols()):
                col_size = self.grid.GetColSize(col)
                self.settings.set('column sizes', str(col), str(col_size))

            if not self.settings.has_section('general'):
                self.settings.add_section('general')
            self.settings.set( 'general', 'space as dot', str(self.grid.space_as_dot))

            self.GetSizer().Remove(self.panel_components.GetSizer())
            self.grid.Destroy()

        # New grid
        self.grid = Grid(self.panel_components, self)
        # Events
        self.grid.Bind(
            wx.grid.EVT_GRID_SELECT_CELL,
            self.on_select_cell
            )
        self.grid.Bind(
            wx.grid.EVT_GRID_RANGE_SELECT,
            self.on_select
            )
        self.grid.Bind(
            wx.grid.EVT_GRID_CELL_CHANGE,
            self.on_grid_change
            )
        self.grid.Bind(
            wx.EVT_CONTEXT_MENU,
            self.on_grid_popup
            )
        self.grid.Bind(
            wx.grid.EVT_GRID_CELL_RIGHT_CLICK,
            self.on_grid_popup
            )
        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)
        self.panel_components.SetSizer(sizer)
        self.panel_components.Layout()
        sizer.Fit(self.panel_components)
        self.Layout()
        self.grid.SetFocus()

        # Restore grid options
        if hasattr(self, 'settings'):
            if self.settings.has_section('column sizes'):
                for col in self.settings.options('column sizes'):
                    col_size = self.settings.getint('column sizes', col)
                    self.grid.SetColSize(int(col), col_size)
            if self.settings.has_section('general'):
                if self.settings.has_option('general', 'space as dot'):
                    self.grid.space_as_dot = self.settings.getboolean('general', 'space as dot')

    def apply_auto_groups(self):
        """
        Set group names defined for component type.

        """
        for row in range(self.grid.GetNumberRows()):
            group_name = self.grid.GetCellValue(row, 1)
            if group_name == u'':
                ref = self.grid.GetCellValue(row, 2)
                ref = self.grid.get_pure_ref(ref)
                ref_type = ref.rstrip('0123456789')
                for pattern in self.auto_groups_dict.keys():
                    re_pattern = pattern.replace('?', '.?')
                    re_pattern = re_pattern.replace('*', '.*')
                    if re.match(re_pattern, ref_type) \
                            and self.auto_groups_dict[pattern].startswith('1'):
                        group_name = self.auto_groups_dict[pattern][1:]
                        self.grid.set_cell_value(row, 1, group_name)
                        break
        if self.grid.is_changed():
            self.on_grid_change()

    def splitter_mainOnIdle(self, event):
        """
        Overwrite event handler generated by wxFormBuilder
        for initializing sash position after main window showing.

        """
        self.splitter_main.Unbind(wx.EVT_IDLE)

        if self.settings.has_section('comp fields panel'):
            if self.settings.has_option('comp fields panel', 'name width'):
                width = self.settings.getint('comp fields panel', 'name width')
                self.comp_fields_panel_grid.SetColSize(0, width)
            if self.settings.has_option('comp fields panel', 'value width'):
                width = self.settings.getint('comp fields panel', 'value width')
                self.comp_fields_panel_grid.SetColSize(1, width)
            if self.settings.has_option('comp fields panel', 'show'):
                if self.settings.getboolean('comp fields panel', 'show'):
                    self.show_comp_fields_panel()
                    return
        self.hide_comp_fields_panel()

    def on_splitter_size_changed(self, event):
        """
        Update position of splitter sash.

        """
        if self.splitter_main.IsSplit():
            width = -350
            if hasattr(self, 'settings'):
                if self.settings.has_section('comp fields panel'):
                    if self.settings.has_option('comp fields panel', 'width'):
                        width = self.settings.getint('comp fields panel', 'width')
            self.splitter_main.SetSashPosition(width)
        else:
            event.Skip()

    def on_splitter_sash_changed(self, event):
        """
        Save new position of splitter sash.

        """
        if not self.settings.has_section('comp fields panel'):
            self.settings.add_section('comp fields panel')
        width = self.splitter_main.GetSashPosition() - self.splitter_main.GetSize().GetWidth()
        self.settings.set('comp fields panel', 'width', str(width))
        event.Skip()

    def on_comp_fields_panel_grid_select(self, event):
        """
        Clear selection.

        """
        self.comp_fields_panel_grid.Unbind(
            wx.grid.EVT_GRID_RANGE_SELECT
            )
        self.comp_fields_panel_grid.ClearSelection()
        self.comp_fields_panel_grid.Bind(
            wx.grid.EVT_GRID_RANGE_SELECT,
            self.on_comp_fields_panel_grid_select
            )

    def on_comp_fields_panel_grid_popup(self, event):
        """
        Popup menu for grid from component fields panel.

        """
        def on_copy(event):
            """
            Copy text from cell.

            """
            if wx.TheClipboard.Open():
                row = self.comp_fields_panel_grid.GetGridCursorRow()
                col = self.comp_fields_panel_grid.GetGridCursorCol()
                text = self.comp_fields_panel_grid.GetCellValue(row, col)
                wx.TheClipboard.SetData(wx.TextDataObject(text))
                wx.TheClipboard.Close()

        menu = wx.Menu()
        menu.copy_id = wx.NewId()
        item = wx.MenuItem(menu, menu.copy_id, u'Копировать')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-copy_small.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, on_copy, item)
        self.comp_fields_panel_grid.PopupMenu(menu, event.GetPosition())

    def show_comp_fields_panel(self):
        """
        Show component fields panel.

        """
        width = -350
        if self.settings.has_section('comp fields panel'):
            if self.settings.has_option('comp fields panel', 'width'):
                width = self.settings.getint('comp fields panel', 'width')
        self.panel_comp_fields.Show()
        self.splitter_main.SplitVertically(
                self.panel_components,
                self.panel_comp_fields,
                width
                )
        self.update_comp_fields_panel()

    def hide_comp_fields_panel(self):
        """
        Hide components fields panel.

        """
        if self.splitter_main.IsSplit():
            self.splitter_main.Unsplit()
        self.panel_comp_fields.Hide()

    def update_comp_fields_panel(self, row=None):
        """
        Show all fields for selected component.

        """
        def component_has_ref(comp, ref):
            """
            Returns true if component has specified reference.

            """
            if comp.fields[0].text == ref:
                return True
            else:
                if hasattr(comp, 'path_and_ref'):
                    for path_and_ref in comp.path_and_ref:
                        if path_and_ref[1] == ref:
                            return True
            return False

        if not self.splitter_main.IsSplit():
            return
        if self.comp_fields_panel_grid.GetNumberRows():
            self.comp_fields_panel_grid.DeleteRows(
                    0,
                    self.comp_fields_panel_grid.GetNumberRows()
                    )
        if self.grid.GetNumberRows() > 0:
            self.comp_fields_panel_grid.Show()
            if row == None:
                row = self.grid.GetGridCursorRow()
            if self.library:
                name = self.grid.GetCellValue(row, 4)
                self.comp_fields_panel_ref_label.SetLabelText(name)
                for component in self.library.components:
                    if component.fields[1].text == name:
                        self.comp_fields_panel_file_label.SetLabelText(self.library.lib_name)
                        for i, field in enumerate(component.fields):
                            self.comp_fields_panel_grid.AppendRows()
                            self.comp_fields_panel_grid.SetRowLabelValue(i, str(field.number))
                            if i == 0:
                                self.comp_fields_panel_grid.SetCellValue(i, 0, u'Обозначение')
                                self.comp_fields_panel_grid.SetCellValue(i, 1, field.text)
                            elif i == 1:
                                self.comp_fields_panel_grid.SetCellValue(i, 0, u'Значение')
                                self.comp_fields_panel_grid.SetCellValue(i, 1, field.text)
                            elif i == 2:
                                self.comp_fields_panel_grid.SetCellValue(i, 0, u'Посад.место')
                                self.comp_fields_panel_grid.SetCellValue(i, 1, field.text)
                            elif i == 3:
                                self.comp_fields_panel_grid.SetCellValue(i, 0, u'Документация')
                                self.comp_fields_panel_grid.SetCellValue(i, 1, field.text)
                            else:
                                if hasattr(field, 'name'):
                                    self.comp_fields_panel_grid.SetCellValue(i, 0, field.name)
                                self.comp_fields_panel_grid.SetCellValue(i, 1, field.text)
                        break
            else:
                ref = self.grid.GetCellValue(row, 2)
                self.comp_fields_panel_ref_label.SetLabelText(ref)
                ref = self.grid.get_pure_ref(ref)
                refs = [ref]
                for schematic in self.schematics:
                    for item in schematic.items:
                        if item.__class__.__name__ == u'Comp':
                            if component_has_ref(item, ref):
                                if hasattr(item, 'path_and_ref'):
                                    for path_and_ref in item.path_and_ref:
                                        refs.append(path_and_ref[1])
                                refs = list(set(refs))
                                refs.remove(ref)
                                refs.insert(0, ref)
                                self.comp_fields_panel_ref_label.SetLabelText(', '.join(refs))
                                self.comp_fields_panel_file_label.SetLabelText(schematic.sch_name)
                                for i, field in enumerate(item.fields):
                                    self.comp_fields_panel_grid.AppendRows()
                                    self.comp_fields_panel_grid.SetRowLabelValue(i, str(field.number))
                                    if i == 0:
                                        self.comp_fields_panel_grid.SetCellValue(i, 0, u'Обозначение')
                                        self.comp_fields_panel_grid.SetCellValue(i, 1, field.text)
                                    elif i == 1:
                                        self.comp_fields_panel_grid.SetCellValue(i, 0, u'Значение')
                                        self.comp_fields_panel_grid.SetCellValue(i, 1, field.text)
                                    elif i == 2:
                                        self.comp_fields_panel_grid.SetCellValue(i, 0, u'Посад.место')
                                        self.comp_fields_panel_grid.SetCellValue(i, 1, field.text)
                                    elif i == 3:
                                        self.comp_fields_panel_grid.SetCellValue(i, 0, u'Документация')
                                        self.comp_fields_panel_grid.SetCellValue(i, 1, field.text)
                                    else:
                                        if hasattr(field, 'name'):
                                            self.comp_fields_panel_grid.SetCellValue(i, 0, field.name)
                                        self.comp_fields_panel_grid.SetCellValue(i, 1, field.text)
                                break
        else:
            self.comp_fields_panel_ref_label.SetLabelText('...')
            self.comp_fields_panel_file_label.SetLabelText('')
            self.comp_fields_panel_grid.Hide()
        self.panel_comp_fields.Layout()

    def add_to_recent(self, file_name, file_type):
        """
        Add file to the menu with list of the recent files.

        """
        menu = None
        if file_type == 'sch':
            menu = self.submenu_recent_sch
        elif file_type == 'lib':
            menu = self.submenu_recent_lib

        recent_files = []
        for recent_menuitem in menu.GetMenuItems():
            recent_files.append(recent_menuitem.GetLabel())
        if file_name in recent_files:
            recent_files.remove(file_name)
        recent_files.insert(0, file_name)
        recent_files = recent_files[:10]
        self.build_recent_menu(recent_files, file_type)

    def remove_from_recent(self, file_name, file_type):
        """
        Remove file from the menu with list of the recent files.

        """
        menu = None
        if file_type == 'sch':
            menu = self.submenu_recent_sch
        elif file_type == 'lib':
            menu = self.submenu_recent_lib

        recent_files = []
        for recent_menuitem in menu.GetMenuItems():
            recent_files.append(recent_menuitem.GetLabel())
        if file_name in recent_files:
            recent_files.remove(file_name)
        self.build_recent_menu(recent_files, file_type)

    def build_recent_menu(self, file_names, file_type):
        """
        Fill submenu with recent files.

        """
        id_offset = 0
        menu = None
        event_handler = None
        if file_type == 'sch':
            id_offset += 0
            menu = self.submenu_recent_sch
            event_handler = self.on_recent_sch
        elif file_type == 'lib':
            id_offset += 10
            menu = self.submenu_recent_lib
            event_handler = self.on_recent_lib

        for menuitem in menu.GetMenuItems():
            menu.Delete(menuitem.GetId())
        if file_names:
            for index, file_name in enumerate(file_names):
                menu.AppendItem(wx.MenuItem(
                    menu,
                    ID_RECENT + id_offset + index,
                    file_name,
                    wx.EmptyString,
                    wx.ITEM_NORMAL
                    ))
            self.Bind(
                    wx.EVT_MENU,
                    event_handler,
                    id = ID_RECENT + id_offset,
                    id2 = ID_RECENT + id_offset + len(file_names) - 1
                    )

    def get_schematic_values(self):
        """
        Returns list of fields values of components from schematic.

        """
        values = []
        complist = CompList()
        for schematic in self.schematics:
            for comp in complist.get_components(schematic.sch_name, True):
                # Skip components with not supported ref type
                if not re.match(REF_REGEXP, comp.fields[0].text):
                    continue
                # Skip parts of the same component
                for row in values:
                    if comp.fields[0].text == row[2]:
                        break
                else:
                    row = [
                        u'1', # Used
                        u'',  # Group
                        comp.fields[0].text,  # Reference
                        u'',  # Mark
                        u'',  # Value
                        u'',  # Accuracy
                        u'',  # Type
                        u'',  # GOST
                        u'',  # Comment
                        schematic.sch_name  # Schematic file name
                        ]
                    if self.aliases_dict[u'значение'] == u'':
                        row[4] = comp.fields[1].text
                    for field in comp.fields:
                        if hasattr(field, 'name'):
                            if field.name == u'Исключён из ПЭ':
                                row[0] = u'0'
                            if field.name == self.aliases_dict[u'группа']:
                                row[1] = field.text
                            if field.name == u'Подбирают при регулировании':
                                row[2] += '*'
                            if field.name == self.aliases_dict[u'марка']:
                                row[3] = field.text
                            if self.aliases_dict[u'значение'] != u'' and \
                                    field.name == self.aliases_dict[u'значение']:
                                row[4] = field.text
                            if field.name == self.aliases_dict[u'класс точности']:
                                row[5] = field.text
                            if field.name == self.aliases_dict[u'тип']:
                                row[6] = field.text
                            if field.name == self.aliases_dict[u'стандарт']:
                                row[7] = field.text
                            if field.name == self.aliases_dict[u'примечание']:
                                row[8] = field.text
                    if hasattr(comp, 'path_and_ref'):
                        prefix = '(*)'
                        # Do not mark components that only has parts (not copies)
                        # on different sheets.
                        for ref in comp.path_and_ref:
                            if re.match(REF_REGEXP, ref[1]) \
                                    and ref[1] != comp.fields[0].text:
                                # Has copy
                                break
                        else:
                            prefix = ''
                        for ref in comp.path_and_ref:
                            # Skip components with not supported ref type
                            if not re.match(REF_REGEXP, ref[1]):
                                continue
                            # Skip parts of the same comp from different sheets
                            for value in values:
                                tmp_ref = self.grid.get_pure_ref(value[2])
                                if tmp_ref == ref[1]:
                                    break
                            else:
                                new_row = list(row)
                                if ref[1] == comp.fields[0].text:
                                    new_row[2] = prefix + comp.fields[0].text
                                else:
                                    new_row[2] = '({}){}'.format(comp.fields[0].text, ref[1])
                                # Copy "need adjust" mark
                                if row[2].endswith('*'):
                                    new_row[2] += '*'
                                values.append(new_row)
                    else:
                        values.append(row)
        return values

    def set_schematic_values(self, values):
        """
        Set values to fields of the components of schematic.

        """
        sorted_values = sorted(values, key=itemgetter(-1))
        field_names = {
            1:self.aliases_dict[u'группа'],
            3:self.aliases_dict[u'марка'],
            4:self.aliases_dict[u'значение'],
            5:self.aliases_dict[u'класс точности'],
            6:self.aliases_dict[u'тип'],
            7:self.aliases_dict[u'стандарт'],
            8:self.aliases_dict[u'примечание']
            }
        for schematic in self.schematics:
            for item in schematic.items:
                if item.__class__.__name__ == 'Comp':
                    # Only components with supported ref type
                    if re.match(REF_REGEXP, item.fields[0].text):
                        for value in sorted_values:
                            # Skip copies of the one component (see 'path_and_ref' in Comp)
                            if self.grid.comp_is_copy(value[2]):
                                continue
                            if self.grid.get_pure_ref(value[2]) == item.fields[0].text:
                                # Default field of "value"
                                if field_names[4] == u'':
                                    item.fields[1].text = value[4]
                                for index, field_name in field_names.items():
                                    # Skip "value" if used standard field for it
                                    if index == 4 and field_name == u'':
                                        continue
                                    if value[index] != u'':
                                        for field in item.fields:
                                            if hasattr(field, 'name'):
                                                if field.name == field_name:
                                                    field.text = value[index]
                                                    break
                                        else:
                                            str_field = u'F ' + str(len(item.fields))
                                            str_field += u' "' + value[index] + u'" '
                                            str_field += u' H ' + str(item.pos_x) + u' ' + str(item.pos_y) + u' 60'
                                            str_field += u' 0001 C CNN'
                                            str_field += u' "' + field_name + '"'
                                            item.fields.append(schematic.Comp.Field(str_field))
                                    else:
                                        for field_index, field in enumerate(item.fields):
                                            if hasattr(field, 'name'):
                                                if field.name == field_name:
                                                    del item.fields[field_index]
                                                    break

                                if value[0] == '0':
                                    # Check if field present
                                    for field in item.fields:
                                        if hasattr(field, 'name'):
                                            if field.name == u'Исключён из ПЭ':
                                                # Already present
                                                break
                                    else:
                                        # Create field
                                        str_field = u'F ' + str(len(item.fields))
                                        str_field += u' "~" '
                                        str_field += u' H ' + str(item.pos_x) + u' ' + str(item.pos_y) + u' 60'
                                        str_field += u' 0001 C CNN'
                                        str_field += u' "Исключён из ПЭ"'
                                        item.fields.append(schematic.Comp.Field(str_field))
                                else:
                                    # Delete field
                                    for field_index, field in enumerate(item.fields):
                                        if hasattr(field, 'name'):
                                            if field.name == u'Исключён из ПЭ':
                                                del item.fields[field_index]
                                                break

                                # By default, every time create new field with correct position.
                                # But if field is already present and its value was changed,
                                # then leave field as is ("manual mode")
                                if value[2].endswith('*'):
                                    for field_index, field in enumerate(item.fields):
                                        if hasattr(field, 'name'):
                                            if field.name == u'Подбирают при регулировании':
                                                if field.text == '*':
                                                    # Recreate field
                                                    del item.fields[field_index]
                                                else:
                                                    # Leave field as is
                                                    break
                                    else:
                                        # Create field
                                        # Place field value behind reference
                                        h_offset = 0
                                        v_offset = 0
                                        # Orientations that inverts justify of text
                                        if item.fields[0].orientation == 'H':
                                            invert_orient = (
                                                    (-1, 0, 0, 1),
                                                    (0, 1, 1, 0),
                                                    (-1, 0, 0, -1),
                                                    (0, -1, 1, 0)
                                                    )
                                        else:
                                            invert_orient = (
                                                    (0, -1, -1, 0),
                                                    (-1, 0, 0, 1),
                                                    (1, 0, 0, 1),
                                                    (0, -1, 1, 0)
                                                    )
                                        # Calculate correct position of "*" mark
                                        # according to field justify and component orientation
                                        if item.fields[0].hjustify == 'L':
                                            if item.orient_matrix in invert_orient:
                                                h_offset = -1 * item.fields[0].size / 2
                                            else:
                                                h_offset = item.fields[0].size * (len(item.fields[0].text) + 0.5)
                                        elif item.fields[0].hjustify == 'R':
                                            if item.orient_matrix in invert_orient:
                                                h_offset = item.fields[0].size * (len(item.fields[0].text) + 0.5)
                                                h_offset *= -1
                                            else:
                                                h_offset = item.fields[0].size / 2
                                        elif item.fields[0].hjustify == 'C':
                                            h_offset = item.fields[0].size * (len(item.fields[0].text) + 1) / 2
                                            if item.orient_matrix in invert_orient:
                                                h_offset *= -1
                                        # Swap H and V offsets for vertical orientation
                                        if item.fields[0].orientation == 'V':
                                            v_offset = h_offset
                                            h_offset = 0

                                        str_field = u'F {} "*" {} {} {} {} {} {} {}{}{} "Подбирают при регулировании"'.format(
                                            len(item.fields),
                                            item.fields[0].orientation,
                                            item.fields[0].pos_x + int(h_offset),
                                            item.fields[0].pos_y + int(v_offset),
                                            item.fields[0].size,
                                            {True:'0000', False:'0001'}[self.show_need_adjust_mark],
                                            'C',
                                            item.fields[0].vjustify,
                                            {True:'I', False:'N'}[item.fields[0].italic],
                                            {True:'B', False:'N'}[item.fields[0].italic]
                                            )
                                        item.fields.append(schematic.Comp.Field(str_field))
                                else:
                                    # Delete field if it present
                                    for field_index, field in enumerate(item.fields):
                                        if hasattr(field, 'name'):
                                            if field.name == u'Подбирают при регулировании':
                                                del item.fields[field_index]
                                                break
                                # Update fields numbers
                                for field_index, field in enumerate(item.fields):
                                    field.number = field_index

    def get_library_values(self):
        """
        Returns list of fields values of components from library.

        """
        values = []
        for comp in self.library.components:
            if comp.reference.startswith('#'):
                continue
            row = [
                u'1', # Used
                u'',  # Group
                comp.fields[0].text,  # Reference
                u'',  # Mark
                comp.fields[1].text,  # Value
                u'',  # Acceracy
                u'',  # Type
                u'',  # GOST
                u'',  # Comment
                self.library.lib_name  # Library name
                ]
            for field in comp.fields:
                if hasattr(field, 'name'):
                    if field.name == self.aliases_dict[u'группа']:
                        row[1] = field.text
                    if field.name == self.aliases_dict[u'марка']:
                        row[3] = field.text
                    if field.name == self.aliases_dict[u'класс точности']:
                        row[5] = field.text
                    if field.name == self.aliases_dict[u'тип']:
                        row[6] = field.text
                    if field.name == self.aliases_dict[u'стандарт']:
                        row[7] = field.text
                    if field.name == self.aliases_dict[u'примечание']:
                        row[8] = field.text
            values.append(row)
        return values

    def set_library_values(self, values):
        """
        Set values to fields of the components of library.

        """
        sorted_values = values[:]
        field_names = {
            1:self.aliases_dict[u'группа'],
            3:self.aliases_dict[u'марка'],
            5:self.aliases_dict[u'класс точности'],
            6:self.aliases_dict[u'тип'],
            7:self.aliases_dict[u'стандарт'],
            8:self.aliases_dict[u'примечание']
            }
        for comp in self.library.components:
            if not comp.reference.startswith('#'):
                for value in sorted_values:
                    if value[4] == comp.name:
                        for index, field_name in field_names.items():
                            if value[index] != u'':
                                for field in comp.fields:
                                    if hasattr(field, 'name'):
                                        if field.name == field_name:
                                            field.text = value[index]
                                            break
                                else:
                                    str_field = u'F' + str(len(comp.fields))
                                    str_field += u' "' + value[index] + u'" '
                                    str_field += u' 0 0 60 H I C CNN'
                                    str_field += u' "' + field_name + '"'
                                    comp.fields.append(self.library.Component.Field(str_field))
                            else:
                                for field_index, field in enumerate(comp.fields):
                                    if hasattr(field, 'name'):
                                        if field.name == field_name:
                                            del comp.fields[field_index]
                        for field_index, field in enumerate(comp.fields):
                            field.number = field_index

    def get_checked_cols(self):
        """
        Returns list of indexes of selected columns from field selector.

        """

        def on_checkbox_all_clicked(event):
            """
            Check/uncheck all fields in field selector.

            """
            state = selector.checkbox_all.GetValue()
            for col in (1, 3, 4, 5, 6, 7, 8):
                checkbox = getattr(selector, 'checkbox_{}'.format(col))
                checkbox.SetValue(state)

        selector = gui.FieldSelector(self)
        selector.checkbox_all.Bind(wx.EVT_CHECKBOX, on_checkbox_all_clicked)
        if self.library:
            selector.checkbox_4.SetValue(False)
            selector.checkbox_4.Hide()
            selector.Layout()
            selector.GetSizer().Fit(selector)
        result = selector.ShowModal()
        selected_cols = []
        if result == wx.ID_OK:
            for i in range(1, 9):
                if i == 2:
                    continue
                if getattr(selector, 'checkbox_' + str(i)).IsChecked():
                    selected_cols.append(i)
        return selected_cols

    def on_recent_sch(self, event):
        """
        Open recent schematic file.

        """
        file_name = self.submenu_recent_sch.GetLabel(event.GetId())
        self.on_open_sch(sch_file_name=file_name)

    def on_recent_lib(self, event):
        """
        Open recent library file.

        """
        file_name = self.submenu_recent_lib.GetLabel(event.GetId())
        self.on_open_lib(lib_file_name=file_name)

    def on_update_toolbar(self, event):
        """
        Change enable/disable future of the toolbar as same as menuitem.

        """
        menuitem = event.GetId()
        if menuitem > gui.ID_OPEN_SCH:
            self.toolbar.EnableTool(menuitem, self.menubar.IsEnabled(menuitem))
            if menuitem == gui.ID_COMP_FIELDS_PANEL:
                if self.splitter_main.IsSplit():
                    self.toolbar.ToggleTool(menuitem, True)
                    self.menubar.Check(menuitem, True)
                else:
                    self.toolbar.ToggleTool(menuitem, False)
                    self.menubar.Check(menuitem, False)
        event.Skip()

    def on_adjust_flag_switch(self, event):
        """
        Switch "need adjusting" flag state.

        """
        menu = event.GetEventObject()
        rows = self.grid.GetSelectedRows()
        for row in rows:
            # By default flag is unset
            value = self.grid.GetCellValue(row, 2).rstrip('*')
            # Set flag if needed
            if menu.IsChecked(menu.adjust_id):
                value += '*'
            self.grid.set_cell_value(row, 2, value)
        if self.grid.is_changed():
            self.on_grid_change()

    def on_grid_change(self, event=None):
        """
        Update GUI after changes.

        """
        self.grid.undo_buffer.append(self.grid.get_values())
        self.grid.redo_buffer = []
        self.menuitem_redo.Enable(False)
        if len(self.grid.undo_buffer) > 1:
            self.menuitem_undo.Enable(True)
        else:
            self.menuitem_undo.Enable(False)
        self.saved = False
        if self.library:
            self.menuitem_save_lib.Enable(True)
        else:
            self.menuitem_save_sch.Enable(True)

    def on_grid_popup(self, event):
        """
        Show popup menu for grid.

        """
        if self.grid.IsCellEditControlEnabled():
            event.Skip()
            return

        menu = wx.Menu()

        menu.copy_id = wx.NewId()
        menu.cut_id = wx.NewId()
        menu.paste_id = wx.NewId()
        menu.edit_id = wx.NewId()
        menu.clear_id = wx.NewId()
        menu.adjust_id = wx.NewId()

        item = wx.MenuItem(menu, menu.copy_id, u'Копировать поля')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-copy.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_copy, item)
        menu.Enable(menu.copy_id, self.menuitem_copy.IsEnabled())

        item = wx.MenuItem(menu, menu.cut_id, u'Вырезать поля…')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-cut.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_cut, item)
        menu.Enable(menu.cut_id, self.menuitem_cut.IsEnabled())

        item = wx.MenuItem(menu, menu.paste_id, u'Вставить поля…')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-paste.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_paste, item)
        menu.Enable(menu.paste_id, self.menuitem_paste.IsEnabled())

        menu.Append(wx.ID_SEPARATOR)

        item = wx.MenuItem(menu, menu.edit_id, u'Редактировать поля…')
        item.SetBitmap(wx.Bitmap(u'bitmaps/gtk-edit.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_edit_fields, item)
        menu.Enable(menu.edit_id, self.menuitem_edit.IsEnabled())

        item = wx.MenuItem(menu, menu.clear_id, u'Очистить поля…')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-clear.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_clear_fields, item)
        menu.Enable(menu.clear_id, self.menuitem_clear.IsEnabled())

        menu.Append(wx.ID_SEPARATOR)

        item = wx.MenuItem(menu, menu.adjust_id, u'Подбирают при регулировании', kind=wx.ITEM_CHECK)
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_adjust_flag_switch, item)
        menu.Enable(menu.adjust_id, self.menuitem_edit.IsEnabled())
        rows = self.grid.GetSelectedRows()
        if rows:
            for row in rows:
                if not self.grid.GetCellValue(row, 2).endswith('*'):
                    item.Check(False)
                    break
            else:
                item.Check(True)
        else:
            menu.Enable(menu.adjust_id, False)

        self.grid.PopupMenu(menu, event.GetPosition())
        menu.Destroy()

    def on_undo(self, event):
        """
        Undo last change in the grid.

        """
        self.grid.redo_buffer.append(self.grid.undo_buffer[-1])
        del self.grid.undo_buffer[-1]
        self.grid.set_values(self.grid.undo_buffer[-1])
        if len(self.grid.undo_buffer) == 1:
            self.menuitem_undo.Enable(False)
        self.menuitem_redo.Enable(True)
        self.saved = False
        if self.library:
            self.menuitem_save_lib.Enable(True)
        else:
            self.menuitem_save_sch.Enable(True)

    def on_redo(self, event):
        """
        Redo previous change to the grid.

        """
        self.grid.undo_buffer.append(self.grid.redo_buffer[-1])
        self.grid.set_values(self.grid.redo_buffer[-1])
        del self.grid.redo_buffer[-1]
        if len(self.grid.redo_buffer) == 0:
            self.menuitem_redo.Enable(False)
        self.menuitem_undo.Enable(True)
        self.saved = False
        if self.library:
            self.menuitem_save_lib.Enable(True)
        else:
            self.menuitem_save_sch.Enable(True)

    def on_tool(self, event):
        """
        Switch visible of the toolbar.

        """
        if event.IsChecked():
            self.toolbar.Show()
        else:
            self.toolbar.Hide()
        self.SendSizeEvent()

    def on_comp_fields_panel(self, event):
        """
        Switch visible of the component fields panel.

        """
        if event.IsChecked():
            self.show_comp_fields_panel()
        else:
            self.hide_comp_fields_panel()
        event.Skip()

    def on_copy(self, event=None):
        """
        Copy values of the fields.

        """
        if len(self.grid.GetSelectedRows()) > 1:
            if wx.MessageBox(
                u'В таблице выделено несколько элементов!\n' \
                u'Будут скопированы поля только из первого выделенного элемента.\n' \
                u'Продолжить?',
                u'Внимание!',
                wx.ICON_QUESTION|wx.YES_NO, self
                ) == wx.NO:

                return
        self.buffer = []
        row = self.grid.GetSelectedRows()[0]
        for col in range(1, 9):
            if col == 2:
                self.buffer.append(u'')
                continue
            self.buffer.append(self.grid.GetCellValue(row, col))
        # Update state of menu entries and toolbar buttons
        self.on_select()

    def on_cut(self, event):
        """
        Cut values of the fields.

        """
        if len(self.grid.GetSelectedRows()) > 1:
            if wx.MessageBox(
                    u'В таблице выделено несколько элементов!\n' \
                    u'Будут вырезаны поля только из первого выделенного элемента.\n' \
                    u'Продолжить?',
                    u'Внимание!',
                    wx.ICON_QUESTION|wx.YES_NO, self
                    ) == wx.NO:
                return

        self.buffer = []
        selected_cols = self.get_checked_cols()
        row = self.grid.GetSelectedRows()[0]
        for col in range(1, 9):
            if col == 2:
                self.buffer.append(u'')
                continue
            self.buffer.append(self.grid.GetCellValue(row, col))
            if col in selected_cols:
                self.grid.set_cell_value(row, col, u'')
        # Update state of menu entries and toolbar buttons
        self.on_select()
        if self.grid.is_changed():
            self.on_grid_change()

    def on_paste(self, event):
        """
        Paste values to the fields of the selected components from buffer.

        """
        def on_button(event):
            for row in selected_rows:
                for col in range(1, col_num):
                    if col == 2:
                        continue
                    if self.library and col == 4:
                        continue
                    new_value = getattr(editor, 'editor_ctrl_%i' % col).get_value()
                    if new_value == u'<не изменять>':
                        continue
                    else:
                        self.grid.set_cell_value(row, col, new_value)
            if self.grid.is_changed():
                self.on_grid_change()
            event.Skip()

        def on_size(event):
            """
            Save dialog width

            """
            if not self.settings.has_section('window'):
                self.settings.add_section('window')
            self.settings.set(
                'window',
                'editor width',
                str(editor.GetSize().GetWidth())
                )
            event.Skip()

        if len(self.grid.GetSelectedRows()) >= 1:

            editor = gui.EditorDialog(self)
            editor.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
            editor.SetTitle(u'Вставка полей')
            editor.checkbox.Hide()
            editor.space_as_dot = self.grid.space_as_dot
            col_num = self.grid.GetNumberCols()
            selected_rows = self.grid.GetSelectedRows()
            for i in range(1, col_num):
                if i == 2:
                    continue
                cur_editor_ctrl = getattr(editor, 'editor_ctrl_%i' % i)
                cur_editor_ctrl.set_items(
                    [self.buffer[i - 1]],
                    None,
                    u'<не изменять>'
                    )
                cur_editor_ctrl.text_ctrl.SetValue(self.buffer[i - 1])
            # Layout
            if self.library:
                editor.statictext_4.Hide()
                editor.editor_ctrl_4.Hide()
            editor.Layout()
            editor.Fit()
            min_size = editor.GetSize()
            editor.SetSizeHints(
                min_size.GetWidth(),
                min_size.GetHeight(),
                -1,
                min_size.GetHeight()
                )
            # Load dialog width
            if self.settings.has_section('window'):
                if self.settings.has_option('window', 'editor width'):
                   editor.SetSize(
                        wx.Size(
                            self.settings.getint('window', 'editor width'),
                            -1
                            )
                        )
            editor.CenterOnParent()
            # Events
            editor.Bind(wx.EVT_SIZE, on_size)
            editor.dialog_buttonsOK.Bind(wx.EVT_BUTTON, on_button)
            # Need to use Show instead of ShowModal otherwise EditorCtrlPopup
            # was freezed.
            editor.Show()

    def on_select(self, event=None):
        """
        Process selection event.

        """
        writing_enabled = False
        selected_rows = self.grid.GetSelectedRows()
        for row in selected_rows:
            if not self.grid.comp_is_copy(
                    self.grid.GetCellValue(row, 2)
                    ):
                writing_enabled = True

        if self.grid.GetSelectedRows():
            self.menuitem_copy.Enable(True)
            self.menuitem_cut.Enable(writing_enabled)
            self.menuitem_edit.Enable(writing_enabled)
            self.menuitem_clear.Enable(writing_enabled)
            self.menuitem_paste.Enable(writing_enabled and bool(self.buffer))
        else:
            self.menuitem_copy.Enable(False)
            self.menuitem_cut.Enable(False)
            self.menuitem_edit.Enable(False)
            self.menuitem_clear.Enable(False)
            self.menuitem_paste.Enable(False)
        if event:
            event.Skip()

    def on_select_cell(self, event=None):
        """
        Process cell selection event.

        """
        self.update_comp_fields_panel(event.GetRow())

    def on_open_sch(self, event=None, sch_file_name=''):
        """
        Load all components from selected schematic
        (include hierarchical sheets) to the table for editing.

        """
        if not self.saved:
            if wx.MessageBox(
                u'Последние изменения в полях компонентов не были сохранены!\n' \
                u'Продолжить?',
                u'Внимание!',
                wx.ICON_QUESTION|wx.YES_NO, self
                ) == wx.NO:

                return
        if sch_file_name:
            self.schematic_file = sch_file_name
        else:
            open_sch_dialog = wx.FileDialog(
                self,
                u'Выбор файла схемы',
                u'',
                u'',
                u'Схема (*.sch)|*.sch|Все файлы (*.*)|*.*',
                wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
                )
            if open_sch_dialog.ShowModal() == wx.ID_CANCEL:
                return
            self.schematic_file = open_sch_dialog.GetPath()

        try:
            # Set cursor to 'wait'
            wx.BeginBusyCursor()
            wx.SafeYield()

            # Reset title
            self.SetTitle('kicadbom2spec')

            # Menu & Toolbar
            self.menuitem_complist.Enable(False)
            self.menuitem_save_sch.Enable(False)
            self.menuitem_save_sch_as.Enable(False)
            self.menuitem_save_lib.Enable(False)
            self.menuitem_save_lib_as.Enable(False)
            self.menuitem_copy.Enable(False)
            self.menuitem_cut.Enable(False)
            self.menuitem_edit.Enable(False)
            self.menuitem_clear.Enable(False)
            self.menuitem_find.Enable(False)
            self.menuitem_replace.Enable(False)

            self.library_file = ''
            file_format = u'.ods'
            if self.settings.has_section('complist'):
                if self.settings.has_option('complist', 'file_format'):
                    file_format = self.settings.get('complist', 'file_format')
            self.complist_file = os.path.splitext(self.schematic_file)[0] + file_format
            self.library = None
            self.init_grid()
            complist = CompList()
            schematic_names = [self.schematic_file]
            schematic_names.extend(complist.get_sheets(self.schematic_file))
            self.schematics = []
            for schematic_name in schematic_names:
                self.schematics.append(Schematic(schematic_name))
            sch_values = self.get_schematic_values()
            if len(sch_values) == 0:
                wx.MessageBox(
                    u'Похоже, в открываемой схеме компоненты отсутствуют\n' + \
                    u'или имеют неверные обозначения.\n' + \
                    u'\n' + \
                    u'Убедитесь, что в схеме присутствуют компоненты с\n' + \
                    u'корректными позиционными обозначениями и попытайтесь\n' + \
                    u'открыть файл схемы снова.',
                    u'Внимание!',
                    wx.ICON_INFORMATION|wx.OK, self
                    )
            else:
                self.grid.AppendRows(len(sch_values))
                self.grid.set_values(sch_values)
                self.grid.undo_buffer = []
                self.grid.redo_buffer = []
                self.grid.on_sort()
                self.on_grid_change()
                self.saved = True

                # Stamp fields
                sch = Schematic(self.schematic_file)
                self.stamp_dict['decimal_num'] = sch.descr.comment1
                self.stamp_dict['developer'] = sch.descr.comment2
                self.stamp_dict['verifier'] = sch.descr.comment3
                self.stamp_dict['approver'] = sch.descr.comment4
                self.stamp_dict['comp'] = sch.descr.comp
                self.stamp_dict['title'] = sch.descr.title

                # Menu & Toolbar
                self.menuitem_complist.Enable(True)
                self.menuitem_save_sch.Enable(False)
                self.menuitem_save_sch_as.Enable(True)
                self.menuitem_find.Enable(True)
                self.menuitem_replace.Enable(True)
                self.add_to_recent(self.schematic_file, 'sch')
                self.update_comp_fields_panel()

                # Title
                self.SetTitle('kicadbom2spec - ' + self.schematic_file)

                # Automatic group filling
                self.apply_auto_groups()

            # Set cursor back to 'normal'
            wx.EndBusyCursor()

        except IOError as e:
            # Set cursor back to 'normal'
            if wx.IsBusy():
                wx.EndBusyCursor()

            # Title
            self.SetTitle('kicadbom2spec')

            # Menu & Toolbar
            self.menuitem_complist.Enable(False)
            self.menuitem_save_sch.Enable(False)
            self.menuitem_save_sch_as.Enable(False)
            self.menuitem_save_lib.Enable(False)
            self.menuitem_save_lib_as.Enable(False)
            self.menuitem_copy.Enable(False)
            self.menuitem_cut.Enable(False)
            self.menuitem_edit.Enable(False)
            self.menuitem_clear.Enable(False)
            self.menuitem_find.Enable(False)
            self.menuitem_replace.Enable(False)

            # Initialize grid of the components
            self.init_grid()

            # Remove bad file from recent
            self.remove_from_recent(self.schematic_file, 'sch')

            wx.MessageBox(
                u'При открытии файла схемы:\n' +
                self.schematic_file + '\n' \
                u'возникла ошибка:\n' + \
                e.strerror,
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )
        except:
            self.on_error()

    def on_save_sch(self, event):
        """
        Save changes in the fields of the components to the schematic file.

        """
        comp_values = self.grid.get_values()
        self.set_schematic_values(comp_values)
        for schematic in self.schematics:
            if schematic.sch_name == self.schematic_file:
                # Stamp fields only for root sheet
                schematic.descr.comment1 = self.stamp_dict['decimal_num']
                schematic.descr.comment2 = self.stamp_dict['developer']
                schematic.descr.comment3 = self.stamp_dict['verifier']
                schematic.descr.comment4 = self.stamp_dict['approver']
                schematic.descr.comp = self.stamp_dict['comp']
                schematic.descr.title = self.stamp_dict['title']

            try:
                if os.path.exists(schematic.sch_name + '.tmp'):
                    os.remove(schematic.sch_name + '.tmp')
                schematic.save(schematic.sch_name + '.tmp')
                os.remove(schematic.sch_name)
                os.rename(schematic.sch_name + '.tmp', schematic.sch_name)
                self.saved = True
                self.menuitem_save_sch.Enable(False)
                self.update_comp_fields_panel()
            except IOError as e:
                if os.path.exists(schematic.sch_name + '.tmp') \
                        and os.path.exists(schematic.sch_name):
                    os.remove(schematic.sch_name + '.tmp')
                wx.MessageBox(
                    u'При сохранении файла схемы:\n' +
                    schematic.sch_name + '\n' \
                    u'возникла ошибка:\n' +
                    e.strerror + '\n\n' +
                    u'Файл не сохранен.',
                    u'Внимание!',
                    wx.ICON_ERROR|wx.OK, self
                    )
            except:
                self.on_error()

    def on_save_sch_as(self, event, file_name=None):
        """
        Save changes in the fields of the components to the separate
        schematic file(s).

        """
        comp_values = self.grid.get_values()
        self.set_schematic_values(comp_values)

        if file_name == None:
            save_sch_dialog = wx.FileDialog(
                self,
                u'Сохранить схему как...',
                os.path.dirname(self.schematic_file),
                os.path.basename(self.schematic_file),
                u'Схема (*.sch)|*.sch|Все файлы (*.*)|*.*',
                wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
                )
            if save_sch_dialog.ShowModal() == wx.ID_CANCEL:
                return
            file_name = save_sch_dialog.GetPath()

        base_dir = os.path.dirname(self.schematic_file)
        new_dir, new_file = os.path.split(file_name)

        for schematic in self.schematics:
            sch_dir, sch_file = os.path.split(schematic.sch_name)
            sch_reldir = os.path.relpath(sch_dir, base_dir)

            if schematic.sch_name == self.schematic_file:
                # Stamp fields only for root sheet
                schematic.descr.comment1 = self.stamp_dict['decimal_num']
                schematic.descr.comment2 = self.stamp_dict['developer']
                schematic.descr.comment3 = self.stamp_dict['verifier']
                schematic.descr.comment4 = self.stamp_dict['approver']
                schematic.descr.comp = self.stamp_dict['comp']
                schematic.descr.title = self.stamp_dict['title']
                # New name for root sheet only
                sch_file = new_file

            new_dir = os.path.join(new_dir, sch_reldir)
            new_path = os.path.join(new_dir, sch_file)

            try:
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                if os.path.exists(new_path  + '.tmp'):
                    os.remove(new_path + '.tmp')
                schematic.save(new_path + '.tmp')
                if os.path.exists(new_path):
                    os.remove(new_path)
                os.rename(new_path + '.tmp', new_path)
            except IOError as e:
                if os.path.exists(new_path + '.tmp') \
                        and os.path.exists(new_path):
                    os.remove(new_path + '.tmp')
                wx.MessageBox(
                    u'При сохранении файла схемы:\n' +
                    new_path + '\n' \
                    u'возникла ошибка:\n' +
                    e.strerror + '\n\n' \
                    u'Файл не сохранен.',
                    u'Внимание!',
                    wx.ICON_ERROR|wx.OK, self
                    )
            except:
                self.on_error()

    def on_open_lib(self, event=None, lib_file_name=''):
        """
        Load all components from selected schematic
        (include hierarchical sheets) to the table for editing.

        """
        if not self.saved:
            if wx.MessageBox(
                u'Последние изменения в полях компонентов не были сохранены!\n' \
                u'Продолжить?',
                u'Внимание!',
                wx.ICON_QUESTION|wx.YES_NO, self
                ) == wx.NO:

                return
        if lib_file_name:
            self.library_file = lib_file_name
        else:
            open_lib_dialog = wx.FileDialog(
                self,
                u'Выбор файла библиотеки',
                u'',
                u'',
                u'Библиотека (*.lib)|*.lib|Все файлы (*.*)|*.*',
                wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
                )
            if open_lib_dialog.ShowModal() == wx.ID_CANCEL:
                return
            self.library_file = open_lib_dialog.GetPath()

        try:
            # Set cursor to 'wait'
            wx.BeginBusyCursor()
            wx.SafeYield()

            # Menu & Toolbar
            self.menuitem_complist.Enable(False)
            self.menuitem_save_sch.Enable(False)
            self.menuitem_save_sch_as.Enable(False)
            self.menuitem_save_lib.Enable(False)
            self.menuitem_save_lib_as.Enable(False)
            self.menuitem_copy.Enable(False)
            self.menuitem_cut.Enable(False)
            self.menuitem_edit.Enable(False)
            self.menuitem_clear.Enable(False)
            self.menuitem_find.Enable(False)
            self.menuitem_replace.Enable(False)

            self.schematic_file = ''
            self.complist_file = ''
            self.library = Library(self.library_file)
            self.init_grid()
            lib_values = self.get_library_values()
            self.grid.AppendRows(len(lib_values))
            self.grid.set_values(lib_values)
            self.grid.undo_buffer = []
            self.grid.redo_buffer = []
            self.grid.on_sort()
            self.on_grid_change()
            self.saved = True

            # Menu & Toolbar
            self.menuitem_save_lib.Enable(False)
            self.menuitem_save_lib_as.Enable(True)
            self.menuitem_find.Enable(True)
            self.menuitem_replace.Enable(True)
            self.add_to_recent(self.library_file, 'lib')
            self.update_comp_fields_panel()

            # Set cursor back to 'normal'
            wx.EndBusyCursor()

            # Title
            self.SetTitle('kicadbom2spec - ' + self.library_file)

        except IOError as e:
            # Set cursor back to 'normal'
            if wx.IsBusy():
                wx.EndBusyCursor()

            # Title
            self.SetTitle('kicadbom2spec')

            # Menu & Toolbar
            self.menuitem_complist.Enable(False)
            self.menuitem_save_sch.Enable(False)
            self.menuitem_save_sch_as.Enable(False)
            self.menuitem_save_lib.Enable(False)
            self.menuitem_save_lib_as.Enable(False)
            self.menuitem_copy.Enable(False)
            self.menuitem_cut.Enable(False)
            self.menuitem_edit.Enable(False)
            self.menuitem_clear.Enable(False)
            self.menuitem_find.Enable(False)
            self.menuitem_replace.Enable(False)

            # Initialize grid of the components
            self.init_grid()

            # Remove bad file from recent
            self.remove_from_recent(self.library_file, 'lib')

            wx.MessageBox(
                u'При открытии файла библиотеки:\n' +
                self.library_file + '\n' \
                u'возникла ошибка:\n' + \
                e.strerror,
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )
        except:
            self.on_error()

    def on_save_lib(self, event):
        """
        Save changes in the fields of the components to the library file.

        """
        comp_values = self.grid.get_values()
        self.set_library_values(comp_values)
        try:
            if os.path.exists(self.library_file + '.tmp'):
                os.remove(self.library_file + '.tmp')
            self.library.save(self.library_file + '.tmp')
            os.remove(self.library_file)
            os.rename(self.library_file + '.tmp', self.library_file)
            self.saved = True
            self.menuitem_save_lib.Enable(False)
            self.update_comp_fields_panel()
        except IOError as e:
            if os.path.exists(self.library_file + '.tmp') \
                    and os.path.exists(self.library_file):
                os.remove(self.library_file + '.tmp')
            wx.MessageBox(
                u'При сохранении файла библиотеки:\n' +
                self.library_file + '\n' \
                u'возникла ошибка:\n' +
                e.strerror + '\n\n' \
                u'Файл не сохранен.',
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )
        except:
            self.on_error()

    def on_save_lib_as(self, event):
        """
        Save changes in the fields of the components to the separate
        library file.

        """
        comp_values = self.grid.get_values()
        self.set_library_values(comp_values)

        save_lib_dialog = wx.FileDialog(
            self,
            u'Сохранить библиотеку как...',
            os.path.dirname(self.library_file),
            os.path.basename(self.library_file),
            u'Библиотека (*.lib)|*.lib|Все файлы (*.*)|*.*',
            wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
            )
        if save_lib_dialog.ShowModal() == wx.ID_CANCEL:
            return
        new_library_file = save_lib_dialog.GetPath()

        try:
            if os.path.exists(new_library_file + '.tmp'):
                os.remove(new_library_file + '.tmp')
            self.library.save(new_library_file + '.tmp')
            if os.path.exists(new_library_file):
                os.remove(new_library_file)
            os.rename(new_library_file + '.tmp', new_library_file)
        except IOError as e:
            if os.path.exists(new_library_file + '.tmp') \
                    and os.path.exists(new_library_file):
                os.remove(new_library_file + '.tmp')
            wx.MessageBox(
                u'При сохранении файла библиотеки:\n' +
                self.library_file + '\n' \
                u'возникла ошибка:\n' +
                e.strerror + '\n\n' \
                u'Файл не сохранен.',
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )
        except:
            self.on_error()

    def get_singular_group_name(self, group_name):
        """
        Get name of the group in singular.
        """
        if self.group_names_dict.has_key(group_name):
            return self.group_names_dict[group_name]
        else:
            request_dialog = gui.SingularGroupNameDialog(self)
            request_dialog.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
            request_dialog.group_name_text.SetValue(group_name)
            request_dialog.singular_group_name_text.SetValue(group_name)
            request_dialog.group_name_text.SetEditable(False)
            request_dialog.group_name_text.Enable(False)
            result = request_dialog.ShowModal()
            singular = request_dialog.singular_group_name_text.GetValue()
            if result == wx.ID_OK and singular != u'':
                self.group_names_dict[group_name] = singular
                return singular
            else:
                return group_name

    def on_complist(self, event):
        """
        Make list of the components.

        """
        def on_file_name_changed(event):
            """
            Update file format.
            """
            file_name = complist_dialog.filepicker_complist.GetPath()
            if file_name.endswith(u'.odt'):
                complist_dialog.rbutton_odt.SetValue(True)
            elif file_name.endswith(u'.ods'):
                complist_dialog.rbutton_ods.SetValue(True)
            elif file_name.endswith(u'.csv'):
                complist_dialog.rbutton_csv.SetValue(True)

        def on_decimal_num_changed(event):
            """
            Show converted value of decimal number.

            """
            value = complist_dialog.stamp_decimal_num_text.GetValue()
            value = complist.convert_decimal_num(value)
            complist_dialog.stamp_decimal_num_converted.SetLabel(value)

        def on_title_changed(event):
            """
            Show converted value of title.

            """
            value = complist_dialog.stamp_title_text.GetValue()
            value = value.replace('\n', '\\n')
            value = complist.convert_title(value)
            value = value.replace('\\n', '\n')
            complist_dialog.stamp_title_converted.SetLabel(value)
            # Resize dialog min height
            dialog_width = complist_dialog.GetSize().GetWidth()
            dialog_height = complist_dialog.GetSize().GetHeight()
            complist_dialog.SetSizeHints(
                    -1,
                    -1,
                    -1,
                    -1
                )
            complist_dialog.Fit()
            complist_dialog.SetSizeHints(
                complist_dialog.GetSize().GetWidth(),
                complist_dialog.GetSize().GetHeight(),
                    -1,
                    -1
                )
            complist_dialog.SetSize(
                    wx.Size(
                        dialog_width,
                        dialog_height
                    )
                )

        def on_first_usage_checked(event):
            """
            Enable or disable child checkbox.

            """
            if event.IsChecked():
                complist_dialog.checkbox_first_usage_fill.Enable(True)
            else:
                complist_dialog.checkbox_first_usage_fill.Enable(False)

        def on_add_units_checked(event):
            """
            Enable or disable child checkbox.

            """
            if event.IsChecked():
                complist_dialog.checkbox_space_before_units.Enable(True)
            else:
                complist_dialog.checkbox_space_before_units.Enable(False)

        def set_file_ext(ext):
            """
            Set file extension in filepicker.
            """
            complist_dialog.filepicker_complist.Unbind(wx.EVT_FILEPICKER_CHANGED)
            file_name = complist_dialog.filepicker_complist.GetPath()
            name_and_ext = os.path.splitext(file_name)
            complist_dialog.filepicker_complist.SetPath(name_and_ext[0] + ext)
            complist_dialog.filepicker_complist.Bind(wx.EVT_FILEPICKER_CHANGED, on_file_name_changed)
            complist_dialog.filepicker_complist.SetFocus()

        def on_rbutton_odt(event):
            """
            Update file extension.
            """
            set_file_ext(u'.odt')

        def on_rbutton_ods(event):
            """
            Update file extension.
            """
            set_file_ext(u'.ods')

        def on_rbutton_csv(event):
            """
            Update file extension.
            """
            set_file_ext(u'.csv')

        complist = CompList()
        # Specify callback
        complist.get_singular_group_name = self.get_singular_group_name

        # Dialog
        complist_dialog = gui.CompListDialog(self)

        # Calculate and set min size for title text control
        complist_dialog.Fit()
        textctl_minsize = complist_dialog.stamp_title_text.GetSize()
        textctl_minsize.SetHeight(textctl_minsize.GetHeight() * 2)
        textctl_minsize.SetWidth(-1)
        complist_dialog.stamp_title_text.SetMinSize(textctl_minsize)
        complist_dialog.SetInitialSize()

        # Set min size of dialog
        complist_dialog.Fit()
        complist_dialog.SetMinSize(
                wx.Size(
                    complist_dialog.GetSize().GetWidth(),
                    complist_dialog.GetSize().GetHeight()
                )
            )

        # Events
        complist_dialog.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
        complist_dialog.filepicker_complist.Bind(wx.EVT_FILEPICKER_CHANGED, on_file_name_changed)
        complist_dialog.stamp_decimal_num_text.Bind(wx.EVT_TEXT, on_decimal_num_changed)
        complist_dialog.stamp_title_text.Bind(wx.EVT_TEXT, on_title_changed)
        complist_dialog.checkbox_first_usage.Bind(wx.EVT_CHECKBOX, on_first_usage_checked)
        complist_dialog.checkbox_add_units.Bind(wx.EVT_CHECKBOX, on_add_units_checked)
        complist_dialog.rbutton_odt.Bind(wx.EVT_RADIOBUTTON, on_rbutton_odt)
        complist_dialog.rbutton_ods.Bind(wx.EVT_RADIOBUTTON, on_rbutton_ods)
        complist_dialog.rbutton_csv.Bind(wx.EVT_RADIOBUTTON, on_rbutton_csv)

        # Load settings
        open_complist = False

        if self.settings.has_section('complist'):
            width = -1
            height = -1
            if self.settings.has_option('complist', 'dialog width'):
                width = self.settings.getint('complist', 'dialog width')
            if self.settings.has_option('complist', 'dialog height'):
                height = self.settings.getint('complist', 'dialog height')
            complist_dialog.SetSize(wx.Size(width, height))
            complist_dialog.CentreOnParent()
            if self.settings.has_option('complist', 'all'):
                complist.all_components = self.settings.getboolean('complist', 'all')
            if self.settings.has_option('complist', 'units'):
                complist.add_units = self.settings.getboolean('complist', 'units')
            if self.settings.has_option('complist', 'space_before_units'):
                complist.space_before_units = self.settings.getboolean('complist', 'space_before_units')
            if self.settings.has_option('complist', 'inspector'):
                self.stamp_dict['inspector'] = self.settings.get('complist', 'inspector')
            if self.settings.has_option('complist', 'file_format'):
                complist.file_format = self.settings.get('complist', 'file_format')
            if self.settings.has_option('complist', 'empty_row_after_name'):
                complist.empty_row_after_name = self.settings.getboolean('complist', 'empty_row_after_name')
            if self.settings.has_option('complist', 'empty_rows_after_group'):
                complist.empty_rows_after_group = self.settings.getint('complist', 'empty_rows_after_group')
            if self.settings.has_option('complist', 'empty_rows_everywhere'):
                complist.empty_rows_everywhere = self.settings.getboolean('complist', 'empty_rows_everywhere')
            if self.settings.has_option('complist', 'prohibit_empty_rows_on_top'):
                complist.prohibit_empty_rows_on_top = self.settings.getboolean('complist', 'prohibit_empty_rows_on_top')
            if self.settings.has_option('complist', 'gost_in_group_name'):
                complist.gost_in_group_name = self.settings.getboolean('complist', 'gost_in_group_name')
            if self.settings.has_option('complist', 'singular_group_name'):
                complist.singular_group_name = self.settings.getboolean('complist', 'singular_group_name')
            if self.settings.has_option('complist', 'join_same_name_groups'):
                complist.join_same_name_groups = self.settings.getboolean('complist', 'join_same_name_groups')
            if self.settings.has_option('complist', 'first_usage'):
                complist.add_first_usage = self.settings.getboolean('complist', 'first_usage')
            if self.settings.has_option('complist', 'prohibit_group_name_at_bottom'):
                complist.prohibit_group_name_at_bottom = self.settings.getboolean('complist', 'prohibit_group_name_at_bottom')
            if self.settings.has_option('complist', 'fill_first_usage'):
                complist.fill_first_usage = self.settings.getboolean('complist', 'fill_first_usage')
            if self.settings.has_option('complist', 'customer_fields'):
                complist.add_customer_fields = self.settings.getboolean('complist', 'customer_fields')
            if self.settings.has_option('complist', 'changes_sheet'):
                complist.add_changes_sheet = self.settings.getboolean('complist', 'changes_sheet')
            if self.settings.has_option('complist', 'count_for_changes_sheet'):
                complist.count_for_changes_sheet = self.settings.getint('complist', 'count_for_changes_sheet')
            if self.settings.has_option('complist', 'italic'):
                complist.italic = self.settings.getboolean('complist', 'italic')
            if self.settings.has_option('complist', 'underline_group_name'):
                complist.underline_group_name = self.settings.getboolean('complist', 'underline_group_name')
            if self.settings.has_option('complist', 'center_group_name'):
                complist.center_group_name = self.settings.getboolean('complist', 'center_group_name')
            if self.settings.has_option('complist', 'center_reference'):
                complist.center_reference = self.settings.getboolean('complist', 'center_reference')
            if self.settings.has_option('complist', 'extremal_width_factor'):
                complist.extremal_width_factor = self.settings.getint('complist', 'extremal_width_factor')

            if self.settings.has_option('complist', 'open'):
                open_complist = self.settings.getboolean('complist', 'open')

        # Options
        complist_dialog.filepicker_complist.SetPath(self.complist_file)
        if complist.file_format == u'.odt':
            complist_dialog.rbutton_odt.SetValue(True)
        elif complist.file_format == u'.ods':
            complist_dialog.rbutton_ods.SetValue(True)
        elif complist.file_format == u'.csv':
            complist_dialog.rbutton_csv.SetValue(True)
        complist_dialog.checkbox_all_components.SetValue(complist.all_components)
        complist_dialog.checkbox_add_units.SetValue(complist.add_units)
        complist_dialog.checkbox_space_before_units.SetValue(complist.space_before_units)
        complist_dialog.checkbox_empty_row_after_name.SetValue(complist.empty_row_after_name)
        complist_dialog.choice_after_groups.SetSelection(complist.empty_rows_after_group)
        complist_dialog.checkbox_empty_rows_everywhere.SetValue(complist.empty_rows_everywhere)
        complist_dialog.checkbox_prohibit_empty_rows_on_top.SetValue(complist.prohibit_empty_rows_on_top)
        complist_dialog.checkbox_gost_in_group_name.SetValue(complist.gost_in_group_name)
        complist_dialog.checkbox_singular_group_name.SetValue(complist.singular_group_name)
        complist_dialog.checkbox_join_same_name_groups.SetValue(complist.join_same_name_groups)
        complist_dialog.checkbox_prohibit_group_name_at_bottom.SetValue(complist.prohibit_group_name_at_bottom)
        complist_dialog.checkbox_first_usage.SetValue(complist.add_first_usage)
        complist_dialog.checkbox_first_usage_fill.SetValue(complist.fill_first_usage)
        complist_dialog.checkbox_first_usage_fill.Enable(complist.add_first_usage)
        complist_dialog.checkbox_customer_fields.SetValue(complist.add_customer_fields)
        complist_dialog.checkbox_changes_sheet.SetValue(complist.add_changes_sheet)
        complist_dialog.spinctrl_count_for_changes_sheet.SetValue(complist.count_for_changes_sheet)
        complist_dialog.checkbox_italic.SetValue(complist.italic)
        complist_dialog.checkbox_underline_group.SetValue(complist.underline_group_name)
        complist_dialog.checkbox_center_group.SetValue(complist.center_group_name)
        complist_dialog.checkbox_center_ref.SetValue(complist.center_reference)
        complist_dialog.spinctrl_extremal_width_factor.SetValue(complist.extremal_width_factor)

        complist_dialog.checkbox_open.SetValue(open_complist)

        # Stamp
        for field in self.stamp_dict.keys():
            field_text = getattr(complist_dialog, 'stamp_{}_text'.format(field))
            value = self.stamp_dict[field]
            value = value.replace('\\\\n', '\n')
            value = value.replace('\\"', '"')
            field_text.SetValue(value)

        complist_dialog.dialog_buttonsOK.SetFocus()
        result = complist_dialog.ShowModal()

        # Save dialog size
        if not self.settings.has_section('complist'):
            self.settings.add_section('complist')
        self.settings.set(
            'complist',
            'dialog width',
            str(complist_dialog.GetSize().GetWidth())
            )
        self.settings.set(
            'complist',
            'dialog height',
            str(complist_dialog.GetSize().GetHeight())
            )

        if result == wx.ID_OK:
            # Set cursor to 'wait'
            wx.BeginBusyCursor()
            wx.SafeYield()

            # File name and format
            if complist_dialog.rbutton_odt.GetValue() == True:
                complist.file_format = u'.odt'
            elif complist_dialog.rbutton_ods.GetValue() == True:
                complist.file_format = u'.ods'
            elif complist_dialog.rbutton_csv.GetValue() == True:
                complist.file_format = u'.csv'
            self.complist_file = complist_dialog.filepicker_complist.GetPath()
            self.complist_file = os.path.splitext(self.complist_file)[0] + complist.file_format

            # Save settings from complist dialog
            complist.all_components = complist_dialog.checkbox_all_components.IsChecked()
            complist.add_units = complist_dialog.checkbox_add_units.IsChecked()
            complist.space_before_units = complist_dialog.checkbox_space_before_units.IsChecked()
            complist.empty_row_after_name = complist_dialog.checkbox_empty_row_after_name.GetValue()
            complist.empty_rows_after_group = complist_dialog.choice_after_groups.GetSelection()
            complist.empty_rows_everywhere = complist_dialog.checkbox_empty_rows_everywhere.GetValue()
            complist.prohibit_empty_rows_on_top = complist_dialog.checkbox_prohibit_empty_rows_on_top.GetValue()
            complist.gost_in_group_name = complist_dialog.checkbox_gost_in_group_name.GetValue()
            complist.singular_group_name = complist_dialog.checkbox_singular_group_name.GetValue()
            complist.join_same_name_groups = complist_dialog.checkbox_join_same_name_groups.GetValue()
            complist.prohibit_group_name_at_bottom = complist_dialog.checkbox_prohibit_group_name_at_bottom.GetValue()
            complist.add_first_usage = complist_dialog.checkbox_first_usage.IsChecked()
            complist.fill_first_usage = complist_dialog.checkbox_first_usage_fill.IsChecked()
            complist.add_customer_fields = complist_dialog.checkbox_customer_fields.IsChecked()
            complist.add_changes_sheet = complist_dialog.checkbox_changes_sheet.IsChecked()
            complist.count_for_changes_sheet = complist_dialog.spinctrl_count_for_changes_sheet.GetValue()
            complist.italic = complist_dialog.checkbox_italic.GetValue()
            complist.underline_group_name = complist_dialog.checkbox_underline_group.GetValue()
            complist.center_group_name = complist_dialog.checkbox_center_group.GetValue()
            complist.center_reference = complist_dialog.checkbox_center_ref.GetValue()
            complist.extremal_width_factor = complist_dialog.spinctrl_extremal_width_factor.GetValue()

            open_complist = complist_dialog.checkbox_open.GetValue()

            # Stamp
            for field in self.stamp_dict.keys():
                field_text = getattr(complist_dialog, 'stamp_{}_text'.format(field))
                value = field_text.GetValue()
                value = value.replace('\n', '\\\\n')
                value = value.replace('"', '\\"')
                if self.stamp_dict[field] != value:
                    self.stamp_dict[field] = value
                    if field != 'inspector':
                        self.saved = False
                        self.menuitem_save_sch.Enable(True)

            # Save settings
            if not self.settings.has_section('complist'):
                self.settings.add_section('complist')
            self.settings.set('complist', 'all', str(complist.all_components))
            self.settings.set('complist', 'units', str(complist.add_units))
            self.settings.set('complist', 'space_before_units', str(complist.space_before_units))
            self.settings.set('complist', 'file_format', complist.file_format)
            self.settings.set('complist', 'empty_row_after_name', str(complist.empty_row_after_name))
            self.settings.set('complist', 'empty_rows_after_group', str(complist.empty_rows_after_group))
            self.settings.set('complist', 'empty_rows_everywhere', str(complist.empty_rows_everywhere))
            self.settings.set('complist', 'prohibit_empty_rows_on_top', str(complist.prohibit_empty_rows_on_top))
            self.settings.set('complist', 'gost_in_group_name', str(complist.gost_in_group_name))
            self.settings.set('complist', 'singular_group_name', str(complist.singular_group_name))
            self.settings.set('complist', 'join_same_name_groups', str(complist.join_same_name_groups))
            self.settings.set('complist', 'prohibit_group_name_at_bottom', str(complist.prohibit_group_name_at_bottom))
            self.settings.set('complist', 'first_usage', str(complist.add_first_usage))
            self.settings.set('complist', 'fill_first_usage', str(complist.fill_first_usage))
            self.settings.set('complist', 'customer_fields', str(complist.add_customer_fields))
            self.settings.set('complist', 'changes_sheet', str(complist.add_changes_sheet))
            self.settings.set('complist', 'count_for_changes_sheet', str(complist.count_for_changes_sheet))
            self.settings.set('complist', 'italic', str(complist.italic))
            self.settings.set('complist', 'underline_group_name', str(complist.underline_group_name))
            self.settings.set('complist', 'center_group_name', str(complist.center_group_name))
            self.settings.set('complist', 'center_reference', str(complist.center_reference))
            self.settings.set('complist', 'extremal_width_factor', str(complist.extremal_width_factor))

            self.settings.set('complist', 'open', str(open_complist))
            self.settings.set('complist', 'inspector', self.stamp_dict['inspector'])

            try:
                # Save entire schematic with current changes to temporary directory
                temp_dir = tempfile.mkdtemp(prefix='kicadbom2spec_')
                sch_file = os.path.basename(self.schematic_file)
                temp_file = os.path.join(temp_dir, sch_file)
                self.on_save_sch_as(None, file_name=temp_file)
                # Options
                complist.aliases_dict = self.aliases_dict
                complist.separators_dict = self.separators_dict
                # Stamp
                complist.decimal_num = complist.convert_decimal_num(self.stamp_dict['decimal_num'])
                complist.developer = self.stamp_dict['developer']
                complist.verifier = self.stamp_dict['verifier']
                complist.inspector = self.stamp_dict['inspector']
                complist.approver = self.stamp_dict['approver']
                complist.comp = self.stamp_dict['comp']
                complist.title = complist.convert_title(self.stamp_dict['title'])
                # Load components
                complist.load(temp_file)
                # Save comp list
                complist.save(self.complist_file)
                # Remove temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
            except IOError as e:
                wx.MessageBox(
                    u'При создании перечня элементов:\n' +
                    self.complist_file + '\n' \
                    u'возникла ошибка:\n' + \
                    e.strerror + '\n\n' \
                    u'Не удалось создать перечень элементов.',
                    u'Внимание!',
                    wx.ICON_ERROR|wx.OK, self
                    )
                # Set cursor back to 'normal'
                if wx.IsBusy():
                    wx.EndBusyCursor()
                return
            except:
                self.on_error()

            if os.path.exists(self.complist_file):
                if open_complist:
                    if sys.platform == 'linux2':
                        subprocess.Popen(["xdg-open", self.complist_file])
                    else:
                        os.startfile(self.complist_file)
                else:
                    wx.MessageBox(
                        u'Перечень элементов успешно создан и сохранен!',
                        u'kicadbom2spec',
                        wx.ICON_INFORMATION | wx.OK,
                        self
                        )
            else:
                wx.MessageBox(
                    u'Похоже что-то пошло не так!\n' + \
                    u'Файл перечня элементов не был создан.',
                    u'kicadbom2spec',
                    wx.ICON_EXCLAMATION | wx.OK,
                    self
                    )

            # Set cursor back to 'normal'
            if wx.IsBusy():
                wx.EndBusyCursor()

    def on_edit_fields(self, event):
        """
        Open specialized window for editing fields of selected components.

        """
        def on_button(event):
            for row in selected_rows:
                if editor.checkbox.IsChecked():
                    self.grid.set_cell_value(row, 0, '1')
                else:
                    self.grid.set_cell_value(row, 0, '0')
                for col in range(1, col_num):
                    if col == 2:
                        continue
                    new_value = getattr(editor, 'editor_ctrl_%i' % col).get_value()
                    if new_value == u'<не изменять>':
                        continue
                    else:
                        self.grid.set_cell_value(row, col, new_value)
            if self.grid.is_changed():
                self.on_grid_change()

            event.Skip()

        def on_size(event):
            """
            Save dialog width

            """
            if not self.settings.has_section('window'):
                self.settings.add_section('window')
            self.settings.set(
                'window',
                'editor width',
                str(editor.GetSize().GetWidth())
                )
            event.Skip()

        editor = gui.EditorDialog(self)
        editor.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
        editor.space_as_dot = self.grid.space_as_dot
        selected_rows = self.grid.GetSelectedRows()
        col_num = self.grid.GetNumberCols()
        all_choices = self.grid.get_choices(selected_rows, range(0, col_num))
        values_dict_keys = [
            u'',
            u'группа',
            u'',
            u'марка',
            u'значение',
            u'класс точности',
            u'тип',
            u'стандарт',
            u'примечание'
            ]
        for i in range(1, col_num):
            if i == 2:
                continue
            cur_editor_ctrl = getattr(editor, 'editor_ctrl_%i' % i)
            cur_editor_ctrl.set_items(
                all_choices[i],
                self.values_dict[values_dict_keys[i]],
                u'<не изменять>'
                )
        # Layout
        if self.library:
            editor.checkbox.Hide()
            editor.statictext_4.Hide()
            editor.editor_ctrl_4.Hide()
        editor.Layout()
        editor.Fit()
        min_size = editor.GetSize()
        editor.SetSizeHints(
            min_size.GetWidth(),
            min_size.GetHeight(),
            -1,
            min_size.GetHeight()
            )
        # Load dialog width
        if self.settings.has_section('window'):
            if self.settings.has_option('window', 'editor width'):
               editor.SetSize(
                    wx.Size(
                        self.settings.getint('window', 'editor width'),
                        -1
                        )
                    )
        editor.CenterOnParent()
        # Events
        editor.Bind(wx.EVT_SIZE, on_size)
        editor.dialog_buttonsOK.Bind(wx.EVT_BUTTON, on_button)
        # Need to use Show instead of ShowModal otherwise EditorCtrlPopup was
        # freezed.
        editor.Show()

    def on_settings(self, event):
        """
        Open settings manager.

        """

        def split_auto_groups_item(string):
            """
            Split auto_groups_checklistbox item string
            on couple (param, value).

            """
            matches = re.search(r'^(.+) - "(.*)"$', string)
            if matches:
                return matches.groups()
            else:
                return None

        def on_auto_groups_checklistbox_selected(event):
            """
            Enable buttons when item selected.

            """
            settings_editor.auto_groups_edit_button.Enable(True)
            settings_editor.auto_groups_remove_button.Enable(True)

        def on_auto_groups_add_button_clicked(event):
            """
            Add an element to auto_groups_checklistbox.

            """
            add_dialog = gui.EditAutoGroupsDialog(self)
            add_dialog.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
            add_dialog.SetTitle(u'Добавить элемент списка')
            result = add_dialog.ShowModal()
            if result == wx.ID_OK:
                param = add_dialog.param_text.GetValue()
                value = add_dialog.value_text.GetValue()
                item = u'{} - "{}"'.format(param, value)
                settings_editor.auto_groups_checklistbox.Append(item)

        def on_auto_groups_edit_button_clicked(event):
            """
            Edit selected element in auto_groups_checklistbox.

            """
            edit_dialog = gui.EditAutoGroupsDialog(self)
            edit_dialog.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
            edit_dialog.SetTitle(u'Изменить элемент списка')
            index = settings_editor.auto_groups_checklistbox.GetSelections()[0]
            text = settings_editor.auto_groups_checklistbox.GetString(index)
            param, value = split_auto_groups_item(text)
            edit_dialog.param_text.SetValue(param)
            edit_dialog.value_text.SetValue(value)
            result = edit_dialog.ShowModal()
            if result == wx.ID_OK:
                param = edit_dialog.param_text.GetValue()
                value = edit_dialog.value_text.GetValue()
                item = u'{} - "{}"'.format(param, value)
                settings_editor.auto_groups_checklistbox.SetString(index, item)

        def on_auto_groups_remove_button_clicked(event):
            """
            Remove selected element from auto_groups_checklistbox.

            """
            index = settings_editor.auto_groups_checklistbox.GetSelections()[0]
            settings_editor.auto_groups_checklistbox.Delete(index)
            settings_editor.auto_groups_checklistbox.SetSelection(0)

        def mark_spaces_as_dots(event):
            """
            Replace spaces to dots.

            """
            text_ctrl = event.GetEventObject()
            pos = text_ctrl.GetInsertionPoint()
            text = text_ctrl.GetValue()
            text = text.replace(' ', '·')
            text_ctrl.ChangeValue(text)
            text_ctrl.SetInsertionPoint(pos)
            # Sync new value of prefix/suffix with preview panel
            if text_ctrl.name == u'п_марка':
                settings_editor.p_mark_statictext.SetLabel(text)
            elif text_ctrl.name == u'марка_с':
                settings_editor.s_mark_statictext.SetLabel(text)
            elif text_ctrl.name == u'п_значение':
                settings_editor.p_value_statictext.SetLabel(text)
            elif text_ctrl.name == u'значение_с':
                settings_editor.s_value_statictext.SetLabel(text)
            elif text_ctrl.name == u'п_класс точности':
                settings_editor.p_accuracy_statictext.SetLabel(text)
            elif text_ctrl.name == u'класс точности_с':
                settings_editor.s_accuracy_statictext.SetLabel(text)
            elif text_ctrl.name == u'п_тип':
                settings_editor.p_type_statictext.SetLabel(text)
            elif text_ctrl.name == u'тип_с':
                settings_editor.s_type_statictext.SetLabel(text)
            elif text_ctrl.name == u'п_стандарт':
                settings_editor.p_gost_statictext.SetLabel(text)
            elif text_ctrl.name == u'стандарт_с':
                settings_editor.s_gost_statictext.SetLabel(text)
            settings_editor.separators_panel.Layout()
            event.Skip()

        def on_put_to_clipboard(event):
            """
            Replace dots to spaces when text moves outside.

            """
            text_ctrl = event.GetEventObject()
            if wx.TheClipboard.Open():
                text = text_ctrl.GetStringSelection()
                if text:
                    if event.GetEventType() == wx.EVT_TEXT_CUT.typeId:
                        start = text_ctrl.GetSelection()[0]
                        end = text_ctrl.GetSelection()[1]
                        text_ctrl.Remove(start, end)
                        text_ctrl.SetInsertionPoint(start)
                    text = text.replace('·', ' ')
                    wx.TheClipboard.SetData(wx.TextDataObject(text))
                wx.TheClipboard.Close()

        def on_preview_checkbox(event):
            """
            Show or hide selected part of name in preview panel.

            """
            part_name = event.GetEventObject().GetLabel()
            state = event.IsChecked()
            if part_name == u'Марка':
                settings_editor.p_mark_statictext.Show(state)
                settings_editor.mark_statictext.Show(state)
                settings_editor.s_mark_statictext.Show(state)
            elif part_name == u'Значение':
                settings_editor.p_value_statictext.Show(state)
                settings_editor.value_statictext.Show(state)
                settings_editor.s_value_statictext.Show(state)
            elif part_name == u'Класс точности':
                settings_editor.p_accuracy_statictext.Show(state)
                settings_editor.accuracy_statictext.Show(state)
                settings_editor.s_accuracy_statictext.Show(state)
            elif part_name == u'Тип':
                settings_editor.p_type_statictext.Show(state)
                settings_editor.type_statictext.Show(state)
                settings_editor.s_type_statictext.Show(state)
            elif part_name == u'Стандарт':
                settings_editor.p_gost_statictext.Show(state)
                settings_editor.gost_statictext.Show(state)
                settings_editor.s_gost_statictext.Show(state)
            settings_editor.separators_panel.Layout()

        def on_group_names_listctrl_selected(event):
            """
            Enable buttons when item selected.

            """
            settings_editor.group_names_edit_button.Enable(True)
            settings_editor.group_names_remove_button.Enable(True)

        def on_group_names_listctrl_unselected(event):
            """
            Disable buttons when item selected.

            """
            settings_editor.group_names_edit_button.Enable(False)
            settings_editor.group_names_remove_button.Enable(False)

        def on_group_names_add_button_clicked(event):
            """
            Add an names pair to group_names_listbox.

            """
            add_dialog = gui.SingularGroupNameDialog(self)
            add_dialog.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
            result = add_dialog.ShowModal()
            if result == wx.ID_OK:
                singular = add_dialog.singular_group_name_text.GetValue()
                plural = add_dialog.group_name_text.GetValue()
                settings_editor.group_names_listctrl.Append((plural, singular))

        def on_group_names_edit_button_clicked(event):
            """
            Edit selected element in group_names_listbox.

            """
            edit_dialog = gui.SingularGroupNameDialog(self)
            edit_dialog.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
            index = settings_editor.group_names_listctrl.GetFirstSelected()
            singular = settings_editor.group_names_listctrl.GetItemText(index, 1)
            plural = settings_editor.group_names_listctrl.GetItemText(index, 0)
            edit_dialog.singular_group_name_text.SetValue(singular)
            edit_dialog.group_name_text.SetValue(plural)
            result = edit_dialog.ShowModal()
            if result == wx.ID_OK:
                singular = edit_dialog.singular_group_name_text.GetValue()
                plural = edit_dialog.group_name_text.GetValue()
                settings_editor.group_names_listctrl.SetStringItem(index, 0, plural)
                settings_editor.group_names_listctrl.SetStringItem(index, 1, singular)

        def on_group_names_remove_button_clicked(event):
            """
            Remove selected element from group_names_listbox.

            """
            index = settings_editor.group_names_listctrl.GetFirstSelected()
            settings_editor.group_names_listctrl.DeleteItem(index)

        settings_editor = gui.SettingsDialog(self)
        # Events
        settings_editor.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
        # Events general
        settings_editor.auto_groups_checklistbox.Bind(wx.EVT_LISTBOX, on_auto_groups_checklistbox_selected)
        settings_editor.auto_groups_checklistbox.Bind(wx.EVT_LISTBOX_DCLICK, on_auto_groups_edit_button_clicked)
        settings_editor.auto_groups_add_button.Bind(wx.EVT_BUTTON, on_auto_groups_add_button_clicked)
        settings_editor.auto_groups_edit_button.Bind(wx.EVT_BUTTON, on_auto_groups_edit_button_clicked)
        settings_editor.auto_groups_remove_button.Bind(wx.EVT_BUTTON, on_auto_groups_remove_button_clicked)
        # Events group_names
        settings_editor.group_names_listctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, on_group_names_listctrl_selected)
        settings_editor.group_names_listctrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, on_group_names_listctrl_unselected)
        settings_editor.group_names_listctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, on_group_names_edit_button_clicked)
        settings_editor.group_names_add_button.Bind(wx.EVT_BUTTON, on_group_names_add_button_clicked)
        settings_editor.group_names_edit_button.Bind(wx.EVT_BUTTON, on_group_names_edit_button_clicked)
        settings_editor.group_names_remove_button.Bind(wx.EVT_BUTTON, on_group_names_remove_button_clicked)
        # Events separators preview
        settings_editor.mark_preview_checkbox.Bind(wx.EVT_CHECKBOX, on_preview_checkbox)
        settings_editor.value_preview_checkbox.Bind(wx.EVT_CHECKBOX, on_preview_checkbox)
        settings_editor.accuracy_preview_checkbox.Bind(wx.EVT_CHECKBOX, on_preview_checkbox)
        settings_editor.type_preview_checkbox.Bind(wx.EVT_CHECKBOX, on_preview_checkbox)
        settings_editor.gost_preview_checkbox.Bind(wx.EVT_CHECKBOX, on_preview_checkbox)

        field_names = (
            u'группа',
            u'марка',
            u'значение',
            u'класс точности',
            u'тип',
            u'стандарт',
            u'примечание',
            )
        for i in range(len(field_names)):
            field_text = getattr(settings_editor, 'field{}_text'.format(i + 1))
            alias_text = getattr(settings_editor, 'alias{}_text'.format(i + 1))
            values = self.values_dict[field_names[i]]
            for value in values:
                field_text.AppendText(value + '\n')
            alias_value = self.aliases_dict[field_names[i]]
            # Default alias shows as empty field
            if field_names[i] == u'значение':
                # "Value" field accessed by index
                alias_text.SetValue(self.aliases_dict[field_names[i]])
            elif alias_value != field_names[i].capitalize():
                alias_text.SetValue(self.aliases_dict[field_names[i]])

        separators_field_names = (
            u'марка',
            u'значение',
            u'класс точности',
            u'тип',
            u'стандарт',
            )
        for i in range(len(separators_field_names)):
            prefix_text = getattr(settings_editor, 'separator{}_prefix_text'.format(i + 1))
            suffix_text = getattr(settings_editor, 'separator{}_suffix_text'.format(i + 1))
            # names is needed for syncing the values with preview panel
            prefix_text.name = u'п_{}'.format(separators_field_names[i])
            suffix_text.name = u'{}_с'.format(separators_field_names[i])
            prefix_text.Bind(wx.EVT_TEXT, mark_spaces_as_dots)
            suffix_text.Bind(wx.EVT_TEXT, mark_spaces_as_dots)
            prefix_text.Bind(wx.EVT_TEXT_COPY, on_put_to_clipboard)
            suffix_text.Bind(wx.EVT_TEXT_COPY, on_put_to_clipboard)
            prefix_text.Bind(wx.EVT_TEXT_CUT, on_put_to_clipboard)
            suffix_text.Bind(wx.EVT_TEXT_CUT, on_put_to_clipboard)
            prefix = self.separators_dict[separators_field_names[i]][0]
            suffix = self.separators_dict[separators_field_names[i]][1]
            prefix_text.SetValue(prefix)
            suffix_text.SetValue(suffix)

        settings_editor.space_as_dot_checkbox.SetValue(self.grid.space_as_dot)
        settings_editor.show_need_adjust_mark_checkbox.SetValue(self.show_need_adjust_mark)

        for suffix, value in self.auto_groups_dict.items():
            checked = {'1':True, '0':False}[value[:1]]
            value = u'{} - "{}"'.format(suffix, value[1:])
            index = settings_editor.auto_groups_checklistbox.Append(value)
            settings_editor.auto_groups_checklistbox.Check(index, checked)

        settings_editor.group_names_listctrl.InsertColumn(0, u'В множественном числе')
        settings_editor.group_names_listctrl.InsertColumn(1, u'В единственном числе')
        listctrl_width = settings_editor.group_names_listctrl.GetSize().GetWidth()
        settings_editor.group_names_listctrl.SetColumnWidth(0, listctrl_width / 2)
        settings_editor.group_names_listctrl.SetColumnWidth(1, listctrl_width / 2)
        for plural in self.group_names_dict.keys():
            singular = self.group_names_dict[plural]
            settings_editor.group_names_listctrl.Append((plural, singular))

        settings_editor.dialog_buttonsOK.SetFocus()
        result = settings_editor.ShowModal()
        if result == wx.ID_OK:
            for i in range(len(field_names)):
                field_text = getattr(settings_editor, 'field{}_text'.format(i + 1))
                alias_text = getattr(settings_editor, 'alias{}_text'.format(i + 1))
                self.values_dict[field_names[i]] = []
                for line in range(field_text.GetNumberOfLines()):
                    line_text = field_text.GetLineText(line)
                    if line_text:
                        self.values_dict[field_names[i]].append(line_text)
                alias_value = alias_text.GetValue()
                if alias_value == '' and field_names[i] != u'значение':
                    # Default value
                    self.aliases_dict[field_names[i]] = field_names[i].capitalize()
                else:
                    self.aliases_dict[field_names[i]] = alias_value


            for i in range(len(separators_field_names)):
                prefix_text = getattr(settings_editor, 'separator{}_prefix_text'.format(i + 1))
                suffix_text = getattr(settings_editor, 'separator{}_suffix_text'.format(i + 1))
                self.separators_dict[separators_field_names[i]] = ['','']
                prefix = prefix_text.GetValue()
                suffix = suffix_text.GetValue()
                prefix = prefix.replace('·', ' ')
                suffix = suffix.replace('·', ' ')
                self.separators_dict[separators_field_names[i]][0] = prefix
                self.separators_dict[separators_field_names[i]][1] = suffix

            if not self.settings.has_section('values'):
                self.settings.add_section('values')
            for field in self.values_dict.keys():
                field_values = SETTINGS_SEPARATOR.join(self.values_dict[field])
                field_values = field_values.replace('%', '%%')
                if field_values:
                    self.settings.set('values', field, field_values)

            self.grid.space_as_dot = settings_editor.space_as_dot_checkbox.GetValue()
            self.show_need_adjust_mark = settings_editor.show_need_adjust_mark_checkbox.GetValue()
            if not self.settings.has_section('general'):
                self.settings.add_section('general')
            self.settings.set(
                'general',
                'space as dot',
                {True:'1', False:'0'}[self.grid.space_as_dot]
                )
            self.settings.set(
                'general',
                'show need adjust mark',
                {True:'1', False:'0'}[self.show_need_adjust_mark]
                )

            auto_groups_items_count = settings_editor.auto_groups_checklistbox.GetCount()
            self.auto_groups_dict = {}
            for item in range(auto_groups_items_count):
                value = {True:u'1', False:u'0'}[settings_editor.auto_groups_checklistbox.IsChecked(item)]
                text = settings_editor.auto_groups_checklistbox.GetString(item)
                parts = split_auto_groups_item(text)
                if parts:
                    self.auto_groups_dict[parts[0]] = value + parts[1]

            self.group_names_dict = {}
            for i in range(settings_editor.group_names_listctrl.GetItemCount()):
                singular = settings_editor.group_names_listctrl.GetItemText(i, 1)
                plural = settings_editor.group_names_listctrl.GetItemText(i, 0)
                self.group_names_dict[plural] = singular

            self.Refresh()

    def on_settings_import(self, event):
        """
        Import settings from specified file.

        """
        try:
            settings_import_dialog = wx.FileDialog( self,
                u'Загрузить параметры из файла...',
                os.path.dirname(DEFAULT_SETTINGS_FILE_NAME),
                os.path.basename(DEFAULT_SETTINGS_FILE_NAME),
                u'Конфигурационный файл (*.ini)|*.ini|Все файлы (*.*)|*.*',
                wx.FD_OPEN
                )
            if settings_import_dialog.ShowModal() == wx.ID_CANCEL:
                return
            settings_file_name = settings_import_dialog.GetPath()
            self.load_settings(settings_file_name, True)
        except IOError as e:
            wx.MessageBox(
                u'При загрузке параметров из файла:\n' +
                settings_file_name + '\n' \
                u'возникла ошибка:\n' +
                e.strerror + '\n\n' \
                'Параметры не загружены или загружены не полностью.',
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )
        except:
            self.on_error()

    def on_settings_export(self, event):
        """
        Export settings to specified file.

        """
        try:
            settings_export_dialog = wx.FileDialog( self,
                u'Сохранить параметры в файл...',
                os.path.dirname(DEFAULT_SETTINGS_FILE_NAME),
                os.path.basename(DEFAULT_SETTINGS_FILE_NAME),
                u'Конфигурационный файл (*.ini)|*.ini|Все файлы (*.*)|*.*',
                wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
                )
            if settings_export_dialog.ShowModal() == wx.ID_CANCEL:
                return
            settings_file_name = settings_export_dialog.GetPath()
            self.save_settings(settings_file_name)
        except IOError as e:
            wx.MessageBox(
                u'При сохранении параметров в файл:\n' +
                settings_file_name + '\n' \
                u'возникла ошибка:\n' +
                e.strerror + '\n\n' \
                u'Параметры не сохранены или сохранены не полностью.',
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )
        except:
            self.on_error()

    def on_exit(self, event):
        """
        Close the program.

        """
        if not self.saved:
            if wx.MessageBox(
                u'Имеются не сохранённые изменения!\nВыйти из приложения?',
                u'Внимание!',
                wx.ICON_QUESTION|wx.YES_NO, self
                ) == wx.NO:

                return

        self.save_settings(self.settings_file)
        self.Destroy()

    def on_clear_fields(self, event):
        """
        Clears user specified fields of selected components.

        """
        selected_rows = self.grid.GetSelectedRows()
        selected_cols = self.get_checked_cols()
        for row in selected_rows:
            for col in selected_cols:
                self.grid.set_cell_value(row, col, u'')
        if self.grid.is_changed():
            self.on_grid_change()

    def on_find_replace(self, event):
        """
        Find specified text in grid's cells.

        """

        def on_find_next(event):
            """
            Find next match.

            """
            find_str = find_dialog.textctrl_find.GetValue()
            case_sensitive = find_dialog.checkbox_case_sensitive.GetValue()
            whole_word = find_dialog.checkbox_whole_word.GetValue()
            if not find_str:
                return

            rows = self.grid.GetNumberRows()
            cols = self.grid.GetNumberCols()
            cur_row = self.grid.GetGridCursorRow()
            cur_col = self.grid.GetGridCursorCol()
            for row in range(cur_row, rows):
                for col in range(1, cols):
                    if row == cur_row and col <= cur_col:
                        continue
                    cell_value = self.grid.GetCellValue(row, col)
                    if not case_sensitive:
                        cell_value = cell_value.lower()
                        find_str = find_str.lower()
                    if whole_word:
                        cell_value = cell_value.split()
                    if find_str in cell_value:
                        self.not_found = False
                        self.grid.SetGridCursor(row, col)
                        self.grid.SelectRow(row)
                        self.grid.MakeCellVisible(row, col)
                        self.grid.SetFocus()
                        return
            if not self.not_found and wx.MessageBox(
                u'Достигнут конец таблицы.\nПродолжить сначала?',
                u'Поиск',
                wx.ICON_QUESTION | wx.YES_NO, self
                ) == wx.YES:

                self.not_found = True
                self.grid.SetGridCursor(0, 0)
                on_find_next(event)
            elif self.not_found:
                wx.MessageBox(
                    u'Совпадения не найдены!',
                    u'Поиск',
                    wx.ICON_INFORMATION | wx.OK, self
                    )

        def on_find_prev(event):
            """
            Find previous match.

            """
            find_str = find_dialog.textctrl_find.GetValue()
            case_sensitive = find_dialog.checkbox_case_sensitive.GetValue()
            whole_word = find_dialog.checkbox_whole_word.GetValue()
            if not find_str:
                return
            rows = self.grid.GetNumberRows()
            cols = self.grid.GetNumberCols()
            cur_row = self.grid.GetGridCursorRow()
            cur_col = self.grid.GetGridCursorCol()
            for row in reversed(range(0, cur_row)):
                for col in reversed(range(1, cols)):
                    if row == cur_row and col >= cur_col:
                        continue
                    cell_value = self.grid.GetCellValue(row, col)
                    if not case_sensitive:
                        cell_value = cell_value.lower()
                        find_str = find_str.lower()
                    if whole_word:
                        cell_value = cell_value.split()
                    if find_str in cell_value:
                        self.not_found = False
                        self.grid.SetGridCursor(row, col)
                        self.grid.SelectRow(row)
                        self.grid.MakeCellVisible(row, col)
                        self.grid.SetFocus()
                        return
            if not self.not_found and wx.MessageBox(
                u'Достигнуто начало таблицы.\nПродолжить с конца?',
                u'Поиск',
                wx.ICON_QUESTION | wx.YES_NO,
                self
                ) == wx.YES:

                self.not_found = True
                self.grid.SetGridCursor(rows, cols)
                on_find_prev(event)
            elif self.not_found:
                wx.MessageBox(
                    u'Совпадения не найдены!',
                    u'Поиск',
                    wx.ICON_INFORMATION | wx.OK, self
                    )

        def on_replace(event):
            """
            Replace the text in selected cell.

            """
            replace_str = find_dialog.textctrl_replace.GetValue()
            if not replace_str:
                return
            cur_col = self.grid.GetGridCursorCol()
            if cur_col == 2 or (cur_col == 4 and self.library):
                return
            cur_row = self.grid.GetGridCursorRow()
            cell_value = self.grid.GetCellValue(cur_row, cur_col)
            find_str = find_dialog.textctrl_find.GetValue()
            replace_str = find_dialog.textctrl_replace.GetValue()
            if find_str not in cell_value:
                wx.MessageBox(
                    u'В выделенной ячейке не найдено совпадений для замены!',
                    u'Замена',
                    wx.ICON_ERROR | wx.OK, self
                    )
                return
            new_cell_value = cell_value.replace(find_str, replace_str, 1)
            self.grid.set_cell_value(cur_row, cur_col, new_cell_value)
            self.on_grid_change()

        def on_find_replace_close(event):
            """
            Enable menu items when find/replace dialog closed.

            """
            self.menuitem_find.Enable(True)
            self.menuitem_replace.Enable(True)
            event.Skip()

        self.menuitem_find.Enable(False)
        self.menuitem_replace.Enable(False)
        find_dialog = gui.FindReplaceDialog(self)
        find_dialog.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
        find_dialog.Bind(wx.EVT_CLOSE, on_find_replace_close)
        find_dialog.button_find_next.Bind(wx.EVT_BUTTON, on_find_next)
        find_dialog.textctrl_find.Bind(wx.EVT_TEXT_ENTER, on_find_next)
        find_dialog.button_find_prev.Bind(wx.EVT_BUTTON, on_find_prev)
        if event.GetId() == gui.ID_FIND:
            find_dialog.SetTitle(u'Поиск')
            find_dialog.panel_replace.Hide()
            find_dialog.GetSizer().Fit(find_dialog)
        elif event.GetId() == gui.ID_REPLACE:
            find_dialog.SetTitle(u'Замена')
            find_dialog.button_replace.Bind(wx.EVT_BUTTON, on_replace)
        find_dialog.textctrl_find.SetFocus()
        find_dialog.Show()

    def on_about(self, event):
        """
        Shows about dialog.

        """
        about_dialog = gui.AboutDialog(self)
        about_dialog.Bind(wx.EVT_CHAR_HOOK, self.on_esc_key)
        about_dialog.statictext_version.SetLabel(
                about_dialog.statictext_version.GetLabel() + \
                str(VERSION) + '\n' + \
                'Python: {}.{}.{}-{}'.format(
                    sys.version_info[0],
                    sys.version_info[1],
                    sys.version_info[2],
                    sys.version_info[3]
                    ) + '\n' + \
                'wxWidgets: {}'.format(wx.version()) + '\n' + \
                'odfpy: {}'.format(odfpy_version.split('/')[-1])
                )
        about_dialog.hyperlink_email.SetURL(
                '{}%20v{}'.format(
                    about_dialog.hyperlink_email.GetURL(),
                    VERSION
                    )
                )
        about_dialog.Layout()
        about_dialog.Fit()
        about_dialog.CentreOnParent()
        about_dialog.dialog_buttonOK.SetFocus()
        about_dialog.ShowModal()

    def on_help(self, event):
        """
        Shows help manual.

        """
        exec_dir = os.path.dirname(os.path.abspath(__file__))
        help_file = os.path.join(exec_dir, 'doc', 'user_manual.html')
        webbrowser.open_new(help_file)

    def on_esc_key(self, event):
        """
        Close  dialog if ESC key pressed.

        """
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            event_object = event.GetEventObject()
            while event_object != None:
                class_name = event_object.GetClassName()
                if class_name == 'wxDialog':
                    event_object.Close()
                    break
                event_object = event_object.GetParent()
        else:
            event.Skip()

    def on_error(self):
        """
        Show message of critical error.
        """
        try:
            trace_frame = inspect.trace()[-1]
            arg_values = inspect.getargvalues(trace_frame[0])
            last_call = u'\n\t{fname}{aval}'.format(
                    fname = trace_frame[3],
                    aval = inspect.formatargvalues(*arg_values)
                    )
        except:
            last_call = ''
        logging.exception(last_call)
        log_filename = os.path.join(
                self.config_path,
                DEFAULT_LOGGING_FILE_NAME
                )
        log_text = '...\n'
        if os.path.exists(log_filename):
            with codecs.open(log_filename, 'r', encoding='utf-8') as log_file:
                log_lines = log_file.readlines()
                log_lines.reverse()
                log_text = u''
                line_num = 0
                for line in log_lines:
                    log_text = line + log_text
                    line_num += 1
                    if line[:4].isdigit() and line.endswith(u'ERROR'):
                        break
                    elif line_num > 9:
                        break
        error_message = wx.MessageDialog(
                self,
                u'В программе произошёл сбой!\n' +
                u'Подробное описание ошибки записано в файл\n' +
                log_filename,
                u'Внимание!',
                wx.ICON_ERROR|wx.OK|wx.CANCEL
                )
        error_message.SetExtendedMessage(log_text)
        error_message.SetOKLabel(u'Открыть файл...')
        result = error_message.ShowModal()
        if result == wx.ID_OK:
            webbrowser.open_new(log_filename)
        # Set cursor back to 'normal'
        if wx.IsBusy():
            wx.EndBusyCursor()

        raise


def main():
    """
    Main function - called at start.

    """
    # Parsing of command-line arguments
    parser = argparse.ArgumentParser(
        description=(
            u'Приложение создаёт файл перечня элементов оформленный ' \
            u'в соответствии с ЕСКД для схемы выполненной в САПР KiCad.\n'
            )
        )
    parser.add_argument(
        'schematic',
        default='',
        nargs='?',
        type=str,
        help=u'полное или относительное имя файла схемы в формате KiCad'
        )
    parser.add_argument(
        'complist',
        default='',
        nargs='?',
        type=str,
        help=u'полное или относительное имя файла перечня элементов'
        )
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help=u'отобразить версию программы и выйти'
        )
    args = parser.parse_args()

    # Current version
    version_file = codecs.open('version', 'r', 'utf-8')
    global VERSION
    VERSION = version_file.read()
    VERSION = VERSION.replace('\n', '')
    version_file.close()

    if args.version:
        print VERSION
        exit()

    app = wx.App(False)
    window = Window(None)
    app.SetTopWindow(window)

    if args.schematic:
        os.chdir(os.path.abspath(EXEC_PATH))
        sch_file_name = os.path.splitext(os.path.abspath(args.schematic))[0] + '.sch'
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        if os.path.isfile(sch_file_name):
            window.on_open_sch(sch_file_name=sch_file_name)
            if args.complist:
                os.chdir(os.path.abspath(EXEC_PATH))
                name_and_ext = os.path.splitext(os.path.abspath(args.complist))
                if name_and_ext[-1] in (u'.odt', u'.ods', u'csv'):
                    window.complist_file = ''.join(name_and_ext)
                else:
                    window.complist_file = name_and_ext[0] + u'.ods'
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
        else:
            if wx.MessageBox(
                u'Указанный файл схемы:\n' +
                sch_file_name + '\n' \
                u'не найден!\n' + \
                u'Выбрать нужный файл вручную?',
                u'Внимание!',
                wx.ICON_QUESTION|wx.YES_NO, window
                ) == wx.YES:
                window.on_open_sch()
            else:
                exit()

    window.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
