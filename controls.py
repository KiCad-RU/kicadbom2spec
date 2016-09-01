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

import re
import sys
import wx
import wx.grid
from operator import itemgetter
from complist import REF_REGULAR_EXPRESSION

class EditorCtrlPopup(wx.Dialog):
    """
    Popup for EditorCtrl.

    """

    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize, id=wx.ID_ANY, style=wx.NO_BORDER, title=u'', name = u''):
        """
        Create popup for EditorCtrl.

        """
        wx.Dialog.__init__(self, parent, id, title, pos, size, style, name)

        self.Bind(wx.EVT_ACTIVATE, self.on_activate)

        # Variables
        self.items = []
        self.selected_item = None

        sizer = wx.BoxSizer()
        scrolled_window = wx.ScrolledWindow(
            parent=self,
            style=wx.VERTICAL
            )
        scrolled_window.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_DEFAULT)
        scrolled_window.DisableKeyboardScrolling()
        scrolled_window.SetScrollRate(5, 5)


        sizer_items = wx.BoxSizer(wx.VERTICAL)

        # Default value
        if parent.default_value:
            panel = wx.Panel(
                parent=scrolled_window
                )
            panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            panel.Bind(wx.EVT_MOTION, self.on_item_select)
            sizer_panel = wx.BoxSizer(wx.HORIZONTAL)
            panel.text = wx.StaticText(
                parent=panel,
                label=parent.default_value
                )
            panel.text.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            panel.text.Bind(wx.EVT_MOTION, self.on_item_select)
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            panel.text.SetFont(font)
            sizer_panel.Add(
                panel.text,
                0,
                wx.EXPAND | wx.ALL,
                5
                )
            panel.SetSizer(sizer_panel)
            panel.Layout()
            sizer_items.Add(
                panel,
                0,
                wx.EXPAND
                )
            self.items.append(panel)

            # Separate default and other values
            if parent.std_values or set(parent.values) - set(parent.std_values):
                sizer_items.Add(
                        wx.StaticLine(scrolled_window),
                        0,
                        wx.EXPAND
                        )

        # Standard values at the top.
        for value in parent.std_values:
            panel = wx.Panel(
                parent=scrolled_window
                )
            panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            panel.Bind(wx.EVT_MOTION, self.on_item_select)
            sizer_panel = wx.BoxSizer(wx.HORIZONTAL)
            panel.text = wx.StaticText(
                parent=panel,
                label=value
                )
            panel.text.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            panel.text.Bind(wx.EVT_MOTION, self.on_item_select)
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            panel.text.SetFont(font)
            sizer_panel.Add(
                panel.text,
                0,
                wx.EXPAND | wx.ALL,
                5
                )
            panel.SetSizer(sizer_panel)
            panel.Layout()
            sizer_items.Add(
                panel,
                0,
                wx.EXPAND
                )
            self.items.append(panel)

        # Separate standard and common values
        if parent.std_values and set(parent.values) - set(parent.std_values):
            sizer_items.Add(
                    wx.StaticLine(scrolled_window),
                    0,
                    wx.EXPAND
                    )

        # Common values
        for value in parent.values:
            if value in parent.std_values:
                continue
            panel = wx.Panel(
                parent=scrolled_window
                )
            panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            panel.Bind(wx.EVT_MOTION, self.on_item_select)
            sizer_panel = wx.BoxSizer(wx.HORIZONTAL)
            panel.text = wx.StaticText(
                parent=panel,
                label=value
                )
            panel.text.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            panel.text.Bind(wx.EVT_MOTION, self.on_item_select)
            sizer_panel.Add(
                panel.text,
                0,
                wx.EXPAND | wx.ALL,
                5
                )
            panel.SetSizer(sizer_panel)
            panel.Layout()
            sizer_items.Add(
                panel,
                0,
                wx.EXPAND
                )
            self.items.append(panel)

        self.select_item(0)
        item_height = self.items[0].GetSize().GetHeight()

        scrolled_window.SetSizer(sizer_items)
        scrolled_window.Layout()
        sizer_items.Fit(scrolled_window)

        sizer.Add(
            scrolled_window,
            1,
            wx.ALL | wx.EXPAND,
            1
            )
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.SetSizer(sizer)
        self.Layout()
        self.Fit()

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        # Calculate optimal size and position of the popup
        display_width, display_height = wx.DisplaySize()
        parent_rect = parent.GetScreenRect()
        # Internal border size = 1px
        popup_height = sizer_items.GetSize().GetHeight() + 2
        popup_max_height = 200
        if popup_height > popup_max_height:
            popup_height = popup_max_height

        if popup_height + parent_rect.GetBottom() < display_height:
            self.SetPosition(
                wx.Point(
                    parent_rect.GetLeft(),
                    parent_rect.GetBottom()
                    )
                )
        else:
            self.SetPosition(
                wx.Point(
                    parent_rect.GetLeft(),
                    parent_rect.GetTop() - popup_height
                    )
                )
        self.SetSize(
            wx.Size(
                parent_rect.GetWidth(),
                popup_height
                )
            )

    def select_item(self, index):
        """
        Selecr item in popup by index.

        """
        # Reset previous selection
        if self.selected_item != None:
            self.items[self.selected_item].text.SetForegroundColour(wx.NullColour)
            self.items[self.selected_item].SetBackgroundColour(wx.NullColour)
            self.items[self.selected_item].Refresh()
        # Select item
        self.items[index].text.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
        self.items[index].SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        self.items[index].SetFocus()
        self.items[index].Refresh()
        self.selected_item = index

    def get_selected_value(self):
        """
        Return value of the selected item.

        """
        value = self.items[self.selected_item].text.GetLabel()
        return value

    def on_activate(self, event):
        """
        Close popup on losing focus.

        """
        if not event.GetActive():
            self.Destroy()
        event.Skip()

    def on_key(self, event):
        """
        Process key events.

        """
        index = self.items.index(event.GetEventObject())
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif event.GetKeyCode() == wx.WXK_RETURN:
            self.EndModal(wx.ID_OK)
        elif event.GetKeyCode() == wx.WXK_UP:
            if index > 0:
                self.select_item(index - 1)
        elif event.GetKeyCode() == wx.WXK_DOWN:
            if index < len(self.items) - 1:
                self.select_item(index + 1)
        else:
            event.Skip()

    def on_left_up(self, event):
        """
        Left click.

        """
        self.EndModal(wx.ID_OK)

    def on_item_select(self, event):
        """
        Select item by mouse movement.

        """
        if event.GetEventObject().GetClassName() == 'wxStaticText':
            panel = event.GetEventObject().GetParent()
        else:
            panel = event.GetEventObject()
        index = self.items.index(panel)
        if index != self.select_item:
            self.select_item(self.items.index(panel))


