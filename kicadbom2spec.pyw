#!/usr/bin/env python
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

import os
from os import path
import sys
import subprocess
import re
import codecs
import locale
import argparse
from operator import itemgetter

import wx
import wx.grid

import gui
from kicadsch import *
from spec import *

# Set default encoding
reload(sys)
sys.setdefaultencoding('utf-8')


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
        self.add_units = False
        self.all_components = False
        self.init_grid()

    def init_grid(self):
        """
        Initialize the grid for the components.

        """
        self.last_sorted_col = -1
        self.reversed_sorting = False

        if hasattr(self, 'grid_components'):
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
        self.menuitem_find.Enable(True)
        self.menuitem_replace.Enable(True)

    def on_save_sch(self, event):
        """
        Save changes in the fields of the components to the schematic file.

        """
        comp_values = self.get_grid_values()
        self.set_schematic_values(comp_values)
        for sheet in self.sheets:
            sheet.save()
        self.saved = True
        self.menuitem_save_sch.Enable(False)

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
        self.menuitem_save_lib.Enable(False)
        self.menuitem_find.Enable(True)
        self.menuitem_replace.Enable(True)

    def on_save_lib(self, event):
        """
        Save changes in the fields of the components to the library file.

        """
        comp_values = self.get_grid_values()
        self.set_library_values(comp_values)
        self.library.save()
        self.saved = True
        self.menuitem_save_lib.Enable(False)

    def on_spec(self, event):
        """
        Make specification.

        """
        spec_dialog = gui.SpecDialog(self)
        spec_dialog.filepicker_spec.SetPath(self.specification_file)
        spec_dialog.checkbox_add_units.SetValue(self.add_units)
        spec_dialog.checkbox_all_components.SetValue(self.all_components)
        result = spec_dialog.ShowModal()
        if result == wx.ID_OK:
            comp_fields = []
            self.specification_file = spec_dialog.filepicker_spec.GetPath()
            self.all_components = spec_dialog.checkbox_all_components.IsChecked()
            grid_values = self.get_grid_values()
            for row in grid_values:
                if (row[0] == u'1') | self.all_components:
                    fields = row[1:-1]
                    fields.insert(1, re.search(r'[A-Z]+', fields[1]).group())
                    fields[2] = re.search(r'[0-9]+', fields[2]).group()
                    fields.append('1')
                    comp_fields.append(fields)
            spec = Specification()
            self.add_units = spec_dialog.checkbox_add_units.IsChecked()
            spec.add_units = self.add_units
            spec.load(self.schematic_file, comp_fields)
            spec.save(self.specification_file)
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
            field_choices = []
            for row in selected_rows:
                cell_value = self.grid_components.GetCellValue(row, col)
                if cell_value and not cell_value in field_choices:
                    field_choices.append(cell_value)
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

    def on_exit(self, event):
        """
        Close the program.

        """
        if not self.saved:
            if wx.MessageBox(
                u'Имеются не сохраненные изменения!\nПродолжить?',
                u'Внимание!',
                wx.ICON_QUESTION|wx.YES_NO, self
                ) == wx.YES:

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
                    sheet.sch_name  # Sheet name
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
        top_left = self.grid_components.GetSelectionBlockTopLeft()
        bottom_right =  self.grid_components.GetSelectionBlockBottomRight()
        selected_rows = []
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
        selector = gui.FieldSelector(self)
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
