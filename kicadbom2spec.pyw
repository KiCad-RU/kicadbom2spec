#!/usr/bin/env python2
# -*-    Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4    -*-
### BEGIN LICENSE
# Copyright (C) 2012 Baranovskiy Konstantin (baranovskiykonstantin@gmail.com)
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

VERSION=3.5

import os
from os import path, remove, rename
import sys
import subprocess
import re
import codecs
import locale
import argparse
from operator import itemgetter
from types import *
from ConfigParser import SafeConfigParser
from shutil import copyfile

import wx
import wx.grid

import gui
from kicadsch import *
from spec import *

# Set default encoding
reload(sys)
sys.setdefaultencoding('utf-8')

# Global
settings_file_name = 'settings.ini'
settings_separator = ';;;'

class Window(gui.MainFrame):
    """
    Graphical user interface for kicdbom2spec.

    """

    def __init__(self, parent):
        """
        Initialize main window.

        """
        gui.MainFrame.__init__(self,parent)

        if sys.platform == 'win32':
            icon_bundle = wx.IconBundle()
            for size in [16, 32, 48]:
                icon = wx.Icon('bitmaps/icon.ico', wx.BITMAP_TYPE_ICO, size, size)
                icon_bundle.AddIcon(icon)
            self.SetIcons(icon_bundle)
        else:
            icon = wx.Icon('bitmaps/icon.xpm', wx.BITMAP_TYPE_XPM)
            self.SetIcon(icon)

        self.Bind(wx.EVT_UPDATE_UI, self.on_menu)
        self.schematic_file = ''
        self.library_file = ''
        self.specification_file = ''
        self.sheets = []
        self.library = None
        self.saved = True
        self.not_found = False
        self.undo_buffer = []
        self.redo_buffer = []
        self.load_settings()
        self.init_grid()

    def load_settings(self):
        """
        Loads setttings from configuration file.

        """
        self.settings = SafeConfigParser()
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

        if path.isfile(settings_file_name):
            # Load settings from file
            self.settings.readfp(codecs.open(settings_file_name, 'r', encoding='utf-8'))

            if self.settings.has_section('window'):
                self.save_window_size_pos = True
                x, y = self.GetPosition()
                width, height = self.GetSize()
                if self.settings.has_option('window', 'x'):
                    x = self.settings.getint('window', 'x')
                if self.settings.has_option('window', 'y'):
                    y = self.settings.getint('window', 'y')
                if self.settings.has_option('window', 'width'):
                    width = self.settings.getint('window', 'width')
                if self.settings.has_option('window', 'height'):
                    height = self.settings.getint('window', 'height')
                self.SetDimensions(x, y, width, height)
                if self.settings.has_option('window', 'maximized'):
                    if self.settings.getint('window', 'maximized'):
                        self.Maximize()

            if self.settings.has_section('column sizes'):
                self.save_col_size = True

            if self.settings.has_section('values'):
                for item in self.values_dict.keys():
                    if self.settings.has_option('values', item):
                        values_list = self.settings.get('values', item)
                        values_list = values_list.split(settings_separator)
                        self.values_dict[item].extend(values_list)

            if self.settings.has_section('general'):
                if self.settings.has_option('general', 'remember selection'):
                    self.save_selected_mark = self.settings.getboolean('general', 'remember selection')

            if self.settings.has_section('auto filling groups'):
                for param in self.settings.options('auto filling groups'):
                    value = self.settings.get('auto filling groups', param)
                    if value.startswith(u'1'):
                        self.auto_groups_dict[param.upper()] = value[1:]

    def init_grid(self):
        """
        Initialize the grid for the components.

        """
        self.last_sorted_col = -1
        self.reversed_sorting = False

        if hasattr(self, 'grid_components'):
            if self.save_col_size:
                if not self.settings.has_section('column sizes'):
                    self.settings.add_section('column sizes')
                for col in range(self.grid_components.GetNumberCols()):
                    col_size = self.grid_components.GetColSize(col)
                    self.settings.set('column sizes', str(col), str(col_size))

            self.GetSizer().Remove(self.panel_components.GetSizer())
            self.grid_components.Destroy()

        self.grid_components = wx.grid.Grid(
            self.panel_components,
            wx.ID_ANY, wx.DefaultPosition,
            wx.DefaultSize,
            0
            )

        # Grid
        self.grid_components.CreateGrid(0, 9)
        self.grid_components.EnableEditing(True)
        self.grid_components.SetSelectionMode(wx.grid.Grid.SelectRows)

        attr = wx.grid.GridCellAttr()
        attr.SetReadOnly()
        attr.SetRenderer(wx.grid.GridCellBoolRenderer())
        self.grid_components.SetColAttr(0, attr)
        attr = wx.grid.GridCellAttr()
        attr.SetReadOnly()
        attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.grid_components.SetColAttr(2, attr)
        if self.library:
            self.grid_components.SetColAttr(4, attr.Clone())
        else:
            attr = self.grid_components.GetOrCreateCellAttr(0, 1)
            self.grid_components.SetColAttr(4, attr)

        # Events
        self.grid_components.Bind(
            wx.grid.EVT_GRID_CELL_LEFT_CLICK,
            self.on_grid_left_click
            )
        self.grid_components.Bind(
            wx.EVT_KEY_DOWN,
            self.on_grid_key_down
            )
        if self.library:
            self.grid_components.Unbind(
                wx.grid.EVT_GRID_CELL_LEFT_CLICK,
                handler=self.on_grid_left_click
                )
            self.grid_components.Unbind(
                wx.EVT_KEY_DOWN,
                handler=self.on_grid_key_down
                )
        self.grid_components.Bind(
            wx.grid.EVT_GRID_LABEL_LEFT_CLICK,
            self.on_grid_sort
            )
        self.grid_components.Bind(
            wx.grid.EVT_GRID_CELL_CHANGE,
            self.on_grid_change
            )
        self.grid_components.Bind(
            wx.grid.EVT_GRID_RANGE_SELECT,
            self.on_select
            )

        # Columns
        self.grid_components.SetDefaultColSize(150)
        self.grid_components.SetColSize(0, 20)
        if hasattr(self, 'settings'):
            if self.settings.has_section('column sizes'):
                for col in self.settings.options('column sizes'):
                    col_size = self.settings.getint('column sizes', col)
                    self.grid_components.SetColSize(int(col), col_size)
        self.grid_components.EnableDragColSize(True)
        self.grid_components.SetColLabelSize(30)
        self.grid_components.SetColLabelValue(0, u' ')
        self.grid_components.SetColLabelValue(1, u'Группа')
        self.grid_components.SetColLabelValue(2, u'Обозначение')
        self.grid_components.SetColLabelValue(3, u'Марка')
        self.grid_components.SetColLabelValue(4, u'Значение')
        self.grid_components.SetColLabelValue(5, u'Класс точности')
        self.grid_components.SetColLabelValue(6, u'Тип')
        self.grid_components.SetColLabelValue(7, u'Стандарт')
        self.grid_components.SetColLabelValue(8, u'Примечание')
        self.grid_components.SetColLabelAlignment(
            wx.ALIGN_CENTRE,
            wx.ALIGN_CENTRE
            )

        # Rows
        self.grid_components.EnableDragRowSize(False)
        self.grid_components.SetRowLabelSize(1)
        self.grid_components.SetRowLabelAlignment(
            wx.ALIGN_CENTRE,
            wx.ALIGN_CENTRE
            )

        # Cell Defaults
        self.grid_components.SetDefaultCellAlignment(
            wx.ALIGN_LEFT,
            wx.ALIGN_CENTRE
            )

        # Layout
        sizer_components = wx.BoxSizer(wx.HORIZONTAL)
        sizer_components.Add(self.grid_components, 1, wx.EXPAND|wx.ALL, 5)
        self.panel_components.SetSizer(sizer_components)
        self.panel_components.Layout()
        sizer_components.Fit(self.panel_components)
        self.Layout()

    def on_grid_key_down(self, event):
        """
        Switch state of the checkbox in 0 column by pressing space key.

        """
        cur_col = self.grid_components.GetGridCursorCol()
        cur_row = self.grid_components.GetGridCursorRow()
        if event.GetKeyCode() == wx.WXK_SPACE and cur_col == 0:
            cell_value = self.grid_components.GetCellValue(cur_row, cur_col)
            if cell_value == '1':
                self.grid_components.SetCellValue(cur_row, cur_col, '0')
            else:
                self.grid_components.SetCellValue(cur_row, cur_col, '1')
            self.on_grid_change()
        else:
            event.Skip()

    def on_grid_left_click(self, event):
        """
        Switch state of the checkbox in 0 column
        by clicking left button of the mouse.

        """
        if event.GetCol() == 0:
            cell_value = self.grid_components.GetCellValue(
                event.GetRow(),
                event.GetCol()
                )
            if cell_value == '1':
                self.grid_components.SetCellValue(
                    event.GetRow(),
                    event.GetCol(),
                    '0'
                    )
            else:
                self.grid_components.SetCellValue(
                    event.GetRow(),
                    event.GetCol(),
                    '1'
                    )
            self.on_grid_change()
        else:
            event.Skip()

    def on_grid_sort(self, event):
        """
        Sort table rows by selected column values.

        """

        def compare_ref(ref):
            """
            Returns integer equivalent value of reference
            fo comparison in sort() function.

            """
            ref_val = 0
            matches = re.search(r'^([A-Z]+)\d+', ref[2])
            if matches != None:
                for ch in range(len(matches.group(1))):
                    #  Ref begins maximum of two letters, the first
                    #  is multiplied by 10^5, the second by 10^4
                    ref_val += ord(matches.group(1)[ch]) * 10 ** 5 / (10 ** ch)
            matches = re.search(r'^[A-Z]+(\d+)', ref[2])
            if matches != None:
                ref_val += int(matches.group(1))
            return ref_val

        sort_col = event.GetCol()
        grid_data = self.get_grid_values()
        if sort_col == 2 and not self.library:
            sorted_data = sorted(grid_data, key=compare_ref)
        else:
            sorted_data = sorted(grid_data, key=itemgetter(sort_col))
        if sort_col == self.last_sorted_col:
            self.reversed_sorting = not self.reversed_sorting
            if self.reversed_sorting:
                sorted_data.reverse()
        else:
            self.reversed_sorting = False
        self.set_grid_values(sorted_data, False)
        self.last_sorted_col = sort_col
        event.Skip()

    def on_menu(self, event):
        """
        Change enable/disable future of the toolbar as same as menuitem.

        """
        menuitem = event.GetId()
        if menuitem > gui.ID_OPEN_SCH:
            self.toolbar.EnableTool(menuitem, self.menubar.IsEnabled(menuitem))
        event.Skip()

    def on_undo(self, event):
        """
        Undo last change in the grid.

        """
        self.redo_buffer.append(self.undo_buffer[-1])
        del self.undo_buffer[-1]
        self.set_grid_values(self.undo_buffer[-1])
        if len(self.undo_buffer) == 1:
            self.menuitem_undo.Enable(False)
            self.saved = True
            if self.library:
                self.menuitem_save_lib.Enable(False)
            else:
                self.menuitem_save_sch.Enable(False)
        self.menuitem_redo.Enable(True)

    def on_redo(self, event):
        """
        Redo previos change to the grid.

        """
        self.undo_buffer.append(self.redo_buffer[-1])
        self.set_grid_values(self.redo_buffer[-1])
        del self.redo_buffer[-1]
        if len(self.redo_buffer) == 0:
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

    def on_grid_change(self, event=None):
        """
        Put the grid data into undo buffer if changes made.

        """
        self.undo_buffer.append(self.get_grid_values())
        self.redo_buffer = []
        self.menuitem_redo.Enable(False)
        if len(self.undo_buffer) > 1:
            self.menuitem_undo.Enable(True)
        else:
            self.menuitem_undo.Enable(False)
        self.saved = False
        if self.library:
            self.menuitem_save_lib.Enable(True)
        else:
            self.menuitem_save_sch.Enable(True)


    def on_copy(self, event=None):
        """
        Copy values of the fields.

        """
        if len(self.get_selected_rows()) > 1:
            if wx.MessageBox(
                u'В таблице выделено несколько элементов!\n' \
                u'Будут скопированы поля только из первого выделеного элемента.\n' \
                u'Продолжить?',
                u'Внимание!',
                wx.ICON_QUESTION|wx.YES_NO, self
                ) == wx.NO:

                return
        self.buffer = []
        row = self.get_selected_rows()[0]
        for col in range(1, 9):
            if col == 2:
                self.buffer.append(u'')
                continue
            self.buffer.append(self.grid_components.GetCellValue(row, col))
        self.menuitem_paste.Enable(True)

    def on_cut(self, event):
        """
        Cut values of the fields.

        """
        if len(self.get_selected_rows()) > 1:
            if wx.MessageBox(
                u'В таблице выделено несколько элементов!\n' \
                u'Будут вырезаны поля только из первого выделеного элемента.\n' \
                u'Продолжить?',
                u'Внимание!',
                wx.ICON_QUESTION|wx.YES_NO, self
                ) == wx.NO:

                return
        self.buffer = []
        selected_cols = self.get_selected_cols()
        row = self.get_selected_rows()[0]
        for col in range(1, 9):
            if col == 2:
                self.buffer.append(u'')
                continue
            self.buffer.append(self.grid_components.GetCellValue(row, col))
            if col in selected_cols:
                self.grid_components.SetCellValue(row, col, u'')
        self.menuitem_paste.Enable(True)
        if self.is_grid_chaged():
            self.on_grid_change()

    def on_paste(self, event):
        """
        Paste values to the fields of the selected components from buffer.

        """
        rows = self.get_selected_rows()
        cols = self.get_selected_cols()
        for row in rows:
            for col in cols:
                if col == 2:
                    continue
                self.grid_components.SetCellValue(
                    row,
                    col,
                    self.buffer[col - 1]
                    )
        if self.is_grid_chaged():
            self.on_grid_change()

    def on_select(self, event):
        """
        Process selection event.

        """
        if self.get_selected_rows():
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

        if sch_file_name:
            self.schematic_file = sch_file_name
        else:
            if not self.saved:
                if wx.MessageBox(
                    u'Последние изменения в полях компонентов не были сохранены!\n' \
                    u'Продолжить?',
                    u'Внимание!',
                    wx.ICON_QUESTION|wx.YES_NO, self
                    ) == wx.NO:

                    return
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

        self.library_file = ''
        self.specification_file = path.splitext(self.schematic_file)[0] + '.ods'
        self.sheets = []
        self.library = None
        spec = Specification()
        sheet_names = [self.schematic_file]
        sheet_names.extend(spec.get_sheets(self.schematic_file))
        sheet_names = sorted(sheet_names)
        self.sheets = []
        for sheet_name in sheet_names:
            self.sheets.append(Schematic(sheet_name))
        self.init_grid()
        sch_values = self.get_schematic_values()
        self.grid_components.AppendRows(len(sch_values))
        self.set_grid_values(sch_values)
        self.undo_buffer = []
        self.redo_buffer = []
        self.on_grid_change()
        self.saved = True

        # Menu & Toolbar
        self.menuitem_spec.Enable(True)
        self.menuitem_save_sch.Enable(False)
        self.menuitem_save_sch_as.Enable(True)
        self.menuitem_save_lib.Enable(False)
        self.menuitem_save_lib_as.Enable(False)
        self.menuitem_find.Enable(True)
        self.menuitem_replace.Enable(True)

    def on_save_sch(self, event):
        """
        Save changes in the fields of the components to the schematic file.

        """
        comp_values = self.get_grid_values()
        self.set_schematic_values(comp_values)
        for sheet in self.sheets:
            try:
                if path.exists(sheet.sch_name + '.tmp'):
                    remove(sheet.sch_name + '.tmp')
                sheet.save(sheet.sch_name + '.tmp')
                remove(sheet.sch_name)
                rename(sheet.sch_name + '.tmp', sheet.sch_name)
                self.saved = True
                self.menuitem_save_sch.Enable(False)
            except:
                if path.exists(sheet.sch_name + '.tmp'):
                    remove(sheet.sch_name + '.tmp')
                wx.MessageBox(
                    u'При сохранении файла схемы:\n' +
                    sheet.sch_name + '\n' \
                    u'возникла ошибка. Файл не сохранен.',
                    u'Внимание!',
                    wx.ICON_ERROR|wx.OK, self
                    )

    def on_save_sch_as(self, event):
        """
        Save changes in the fields of the components to the separate
        schematic file(s).

        """
        comp_values = self.get_grid_values()
        self.set_schematic_values(comp_values)
        new_schematic_file = ''
        for sheet in self.sheets:
            try:
                save_sch_dialog = wx.FileDialog(
                    self,
                    u'Сохранить схему как...',
                    path.dirname(sheet.sch_name),
                    path.basename(sheet.sch_name),
                    u'Схема (*.sch)|*.sch|Все файлы (*.*)|*.*',
                    wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
                    )
                if save_sch_dialog.ShowModal() == wx.ID_CANCEL:
                    return
                new_schematic_file = save_sch_dialog.GetPath()
                if path.exists(new_schematic_file  + '.tmp'):
                    remove(new_schematic_file + '.tmp')
                sheet.save(new_schematic_file + '.tmp')
                if path.exists(new_schematic_file):
                    remove(new_schematic_file)
                rename(new_schematic_file + '.tmp', new_schematic_file)
                if new_schematic_file == sheet.sch_name:
                    self.saved = True
                    self.menuitem_save_sch.Enable(False)
            except:
                if path.exists(new_schematic_file + '.tmp'):
                    remove(new_schematic_file + '.tmp')
                wx.MessageBox(
                    u'При сохранении файла схемы:\n' +
                    new_schematic_file + '\n' \
                    u'возникла ошибка. Файл не сохранен.',
                    u'Внимание!',
                    wx.ICON_ERROR|wx.OK, self
                    )

    def on_open_lib(self, event):
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
        self.schematic_file = ''
        self.specification_file = ''
        self.library_file = open_lib_dialog.GetPath()
        self.library = Library(self.library_file)
        self.init_grid()
        lib_values = self.get_library_values()
        self.grid_components.AppendRows(len(lib_values))
        self.set_grid_values(lib_values)
        self.undo_buffer = []
        self.redo_buffer = []
        self.on_grid_change()
        self.saved = True

        # Menu & Toolbar
        self.menuitem_spec.Enable(False)
        self.menuitem_save_sch.Enable(False)
        self.menuitem_save_sch_as.Enable(False)
        self.menuitem_save_lib.Enable(False)
        self.menuitem_save_lib_as.Enable(True)
        self.menuitem_find.Enable(True)
        self.menuitem_replace.Enable(True)

    def on_save_lib(self, event):
        """
        Save changes in the fields of the components to the library file.

        """
        comp_values = self.get_grid_values()
        self.set_library_values(comp_values)
        try:
            if path.exists(self.library_file + '.tmp'):
                remove(self.library_file + '.tmp')
            self.library.save(self.library_file + '.tmp')
            remove(self.library_file)
            rename(self.library_file + '.tmp', self.library_file)
            self.saved = True
            self.menuitem_save_lib.Enable(False)
        except:
            if path.exists(self.library_file + '.tmp'):
                remove(self.library_file + '.tmp')
            wx.MessageBox(
                u'При сохранении файла библиотеки:\n' +
                self.library_file + '\n' \
                u'возникла ошибка. Файл не сохранен.',
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )

    def on_save_lib_as(self, event):
        """
        Save changes in the fields of the components to the separate
        library file.

        """
        comp_values = self.get_grid_values()
        self.set_library_values(comp_values)
        new_library_file = ''
        try:
            save_lib_dialog = wx.FileDialog(
                self,
                u'Сохранить библиотеку как...',
                path.dirname(self.library_file),
                path.basename(self.library_file),
                u'Библиотека (*.lib)|*.lib|Все файлы (*.*)|*.*',
                wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
                )
            if save_lib_dialog.ShowModal() == wx.ID_CANCEL:
                return
            new_library_file = save_lib_dialog.GetPath()
            if path.exists(new_library_file + '.tmp'):
                remove(new_library_file + '.tmp')
            self.library.save(new_library_file + '.tmp')
            if path.exists(new_library_file):
                remove(new_library_file)
            rename(new_library_file + '.tmp', new_library_file)
            self.saved = True
            self.menuitem_save_lib.Enable(False)
        except:
            if path.exists(new_library_file + '.tmp'):
                remove(new_library_file + '.tmp')
            wx.MessageBox(
                u'При сохранении файла библиотеки:\n' +
                self.library_file + '\n' \
                u'возникла ошибка. Файл не сохранен.',
                u'Внимание!',
                wx.ICON_ERROR|wx.OK, self
                )

    def on_spec(self, event):
        """
        Make specification.

        """
        spec_dialog = gui.SpecDialog(self)
        # Load settings
        all_components = False
        add_units = False
        open_spec = False
        need_changes_sheet = True
        if self.settings.has_section('spec'):
            if self.settings.has_option('spec', 'all'):
                all_components = self.settings.getboolean('spec', 'all')
            if self.settings.has_option('spec', 'units'):
                add_units = self.settings.getboolean('spec', 'units')
            if self.settings.has_option('spec', 'changes_sheet'):
                need_changes_sheet = self.settings.getboolean('spec', 'changes_sheet')
            if self.settings.has_option('spec', 'open'):
                open_spec = self.settings.getboolean('spec', 'open')

        spec_dialog.filepicker_spec.SetPath(self.specification_file)
        spec_dialog.checkbox_add_units.SetValue(add_units)
        spec_dialog.checkbox_all_components.SetValue(all_components)
        spec_dialog.checkbox_changes_sheet.SetValue(need_changes_sheet)
        spec_dialog.checkbox_open.SetValue(open_spec)

        result = spec_dialog.ShowModal()

        if result == wx.ID_OK:
            # Set cursor to 'wait'
            wx.BeginBusyCursor()
            wx.SafeYield()

            # Save settings from spec dialog
            all_components = spec_dialog.checkbox_all_components.IsChecked()
            add_units = spec_dialog.checkbox_add_units.IsChecked()
            need_changes_sheet = spec_dialog.checkbox_changes_sheet.IsChecked()
            open_spec = spec_dialog.checkbox_open.GetValue()

            if not self.settings.has_section('spec'):
                self.settings.add_section('spec')
            self.settings.set('spec', 'all', str(all_components))
            self.settings.set('spec', 'units', str(add_units))
            self.settings.set('spec', 'changes_sheet', str(need_changes_sheet))
            self.settings.set('spec', 'open', str(open_spec))
            self.specification_file = spec_dialog.filepicker_spec.GetPath()
            self.specification_file = path.splitext(self.specification_file)[0] + '.ods'
            comp_fields = []
            grid_values = self.get_grid_values()
            for row in grid_values:
                if (row[0] == u'1') | all_components:
                    fields = row[1:-1]
                    fields.insert(1, re.search(r'[A-Z]+', fields[1]).group())
                    fields[2] = re.search(r'[0-9]+', fields[2]).group()
                    fields.append('1')
                    comp_fields.append(fields)
            spec = Specification()
            spec.add_units = add_units
            spec.need_changes_sheet = need_changes_sheet
            spec.load(self.schematic_file, comp_fields)
            spec.save(self.specification_file)
            # Set cursor back to 'normal'
            if wx.IsBusy():
                wx.EndBusyCursor()

            if open_spec:
                if sys.platform == 'linux2':
                    subprocess.call(["xdg-open", self.specification_file])
                else:
                    os.startfile(self.specification_file)
            else:
                wx.MessageBox(
                    u'Перечень элементов успешно создан и сохранен!',
                    u'kicdbom2spec',
                    wx.ICON_INFORMATION | wx.OK,
                    self
                    )

    def on_edit_fields(self, event):
        """
        Open specialized window for editing fields of selected components.

        """
        editor = gui.EditorDialog(self)
        selected_rows = self.get_selected_rows()
        col_num = self.grid_components.GetNumberCols()
        all_choices = []
        for col in range(1, col_num):
            if col == 2:
                all_choices.append([])
                continue
            field_choices = self.values_dict[self.grid_components.GetColLabelValue(col).lower()][:]
            for row in selected_rows:
                cell_value = self.grid_components.GetCellValue(row, col)
                if cell_value and not cell_value in field_choices:
                    field_choices.append(cell_value)
            while '' in field_choices:
                field_choices.remove('')
            all_choices.append(field_choices)
        for i in range(1, col_num):
            if i == 2:
                continue
            for choice in all_choices[i - 1]:
                getattr(editor, 'combobox_' + str(i)).Append(choice)
        if self.library:
            editor.checkbox.Hide()
            editor.statictext_4.Hide()
            editor.combobox_4.Hide()
            editor.Layout()
            editor.GetSizer().Fit(editor)
        result = editor.ShowModal()
        if result == wx.ID_OK:
            for row in selected_rows:
                if editor.checkbox.IsChecked():
                    self.grid_components.SetCellValue(row, 0, '1')
                else:
                    self.grid_components.SetCellValue(row, 0, '0')
                for col in range(1, 9):
                    if col == 2:
                        continue
                    new_value = getattr(editor, 'combobox_' + str(col)).GetValue()
                    if new_value == u'<не изменять>':
                        continue
                    else:
                        self.grid_components.SetCellValue(row, col, new_value)
            if self.is_grid_chaged():
                self.on_grid_change()

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
            settings_editor = event.GetEventObject().GetGrandParent().GetParent()
            settings_editor.auto_groups_edit_button.Enable(True)
            settings_editor.auto_groups_remove_button.Enable(True)

        def on_auto_groups_add_button_clicked(event):
            """
            Add an element to auto_groups_checklistbox.

            """
            settings_editor = event.GetEventObject().GetGrandParent().GetParent()
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
            settings_editor = event.GetEventObject().GetGrandParent().GetParent()
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
            settings_editor = event.GetEventObject().GetGrandParent().GetParent()
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
            values = self.values_dict[field_names[i]]
            for value in values:
                field_text.AppendText(value + '\n')

        settings_editor.window_checkbox.SetValue(self.save_window_size_pos)

        settings_editor.col_size_checkbox.SetValue(self.save_col_size)

        settings_editor.remember_selection_checkbox.SetValue(self.save_selected_mark)

        if self.settings.has_section('auto filling groups'):
            settings_editor.auto_groups_checklistbox.Clear()
            for param in self.settings.options('auto filling groups'):
                value = self.settings.get('auto filling groups', param)
                checked = {'1':True, '0':False}[value[0]]
                value = u'{} - "{}"'.format(param.upper(), value[1:])
                index = settings_editor.auto_groups_checklistbox.Append(value)
                settings_editor.auto_groups_checklistbox.Check(index, checked)

        result = settings_editor.ShowModal()
        if result == wx.ID_OK:
            for i in range(len(field_names)):
                field_text = getattr(settings_editor, 'field{}_text'.format(i + 1))
                self.values_dict[field_names[i]] = []
                for line in range(field_text.GetNumberOfLines()):
                    line_text = field_text.GetLineText(line)
                    if line_text:
                        self.values_dict[field_names[i]].append(line_text)

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
            self.settings.remove_section('auto filling groups')
            self.auto_groups_dict = {}
            if not self.settings.has_section('auto filling groups') and auto_groups_items_count:
                self.settings.add_section('auto filling groups')
                for item in range(auto_groups_items_count):
                    value = {True:u'1', False:u'0'}[settings_editor.auto_groups_checklistbox.IsChecked(item)]
                    text = settings_editor.auto_groups_checklistbox.GetString(item)
                    param = split_auto_groups_item(text)
                    if param:
                        value += param[1]
                        param = param[0]
                        self.settings.set('auto filling groups', param, value)
                        if value.startswith('1'):
                            self.auto_groups_dict[param] = value[1:]

    def on_exit(self, event):
        """
        Close the program.

        """
        if not self.saved:
            if wx.MessageBox(
                u'Имеются не сохраненные изменения!\nПродолжить?',
                u'Внимание!',
                wx.ICON_QUESTION|wx.YES_NO, self
                ) == wx.NO:

                return

        if self.save_window_size_pos:
            if not self.settings.has_section('window'):
                self.settings.add_section('window')
            if self.IsMaximized():
                self.settings.set('window', 'maximized', '1')
            else:
                self.settings.set('window', 'maximized', '0')
                x, y = self.GetPosition()
                width, height = self.GetSize()
                self.settings.set('window', 'x', str(x))
                self.settings.set('window', 'y', str(y))
                self.settings.set('window', 'width', str(width))
                self.settings.set('window', 'height', str(height))
        else:
            self.settings.remove_section('window')

        if self.save_col_size:
            if not self.settings.has_section('column sizes'):
                self.settings.add_section('column sizes')
            for col in range(self.grid_components.GetNumberCols()):
                col_size = self.grid_components.GetColSize(col)
                self.settings.set('column sizes', str(col), str(col_size))
        else:
            self.settings.remove_section('column sizes')

        self.settings.write(codecs.open(settings_file_name, 'w', encoding='utf-8'))

        self.Destroy()

    def on_clear_fields(self, event):
        """
        Clears user specified fields of selected components.

        """
        selected_rows = self.get_selected_rows()
        selected_cols = self.get_selected_cols()
        for row in selected_rows:
            for col in selected_cols:
                self.grid_components.SetCellValue(row, col, u'')
        if self.is_grid_chaged():
            self.on_grid_change()

    def on_find_replace(self, event):
        """
        Find specified text in grid's cells.

        """

        def on_find_next(event):
            """
            Find next match.

            """
            find_str = event.GetEventObject().GetGrandParent().textctrl_find.GetValue()
            case_sensitive = event.GetEventObject().GetGrandParent().checkbox_case_sensitive.GetValue()
            whole_word = event.GetEventObject().GetGrandParent().checkbox_whole_word.GetValue()
            if not find_str:
                return

            rows = self.grid_components.GetNumberRows()
            cols = self.grid_components.GetNumberCols()
            cur_row = self.grid_components.GetGridCursorRow()
            cur_col = self.grid_components.GetGridCursorCol()
            for row in range(cur_row, rows):
                for col in range(1, cols):
                    if row == cur_row and col <= cur_col:
                        continue
                    cell_value = self.grid_components.GetCellValue(row, col)
                    if not case_sensitive:
                        cell_value = cell_value.lower()
                        find_str = find_str.lower()
                    if whole_word:
                        cell_value = cell_value.split()
                    if find_str in cell_value:
                        self.not_found = False
                        self.grid_components.SetGridCursor(row, col)
                        self.grid_components.SelectRow(row)
                        self.grid_components.MakeCellVisible(row, col)
                        self.grid_components.SetFocus()
                        return
            if not self.not_found and wx.MessageBox(
                u'Достигнут конец таблицы.\nПродолжить сначала?',
                u'Поиск',
                wx.ICON_QUESTION | wx.YES_NO, self
                ) == wx.YES:

                self.not_found = True
                self.grid_components.SetGridCursor(0, 0)
                on_find_next(event)
            elif self.not_found:
                wx.MessageBox(
                    u'Совпадения не найдены!',
                    u'Поиск',
                    wx.ICON_INFORMATION | wx.OK, self
                    )

        def on_find_prev(event):
            """
            Find previos match.

            """
            find_str = event.GetEventObject().GetGrandParent().textctrl_find.GetValue()
            case_sensitive = event.GetEventObject().GetGrandParent().checkbox_case_sensitive.GetValue()
            if not find_str:
                return
            rows = self.grid_components.GetNumberRows()
            cols = self.grid_components.GetNumberCols()
            cur_row = self.grid_components.GetGridCursorRow()
            cur_col = self.grid_components.GetGridCursorCol()
            for row in reversed(range(0, cur_row)):
                for col in reversed(range(1, cols)):
                    if row == cur_row and col >= cur_col:
                        continue
                    cell_value = self.grid_components.GetCellValue(row, col)
                    if not case_sensitive:
                        cell_value = cell_value.lower()
                        find_str = find_str.lower()
                    if whole_word:
                        cell_value = cell_value.split()
                    if find_str in cell_value:
                        self.not_found = False
                        self.grid_components.SetGridCursor(row, col)
                        self.grid_components.SelectRow(row)
                        self.grid_components.MakeCellVisible(row, col)
                        self.grid_components.SetFocus()
                        return
            if not self.not_found and wx.MessageBox(
                u'Достигнуто начало таблицы.\nПродолжить с конца?',
                u'Поиск',
                wx.ICON_QUESTION | wx.YES_NO,
                self
                ) == wx.YES:

                self.not_found = True
                self.grid_components.SetGridCursor(rows, cols)
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
            replace_str = event.GetEventObject().GetGrandParent().textctrl_replace.GetValue()
            if not replace_str:
                return
            cur_col = self.grid_components.GetGridCursorCol()
            if cur_col == 2 or (cur_col == 4 and self.library):
                return
            cur_row = self.grid_components.GetGridCursorRow()
            cell_value = self.grid_components.GetCellValue(cur_row, cur_col)
            find_str = event.GetEventObject().GetGrandParent().textctrl_find.GetValue()
            replace_str = event.GetEventObject().GetGrandParent().textctrl_replace.GetValue()
            if find_str not in cell_value:
                wx.MessageBox(
                    u'В выделеной ячейке не найдено совпадений для замены!',
                    u'Замена',
                    wx.ICON_ERROR | wx.OK, self
                    )
                return
            new_cell_value = cell_value.replace(find_str, replace_str, 1)
            self.grid_components.SetCellValue(cur_row, cur_col, new_cell_value)
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
        about_dialog.statictext_version.SetLabel(
                about_dialog.statictext_version.GetLabel() + \
                str(VERSION) + '\n' + \
                'Python: {}.{}.{}-{}'.format(
                    sys.version_info[0],
                    sys.version_info[1],
                    sys.version_info[2],
                    sys.version_info[3]
                    ) + '\n' + \
                'wxWidgets: {}'.format(wx.version())
                )
        about_dialog.dialog_buttonOK.SetFocus()
        about_dialog.ShowModal()

    def on_help(self, event):
        """
        Shows help manual.

        """
        if sys.platform == 'linux2':
            subprocess.call(["xdg-open", 'help_linux.pdf'])
        else:
            os.startfile('help_windows.pdf')

    def get_grid_values(self):
        """
        Returns list of cell values of grid.

        """
        rows = self.grid_components.GetNumberRows()
        cols = self.grid_components.GetNumberCols()
        values_temp = []
        for row in range(rows):
            rows_temp = []
            for col in range(cols):
                value = self.grid_components.GetCellValue(row, col)
                value = value.replace(u'"', u'\\"')
                rows_temp.append(value)
            rows_temp.append(self.grid_components.GetRowLabelValue(row))
            values_temp.append(rows_temp)
        return values_temp

    def set_grid_values(self, grid_values, accordingly=True):
        """
        Set values from 'values' to cells of grid.

        """
        rows = self.grid_components.GetNumberRows()
        cols = self.grid_components.GetNumberCols()
        values = grid_values[:]
        for row in range(rows):
            for values_index, values_row in enumerate(values):
                if self.library:
                    comp1 = self.grid_components.GetCellValue(row, 4)
                    comp2 = values_row[4]
                else:
                    comp1 = self.grid_components.GetCellValue(row, 2)
                    comp2 = values_row[2]
                if (comp1 == comp2 or not comp1) | (not accordingly):
                    for col in range(cols):
                        value = values[values_index][col].replace(u'\\"', u'"')
                        self.grid_components.SetCellValue(row, col, value)
                    self.grid_components.SetRowLabelValue(row, values[values_index][-1])
                    del values[values_index]
                    break

    def get_schematic_values(self):
        """
        Returns list of fields values of components from schematic.

        """
        values = []
        spec = Specification()
        for sheet in self.sheets:
            for comp in spec.get_components(sheet.sch_name, True):
                if not comp.fields[0].text or comp.fields[0].text.endswith('?'):
                    continue
                is_present = False
                for row in values:
                    if comp.fields[0].text == row[2] and \
                       sheet.sch_name == row[-1]:
                           is_present = True
                if is_present:
                    continue
                row = [
                    u'1',  # Used
                    u'',  # Group
                    comp.fields[0].text,  # Reference
                    u'',  # Mark
                    comp.fields[1].text,  # Value
                    u'',  # Accuracy
                    u'',  # Type
                    u'',  # GOST
                    u'',  # Comment
                    sheet.sch_name  # Sheet name
                    ]
                for field in comp.fields:
                    if hasattr(field, 'name'):
                        if field.name == u'Исключен из ПЭ':
                            row[0] = u'0'
                        elif field.name == u'Группа':
                            row[1] = field.text
                        elif field.name == u'Марка':
                            row[3] = field.text
                        elif field.name == u'Класс точности':
                            row[5] = field.text
                        elif field.name == u'Тип':
                            row[6] = field.text
                        elif field.name == u'Стандарт':
                            row[7] = field.text
                        elif field.name == u'Примечание':
                            row[8] = field.text
                if row[1] == u'':
                    for sufix in self.auto_groups_dict.keys():
                        if row[2].startswith(sufix):
                            row[1] = self.auto_groups_dict[sufix]
                            break
                values.append(row)
        return values

    def set_schematic_values(self, values):
        """
        Set values to fields of the components of schematic.

        """
        sorted_values = sorted(values, key=itemgetter(-1))
        field_names = {
            1:u'Группа',
            3:u'Марка',
            5:u'Класс точности',
            6:u'Тип',
            7:u'Стандарт',
            8:u'Примечание'
            }
        for sheet in self.sheets:
            for item in sheet.items:
                if item.__class__.__name__ == 'Comp':
                    if not item.ref.startswith('#'):
                        for value in sorted_values:
                            if value[2] == item.ref and value[-1] == sheet.sch_name:
                                item.fields[1].text = value[4]
                                for ind, field_name in field_names.items():
                                    if value[ind] != u'':
                                        for field in item.fields:
                                            if hasattr(field, 'name'):
                                                if field.name == field_name:
                                                    field.text = value[ind]
                                                    break
                                        else:
                                            str_field = u'F ' + str(len(item.fields))
                                            str_field += u' "' + value[ind] + u'" '
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
                                    str_field += u' "Исключен из ПЭ"'
                                    item.fields.append(sheet.Comp.Field(str_field.encode('utf-8')))
                                else:
                                    for field_index, field in enumerate(item.fields):
                                        if hasattr(field, 'name'):
                                            if field.name == u'Исключен из ПЭ':
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
                    if field.name == u'Группа':
                        row[1] = field.text
                    elif field.name == u'Марка':
                        row[3] = field.text
                    elif field.name == u'Класс точности':
                        row[5] = field.text
                    elif field.name == u'Тип':
                        row[6] = field.text
                    elif field.name == u'Стандарт':
                        row[7] = field.text
                    elif field.name == u'Примечание':
                        row[8] = field.text
            values.append(row)
        return values

    def set_library_values(self, values):
        """
        Set values to fields of the components of library.

        """
        sorted_values = values[:]
        field_names = {
            1:u'Группа',
            3:u'Марка',
            5:u'Класс точности',
            6:u'Тип',
            7:u'Стандарт',
            8:u'Примечание'
            }
        for comp in self.library.components:
            if not comp.reference.startswith('#'):
                for value in sorted_values:
                    if value[4] == comp.name:
                        for ind, field_name in field_names.items():
                            if value[ind] != u'':
                                for field in comp.fields:
                                    if hasattr(field, 'name'):
                                        if field.name == field_name:
                                            field.text = value[ind]
                                            break
                                else:
                                    str_field = u'F' + str(len(comp.fields))
                                    str_field += u' "' + value[ind] + u'" '
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

    def is_grid_chaged(self):
        """
        Returns True if values of the grid was changed.

        """
        rows = self.grid_components.GetNumberRows()
        cols = self.grid_components.GetNumberCols()
        old_values = self.undo_buffer[-1][:]
        for row in range(rows):
            ref = self.grid_components.GetCellValue(row, 2)
            for old_row in range(len(old_values)):
                if ref == old_values[old_row][2]:
                    for col in range(cols):
                        old_value = old_values[old_row][col].replace('\\"', '"')
                        value = self.grid_components.GetCellValue(row, col)
                        if old_value != value:
                            return True
                    del old_values[old_row]
                    break
        return False

    def get_selected_rows(self):
        """
        Returns list of indexes of selected rows.

        """
        selected_rows = []
        if int(wx.version().split(' ')[0].split('.')[0]) == 3:
            selected_rows = self.grid_components.GetSelectedRows()
        else:
            top_left = self.grid_components.GetSelectionBlockTopLeft()
            bottom_right =  self.grid_components.GetSelectionBlockBottomRight()
            for i in range(len(top_left)):
                row_start, col_start = top_left[i]
                row_end, col_end = bottom_right[i]
                for row in range(row_start, row_end + 1):
                    selected_rows.append(row)
        return selected_rows

    def get_selected_cols(self):
        """
        Returns list of indexes of selected columns from field selector.

        """

        def on_checkbox_all_clicked(event):
            """
            Check/uncheck all fields in field seletor.

            """
            selector = event.GetEventObject().GetGrandParent()
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


def main():
    """
    Main function - called at start.

    """
    # Parsing of command-line arguments
    parser = argparse.ArgumentParser(
        description=(
            u'Приложение создает файл перечня элементов оформленный ' \
            u'в соответствии с ЕСКД для схемы выполненой в САПР KiCAD.\n'
            )
        )
    parser.add_argument(
        'schematic',
        default='',
        nargs='?',
        type=str,
        help=u'полное или относительное имя файла схемы в формате KiCAD'
        )
    parser.add_argument(
        'spec',
        default='',
        nargs='?',
        type=str,
        help=u'полное или относительное имя файла перечня элеменнтов'
        )
    args = parser.parse_args()
    os.chdir(path.dirname(path.abspath(__file__)))
    app = wx.App(False)
    window = Window(None)

    if args.schematic:
        sch_file_name = path.splitext(path.abspath(args.schematic))[0] + '.sch'
        if path.isfile(sch_file_name):
            window.on_open_sch(sch_file_name=sch_file_name)
        else:
            window.on_open_sch()

    if args.spec:
        window.specification_file = path.splitext(path.abspath(args.spec))[0] + '.ods'

    window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