class EditorCtrl(wx.Control):
    """
    Custom field value editor.

    """

    def __init__(self, parent):
        wx.Control.__init__(self, parent, style=wx.NO_BORDER)

        self.SetCanFocus(False)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        # Text control
        self.text_ctrl = wx.TextCtrl(
            parent=self,
            style=wx.TE_PROCESS_ENTER | wx.TE_NOHIDESEL
            )
        self.text_ctrl.Bind(wx.EVT_SET_FOCUS, self.on_text_ctrl_set_focus)
        self.text_ctrl.Bind(wx.EVT_IDLE, self.on_text_ctrl_idle)
        self.text_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.on_text_ctrl_popup)
        if sys.platform == 'win32':
            self.Bind(wx.EVT_SET_FOCUS, lambda event: self.text_ctrl.SetFocus())

        # Popup button
        self.button = wx.Button(
                parent=self,
                label=u'☰',
                style=wx.BU_EXACTFIT
                )
        self.button.SetCanFocus(False)
        self.button.Enable(False)
        self.button.Bind(wx.EVT_BUTTON, self.on_button)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(
            self.text_ctrl,
            1,
            wx.EXPAND,
            0
            )
        sizer.Add(
            self.button,
            0,
            wx.FIXED_MINSIZE,
            0
            )
        self.SetSizer(sizer)

        # Common and standard values is stored separate.
        self.values = []
        self.std_values = []
        self.default_value = None

        self.skip_selecting = False
        self.select_all = False

        # Context menu ID
        self.copy_id = wx.NewId()
        self.cut_id = wx.NewId()
        self.paste_id = wx.NewId()
        self.delete_id = wx.NewId()
        self.select_all_id = wx.NewId()
        self.add_std_value_id = wx.NewId()
        self.remove_std_value_id = wx.NewId()
        self.ref_id = wx.NewId()
        self.value_id = wx.NewId()
        self.footprint_id = wx.NewId()
        self.datasheet_id = wx.NewId()
        self.another_id = wx.NewId()

        self.Layout()

    def set_items(self, values=None, std_values=None, default_value=None):
        """
        Fills the popup of the cell editor.

        """
        if default_value:
            self.default_value = default_value
            self.text_ctrl.SetValue(default_value)
            self.button.Enable(True)
        if values:
            self.values = values
            self.button.Enable(True)
        if std_values:
            self.std_values = std_values
            self.button.Enable(True)

    def clear_items(self):
        """
        Remove all popup items.

        """
        self.default_value = None
        self.values = []
        self.std_values = []
        self.button.Enable(False)

    def on_key(self, event):
        """
        Controls from keyboard.

        """
        # Show popup
        if event.GetKeyCode() == wx.WXK_DOWN:
            if self.button.IsEnabled():
                self.on_button(None)
        # Skip UP key
        elif event.GetKeyCode() == wx.WXK_UP:
            pass
        # Grid specific events
        elif self.GetGrandParent().GetClassName() == 'wxGrid':
            row = self.GetGrandParent().GetGridCursorRow()
            col = self.GetGrandParent().GetGridCursorCol()
            cur_value = self.GetGrandParent().GetCellValue(row, col)
            # Close editor and restore previous value
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.text_ctrl.SetValue(cur_value)
                self.GetGrandParent().DisableCellEditControl()
                self.GetGrandParent().SetGridCursor(row, col)
                self.GetGrandParent().SetFocusIgnoringChildren()
            # Close editor and apply new value
            elif event.GetKeyCode() == wx.WXK_RETURN:
                self.GetGrandParent().DisableCellEditControl()
                self.GetGrandParent().SetGridCursor(row, col)
                self.GetGrandParent().SetFocusIgnoringChildren()
            else:
                event.Skip()
        else:
            event.Skip()

    def on_text_ctrl_set_focus(self, event):
        """
        Set flag for selecting all text on activating text control.

        """
        if not self.skip_selecting:
            self.select_all = True
        else:
            self.skip_selecting = False
        event.Skip()

    def on_text_ctrl_idle(self, event):
        """
        Select all text in text control after activating.

        """
        if self.select_all:
            self.select_all = False
            self.text_ctrl.SelectAll()
        event.Skip()

    def on_text_ctrl_popup(self, event):
        """
        Create popup menu for text control.

        """
        def on_copy(event):
            self.text_ctrl.Copy()
            self.skip_selecting = True

        def on_cut(event):
            self.text_ctrl.Cut()
            self.skip_selecting = True

        def on_paste(event):
            self.text_ctrl.Paste()
            self.skip_selecting = True

        def on_delete(event):
            self.text_ctrl.WriteText(u'')
            self.skip_selecting = True

        def on_select_all(event):
            self.text_ctrl.SelectAll()
            self.skip_selecting = True

        menu = wx.Menu()
        item = wx.MenuItem(menu, self.copy_id, u'Копировать')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-copy_small.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, on_copy, item)

        item = wx.MenuItem(menu, self.cut_id, u'Вырезать')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-cut_small.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, on_cut, item)

        item = wx.MenuItem(menu, self.paste_id, u'Вставить')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-paste_small.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, on_paste, item)

        item = wx.MenuItem(menu, self.delete_id, u'Удалить')
        item.SetBitmap(wx.Bitmap(u'bitmaps/edit-delete_small.png', wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, on_delete, item)

        menu.Append(wx.ID_SEPARATOR)

        item = wx.MenuItem(menu, self.select_all_id, u'Выделить всё')
        item.SetBitmap(
            wx.Bitmap(
                u'bitmaps/edit-select-all_small.png',
                wx.BITMAP_TYPE_PNG
                )
            )
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, on_select_all, item)

        cur_value = self.text_ctrl.GetValue()
        if not cur_value in [u'', u'<не изменять>']:
            menu.Append(wx.ID_SEPARATOR)
            if cur_value in self.std_values:
                if len(cur_value) > 15:
                    cur_value = cur_value[:10] + u'…' + cur_value[-5:]
                item = wx.MenuItem(
                    menu,
                    self.remove_std_value_id,
                    u'Удалить "%s" из стандартных' % cur_value
                    )
                item.SetBitmap(
                    wx.Bitmap(
                        'bitmaps/list-remove_small.png',
                        wx.BITMAP_TYPE_PNG
                        )
                    )
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.on_remove_std_value, item)
            else:
                if len(cur_value) > 15:
                    cur_value = cur_value[:10] + u'…' + cur_value[-5:]
                item = wx.MenuItem(
                        menu,
                        self.add_std_value_id,
                        u'Добавить "%s" в стандартные' % cur_value
                        )
                item.SetBitmap(
                        wx.Bitmap(u'bitmaps/list-add_small.png',
                            wx.BITMAP_TYPE_PNG
                            )
                        )
                menu.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.on_add_std_value, item)

        menu.Append(wx.ID_SEPARATOR)

        submenu = wx.Menu()

        item = wx.MenuItem(menu, self.ref_id, u'${Обозначение}')
        submenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.on_insert, item)

        item = wx.MenuItem(menu, self.value_id, u'${Значение}')
        submenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.on_insert, item)

        item = wx.MenuItem(menu, self.footprint_id, u'${Посад.место}')
        submenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.on_insert, item)

        item = wx.MenuItem(menu, self.datasheet_id, u'${Документация}')
        submenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.on_insert, item)

        item = wx.MenuItem(menu, self.another_id, u'Другую…')
        submenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.on_insert, item)

        submenu_item = wx.MenuItem(
                menu,
                wx.NewId(),
                u'Вставить подстановку…',
                u'',
                wx.ITEM_NORMAL,
                submenu
                )
        submenu_item.SetBitmap(
                wx.Bitmap(
                    u'bitmaps/insert-text_small.png',
                    wx.BITMAP_TYPE_PNG
                    )
                )
        submenu_item = menu.AppendItem(submenu_item)

        if not self.text_ctrl.CanCopy():
            menu.Enable(self.copy_id, False)

        if not self.text_ctrl.CanCut():
            menu.Enable(self.cut_id, False)

        if not self.text_ctrl.CanPaste():
            menu.Enable(self.paste_id, False)

        if not self.text_ctrl.CanCopy():
            menu.Enable(self.delete_id, False)

        if event.GetPosition() == wx.DefaultPosition:
            popup_position = wx.Point(
                self.GetRect().GetWidth(),
                self.GetRect().GetBottom()
                )
        else:
            popup_position = self.ScreenToClient(wx.GetMousePosition())
        self.PopupMenu(menu, popup_position)
        menu.Destroy()

    def on_add_std_value(self, event):
        """
        Add current value to standard values.

        """
        cur_value = self.text_ctrl.GetValue()
        self.std_values.append(cur_value)
        self.skip_selecting = True

    def on_remove_std_value(self, event):
        """
        Remove current value from standard values.

        """
        cur_value = self.text_ctrl.GetValue()
        self.std_values.remove(cur_value)
        self.skip_selecting = True

    def on_insert(self, event):
        """
        Insert substitution for some field.

        """
        cur_id = event.GetId()
        self.skip_selecting = True
        if cur_id == self.ref_id:
            self.text_ctrl.WriteText(u'${Обозначение}')
        elif cur_id == self.value_id:
            self.text_ctrl.WriteText(u'${Значение}')
        elif cur_id == self.footprint_id:
            self.text_ctrl.WriteText(u'${Посад.место}')
        elif cur_id == self.datasheet_id:
            self.text_ctrl.WriteText(u'${Документация}')
        elif cur_id == self.another_id:
            self.text_ctrl.WriteText(u'${}')
            self.text_ctrl.SetInsertionPoint(self.text_ctrl.GetInsertionPoint() - 1)

    def on_button(self, event):
        """
        Show popup with all available values.

        """
        popup = EditorCtrlPopup(self)
        result = popup.ShowModal()
        if result == wx.ID_OK:
            self.text_ctrl.SetValue(popup.get_selected_value())
        self.text_ctrl.SetFocus()


