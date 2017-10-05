#!/usr/bin/env python2
# -*-    Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4    -*-
### BEGIN LICENSE
# Copyright (C) 2016 Baranovskiy Konstantin (baranovskiykonstantin@gmail.com)
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

import os
import sys
import subprocess
import shutil
import re
import codecs
import argparse
import webbrowser
from operator import itemgetter
from ConfigParser import SafeConfigParser

import wx
import wx.grid

from odf.opendocument import __version__ as odfpy_version

EXEC_PATH = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import gui
from controls import *
from kicadsch import *
from complist import *

# Set default encoding
reload(sys)
sys.setdefaultencoding('utf-8')

# Global
version = ''
default_settings_file_name = 'settings.ini'
settings_separator = ';;;'
ID_RECENT = 2000

class Window(gui.MainFrame):
    """
    Graphical user interface for kicdbom2spec.

    """

    def __init__(self, parent):
        """
        Initialize main window.

        """
        gui.MainFrame.__init__(self, parent)

        # Events
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_toolbar)

        # Variables
        self.schematic_file = ''
        self.library_file = ''
        self.complist_file = ''
        self.sheets = []
        self.library = None
        self.saved = True
        self.not_found = False
        self.settings_file = ''

        self.init_grid()

        # Default settings
        self.save_window_size_pos = False
        self.save_selected_mark = False
        self.save_col_size = False
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
            'decimal_num':u'',
            'developer':u'',
            'verifier':u'',
            'inspector':u'',
            'approver':u'',
            'comp':u'',
            'title':u''
            }

        if sys.platform == 'win32':
            icon = wx.Icon('bitmaps/icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)

            self.settings_file = os.path.join(
                    os.environ['APPDATA'],
                    'kicadbom2spec'
                    )
        else:
            icon = wx.Icon('bitmaps/icon.xpm', wx.BITMAP_TYPE_XPM)
            self.SetIcon(icon)

            self.settings_file = os.path.join(
                    os.path.expanduser('~/.config'),
                    'kicadbom2spec'
                    )

        # At this moment in settings_file contains path only
        if not os.path.exists(self.settings_file):
            os.makedirs(self.settings_file)

        self.settings_file = os.path.join(
                self.settings_file,
                default_settings_file_name
                )

        if not os.path.exists(self.settings_file):
            shutil.copy2(default_settings_file_name, self.settings_file)

        self.load_settings(self.settings_file)

    def load_settings(self, settings_file_name=default_settings_file_name, select=False):
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
                    self.save_window_size_pos = True
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
                    self.save_col_size = True
                    if hasattr(self, 'grid'):
                        for col in self.settings.options('column sizes'):
                            col_size = self.settings.getint('column sizes', col)
                            self.grid.SetColSize(int(col), col_size)

                if self.settings.has_section('values'):
                    for item in self.values_dict.keys():
                        if self.settings.has_option('values', item):
                            values_list = self.settings.get('values', item)
                            values_list = values_list.split(settings_separator)
                            if values_list != ['']:
                                self.values_dict[item] = values_list

                if self.settings.has_section('general'):
                    if self.settings.has_option('general', 'remember selection'):
                        self.save_selected_mark = self.settings.getboolean('general', 'remember selection')

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
                    'position':False,
                    'size':False,
                    'column_sizes':False,
                    'values':False,
                    'remember_selection':False,
                    'auto_filling_groups':False,
                    'separators':False,
                    'aliases':False,
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
                if temp_settings.has_section('window'):
                    if temp_settings.has_option('window', 'x') and \
                            temp_settings.has_option('window', 'y'):
                        selector.checkbox_position.SetValue(True)
                        selector.checkbox_position.Show()
                    if temp_settings.has_option('window', 'width') and \
                            temp_settings.has_option('window', 'height'):
                        selector.checkbox_size.SetValue(True)
                        selector.checkbox_size.Show()
                if temp_settings.has_section('column sizes'):
                    selector.checkbox_column_sizes.SetValue(True)
                    selector.checkbox_column_sizes.Show()
                if temp_settings.has_section('values'):
                    selector.checkbox_values.SetValue(True)
                    selector.checkbox_values.Show()
                if temp_settings.has_section('general') and \
                        temp_settings.has_option('general', 'remember selection'):
                    selector.checkbox_remember_selection.SetValue(True)
                    selector.checkbox_remember_selection.Show()
                if temp_settings.has_section('auto filling groups'):
                    selector.checkbox_auto_filling_groups.SetValue(True)
                    selector.checkbox_auto_filling_groups.Show()
                if temp_settings.has_section('prefixes') or \
                       temp_settings.has_section('suffixes'):
                    selector.checkbox_separators.SetValue(True)
                    selector.checkbox_separators.Show()
                if temp_settings.has_section('aliases'):
                    selector.checkbox_aliases.SetValue(True)
                    selector.checkbox_aliases.Show()
                if temp_settings.has_section('complist'):
                    selector.checkbox_complist.SetValue(True)
                    selector.checkbox_complist.Show()
                if temp_settings.has_section('recent sch'):
                    selector.checkbox_recent_sch.SetValue(True)
                    selector.checkbox_recent_sch.Show()
                if temp_settings.has_section('recent lib'):
                    selector.checkbox_recent_lib.SetValue(True)
                    selector.checkbox_recent_lib.Show()
                selector.Layout()
                selector.Fit()
                selector.Centre()
                result = selector.ShowModal()
                if result == wx.ID_OK:
                    for key in import_settings.keys():
                        import_settings[key] = getattr(selector, 'checkbox_' + key).IsChecked()
                    if import_settings['position']:
                        self.save_window_size_pos = True
                        x = temp_settings.getint('window', 'x')
                        y = temp_settings.getint('window', 'y')
                        self.SetPosition(wx.Point(x, y))
                    if import_settings['size']:
                        self.save_window_size_pos = True
                        width = temp_settings.getint('window', 'width')
                        height = temp_settings.getint('window', 'height')
                        if temp_settings.has_option('window', 'maximized'):
                            if temp_settings.getint('window', 'maximized'):
                                self.Maximize()
                        self.SetClientSize(wx.Size(width, height))
                    if import_settings['column_sizes']:
                        self.save_col_size = True
                        if hasattr(self, 'grid'):
                            for col in temp_settings.options('column sizes'):
                                col_size = temp_settings.getint('column sizes', col)
                                self.grid.SetColSize(int(col), col_size)
                    if import_settings['values']:
                        for item in self.values_dict.keys():
                            if temp_settings.has_option('values', item):
                                values_list = temp_settings.get('values', item)
                                values_list = values_list.split(settings_separator)
                                if values_list != ['']:
                                    self.values_dict[item] = values_list
                    if import_settings['remember_selection']:
                        self.save_selected_mark = temp_settings.getboolean('general', 'remember selection')
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

    def save_settings(self, settings_file_name=default_settings_file_name):
        """
        Save settings to configuration file.

        """
        if self.save_window_size_pos:
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
        else:
            self.settings.remove_section('window')

        if self.save_col_size:
            if not self.settings.has_section('column sizes'):
                self.settings.add_section('column sizes')
            for col in range(self.grid.GetNumberCols()):
                col_size = self.grid.GetColSize(col)
                self.settings.set('column sizes', str(col), str(col_size))
        else:
            self.settings.remove_section('column sizes')

        if not self.settings.has_section('values'):
            self.settings.add_section('values')
        for field in self.values_dict.keys():
            field_values = settings_separator.join(self.values_dict[field])
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

        if not self.settings.has_section('general'):
            self.settings.add_section('general')
        self.settings.set(
            'general',
            'remember selection',
            {True:'1', False:'0'}[self.save_selected_mark]
            )

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
        # Save column width
        if hasattr(self, 'grid'):
            if self.save_col_size:
                if not self.settings.has_section('column sizes'):
                    self.settings.add_section('column sizes')
                for col in range(self.grid.GetNumberCols()):
                    col_size = self.grid.GetColSize(col)
                    self.settings.set('column sizes', str(col), str(col_size))

            self.GetSizer().Remove(self.panel_components.GetSizer())
            self.grid.Destroy()

        # New grid
        self.grid = Grid(self.panel_components, self)
        # Events
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

        # Restore column width
        if hasattr(self, 'settings'):
            if self.settings.has_section('column sizes'):
                for col in self.settings.options('column sizes'):
                    col_size = self.settings.getint('column sizes', col)
                    self.grid.SetColSize(int(col), col_size)

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
        for sheet in self.sheets:
            for comp in complist.get_components(sheet.sch_name, True):
                # Skip unannotated components
                if not comp.fields[0].text or comp.fields[0].text.endswith('?'):
                    continue
                # Skip parts of the same component
                for row in values:
                    if comp.fields[0].text == row[2]:
                        break
                else:
                    row = [
                        u'1',  # Used
                        u'',  # Group
                        comp.fields[0].text,  # Reference
                        u'',  # Mark
                        u'',  # Value
                        u'',  # Accuracy
                        u'',  # Type
                        u'',  # GOST
                        u'',  # Comment
                        sheet.sch_name  # Sheet name
                        ]
                    if self.aliases_dict[u'значение'] == u'':
                        row[4] = comp.fields[1].text
                    for field in comp.fields:
                        if hasattr(field, 'name'):
                            if field.name == u'Исключён из ПЭ':
                                row[0] = u'0'
                            if field.name == self.aliases_dict[u'группа']:
                                row[1] = field.text
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
                    if row[1] == u'':
                        for suffix in self.auto_groups_dict.keys():
                            if row[2].startswith(suffix) and self.auto_groups_dict[suffix].startswith('1'):
                                row[1] = self.auto_groups_dict[suffix][1:]
                                break
                    if hasattr(comp, 'path_and_ref'):
                        prefix = '*'
                        # Do not mark components that only has parts (not copies)
                        # on different sheets.
                        for ref in comp.path_and_ref:
                            if ref[1] != comp.fields[0].text:
                                break
                        else:
                            prefix = ''
                        for ref in comp.path_and_ref:
                            # Skip unannotated components
                            if not ref[1] or ref[1].endswith('?'):
                                continue
                            # Skip parts of the same comp from different sheets
                            for value in values:
                                tmp_ref = value[2]
                                tmp_ref = tmp_ref.split('(')[0]
                                tmp_ref = tmp_ref.rstrip('*')
                                if tmp_ref == ref[1]:
                                    break
                            else:
                                new_row = list(row)
                                if ref[1] == comp.fields[0].text:
                                    new_row[2] = comp.fields[0].text + prefix
                                else:
                                    new_row[2] = '{}({})'.format(ref[1], comp.fields[0].text)
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
        for sheet in self.sheets:
            for item in sheet.items:
                if item.__class__.__name__ == 'Comp':
                    if not item.ref.startswith('#'):
                        for value in sorted_values:
                            # Skip copies of the one component (see 'path_and_ref' in Comp)
                            if ('(' in value[2]) and (')' in value[2]):
                                continue
                            if value[2].rstrip('*') == item.fields[0].text \
                                    and value[-1] == sheet.sch_name:
                                # Default field of "value"
                                if field_names[4] == u'':
                                    item.fields[1].text = value[4]
                                for index, field_name in field_names.items():
                                    # Skip "value" if used standard field for it
                                    if index == 4 and field_names == u'':
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
                                            item.fields.append(sheet.Comp.Field(str_field.encode('utf-8')))
                                    else:
                                        for field_index, field in enumerate(item.fields):
                                            if hasattr(field, 'name'):
                                                if field.name == field_name:
                                                    del item.fields[field_index]
                                                    break

                                if self.save_selected_mark and value[0] == '0':
                                    str_field = u'F ' + str(len(item.fields))
                                    str_field += u' "" '
                                    str_field += u' H ' + str(item.pos_x) + u' ' + str(item.pos_y) + u' 60'
                                    str_field += u' 0001 C CNN'
                                    str_field += u' "Исключён из ПЭ"'
                                    item.fields.append(sheet.Comp.Field(str_field.encode('utf-8')))
                                else:
                                    for field_index, field in enumerate(item.fields):
                                        if hasattr(field, 'name'):
                                            if field.name == u'Исключён из ПЭ':
                                                del item.fields[field_index]
                                                break

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
                u'1',  # Used
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
                                    comp.fields.append(self.library.Component.Field(str_field.encode('utf-8')))
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
            Check/uncheck all fields in field seletor.

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

    def isreal(self, s):
        """
        Return true if string contain real number.

        """
        try:
            float(s.replace(',', '.'))
            return True
        except:
            return False

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
        event.Skip()

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

        copy_id = wx.NewId()
        cut_id = wx.NewId()
        paste_id = wx.NewId()
        edit_id = wx.NewId()
        clear_id = wx.NewId()

        menu = wx.Menu()

        item = wx.MenuItem(menu, copy_id, u'Копировать поля')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-copy.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_copy, item)
        menu.Enable(copy_id, self.menuitem_copy.IsEnabled())

        item = wx.MenuItem(menu, cut_id, u'Вырезать поля…')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-cut.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_cut, item)
        menu.Enable(cut_id, self.menuitem_cut.IsEnabled())

        item = wx.MenuItem(menu, paste_id, u'Вставить поля…')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-paste.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_paste, item)
        menu.Enable(paste_id, self.menuitem_paste.IsEnabled())

        menu.Append(wx.ID_SEPARATOR)

        item = wx.MenuItem(menu, edit_id, u'Редактировать поля…')
        item.SetBitmap(wx.Bitmap(u'bitmaps/gtk-edit.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_edit_fields, item)
        menu.Enable(edit_id, self.menuitem_edit.IsEnabled())

        item = wx.MenuItem(menu, clear_id, u'Очистить поля…')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-clear.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.on_clear_fields, item)
        menu.Enable(clear_id, self.menuitem_clear.IsEnabled())

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


    def on_copy(self, event=None):
        """
        Copy values of the fields.

        """
        if len(self.grid.get_selected_rows()) > 1:
            if wx.MessageBox(
                u'В таблице выделено несколько элементов!\n' \
                u'Будут скопированы поля только из первого выделенного элемента.\n' \
                u'Продолжить?',
                u'Внимание!',
                wx.ICON_QUESTION|wx.YES_NO, self
                ) == wx.NO:

                return
        self.buffer = []
        row = self.grid.get_selected_rows()[0]
        for col in range(1, 9):
            if col == 2:
                self.buffer.append(u'')
                continue
            self.buffer.append(self.grid.GetCellValue(row, col))
        self.menuitem_paste.Enable(True)

    def on_cut(self, event):
        """
        Cut values of the fields.

        """
        if len(self.grid.get_selected_rows()) > 1:
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
        row = self.grid.get_selected_rows()[0]
        for col in range(1, 9):
            if col == 2:
                self.buffer.append(u'')
                continue
            self.buffer.append(self.grid.GetCellValue(row, col))
            if col in selected_cols:
                self.grid.set_cell_value(row, col, u'')
        self.menuitem_paste.Enable(True)
        if self.grid.is_changed():
            self.on_grid_change()

    def on_paste(self, event):
        """
        Paste values to the fields of the selected components from buffer.

        """
        def on_idle(event):
            if editor.GetMinSize().GetHeight() == -1:
                editor.SetMinSize(editor.GetSize())
                editor.SetMaxSize(wx.Size(-1, editor.GetSize().GetHeight()))

        def on_button(event):
            for row in selected_rows:
                for col in range(1, col_num):
                    if col == 2:
                        continue
                    if self.library and col == 4:
                        continue
                    new_value = getattr(editor, 'editor_ctrl_%i' % col).text_ctrl.GetValue()
                    if new_value == u'<не изменять>':
                        continue
                    else:
                        self.grid.set_cell_value(row, col, new_value)
            if self.grid.is_changed():
                self.on_grid_change()
            event.Skip()

        if len(self.grid.get_selected_rows()) >= 1:

            editor = gui.EditorDialog(self)
            editor.SetMaxSize((self.GetSize().GetWidth(), -1))
            editor.SetTitle(u'Вставка полей')
            editor.checkbox.Hide()
            col_num = self.grid.GetNumberCols()
            selected_rows = self.grid.get_selected_rows()
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
            if self.library:
                editor.statictext_4.Hide()
                editor.editor_ctrl_4.Hide()
                editor.Layout()
            editor.GetSizer().Fit(editor)
            editor.CenterOnParent()
            editor.Layout()
            editor.Bind(wx.EVT_IDLE, on_idle)
            editor.dialog_buttonsOK.Bind(wx.EVT_BUTTON, on_button)
            # Need to use Show instead of ShowModal otherwise EditorCtrlPopup
            # was freezed.
            editor.Show()

    def on_select(self, event):
        """
        Process selection event.

        """
        if self.grid.get_selected_rows():
            self.menuitem_copy.Enable(True)
            self.menuitem_cut.Enable(True)
            self.menuitem_edit.Enable(True)
            self.menuitem_clear.Enable(True)
        else:
            self.menuitem_copy.Enable(False)
            self.menuitem_cut.Enable(False)
            self.menuitem_edit.Enable(False)
            self.menuitem_clear.Enable(False)
        event.Skip()

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
            self.complist_file = os.path.splitext(self.schematic_file)[0] + '.ods'
            self.library = None
            self.init_grid()
            complist = CompList()
            sheet_names = [self.schematic_file]
            sheet_names.extend(complist.get_sheets(self.schematic_file))
            sheet_names = sorted(sheet_names)
            self.sheets = []
            for sheet_name in sheet_names:
                self.sheets.append(Schematic(sheet_name))
            sch_values = self.get_schematic_values()
            self.grid.AppendRows(len(sch_values))
            self.grid.set_values(sch_values)
            self.grid.undo_buffer = []
            self.grid.redo_buffer = []
            self.grid.on_sort()
            self.on_grid_change()
            self.saved = True

            # Stamp fields
            sch = Schematic(self.schematic_file)
            self.stamp_dict['decimal_num'] = sch.descr.comment1.decode('utf-8')
            self.stamp_dict['developer'] = sch.descr.comment2.decode('utf-8')
            self.stamp_dict['verifier'] = sch.descr.comment3.decode('utf-8')
            self.stamp_dict['approver'] = sch.descr.comment4.decode('utf-8')
            self.stamp_dict['comp'] = sch.descr.comp.decode('utf-8')
            self.stamp_dict['title'] = sch.descr.title.decode('utf-8')

            # Menu & Toolbar
            self.menuitem_complist.Enable(True)
            self.menuitem_save_sch.Enable(False)
            self.menuitem_save_sch_as.Enable(True)
            self.menuitem_find.Enable(True)
            self.menuitem_replace.Enable(True)
            self.add_to_recent(self.schematic_file, 'sch')

            # Set cursor back to 'normal'
            wx.EndBusyCursor()

            # Title
            self.SetTitle('kicadbom2spec - ' + self.schematic_file)

        except:
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

            # Remove bad file from rcent
            self.remove_from_recent(self.schematic_file, 'sch')

            wx.MessageBox(
                u'При открытии файла схемы:\n' +
                self.schematic_file + '\n' \
                u'возникла ошибка:\n' + \
                str(sys.exc_info()[1]),
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )

    def on_save_sch(self, event):
        """
        Save changes in the fields of the components to the schematic file.

        """
        comp_values = self.grid.get_values()
        self.set_schematic_values(comp_values)
        for sheet in self.sheets:
            if sheet.sch_name == self.schematic_file:
                # Stamp fields
                sheet.descr.comment1 = self.stamp_dict['decimal_num']
                sheet.descr.comment2 = self.stamp_dict['developer']
                sheet.descr.comment3 = self.stamp_dict['verifier']
                sheet.descr.comment4 = self.stamp_dict['approver']
                sheet.descr.comp = self.stamp_dict['comp']
                sheet.descr.title = self.stamp_dict['title']

            try:
                if os.path.exists(sheet.sch_name + '.tmp'):
                    os.remove(sheet.sch_name + '.tmp')
                sheet.save(sheet.sch_name + '.tmp')
                os.remove(sheet.sch_name)
                os.rename(sheet.sch_name + '.tmp', sheet.sch_name)
                self.saved = True
                self.menuitem_save_sch.Enable(False)
            except:
                if os.path.exists(sheet.sch_name + '.tmp'):
                    os.remove(sheet.sch_name + '.tmp')
                wx.MessageBox(
                    u'При сохранении файла схемы:\n' +
                    sheet.sch_name + '\n' \
                    u'возникла ошибка:\n' +
                    str(sys.exc_info()[1]) + '\n' +
                    u'Файл не сохранен.',
                    u'Внимание!',
                    wx.ICON_ERROR|wx.OK, self
                    )

    def on_save_sch_as(self, event):
        """
        Save changes in the fields of the components to the separate
        schematic file(s).

        """
        comp_values = self.grid.get_values()
        self.set_schematic_values(comp_values)
        new_schematic_file = ''
        for sheet in self.sheets:
            if sheet.sch_name == self.schematic_file:
                # Stamp fields
                sheet.descr.comment1 = self.stamp_dict['decimal_num']
                sheet.descr.comment2 = self.stamp_dict['developer']
                sheet.descr.comment3 = self.stamp_dict['verifier']
                sheet.descr.comment4 = self.stamp_dict['approver']
                sheet.descr.comp = self.stamp_dict['comp']
                sheet.descr.title = self.stamp_dict['title']

            try:
                save_sch_dialog = wx.FileDialog(
                    self,
                    u'Сохранить схему как...',
                    os.path.dirname(sheet.sch_name),
                    os.path.basename(sheet.sch_name),
                    u'Схема (*.sch)|*.sch|Все файлы (*.*)|*.*',
                    wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
                    )
                if save_sch_dialog.ShowModal() == wx.ID_CANCEL:
                    return
                new_schematic_file = save_sch_dialog.GetPath()
                if os.path.exists(new_schematic_file  + '.tmp'):
                    os.remove(new_schematic_file + '.tmp')
                sheet.save(new_schematic_file + '.tmp')
                if os.path.exists(new_schematic_file):
                    os.remove(new_schematic_file)
                os.rename(new_schematic_file + '.tmp', new_schematic_file)
                if new_schematic_file == sheet.sch_name:
                    self.saved = True
                    self.menuitem_save_sch.Enable(False)
            except:
                if os.path.exists(new_schematic_file + '.tmp'):
                    os.remove(new_schematic_file + '.tmp')
                wx.MessageBox(
                    u'При сохранении файла схемы:\n' +
                    new_schematic_file + '\n' \
                    u'возникла ошибка:\n' +
                    str(sys.exc_info()[1]) + '\n' \
                    u'Файл не сохранен.',
                    u'Внимание!',
                    wx.ICON_ERROR|wx.OK, self
                    )

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

            # Set cursor back to 'normal'
            wx.EndBusyCursor()

            # Title
            self.SetTitle('kicadbom2spec - ' + self.library_file)

        except:
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

            # Remove bad file from rcent
            self.remove_from_recent(self.library_file, 'lib')

            wx.MessageBox(
                u'При открытии файла библиотеки:\n' +
                self.library_file + '\n' \
                u'возникла ошибка:\n' + \
                str(sys.exc_info()[1]),
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )

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
        except:
            if os.path.exists(self.library_file + '.tmp'):
                os.remove(self.library_file + '.tmp')
            wx.MessageBox(
                u'При сохранении файла библиотеки:\n' +
                self.library_file + '\n' \
                u'возникла ошибка:\n' +
                str(sys.exc_info()[1]) + '\n' \
                u'Файл не сохранен.',
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )

    def on_save_lib_as(self, event):
        """
        Save changes in the fields of the components to the separate
        library file.

        """
        comp_values = self.grid.get_values()
        self.set_library_values(comp_values)
        new_library_file = ''
        try:
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
            if os.path.exists(new_library_file + '.tmp'):
                os.remove(new_library_file + '.tmp')
            self.library.save(new_library_file + '.tmp')
            if os.path.exists(new_library_file):
                os.remove(new_library_file)
            os.rename(new_library_file + '.tmp', new_library_file)
            self.saved = True
            self.menuitem_save_lib.Enable(False)
        except:
            if os.path.exists(new_library_file + '.tmp'):
                os.remove(new_library_file + '.tmp')
            wx.MessageBox(
                u'При сохранении файла библиотеки:\n' +
                self.library_file + '\n' \
                u'возникла ошибка:\n' +
                str(sys.exc_info()[1]) + '\n' \
                u'Файл не сохранен.',
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )

    def on_complist(self, event):
        """
        Make list of the components.

        """
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

        complist = CompList()
        complist_dialog = gui.CompListDialog(self)
        complist_dialog.stamp_decimal_num_text.Bind(wx.EVT_TEXT, on_decimal_num_changed)
        complist_dialog.stamp_title_text.Bind(wx.EVT_TEXT, on_title_changed)
        # Load settings
        all_components = False
        add_units = False
        open_complist = False
        need_changes_sheet = True
        if self.settings.has_section('complist'):
            if self.settings.has_option('complist', 'all'):
                all_components = self.settings.getboolean('complist', 'all')
            if self.settings.has_option('complist', 'units'):
                add_units = self.settings.getboolean('complist', 'units')
            if self.settings.has_option('complist', 'changes_sheet'):
                need_changes_sheet = self.settings.getboolean('complist', 'changes_sheet')
            if self.settings.has_option('complist', 'open'):
                open_complist = self.settings.getboolean('complist', 'open')
            if self.settings.has_option('complist', 'inspector'):
                self.stamp_dict['inspector'] = self.settings.get('complist', 'inspector')

        # Options
        complist_dialog.filepicker_complist.SetPath(self.complist_file)
        complist_dialog.checkbox_add_units.SetValue(add_units)
        complist_dialog.checkbox_all_components.SetValue(all_components)
        complist_dialog.checkbox_changes_sheet.SetValue(need_changes_sheet)
        complist_dialog.checkbox_open.SetValue(open_complist)
        # Stamp
        for field in self.stamp_dict.keys():
            field_text = getattr(complist_dialog, 'stamp_{}_text'.format(field))
            value = self.stamp_dict[field]
            value = value.replace('\\\\n', '\n')
            value = value.replace('\\"', '"')
            field_text.SetValue(value)

        result = complist_dialog.ShowModal()

        if result == wx.ID_OK:
            # Set cursor to 'wait'
            wx.BeginBusyCursor()
            wx.SafeYield()

            # Save settings from complist dialog
            all_components = complist_dialog.checkbox_all_components.IsChecked()
            add_units = complist_dialog.checkbox_add_units.IsChecked()
            need_changes_sheet = complist_dialog.checkbox_changes_sheet.IsChecked()
            open_complist = complist_dialog.checkbox_open.GetValue()
            # Stamp
            for field in self.stamp_dict.keys():
                field_text = getattr(complist_dialog, 'stamp_{}_text'.format(field))
                value = field_text.GetValue()
                value = value.replace('\n', '\\\\n')
                value = value.replace('"', '\\"')
                self.stamp_dict[field] = value

            if not self.settings.has_section('complist'):
                self.settings.add_section('complist')
            self.settings.set('complist', 'all', str(all_components))
            self.settings.set('complist', 'units', str(add_units))
            self.settings.set('complist', 'changes_sheet', str(need_changes_sheet))
            self.settings.set('complist', 'open', str(open_complist))
            self.settings.set('complist', 'inspector', self.stamp_dict['inspector'])
            self.complist_file = complist_dialog.filepicker_complist.GetPath()
            self.complist_file = os.path.splitext(self.complist_file)[0] + '.ods'
            comp_fields = []
            grid_values = self.grid.get_values()
            for row in grid_values:
                # Remove extra data from ref in comp like 'R123(R321)' or 'R321*'
                row[2] = row[2].split('(')[0]
                row[2] = row[2].rstrip('*')
                if (row[0] == u'1') | all_components:
                    fields = row[1:-1]
                    # Split reference on index and number
                    fields.insert(1, re.search(REF_REGULAR_EXPRESSION, fields[1]).group(1))
                    fields[2] = re.search(REF_REGULAR_EXPRESSION, fields[2]).group(2)
                    # Automatically units addition
                    if add_units and fields[4] != '':
                        if fields[1] == u'C' and fields[4][-1:] != u'Ф':
                            if fields[4].isdigit():
                                fields[4] += u'п'
                            elif self.isreal(fields[4]):
                                fields[4] += u'мк'
                            fields[4] += u'Ф'
                        elif fields[1] == u'L' and fields[4][-2:] != u'Гн':
                            fields[4] += u'Гн'
                        elif fields[1] == u'R' and fields[4][-2:] != u'Ом':
                            fields[4] += u'Ом'
                    # Adding separators
                    if fields[3]:
                        fields[3] = "{prefix}{value}{suffix}".format(
                                prefix = self.separators_dict[u'марка'][0],
                                value = fields[3],
                                suffix = self.separators_dict[u'марка'][1]
                                )
                    if fields[4]:
                        fields[4] = "{prefix}{value}{suffix}".format(
                                prefix = self.separators_dict[u'значение'][0],
                                value = fields[4],
                                suffix = self.separators_dict[u'значение'][1]
                                )
                    if fields[5]:
                        fields[5] = "{prefix}{value}{suffix}".format(
                                prefix = self.separators_dict[u'класс точности'][0],
                                value = fields[5],
                                suffix = self.separators_dict[u'класс точности'][1]
                                )
                    if fields[6]:
                        fields[6] = "{prefix}{value}{suffix}".format(
                                prefix = self.separators_dict[u'тип'][0],
                                value = fields[6],
                                suffix = self.separators_dict[u'тип'][1]
                                )
                    if fields[7]:
                        fields[7] = "{prefix}{value}{suffix}".format(
                                prefix = self.separators_dict[u'стандарт'][0],
                                value = fields[7],
                                suffix = self.separators_dict[u'стандарт'][1]
                                )
                    fields.append('1')
                    comp_fields.append(fields)
            try:
                complist.need_changes_sheet = need_changes_sheet
                complist.inspector = self.stamp_dict['inspector']
                complist.load(self.schematic_file, comp_fields)
                complist.save(self.complist_file)
            except:
                wx.MessageBox(
                    u'При создании перечня элементов:\n' +
                    self.complist_file + '\n' \
                    u'возникла ошибка:\n' + \
                    str(sys.exc_info()[1]) + '\n' \
                    u'Не удалось создать перечень элементов.',
                    u'Внимание!',
                    wx.ICON_ERROR|wx.OK, self
                    )
                # Set cursor back to 'normal'
                if wx.IsBusy():
                    wx.EndBusyCursor()
                return

            if open_complist:
                if sys.platform == 'linux2':
                    subprocess.Popen(["xdg-open", self.complist_file])
                else:
                    os.startfile(self.complist_file)
            else:
                wx.MessageBox(
                    u'Перечень элементов успешно создан и сохранен!',
                    u'kicdbom2spec',
                    wx.ICON_INFORMATION | wx.OK,
                    self
                    )

            # Set cursor back to 'normal'
            if wx.IsBusy():
                wx.EndBusyCursor()

    def on_edit_fields(self, event):
        """
        Open specialized window for editing fields of selected components.

        """
        def on_idle(event):
            if editor.GetMinSize().GetHeight() == -1:
                editor.SetMinSize(editor.GetSize())
                editor.SetMaxSize(wx.Size(-1, editor.GetSize().GetHeight()))

        def on_button(event):
            for row in selected_rows:
                if editor.checkbox.IsChecked():
                    self.grid.set_cell_value(row, 0, '1')
                else:
                    self.grid.set_cell_value(row, 0, '0')
                for col in range(1, col_num):
                    if col == 2:
                        continue
                    new_value = getattr(editor, 'editor_ctrl_%i' % col).text_ctrl.GetValue()
                    if new_value == u'<не изменять>':
                        continue
                    else:
                        self.grid.set_cell_value(row, col, new_value)
            if self.grid.is_changed():
                self.on_grid_change()

            event.Skip()

        editor = gui.EditorDialog(self)
        editor.SetMaxSize((self.GetSize().GetWidth(), -1))
        selected_rows = self.grid.get_selected_rows()
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
        if self.library:
            editor.checkbox.Hide()
            editor.statictext_4.Hide()
            editor.editor_ctrl_4.Hide()
            editor.Layout()
        editor.GetSizer().Fit(editor)
        editor.CenterOnParent()
        editor.Layout()
        editor.Bind(wx.EVT_IDLE, on_idle)
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

        settings_editor = gui.SettingsDialog(self)
        settings_editor.auto_groups_checklistbox.Bind(wx.EVT_LISTBOX, on_auto_groups_checklistbox_selected)
        settings_editor.auto_groups_checklistbox.Bind(wx.EVT_LISTBOX_DCLICK, on_auto_groups_edit_button_clicked)
        settings_editor.auto_groups_add_button.Bind(wx.EVT_BUTTON, on_auto_groups_add_button_clicked)
        settings_editor.auto_groups_edit_button.Bind(wx.EVT_BUTTON, on_auto_groups_edit_button_clicked)
        settings_editor.auto_groups_remove_button.Bind(wx.EVT_BUTTON, on_auto_groups_remove_button_clicked)

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
            prefix = self.separators_dict[separators_field_names[i]][0]
            suffix = self.separators_dict[separators_field_names[i]][1]
            prefix_text.SetValue(prefix)
            suffix_text.SetValue(suffix)

        settings_editor.window_checkbox.SetValue(self.save_window_size_pos)

        settings_editor.col_size_checkbox.SetValue(self.save_col_size)

        settings_editor.remember_selection_checkbox.SetValue(self.save_selected_mark)

        for suffix, value in self.auto_groups_dict.items():
            checked = {'1':True, '0':False}[value[:1]]
            value = u'{} - "{}"'.format(suffix, value[1:])
            index = settings_editor.auto_groups_checklistbox.Append(value)
            settings_editor.auto_groups_checklistbox.Check(index, checked)

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
                self.separators_dict[separators_field_names[i]][0] = prefix
                self.separators_dict[separators_field_names[i]][1] = suffix

            if not self.settings.has_section('values'):
                self.settings.add_section('values')
            for field in self.values_dict.keys():
                field_values = settings_separator.join(self.values_dict[field])
                field_values = field_values.replace('%', '%%')
                if field_values:
                    self.settings.set('values', field, field_values)

            self.save_window_size_pos = settings_editor.window_checkbox.GetValue()
            self.save_col_size = settings_editor.col_size_checkbox.GetValue()
            if not self.save_col_size:
                self.settings.remove_section('column sizes')
            self.save_selected_mark = settings_editor.remember_selection_checkbox.GetValue()
            if not self.settings.has_section('general'):
                self.settings.add_section('general')
            self.settings.set(
                'general',
                'remember selection',
                {True:'1', False:'0'}[self.save_selected_mark]
                )

            auto_groups_items_count = settings_editor.auto_groups_checklistbox.GetCount()
            self.auto_groups_dict = {}
            for item in range(auto_groups_items_count):
                value = {True:u'1', False:u'0'}[settings_editor.auto_groups_checklistbox.IsChecked(item)]
                text = settings_editor.auto_groups_checklistbox.GetString(item)
                parts = split_auto_groups_item(text)
                if parts:
                    self.auto_groups_dict[parts[0]] = value + parts[1]


    def on_settings_import(self, event):
        """
        Import settings from specified file.

        """
        try:
            settings_import_dialog = wx.FileDialog( self,
                u'Загрузить параметры из файла...',
                os.path.dirname(default_settings_file_name),
                os.path.basename(default_settings_file_name),
                u'Конфигурационный файл (*.ini)|*.ini|Все файлы (*.*)|*.*',
                wx.FD_OPEN
                )
            if settings_import_dialog.ShowModal() == wx.ID_CANCEL:
                return
            settings_file_name = settings_import_dialog.GetPath()
            self.load_settings(settings_file_name, True)
        except:
            wx.MessageBox(
                u'При загрузке параметров из файла:\n' +
                settings_file_name + '\n' \
                u'возникла ошибка:\n' +
                str(sys.exc_info()[1]) + '\n' \
                'Параметры не загружены или загружены не полностью.',
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )

    def on_settings_export(self, event):
        """
        Export settings to specified file.

        """
        try:
            settings_export_dialog = wx.FileDialog( self,
                u'Сохранить параметры в файл...',
                os.path.dirname(default_settings_file_name),
                os.path.basename(default_settings_file_name),
                u'Конфигурационный файл (*.ini)|*.ini|Все файлы (*.*)|*.*',
                wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
                )
            if settings_export_dialog.ShowModal() == wx.ID_CANCEL:
                return
            settings_file_name = settings_export_dialog.GetPath()
            self.save_settings(settings_file_name)
        except:
            wx.MessageBox(
                u'При сохранении параметров в файл:\n' +
                settings_file_name + '\n' \
                u'возникла ошибка:\n' +
                str(sys.exc_info()[1]) + '\n' \
                u'Параметры не сохранены или сохранены не полностью.',
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )

    def on_exit(self, event):
        """
        Close the program.

        """
        if not self.saved:
            if wx.MessageBox(
                u'Имеются не сохраненные изменения!\nВыйти из приложения?',
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
        selected_rows = self.grid.get_selected_rows()
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

        def on_esc_key(event):
            """
            Close find/replace dialog if ESC key pressed.

            """
            key_code = event.GetKeyCode()
            if key_code == wx.WXK_ESCAPE:
                find_dialog.Close()
            else:
                event.Skip()

        self.menuitem_find.Enable(False)
        self.menuitem_replace.Enable(False)
        find_dialog = gui.FindReplaceDialog(self)
        find_dialog.Bind(wx.EVT_CLOSE, on_find_replace_close)
        find_dialog.Bind(wx.EVT_CHAR_HOOK, on_esc_key)
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
        about_dialog.statictext_version.SetLabel(
                about_dialog.statictext_version.GetLabel() + \
                str(version) + '\n' + \
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
                    version
                    )
                )
        about_dialog.Layout()
        about_dialog.Fit()
        about_dialog.Centre()
        about_dialog.dialog_buttonOK.SetFocus()
        about_dialog.ShowModal()

    def on_help(self, event):
        """
        Shows help manual.

        """
        exec_dir = os.path.dirname(os.path.abspath(__file__))
        help_file = os.path.join(exec_dir, 'doc', 'user_manual.html')
        webbrowser.open_new(help_file)


def main():
    """
    Main function - called at start.

    """
    # Parsing of command-line arguments
    parser = argparse.ArgumentParser(
        description=(
            u'Приложение создает файл перечня элементов оформленный ' \
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
    version_file = open('version', 'r')
    global version
    version = version_file.read()
    version = version.replace('\n', '')
    version_file.close()

    if args.version:
        print version
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
                window.complist_file = os.path.splitext(os.path.abspath(args.complist))[0] + '.ods'
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

    window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
