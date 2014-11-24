# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

ID_OPEN_SCH = 1000
ID_SAVE_SCH = 1001
ID_OPEN_LIB = 1002
ID_SAVE_LIB = 1003
ID_SPEC = 1004
ID_EXIT = 1005
ID_UNDO = 1006
ID_REDO = 1007
ID_COPY = 1008
ID_CUT = 1009
ID_PASTE = 1010
ID_FIND = 1011
ID_REPLACE = 1012
ID_EDIT = 1013
ID_CLEAR = 1014
ID_SETTINGS = 1015
ID_TOOL = 1016
ID_HELP = 1017
ID_ABOUT = 1018

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"kicadbom2spec", pos = wx.DefaultPosition, size = wx.Size( 700,500 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.menubar = wx.MenuBar( 0 )
		self.menu_file = wx.Menu()
		self.menuitem_open_sch = wx.MenuItem( self.menu_file, ID_OPEN_SCH, u"&Открыть схему..."+ u"\t" + u"CTRL+O", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_open_sch.SetBitmap( wx.Bitmap( u"bitmaps/document-open.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_open_sch )
		
		self.menuitem_save_sch = wx.MenuItem( self.menu_file, ID_SAVE_SCH, u"Со&хранить схему"+ u"\t" + u"CTRL+W", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_save_sch.SetBitmap( wx.Bitmap( u"bitmaps/document-save.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_save_sch )
		self.menuitem_save_sch.Enable( False )
		
		self.menuitem_open_lib = wx.MenuItem( self.menu_file, ID_OPEN_LIB, u"Открыть &библиотеку..."+ u"\t" + u"CTRL+L", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_open_lib.SetBitmap( wx.Bitmap( u"bitmaps/document-open.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_open_lib )
		
		self.menuitem_save_lib = wx.MenuItem( self.menu_file, ID_SAVE_LIB, u"Со&хра&нить библиотеку", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_save_lib.SetBitmap( wx.Bitmap( u"bitmaps/document-save.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_save_lib )
		self.menuitem_save_lib.Enable( False )
		
		self.menu_file.AppendSeparator()
		
		self.menuitem_spec = wx.MenuItem( self.menu_file, ID_SPEC, u"&Создать перечень элементов..."+ u"\t" + u"CTRL+S", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_spec.SetBitmap( wx.Bitmap( u"bitmaps/document-export.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_spec )
		self.menuitem_spec.Enable( False )
		
		self.menu_file.AppendSeparator()
		
		self.menuitem_exit = wx.MenuItem( self.menu_file, ID_EXIT, u"&Выход"+ u"\t" + u"CTRL+Q", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_exit.SetBitmap( wx.Bitmap( u"bitmaps/window-close.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_exit )
		
		self.menubar.Append( self.menu_file, u"&Файл" ) 
		
		self.menu_edit = wx.Menu()
		self.menuitem_undo = wx.MenuItem( self.menu_edit, ID_UNDO, u"&Отменить"+ u"\t" + u"CTRL+Z", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_undo.SetBitmap( wx.Bitmap( u"bitmaps/edit-undo.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_undo )
		self.menuitem_undo.Enable( False )
		
		self.menuitem_redo = wx.MenuItem( self.menu_edit, ID_REDO, u"&Повторить"+ u"\t" + u"CTRL+Y", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_redo.SetBitmap( wx.Bitmap( u"bitmaps/edit-redo.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_redo )
		self.menuitem_redo.Enable( False )
		
		self.menu_edit.AppendSeparator()
		
		self.menuitem_copy = wx.MenuItem( self.menu_edit, ID_COPY, u"&Копировать", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_copy.SetBitmap( wx.Bitmap( u"bitmaps/edit-copy.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_copy )
		self.menuitem_copy.Enable( False )
		
		self.menuitem_cut = wx.MenuItem( self.menu_edit, ID_CUT, u"&Вырезать...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_cut.SetBitmap( wx.Bitmap( u"bitmaps/edit-cut.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_cut )
		self.menuitem_cut.Enable( False )
		
		self.menuitem_paste = wx.MenuItem( self.menu_edit, ID_PASTE, u"В&ставить...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_paste.SetBitmap( wx.Bitmap( u"bitmaps/edit-paste.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_paste )
		self.menuitem_paste.Enable( False )
		
		self.menu_edit.AppendSeparator()
		
		self.menuitem_find = wx.MenuItem( self.menu_edit, ID_FIND, u"&Найти..."+ u"\t" + u"CTRL+F", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_find.SetBitmap( wx.Bitmap( u"bitmaps/edit-find.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_find )
		self.menuitem_find.Enable( False )
		
		self.menuitem_replace = wx.MenuItem( self.menu_edit, ID_REPLACE, u"&Заменить..."+ u"\t" + u"CTRL+H", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_replace.SetBitmap( wx.Bitmap( u"bitmaps/edit-find-replace.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_replace )
		self.menuitem_replace.Enable( False )
		
		self.menu_edit.AppendSeparator()
		
		self.menuitem_edit = wx.MenuItem( self.menu_edit, ID_EDIT, u"&Редактировать поля..."+ u"\t" + u"CTRL+E", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_edit.SetBitmap( wx.Bitmap( u"bitmaps/gtk-edit.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_edit )
		self.menuitem_edit.Enable( False )
		
		self.menuitem_clear = wx.MenuItem( self.menu_edit, ID_CLEAR, u"О&чистить поля..."+ u"\t" + u"CTRL+R", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_clear.SetBitmap( wx.Bitmap( u"bitmaps/edit-clear.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_clear )
		self.menuitem_clear.Enable( False )
		
		self.menu_edit.AppendSeparator()
		
		self.menuItem_settings = wx.MenuItem( self.menu_edit, ID_SETTINGS, u"Пара&метры...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuItem_settings.SetBitmap( wx.Bitmap( u"bitmaps/document-properties.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuItem_settings )
		
		self.menubar.Append( self.menu_edit, u"&Правка" ) 
		
		self.menu_view = wx.Menu()
		self.menuitem_tool = wx.MenuItem( self.menu_view, ID_TOOL, u"&Панель инструментов", wx.EmptyString, wx.ITEM_CHECK )
		self.menu_view.AppendItem( self.menuitem_tool )
		self.menuitem_tool.Check( True )
		
		self.menubar.Append( self.menu_view, u"&Вид" ) 
		
		self.menu_help = wx.Menu()
		self.menuitem_help = wx.MenuItem( self.menu_help, ID_HELP, u"&Руководство пользователя"+ u"\t" + u"F1", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_help.SetBitmap( wx.Bitmap( u"bitmaps/help-contents.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_help.AppendItem( self.menuitem_help )
		
		self.menu_help.AppendSeparator()
		
		self.menuitem_about = wx.MenuItem( self.menu_help, ID_ABOUT, u"&О программе...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_about.SetBitmap( wx.Bitmap( u"bitmaps/gtk-info.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_help.AppendItem( self.menuitem_about )
		
		self.menubar.Append( self.menu_help, u"Справка" ) 
		
		self.SetMenuBar( self.menubar )
		
		self.toolbar = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.tool_open_sch = self.toolbar.AddLabelTool( ID_OPEN_SCH, u"Открыть схему", wx.Bitmap( u"bitmaps/document-open.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Открыть файл схемы", wx.EmptyString, None ) 
		
		self.tool_save_sch = self.toolbar.AddLabelTool( ID_SAVE_SCH, u"Сохранить схему", wx.Bitmap( u"bitmaps/document-save.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Сохранить изменения пользовательских полей в файл схемы", wx.EmptyString, None ) 
		
		self.toolbar.AddSeparator()
		
		self.tool_spec = self.toolbar.AddLabelTool( ID_SPEC, u"Создать спецификацию", wx.Bitmap( u"bitmaps/document-export.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Создать перечень элементов", wx.EmptyString, None ) 
		
		self.toolbar.AddSeparator()
		
		self.tool_copy = self.toolbar.AddLabelTool( ID_COPY, u"Копировать", wx.Bitmap( u"bitmaps/edit-copy.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Копировать поля", wx.EmptyString, None ) 
		
		self.tool_cut = self.toolbar.AddLabelTool( ID_CUT, u"Вырезать", wx.Bitmap( u"bitmaps/edit-cut.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Вырезать поля", wx.EmptyString, None ) 
		
		self.tool_paste = self.toolbar.AddLabelTool( ID_PASTE, u"Вставить", wx.Bitmap( u"bitmaps/edit-paste.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Вставить поля", wx.EmptyString, None ) 
		
		self.toolbar.AddSeparator()
		
		self.tool_undo = self.toolbar.AddLabelTool( ID_UNDO, u"Отменить", wx.Bitmap( u"bitmaps/edit-undo.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Отменить последнее действие", wx.EmptyString, None ) 
		
		self.tool_redo = self.toolbar.AddLabelTool( ID_REDO, u"Повторить", wx.Bitmap( u"bitmaps/edit-redo.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Повторить предыдущее действие", wx.EmptyString, None ) 
		
		self.toolbar.AddSeparator()
		
		self.tool_edit = self.toolbar.AddLabelTool( ID_EDIT, u"Редактировать", wx.Bitmap( u"bitmaps/gtk-edit.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Редактировать поля", wx.EmptyString, None ) 
		
		self.tool_clear = self.toolbar.AddLabelTool( ID_CLEAR, u"Очистить", wx.Bitmap( u"bitmaps/edit-clear.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Очистить пользовательские поля", wx.EmptyString, None ) 
		
		self.toolbar.AddSeparator()
		
		self.tool_find = self.toolbar.AddLabelTool( ID_FIND, u"Найти", wx.Bitmap( u"bitmaps/edit-find.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Найти текст", wx.EmptyString, None ) 
		
		self.tool_replace = self.toolbar.AddLabelTool( ID_REPLACE, u"Заменить", wx.Bitmap( u"bitmaps/edit-find-replace.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Заменить текст", wx.EmptyString, None ) 
		
		self.toolbar.AddSeparator()
		
		self.tool_help = self.toolbar.AddLabelTool( ID_HELP, u"Справка", wx.Bitmap( u"bitmaps/help-contents.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Открыть справку", wx.EmptyString, None ) 
		
		self.toolbar.Realize() 
		
		sizer_main = wx.BoxSizer( wx.VERTICAL )
		
		self.panel_components = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER|wx.TAB_TRAVERSAL )
		sizer_main.Add( self.panel_components, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( sizer_main )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.on_exit )
		self.Bind( wx.EVT_MENU, self.on_open_sch, id = self.menuitem_open_sch.GetId() )
		self.Bind( wx.EVT_MENU, self.on_save_sch, id = self.menuitem_save_sch.GetId() )
		self.Bind( wx.EVT_MENU, self.on_open_lib, id = self.menuitem_open_lib.GetId() )
		self.Bind( wx.EVT_MENU, self.on_save_lib, id = self.menuitem_save_lib.GetId() )
		self.Bind( wx.EVT_MENU, self.on_spec, id = self.menuitem_spec.GetId() )
		self.Bind( wx.EVT_MENU, self.on_exit, id = self.menuitem_exit.GetId() )
		self.Bind( wx.EVT_MENU, self.on_undo, id = self.menuitem_undo.GetId() )
		self.Bind( wx.EVT_MENU, self.on_redo, id = self.menuitem_redo.GetId() )
		self.Bind( wx.EVT_MENU, self.on_copy, id = self.menuitem_copy.GetId() )
		self.Bind( wx.EVT_MENU, self.on_cut, id = self.menuitem_cut.GetId() )
		self.Bind( wx.EVT_MENU, self.on_paste, id = self.menuitem_paste.GetId() )
		self.Bind( wx.EVT_MENU, self.on_find_replace, id = self.menuitem_find.GetId() )
		self.Bind( wx.EVT_MENU, self.on_find_replace, id = self.menuitem_replace.GetId() )
		self.Bind( wx.EVT_MENU, self.on_edit_fields, id = self.menuitem_edit.GetId() )
		self.Bind( wx.EVT_MENU, self.on_clear_fields, id = self.menuitem_clear.GetId() )
		self.Bind( wx.EVT_MENU, self.on_settings, id = self.menuItem_settings.GetId() )
		self.Bind( wx.EVT_MENU, self.on_tool, id = self.menuitem_tool.GetId() )
		self.Bind( wx.EVT_MENU, self.on_help, id = self.menuitem_help.GetId() )
		self.Bind( wx.EVT_MENU, self.on_about, id = self.menuitem_about.GetId() )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_exit( self, event ):
		event.Skip()
	
	def on_open_sch( self, event ):
		event.Skip()
	
	def on_save_sch( self, event ):
		event.Skip()
	
	def on_open_lib( self, event ):
		event.Skip()
	
	def on_save_lib( self, event ):
		event.Skip()
	
	def on_spec( self, event ):
		event.Skip()
	
	
	def on_undo( self, event ):
		event.Skip()
	
	def on_redo( self, event ):
		event.Skip()
	
	def on_copy( self, event ):
		event.Skip()
	
	def on_cut( self, event ):
		event.Skip()
	
	def on_paste( self, event ):
		event.Skip()
	
	def on_find_replace( self, event ):
		event.Skip()
	
	
	def on_edit_fields( self, event ):
		event.Skip()
	
	def on_clear_fields( self, event ):
		event.Skip()
	
	def on_settings( self, event ):
		event.Skip()
	
	def on_tool( self, event ):
		event.Skip()
	
	def on_help( self, event ):
		event.Skip()
	
	def on_about( self, event ):
		event.Skip()
	

###########################################################################
## Class EditorDialog
###########################################################################

class EditorDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Редактор полей", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CAPTION|wx.CLOSE_BOX )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		sizer_editor = wx.BoxSizer( wx.VERTICAL )
		
		self.panel_editor = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_fields = wx.BoxSizer( wx.VERTICAL )
		
		self.checkbox = wx.CheckBox( self.panel_editor, wx.ID_ANY, u"Включить в спецификацию", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox.SetValue(True) 
		sizer_fields.Add( self.checkbox, 1, wx.ALL, 5 )
		
		sizer_field_1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_1 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Группа:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_CENTRE )
		self.statictext_1.Wrap( -1 )
		sizer_field_1.Add( self.statictext_1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		combobox_1Choices = [ u"<не изменять>" ]
		self.combobox_1 = wx.ComboBox( self.panel_editor, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, combobox_1Choices, 0 )
		self.combobox_1.SetSelection( 0 )
		sizer_field_1.Add( self.combobox_1, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sizer_fields.Add( sizer_field_1, 0, wx.EXPAND, 5 )
		
		sizer_field_3 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_3 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Марка:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_CENTRE )
		self.statictext_3.Wrap( -1 )
		sizer_field_3.Add( self.statictext_3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		combobox_3Choices = [ u"<не изменять>" ]
		self.combobox_3 = wx.ComboBox( self.panel_editor, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, combobox_3Choices, 0 )
		self.combobox_3.SetSelection( 0 )
		sizer_field_3.Add( self.combobox_3, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sizer_fields.Add( sizer_field_3, 0, wx.EXPAND, 5 )
		
		sizer_field_4 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_4 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Значение:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_CENTRE )
		self.statictext_4.Wrap( -1 )
		sizer_field_4.Add( self.statictext_4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		combobox_4Choices = [ u"<не изменять>" ]
		self.combobox_4 = wx.ComboBox( self.panel_editor, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, combobox_4Choices, 0 )
		self.combobox_4.SetSelection( 0 )
		sizer_field_4.Add( self.combobox_4, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sizer_fields.Add( sizer_field_4, 0, wx.EXPAND, 5 )
		
		sizer_field_5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_5 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Класс точности:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_CENTRE )
		self.statictext_5.Wrap( -1 )
		sizer_field_5.Add( self.statictext_5, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		combobox_5Choices = [ u"<не изменять>" ]
		self.combobox_5 = wx.ComboBox( self.panel_editor, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, combobox_5Choices, 0 )
		self.combobox_5.SetSelection( 0 )
		sizer_field_5.Add( self.combobox_5, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sizer_fields.Add( sizer_field_5, 0, wx.EXPAND, 5 )
		
		sizer_field_6 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_6 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Тип:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_CENTRE )
		self.statictext_6.Wrap( -1 )
		sizer_field_6.Add( self.statictext_6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		combobox_6Choices = [ u"<не изменять>" ]
		self.combobox_6 = wx.ComboBox( self.panel_editor, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, combobox_6Choices, 0 )
		self.combobox_6.SetSelection( 0 )
		sizer_field_6.Add( self.combobox_6, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sizer_fields.Add( sizer_field_6, 0, wx.EXPAND, 5 )
		
		sizer_field_7 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_7 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Стандарт:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_CENTRE )
		self.statictext_7.Wrap( -1 )
		sizer_field_7.Add( self.statictext_7, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		combobox_7Choices = [ u"<не изменять>" ]
		self.combobox_7 = wx.ComboBox( self.panel_editor, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, combobox_7Choices, 0 )
		self.combobox_7.SetSelection( 0 )
		sizer_field_7.Add( self.combobox_7, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sizer_fields.Add( sizer_field_7, 0, wx.EXPAND, 5 )
		
		sizer_field_8 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_8 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Примечание:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_CENTRE )
		self.statictext_8.Wrap( -1 )
		sizer_field_8.Add( self.statictext_8, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		combobox_8Choices = [ u"<не изменять>" ]
		self.combobox_8 = wx.ComboBox( self.panel_editor, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, combobox_8Choices, 0 )
		self.combobox_8.SetSelection( 0 )
		sizer_field_8.Add( self.combobox_8, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sizer_fields.Add( sizer_field_8, 0, wx.EXPAND, 5 )
		
		
		self.panel_editor.SetSizer( sizer_fields )
		self.panel_editor.Layout()
		sizer_fields.Fit( self.panel_editor )
		sizer_editor.Add( self.panel_editor, 1, wx.EXPAND, 5 )
		
		dialog_buttons = wx.StdDialogButtonSizer()
		self.dialog_buttonsOK = wx.Button( self, wx.ID_OK )
		dialog_buttons.AddButton( self.dialog_buttonsOK )
		self.dialog_buttonsCancel = wx.Button( self, wx.ID_CANCEL )
		dialog_buttons.AddButton( self.dialog_buttonsCancel )
		dialog_buttons.Realize();
		
		sizer_editor.Add( dialog_buttons, 0, wx.EXPAND|wx.ALL, 5 )
		
		
		self.SetSizer( sizer_editor )
		self.Layout()
		sizer_editor.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class FieldSelector
###########################################################################

class FieldSelector ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Выбор полей", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CAPTION|wx.CLOSE_BOX )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		sizer_field_selector = wx.BoxSizer( wx.VERTICAL )
		
		self.panel_field_selector = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_fields = wx.BoxSizer( wx.VERTICAL )
		
		self.checkbox_1 = wx.CheckBox( self.panel_field_selector, wx.ID_ANY, u"Группа", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_fields.Add( self.checkbox_1, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.checkbox_3 = wx.CheckBox( self.panel_field_selector, wx.ID_ANY, u"Марка", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_fields.Add( self.checkbox_3, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.checkbox_4 = wx.CheckBox( self.panel_field_selector, wx.ID_ANY, u"Значение", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_fields.Add( self.checkbox_4, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.checkbox_5 = wx.CheckBox( self.panel_field_selector, wx.ID_ANY, u"Класс точности", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_fields.Add( self.checkbox_5, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.checkbox_6 = wx.CheckBox( self.panel_field_selector, wx.ID_ANY, u"Тип", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_fields.Add( self.checkbox_6, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.checkbox_7 = wx.CheckBox( self.panel_field_selector, wx.ID_ANY, u"Стандарт", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_fields.Add( self.checkbox_7, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.checkbox_8 = wx.CheckBox( self.panel_field_selector, wx.ID_ANY, u"Примечание", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_fields.Add( self.checkbox_8, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.staticline = wx.StaticLine( self.panel_field_selector, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_fields.Add( self.staticline, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.checkbox_all = wx.CheckBox( self.panel_field_selector, wx.ID_ANY, u"Все поля", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_fields.Add( self.checkbox_all, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.panel_field_selector.SetSizer( sizer_fields )
		self.panel_field_selector.Layout()
		sizer_fields.Fit( self.panel_field_selector )
		sizer_field_selector.Add( self.panel_field_selector, 1, wx.EXPAND |wx.ALL, 5 )
		
		dialog_button = wx.StdDialogButtonSizer()
		self.dialog_buttonOK = wx.Button( self, wx.ID_OK )
		dialog_button.AddButton( self.dialog_buttonOK )
		self.dialog_buttonCancel = wx.Button( self, wx.ID_CANCEL )
		dialog_button.AddButton( self.dialog_buttonCancel )
		dialog_button.Realize();
		
		sizer_field_selector.Add( dialog_button, 0, wx.EXPAND|wx.ALL, 5 )
		
		
		self.SetSizer( sizer_field_selector )
		self.Layout()
		sizer_field_selector.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class FindReplaceDialog
###########################################################################

class FindReplaceDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		sizer_find_replace = wx.BoxSizer( wx.VERTICAL )
		
		self.panel_find = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_find_common = wx.BoxSizer( wx.VERTICAL )
		
		sizer_find = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_find = wx.StaticText( self.panel_find, wx.ID_ANY, u"Найти:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.statictext_find.Wrap( -1 )
		self.statictext_find.SetMinSize( wx.Size( 95,-1 ) )
		
		sizer_find.Add( self.statictext_find, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.textctrl_find = wx.TextCtrl( self.panel_find, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.textctrl_find.SetMinSize( wx.Size( 250,-1 ) )
		
		sizer_find.Add( self.textctrl_find, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.button_find_prev = wx.Button( self.panel_find, wx.ID_ANY, u"Назад", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_find.Add( self.button_find_prev, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.button_find_next = wx.Button( self.panel_find, wx.ID_ANY, u"Далее", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_find.Add( self.button_find_next, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sizer_find_common.Add( sizer_find, 1, wx.EXPAND, 5 )
		
		self.checkbox_case_sensitive = wx.CheckBox( self.panel_find, wx.ID_ANY, u"С учетом регистра", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_find_common.Add( self.checkbox_case_sensitive, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.staticline = wx.StaticLine( self.panel_find, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_find_common.Add( self.staticline, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		self.panel_find.SetSizer( sizer_find_common )
		self.panel_find.Layout()
		sizer_find_common.Fit( self.panel_find )
		sizer_find_replace.Add( self.panel_find, 0, wx.EXPAND, 5 )
		
		self.panel_replace = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_replace = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_replace = wx.StaticText( self.panel_replace, wx.ID_ANY, u"Заменить на:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.statictext_replace.Wrap( -1 )
		self.statictext_replace.SetMinSize( wx.Size( 95,-1 ) )
		
		sizer_replace.Add( self.statictext_replace, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.textctrl_replace = wx.TextCtrl( self.panel_replace, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.textctrl_replace.SetMinSize( wx.Size( 250,-1 ) )
		
		sizer_replace.Add( self.textctrl_replace, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.button_replace = wx.Button( self.panel_replace, wx.ID_ANY, u"Заменить", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_replace.Add( self.button_replace, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		self.panel_replace.SetSizer( sizer_replace )
		self.panel_replace.Layout()
		sizer_replace.Fit( self.panel_replace )
		sizer_find_replace.Add( self.panel_replace, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( sizer_find_replace )
		self.Layout()
		sizer_find_replace.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class AboutDialog
###########################################################################

class AboutDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"О программе", pos = wx.DefaultPosition, size = wx.Size( 460,343 ), style = wx.CAPTION )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		sizer_about_dialog = wx.BoxSizer( wx.VERTICAL )
		
		self.panel_about_dialog = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_about = wx.BoxSizer( wx.VERTICAL )
		
		self.m_bitmap1 = wx.StaticBitmap( self.panel_about_dialog, wx.ID_ANY, wx.Bitmap( u"bitmaps/icon.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_about.Add( self.m_bitmap1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.statictext_about = wx.StaticText( self.panel_about_dialog, wx.ID_ANY, u"kicadbom2spec - приложение для создания\nперечня элементов, оформленного согласно ЕСКД, для схем,\nвыполненных с помощью САПР KiCAD.", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.statictext_about.Wrap( -1 )
		sizer_about.Add( self.statictext_about, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		self.m_staticline1 = wx.StaticLine( self.panel_about_dialog, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_about.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.statictext_version = wx.StaticText( self.panel_about_dialog, wx.ID_ANY, u"Версия: ", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
		self.statictext_version.Wrap( -1 )
		sizer_about.Add( self.statictext_version, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_about.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.statictext_autor = wx.StaticText( self.panel_about_dialog, wx.ID_ANY, u"Автор: Барановский Константин", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
		self.statictext_autor.Wrap( -1 )
		sizer_about.Add( self.statictext_autor, 0, wx.ALL|wx.EXPAND, 5 )
		
		sizer_email = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_email = wx.StaticText( self.panel_about_dialog, wx.ID_ANY, u"Эл. почта:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.statictext_email.Wrap( -1 )
		sizer_email.Add( self.statictext_email, 0, wx.ALL, 5 )
		
		self.hyperlink_email = wx.HyperlinkCtrl( self.panel_about_dialog, wx.ID_ANY, u"baranovskiykonstantin@gmail.com", u"mailto:baranovskiykonstantin@gmail.com?subject=kicadbom2spec%20v3.0", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		sizer_email.Add( self.hyperlink_email, 0, wx.ALL, 5 )
		
		
		sizer_about.Add( sizer_email, 1, wx.EXPAND, 5 )
		
		sizer_homepage = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_homepage = wx.StaticText( self.panel_about_dialog, wx.ID_ANY, u"Домашняя страница:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.statictext_homepage.Wrap( -1 )
		sizer_homepage.Add( self.statictext_homepage, 0, wx.ALL, 5 )
		
		self.hyperlink_homepage = wx.HyperlinkCtrl( self.panel_about_dialog, wx.ID_ANY, u"https://launchpad.net/kicadbom2spec", u"https://launchpad.net/kicadbom2spec", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		sizer_homepage.Add( self.hyperlink_homepage, 0, wx.ALL, 5 )
		
		
		sizer_about.Add( sizer_homepage, 1, wx.EXPAND, 5 )
		
		self.m_staticline2 = wx.StaticLine( self.panel_about_dialog, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_about.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		dialog_button = wx.StdDialogButtonSizer()
		self.dialog_buttonOK = wx.Button( self.panel_about_dialog, wx.ID_OK )
		dialog_button.AddButton( self.dialog_buttonOK )
		dialog_button.Realize();
		
		sizer_about.Add( dialog_button, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT, 15 )
		
		
		self.panel_about_dialog.SetSizer( sizer_about )
		self.panel_about_dialog.Layout()
		sizer_about.Fit( self.panel_about_dialog )
		sizer_about_dialog.Add( self.panel_about_dialog, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( sizer_about_dialog )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class SpecDialog
###########################################################################

class SpecDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Создание перечня элементов", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.CAPTION|wx.CLOSE_BOX )
		
		self.SetSizeHintsSz( wx.Size( 500,-1 ), wx.DefaultSize )
		
		sizer_spec_dialog = wx.BoxSizer( wx.VERTICAL )
		
		self.panel_spec_dialog = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_spec = wx.BoxSizer( wx.VERTICAL )
		
		self.filepicker_spec = wx.FilePickerCtrl( self.panel_spec_dialog, wx.ID_ANY, wx.EmptyString, u"Выбор файла спецификации", u"Таблица (*.ods)|*.ods|Все файлы (*.*)|*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_USE_TEXTCTRL )
		sizer_spec.Add( self.filepicker_spec, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.staticline_1 = wx.StaticLine( self.panel_spec_dialog, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_spec.Add( self.staticline_1, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.checkbox_add_units = wx.CheckBox( self.panel_spec_dialog, wx.ID_ANY, u"Добавить единицы измерения", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_add_units.SetToolTipString( u"Если для резисторов, конденсаторов или индуктивностей указаны только значения и данная опция включена, то к значениям будут добавлены соответствующие единицы измерения (Ом, Ф, Гн)." )
		
		sizer_spec.Add( self.checkbox_add_units, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.checkbox_all_components = wx.CheckBox( self.panel_spec_dialog, wx.ID_ANY, u"Все элементы", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_all_components.SetToolTipString( u"Если данная функция включена, в перечень элементов будут включены все элементы, не зависимо от того установлен флажок для элемента или нет." )
		
		sizer_spec.Add( self.checkbox_all_components, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.checkbox_open = wx.CheckBox( self.panel_spec_dialog, wx.ID_ANY, u"Открыть перечень элементов", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_open.SetToolTipString( u"Если этот параметр установлен, то после создания перечня элементов он будет открыт в редакторе по умолчанию." )
		
		sizer_spec.Add( self.checkbox_open, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.panel_spec_dialog.SetSizer( sizer_spec )
		self.panel_spec_dialog.Layout()
		sizer_spec.Fit( self.panel_spec_dialog )
		sizer_spec_dialog.Add( self.panel_spec_dialog, 1, wx.EXPAND, 5 )
		
		dialog_buttons = wx.StdDialogButtonSizer()
		self.dialog_buttonsOK = wx.Button( self, wx.ID_OK )
		dialog_buttons.AddButton( self.dialog_buttonsOK )
		self.dialog_buttonsCancel = wx.Button( self, wx.ID_CANCEL )
		dialog_buttons.AddButton( self.dialog_buttonsCancel )
		dialog_buttons.Realize();
		
		sizer_spec_dialog.Add( dialog_buttons, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( sizer_spec_dialog )
		self.Layout()
		sizer_spec_dialog.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class SettingsDialog
###########################################################################

class SettingsDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Редактор настроек", pos = wx.DefaultPosition, size = wx.Size( 600,400 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.Size( 600,400 ), wx.Size( -1,-1 ) )
		
		sizer_settings_dialog = wx.BoxSizer( wx.VERTICAL )
		
		self.settings_tabs = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_TOP )
		self.general_tab_scrolledwindow = wx.ScrolledWindow( self.settings_tabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.general_tab_scrolledwindow.SetScrollRate( 5, 5 )
		self.general_tab_scrolledwindow.SetMaxSize( wx.Size( 0,0 ) )
		
		general_tab_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.window_checkbox = wx.CheckBox( self.general_tab_scrolledwindow, wx.ID_ANY, u"Сохранять положение и размер окна", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.window_checkbox.SetToolTipString( u"Если этот параметр установлен, то при закрытии программы будут сохарнены положение и размер окна и при следующем запуске они будут восстановлены." )
		
		general_tab_sizer.Add( self.window_checkbox, 0, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.col_size_checkbox = wx.CheckBox( self.general_tab_scrolledwindow, wx.ID_ANY, u"Сохранять ширину колонок таблицы", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.col_size_checkbox.SetToolTipString( u"Если этот параметр установлен, то в процессе работы и при завершении работы программы будут сохранены размеры ширины столбцов таблицы элементов и при следующем запуске они будут восстановлены." )
		
		general_tab_sizer.Add( self.col_size_checkbox, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5 )
		
		self.remember_selection_checkbox = wx.CheckBox( self.general_tab_scrolledwindow, wx.ID_ANY, u"Запоминать выбор элементов", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.remember_selection_checkbox.SetToolTipString( u"Если этот параметр установлен, то при сохранении схемы элементам, которые не отмечены для вывода в перечень элементов, будет добавлено поле \"Исключен из ПЭ\". \nПри открытии схемы для элементов с полем \"Исключен из ПЭ\" будет автоматически снята отметка о выводе в перечень элементов." )
		
		general_tab_sizer.Add( self.remember_selection_checkbox, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.staticline2 = wx.StaticLine( self.general_tab_scrolledwindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		general_tab_sizer.Add( self.staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.auto_groups_statictext = wx.StaticText( self.general_tab_scrolledwindow, wx.ID_ANY, u"Автоматически заполнять поле \"Группа\" для:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.auto_groups_statictext.Wrap( -1 )
		self.auto_groups_statictext.SetToolTipString( u"Если элементам не назначено значие поля \"Группа\", то при загрузке элементов из файла схемы/библиотеки для выбранных типов они будут сформированны автоматически." )
		
		general_tab_sizer.Add( self.auto_groups_statictext, 0, wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		auto_groups_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		
		auto_groups_sizer.AddSpacer( ( 20, 0), 0, 0, 5 )
		
		auto_groups_checklistboxChoices = []
		self.auto_groups_checklistbox = wx.CheckListBox( self.general_tab_scrolledwindow, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,200 ), auto_groups_checklistboxChoices, wx.LB_NEEDED_SB|wx.LB_SORT )
		auto_groups_sizer.Add( self.auto_groups_checklistbox, 1, wx.ALL|wx.EXPAND, 5 )
		
		auto_groups_buttons_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.auto_groups_add_button = wx.Button( self.general_tab_scrolledwindow, wx.ID_ANY, u"Добавить", wx.DefaultPosition, wx.DefaultSize, 0 )
		auto_groups_buttons_sizer.Add( self.auto_groups_add_button, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.auto_groups_edit_button = wx.Button( self.general_tab_scrolledwindow, wx.ID_ANY, u"Изменить", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.auto_groups_edit_button.Enable( False )
		
		auto_groups_buttons_sizer.Add( self.auto_groups_edit_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		self.auto_groups_remove_button = wx.Button( self.general_tab_scrolledwindow, wx.ID_ANY, u"Удалить", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.auto_groups_remove_button.Enable( False )
		
		auto_groups_buttons_sizer.Add( self.auto_groups_remove_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		
		auto_groups_sizer.Add( auto_groups_buttons_sizer, 0, 0, 5 )
		
		
		general_tab_sizer.Add( auto_groups_sizer, 1, wx.EXPAND, 5 )
		
		
		self.general_tab_scrolledwindow.SetSizer( general_tab_sizer )
		self.general_tab_scrolledwindow.Layout()
		general_tab_sizer.Fit( self.general_tab_scrolledwindow )
		self.settings_tabs.AddPage( self.general_tab_scrolledwindow, u"Основные", True )
		self.values_tab_panel = wx.Panel( self.settings_tabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		values_tab_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.value_notebook = wx.Notebook( self.values_tab_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.field1_panel = wx.Panel( self.value_notebook, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
		field1_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.field1_text = wx.TextCtrl( self.field1_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		field1_sizer.Add( self.field1_text, 1, wx.EXPAND, 5 )
		
		
		self.field1_panel.SetSizer( field1_sizer )
		self.field1_panel.Layout()
		field1_sizer.Fit( self.field1_panel )
		self.value_notebook.AddPage( self.field1_panel, u"Группа", True )
		self.field2_panel = wx.Panel( self.value_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		field2_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.field2_text = wx.TextCtrl( self.field2_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		field2_sizer.Add( self.field2_text, 1, wx.EXPAND, 5 )
		
		
		self.field2_panel.SetSizer( field2_sizer )
		self.field2_panel.Layout()
		field2_sizer.Fit( self.field2_panel )
		self.value_notebook.AddPage( self.field2_panel, u"Марка", False )
		self.field3_panel = wx.Panel( self.value_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		field3_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.field3_text = wx.TextCtrl( self.field3_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		field3_sizer.Add( self.field3_text, 1, wx.EXPAND, 5 )
		
		
		self.field3_panel.SetSizer( field3_sizer )
		self.field3_panel.Layout()
		field3_sizer.Fit( self.field3_panel )
		self.value_notebook.AddPage( self.field3_panel, u"Значение", False )
		self.field4_panel = wx.Panel( self.value_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		field4_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.field4_text = wx.TextCtrl( self.field4_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		field4_sizer.Add( self.field4_text, 1, wx.EXPAND, 5 )
		
		
		self.field4_panel.SetSizer( field4_sizer )
		self.field4_panel.Layout()
		field4_sizer.Fit( self.field4_panel )
		self.value_notebook.AddPage( self.field4_panel, u"Класс точности", False )
		self.field5_panel = wx.Panel( self.value_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		field5_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.field5_text = wx.TextCtrl( self.field5_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		field5_sizer.Add( self.field5_text, 1, wx.EXPAND, 5 )
		
		
		self.field5_panel.SetSizer( field5_sizer )
		self.field5_panel.Layout()
		field5_sizer.Fit( self.field5_panel )
		self.value_notebook.AddPage( self.field5_panel, u"Тип", False )
		self.field6_panel = wx.Panel( self.value_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		field6_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.field6_text = wx.TextCtrl( self.field6_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		field6_sizer.Add( self.field6_text, 1, wx.EXPAND, 5 )
		
		
		self.field6_panel.SetSizer( field6_sizer )
		self.field6_panel.Layout()
		field6_sizer.Fit( self.field6_panel )
		self.value_notebook.AddPage( self.field6_panel, u"Стандарт", False )
		self.field7_panel = wx.Panel( self.value_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		field7_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.field7_text = wx.TextCtrl( self.field7_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		field7_sizer.Add( self.field7_text, 1, wx.EXPAND, 5 )
		
		
		self.field7_panel.SetSizer( field7_sizer )
		self.field7_panel.Layout()
		field7_sizer.Fit( self.field7_panel )
		self.value_notebook.AddPage( self.field7_panel, u"Примечание", False )
		
		values_tab_sizer.Add( self.value_notebook, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.values_tab_panel.SetSizer( values_tab_sizer )
		self.values_tab_panel.Layout()
		values_tab_sizer.Fit( self.values_tab_panel )
		self.settings_tabs.AddPage( self.values_tab_panel, u"Значения полей", False )
		
		sizer_settings_dialog.Add( self.settings_tabs, 1, wx.EXPAND |wx.ALL, 5 )
		
		dialog_buttons = wx.StdDialogButtonSizer()
		self.dialog_buttonsOK = wx.Button( self, wx.ID_OK )
		dialog_buttons.AddButton( self.dialog_buttonsOK )
		self.dialog_buttonsCancel = wx.Button( self, wx.ID_CANCEL )
		dialog_buttons.AddButton( self.dialog_buttonsCancel )
		dialog_buttons.Realize();
		
		sizer_settings_dialog.Add( dialog_buttons, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( sizer_settings_dialog )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class EditAutoGroupsDialog
###########################################################################

class EditAutoGroupsDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		edit_auto_groups_sizer = wx.BoxSizer( wx.VERTICAL )
		
		param_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.param_statictext = wx.StaticText( self, wx.ID_ANY, u"Обозначение элемента:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.param_statictext.Wrap( -1 )
		self.param_statictext.SetToolTipString( u"Одна или две буквы, с которых начинается обозначение элемента. Например, С для конденсаторов, D или DD для микросхем и т.д." )
		
		param_sizer.Add( self.param_statictext, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		param_sizer.AddSpacer( ( 0, 0), 1, 0, 5 )
		
		self.param_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.param_text.SetMaxLength( 2 ) 
		param_sizer.Add( self.param_text, 0, wx.ALL, 5 )
		
		
		edit_auto_groups_sizer.Add( param_sizer, 0, wx.EXPAND, 5 )
		
		value_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.value_statictext = wx.StaticText( self, wx.ID_ANY, u"Значение поля \"Группа\":", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.value_statictext.Wrap( -1 )
		self.value_statictext.SetToolTipString( u"Значение поля \"Группа\" которое будет установлено по умолчанию для указанных элементов." )
		
		value_sizer.Add( self.value_statictext, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.value_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 250,-1 ), 0 )
		value_sizer.Add( self.value_text, 1, wx.ALL, 5 )
		
		
		edit_auto_groups_sizer.Add( value_sizer, 0, wx.EXPAND, 5 )
		
		edit_auto_groups_dialog_buttons = wx.StdDialogButtonSizer()
		self.edit_auto_groups_dialog_buttonsOK = wx.Button( self, wx.ID_OK )
		edit_auto_groups_dialog_buttons.AddButton( self.edit_auto_groups_dialog_buttonsOK )
		self.edit_auto_groups_dialog_buttonsCancel = wx.Button( self, wx.ID_CANCEL )
		edit_auto_groups_dialog_buttons.AddButton( self.edit_auto_groups_dialog_buttonsCancel )
		edit_auto_groups_dialog_buttons.Realize();
		
		edit_auto_groups_sizer.Add( edit_auto_groups_dialog_buttons, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( edit_auto_groups_sizer )
		self.Layout()
		edit_auto_groups_sizer.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	