class CellEditor(wx.grid.PyGridCellEditor):
    """
    Custom cell editor for the grid based on EditorCtrl.

    """

    def __init__(self):
        wx.grid.PyGridCellEditor.__init__(self)

    def Create(self, parent, id, evtHandler):
        self.control = EditorCtrl(parent)
        self.SetControl(self.control)

    def SetSize(self, rect):
        self.control.SetDimensions(
            rect.x,
            rect.y,
            rect.width+2,
            rect.height+2,
            wx.SIZE_ALLOW_MINUS_ONE
            )
    def BeginEdit(self, row, col, grid):
        self.start_value = grid.GetTable().GetValue(row, col)
        self.control.skip_selecting = True
        self.control.text_ctrl.SetValue(self.start_value)
        self.control.text_ctrl.SetInsertionPointEnd()
        self.control.SetFocus()

    def EndEdit(self, row, col, grid, old_value):
        cur_value = self.control.text_ctrl.GetValue()
        if cur_value != old_value:
            return cur_value
        else:
            return None

    def IsAcceptedKey(self, event):
        """
        Disable starting editor from keyboard.
        """
        return False

    def ApplyEdit(self, row, col, grid):
        value = self.control.text_ctrl.GetValue()
        grid.GetTable().SetValue(row, col, value)
        self.start_value = ''
        self.control.text_ctrl.SetValue('')
        self.control.clear_items()

    def Reset(self):
        self.control.skip_selecting = True
        self.control.text_ctrl.SetValue(self.start_value)
        self.control.text_ctrl.SetInsertionPointEnd()

    def Clone(self):
        return CellEditor()

    def set_items(self, values, std_values, default_value=None):
        self.control.set_items(
            values,
            std_values,
            default_value
            )


class Grid(wx.grid.Grid):
    """
    Grid of the fields.

    """

    def __init__(self, parent, window):
        """
        Initialize grid of the fields.

        """
        wx.grid.Grid.__init__(self, parent)

        self.window = window

        self.undo_buffer = []
        self.redo_buffer = []
        self.last_sorted_col = -1
        self.reversed_sorting = False

        # Grid
        self.CreateGrid(0, 9)
        self.EnableEditing(True)
        self.SetSelectionMode(wx.grid.Grid.SelectRows)

        # Events
        if not self.window.library:
            self.Bind(
                wx.grid.EVT_GRID_CELL_LEFT_CLICK,
                handler=self.on_left_click
                )
            self.Bind(
                wx.EVT_KEY_DOWN,
                handler=self.on_key_down
                )
            # For copies of the component (like "R123(R321)")
            self.Bind(
                wx.grid.EVT_GRID_CELL_LEFT_DCLICK,
                handler=self.on_left_dclick
                )
        self.Bind(
            wx.grid.EVT_GRID_LABEL_LEFT_CLICK,
            self.on_sort
            )
        self.Bind(
            wx.grid.EVT_GRID_EDITOR_CREATED,
            self.on_editor_created
            )
        self.Bind(
            wx.grid.EVT_GRID_EDITOR_SHOWN,
            self.on_editor_shown
            )
        self.Bind(
            wx.grid.EVT_GRID_EDITOR_HIDDEN,
            self.on_editor_hidden
            )

        # Columns
        self.SetDefaultColSize(150)
        self.SetColSize(0, 20)
        self.EnableDragColSize(True)
        self.SetColLabelSize(30)
        self.SetColLabelValue(0, u' ')
        self.SetColLabelValue(1, u'Группа')
        self.SetColLabelValue(2, u'Обозначение')
        self.SetColLabelValue(3, u'Марка')
        self.SetColLabelValue(4, u'Значение')
        self.SetColLabelValue(5, u'Класс точности')
        self.SetColLabelValue(6, u'Тип')
        self.SetColLabelValue(7, u'Стандарт')
        self.SetColLabelValue(8, u'Примечание')
        self.SetColLabelAlignment(
            wx.ALIGN_CENTRE,
            wx.ALIGN_CENTRE
            )

        # Rows
        self.EnableDragRowSize(False)
        self.SetRowLabelSize(1)
        self.SetRowLabelAlignment(
            wx.ALIGN_CENTRE,
            wx.ALIGN_CENTRE
            )

        # Cell Defaults
        self.SetDefaultCellAlignment(
            wx.ALIGN_LEFT,
            wx.ALIGN_CENTRE
            )

        # Cell editor
        self.SetDefaultEditor(CellEditor())

    def is_changed(self):
        """
        Returns True if values of the grid was changed.

        """
        rows = self.GetNumberRows()
        cols = self.GetNumberCols()
        old_values = self.undo_buffer[-1][:]
        for row in range(rows):
            ref = self.GetCellValue(row, 2)
            for old_row in range(len(old_values)):
                if ref == old_values[old_row][2]:
                    for col in range(cols):
                        old_value = old_values[old_row][col].replace('\\"', '"')
                        value = self.GetCellValue(row, col)
                        if old_value != value:
                            return True
                    del old_values[old_row]
                    break
        return False

    def set_cell_value(self, row, col, value):
        """
        Set value to cell of the grid and sync fields of the
        current component if needed (for comp like "R123*")

        """
        cur_ref = self.GetCellValue(row, 2)
        # Copies of the component (like "R123(R321)") is read only
        if '(' in cur_ref and ')' in cur_ref:
            return
        self.SetCellValue(row, col, value)
        # Find copies and changes it too.
        if cur_ref.endswith('*'):
            ref_orig = cur_ref.rstrip('*')
            rows = self.GetNumberRows()
            for cur_row in range(rows):
                cur_row_ref = self.GetCellValue(cur_row, 2)
                if cur_row_ref.endswith('(' + ref_orig + ')'):
                    self.SetCellValue(cur_row, col, value)

    def update_attributes(self):
        """
        Update attributes of all cells after changes.

        """
        rows = self.GetNumberRows()
        cols = self.GetNumberCols()
        for row in range(rows):
            ref_value = self.GetCellValue(row, 2)
            for col in range(cols):
                # Set default values
                self.SetCellBackgroundColour(row, col, self.GetDefaultCellBackgroundColour())
                self.SetReadOnly(row, col, False)
                # Checkboxes
                if col == 0:
                    self.SetReadOnly(row, col)
                    self.SetCellRenderer(row, col, wx.grid.GridCellBoolRenderer())
                # Ref is read only
                # Value of the component from library is read only
                elif col == 2 or \
                        (col == 4 and self.window.library):
                    self.SetReadOnly(row, col)
                    self.SetCellAlignment(row, col, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                # Copies of the component (like "R123(R321)") is read only
                if '(' in ref_value and ')' in ref_value:
                    self.SetReadOnly(row, col)
        for col in range(cols):
            # Remove extra characters from title
            col_title = self.GetColLabelValue(col)
            col_title = col_title.replace(u' ▲', u'')
            col_title = col_title.replace(u' ▼', u'')
            # Add sorting indicator
            if self.last_sorted_col == col:
                if self.reversed_sorting:
                    col_title += u' ▲'
                else:
                    col_title += u' ▼'
            self.SetColLabelValue(col, col_title)

    def get_values(self):
        """
        Returns list of cell values of grid.

        """
        rows = self.GetNumberRows()
        cols = self.GetNumberCols()
        values_temp = []
        for row in range(rows):
            rows_temp = []
            for col in range(cols):
                value = self.GetCellValue(row, col)
                value = value.replace(u'"', u'\\"')
                rows_temp.append(value)
            rows_temp.append(self.GetRowLabelValue(row))
            values_temp.append(rows_temp)
        return values_temp

    def set_values(self, grid_values, accordingly=True):
        """
        Set values from 'values' to cells of grid.

        """
        rows = self.GetNumberRows()
        cols = self.GetNumberCols()
        values = grid_values[:]
        for row in range(rows):
            for values_index, values_row in enumerate(values):
                if self.window.library:
                    comp1 = self.GetCellValue(row, 4)
                    comp2 = values_row[4]
                else:
                    comp1 = self.GetCellValue(row, 2)
                    comp2 = values_row[2]
                if (comp1 == comp2 or not comp1) | (not accordingly):
                    for col in range(cols):
                        value = values_row[col].replace(u'\\"', u'"')
                        self.SetCellValue(row, col, value)
                    self.SetRowLabelValue(row, values_row[-1])
                    del values[values_index]
                    break
        self.update_attributes()

    def get_selected_rows(self):
        """
        Returns list of indexes of selected rows.

        """
        selected_rows = []
        if int(wx.version().split(' ')[0].split('.')[0]) == 3:
            selected_rows = self.GetSelectedRows()
        else:
            top_left = self.GetSelectionBlockTopLeft()
            bottom_right =  self.GetSelectionBlockBottomRight()
            for i in range(len(top_left)):
                row_start, col_start = top_left[i]
                row_end, col_end = bottom_right[i]
                for row in range(row_start, row_end + 1):
                    selected_rows.append(row)
        return selected_rows

    def get_choices(self, rows, columns):
        """
        Get all unique values for every column in selected rows.

        """
        col_num = self.GetNumberCols()
        choices = [[]] # First column with checkboxes skiped
        for col in range(1, col_num):
            if not col in columns or col == 2:
                choices.append([])
                continue
            else:
                column_choices = []
                for row in rows:
                    cell_value = self.GetCellValue(row, col)
                    if cell_value != '' and not cell_value in column_choices:
                        column_choices.append(cell_value)
                column_choices.sort()
                choices.append(column_choices)
        return choices

    def on_left_click(self, event):
        """
        Switch state of the checkbox in 0 column
        by clicking left button of the mouse.

        """
        # Copies of the component (like "R123(R321)") is read only
        ref = self.GetCellValue(event.GetRow(), 2)
        if event.GetCol() == 0 and \
                not ('(' in ref and ')' in ref):

            cell_value = self.GetCellValue(
                event.GetRow(),
                event.GetCol()
                )
            if cell_value == '1':
                self.set_cell_value(
                    event.GetRow(),
                    event.GetCol(),
                    '0'
                    )
            else:
                self.set_cell_value(
                    event.GetRow(),
                    event.GetCol(),
                    '1'
                    )
            if hasattr(self.GetGrandParent(), 'on_grid_change'):
                self.GetGrandParent().on_grid_change()
        else:
            event.Skip()

    def on_left_dclick(self, event):
        """
        Show info abut editing copies of the component like "R123(R321)".

        """
        # Copies of the component (like "R123(R321)") is read only
        ref = self.GetCellValue(event.GetRow(), 2)
        if '(' in ref and ')' in ref:
            matches = re.search(r'(.+)\((.+)\)', ref)
            ref_copy = matches.groups()[0]
            ref_orig = matches.groups()[1]
            if wx.MessageBox(
                    u'Компонент "{copy}" является копией компонента "{orig}"\n' \
                    u'и доступен только для чтения. Поля компонентов копий\n' \
                    u'всегда равны полям оригинального компонента.\n\n' \
                    u'Перейти к редактированию оригинального компонента ' \
                    u'"{orig}"?'.format(
                        copy = ref_copy,
                        orig = ref_orig
                        ),
                    u'Внимание!',
                    wx.ICON_QUESTION|wx.YES_NO, self
                    ) == wx.YES:
                rows = self.GetNumberRows()
                for row in range(rows):
                    row_ref = self.GetCellValue(row, 2)
                    if row_ref == ref_orig + '*':
                        self.SetGridCursor(row, event.GetCol())
                        self.SelectRow(row)
                        self.MakeCellVisible(row, event.GetCol())
                        self.SetFocus()
                        return
        else:
            event.Skip()

    def on_key_down(self, event):
        """
        Switch state of the checkbox in 0 column by pressing space key.

        """
        # Skip if table is empty
        if self.GetNumberRows() == 0:
            event.Skip()
            return
        cur_col = self.GetGridCursorCol()
        cur_row = self.GetGridCursorRow()
        # Copies of the component (like "R123(R321)") is read only
        ref = self.GetCellValue(cur_row, 2)
        if event.GetKeyCode() == wx.WXK_SPACE and cur_col == 0 and \
                not ('(' in ref and ')' in ref):
            cell_value = self.GetCellValue(cur_row, cur_col)
            if cell_value == '1':
                self.set_cell_value(cur_row, cur_col, '0')
            else:
                self.set_cell_value(cur_row, cur_col, '1')
            if hasattr(self.GetGrandParent(), 'on_grid_change'):
                self.GetGrandParent().on_grid_change()
        elif event.GetKeyCode() == ord('A') and event.ControlDown():
            self.SelectAll()
        elif event.GetKeyCode() == wx.WXK_RETURN:
            if cur_col != 0 and not self.IsReadOnly(cur_row, cur_col):
                self.EnableCellEditControl()
        else:
            event.Skip()

    def on_sort(self, event=None):
        """
        Sort table rows by selected column values.

        """

        def compare_ref(row):
            """
            Returns value of reference
            for comparison in sort() function.

            """
            ref = row[2]
            # Remove extra data from ref in comp like 'R123(R321)' or 'R321*'
            ref = ref.split('(')[0]
            ref = ref.rstrip('*')

            matches = re.search(REF_REGULAR_EXPRESSION, ref)
            ref_val = matches.group(1)
            return ref_val

        def compare_num(row):
            """
            Returns integer value of number from reference
            for comparison in sort() function.

            """
            ref = row[2]
            # Remove extra data from ref in comp like 'R123(R321)' or 'R321*'
            ref = ref.split('(')[0]
            ref = ref.rstrip('*')

            matches = re.search(REF_REGULAR_EXPRESSION, ref)
            num_val = int(matches.group(2))
            return num_val

        if event:
            sort_col = event.GetCol()
        else:
            sort_col = 2
        grid_data = self.get_values()
        if sort_col == 2 and not self.window.library:
            sorted_data = sorted(grid_data, key=compare_num)
            sorted_data = sorted(sorted_data, key=compare_ref)
        else:
            sorted_data = sorted(grid_data, key=itemgetter(sort_col))
        if sort_col == self.last_sorted_col:
            self.reversed_sorting = not self.reversed_sorting
            if self.reversed_sorting:
                sorted_data.reverse()
        else:
            self.reversed_sorting = False
        self.set_values(sorted_data, False)
        self.last_sorted_col = sort_col
        self.update_attributes()
        if event:
            event.Skip()

    def on_editor_created(self, event):
        """
        Setup cell editor after creating.

        """
        row = event.GetRow()
        col = event.GetCol()
        cell_editor = event.GetControl()
        row_num = self.GetNumberRows()
        rows = range(0, row_num)
        cols = [col]
        choices = self.get_choices(rows, cols)
        std_values = self.window.values_dict[self.window.values_dict_keys[col]]
        cell_editor.set_items(choices[col], std_values)

    def on_editor_shown(self, event):
        """
        Create new default editor.

        """
        cell_editor = CellEditor()
        self.SetDefaultEditor(cell_editor)

    def on_editor_hidden(self, event):
        """
        Sync values after closing editor.

        """
        cell_editor = self.GetCellEditor(event.GetRow(), event.GetCol())
        self.window.values_dict[self.window.values_dict_keys[event.GetCol()]] = cell_editor.control.std_values
