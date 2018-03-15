# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Mar 15 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid
import controls

ID_OPEN_SCH = 1000
ID_SAVE_SCH = 1001
ID_SAVE_SCH_AS = 1002
ID_OPEN_LIB = 1003
ID_SAVE_LIB = 1004
ID_SAVE_LIB_AS = 1005
ID_COMPLIST = 1006
ID_EXIT = 1007
ID_UNDO = 1008
ID_REDO = 1009
ID_COPY = 1010
ID_CUT = 1011
ID_PASTE = 1012
ID_FIND = 1013
ID_REPLACE = 1014
ID_EDIT = 1015
ID_CLEAR = 1016
ID_SETTINGS = 1017
ID_SETTINGS_IMPORT = 1018
ID_SETTINGS_EXPORT = 1019
ID_TOOL = 1020
ID_COMP_FIELDS_PANEL = 1021
ID_HELP = 1022
ID_ABOUT = 1023

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"kicadbom2spec", pos = wx.DefaultPosition, size = wx.Size( 700,500 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.Size( 500,200 ), wx.DefaultSize )
		
		self.menubar = wx.MenuBar( 0 )
		self.menu_file = wx.Menu()
		self.menuitem_open_sch = wx.MenuItem( self.menu_file, ID_OPEN_SCH, u"&Открыть схему..."+ u"\t" + u"CTRL+O", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_open_sch.SetBitmap( wx.Bitmap( u"bitmaps/document-open.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_open_sch )
		
		self.submenu_recent_sch = wx.Menu()
		self.menu_file.AppendSubMenu( self.submenu_recent_sch, u"Нед&авние схемы" )
		
		self.menuitem_save_sch = wx.MenuItem( self.menu_file, ID_SAVE_SCH, u"Со&хранить схему"+ u"\t" + u"CTRL+S", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_save_sch.SetBitmap( wx.Bitmap( u"bitmaps/document-save.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_save_sch )
		self.menuitem_save_sch.Enable( False )
		
		self.menuitem_save_sch_as = wx.MenuItem( self.menu_file, ID_SAVE_SCH_AS, u"Сох&ранить схему как..."+ u"\t" + u"CTRL+SHIFT+S", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_save_sch_as.SetBitmap( wx.Bitmap( u"bitmaps/document-save-as.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_save_sch_as )
		self.menuitem_save_sch_as.Enable( False )
		
		self.menu_file.AppendSeparator()
		
		self.menuitem_open_lib = wx.MenuItem( self.menu_file, ID_OPEN_LIB, u"Открыть &библиотеку..."+ u"\t" + u"CTRL+L", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_open_lib.SetBitmap( wx.Bitmap( u"bitmaps/document-open.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_open_lib )
		
		self.submenu_recent_lib = wx.Menu()
		self.menu_file.AppendSubMenu( self.submenu_recent_lib, u"Н&едавние библиотеки" )
		
		self.menuitem_save_lib = wx.MenuItem( self.menu_file, ID_SAVE_LIB, u"Сохра&нить библиотеку", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_save_lib.SetBitmap( wx.Bitmap( u"bitmaps/document-save.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_save_lib )
		self.menuitem_save_lib.Enable( False )
		
		self.menuitem_save_lib_as = wx.MenuItem( self.menu_file, ID_SAVE_LIB_AS, u"Сохрани&ть библиотеку как...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_save_lib_as.SetBitmap( wx.Bitmap( u"bitmaps/document-save-as.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_save_lib_as )
		self.menuitem_save_lib_as.Enable( False )
		
		self.menu_file.AppendSeparator()
		
		self.menuitem_complist = wx.MenuItem( self.menu_file, ID_COMPLIST, u"&Создать перечень элементов..."+ u"\t" + u"CTRL+G", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_complist.SetBitmap( wx.Bitmap( u"bitmaps/document-export.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_file.AppendItem( self.menuitem_complist )
		self.menuitem_complist.Enable( False )
		
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
		
		self.menuitem_copy = wx.MenuItem( self.menu_edit, ID_COPY, u"&Копировать"+ u"\t" + u"CTRL+C", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_copy.SetBitmap( wx.Bitmap( u"bitmaps/edit-copy.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_copy )
		self.menuitem_copy.Enable( False )
		
		self.menuitem_cut = wx.MenuItem( self.menu_edit, ID_CUT, u"&Вырезать..."+ u"\t" + u"CTRL+X", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_cut.SetBitmap( wx.Bitmap( u"bitmaps/edit-cut.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuitem_cut )
		self.menuitem_cut.Enable( False )
		
		self.menuitem_paste = wx.MenuItem( self.menu_edit, ID_PASTE, u"В&ставить..."+ u"\t" + u"CTRL+V", wx.EmptyString, wx.ITEM_NORMAL )
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
		
		self.menuItem_settings = wx.MenuItem( self.menu_edit, ID_SETTINGS, u"Пара&метры..."+ u"\t" + u"CTRL+P", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuItem_settings.SetBitmap( wx.Bitmap( u"bitmaps/document-properties.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuItem_settings )
		
		self.menuItem_settings_import = wx.MenuItem( self.menu_edit, ID_SETTINGS_IMPORT, u"&Импорт параметров...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuItem_settings_import.SetBitmap( wx.Bitmap( u"bitmaps/properties-import.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuItem_settings_import )
		
		self.menuItem_settings_export = wx.MenuItem( self.menu_edit, ID_SETTINGS_EXPORT, u"&Экспорт параметров...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuItem_settings_export.SetBitmap( wx.Bitmap( u"bitmaps/properties-export.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_edit.AppendItem( self.menuItem_settings_export )
		
		self.menubar.Append( self.menu_edit, u"&Правка" ) 
		
		self.menu_view = wx.Menu()
		self.menuitem_tool = wx.MenuItem( self.menu_view, ID_TOOL, u"&Панель инструментов", wx.EmptyString, wx.ITEM_CHECK )
		self.menu_view.AppendItem( self.menuitem_tool )
		self.menuitem_tool.Check( True )
		
		self.menuitem_comp_fields_panel = wx.MenuItem( self.menu_view, ID_COMP_FIELDS_PANEL, u"П&анель полей компонента", wx.EmptyString, wx.ITEM_CHECK )
		self.menu_view.AppendItem( self.menuitem_comp_fields_panel )
		self.menuitem_comp_fields_panel.Check( True )
		
		self.menubar.Append( self.menu_view, u"&Вид" ) 
		
		self.menu_help = wx.Menu()
		self.menuitem_help = wx.MenuItem( self.menu_help, ID_HELP, u"&Руководство пользователя"+ u"\t" + u"F1", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_help.SetBitmap( wx.Bitmap( u"bitmaps/help-contents.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_help.AppendItem( self.menuitem_help )
		
		self.menu_help.AppendSeparator()
		
		self.menuitem_about = wx.MenuItem( self.menu_help, ID_ABOUT, u"&О программе...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuitem_about.SetBitmap( wx.Bitmap( u"bitmaps/gtk-info.png", wx.BITMAP_TYPE_ANY ) )
		self.menu_help.AppendItem( self.menuitem_about )
		
		self.menubar.Append( self.menu_help, u"&Справка" ) 
		
		self.SetMenuBar( self.menubar )
		
		self.toolbar = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.tool_open_sch = self.toolbar.AddLabelTool( ID_OPEN_SCH, u"Открыть схему", wx.Bitmap( u"bitmaps/document-open.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Открыть файл схемы", wx.EmptyString, None ) 
		
		self.tool_save_sch = self.toolbar.AddLabelTool( ID_SAVE_SCH, u"Сохранить схему", wx.Bitmap( u"bitmaps/document-save.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Сохранить изменения пользовательских полей в файл схемы", wx.EmptyString, None ) 
		
		self.toolbar.AddSeparator()
		
		self.tool_complist = self.toolbar.AddLabelTool( ID_COMPLIST, u"Создать перечень элементов", wx.Bitmap( u"bitmaps/document-export.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Создать перечень элементов", wx.EmptyString, None ) 
		
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
		
		self.tool_comp_fields_panel = self.toolbar.AddLabelTool( ID_COMP_FIELDS_PANEL, u"Панель полей компонента", wx.Bitmap( u"bitmaps/properties-panel.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_CHECK, u"Показать или скрыть панель полей выбранного компонента", wx.EmptyString, None ) 
		
		self.toolbar.Realize() 
		
		sizer_main = wx.BoxSizer( wx.VERTICAL )
		
		self.splitter_main = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D|wx.SP_LIVE_UPDATE )
		self.splitter_main.Bind( wx.EVT_IDLE, self.splitter_mainOnIdle )
		
		self.panel_components = wx.Panel( self.splitter_main, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER|wx.TAB_TRAVERSAL )
		self.panel_comp_fields = wx.Panel( self.splitter_main, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER|wx.TAB_TRAVERSAL )
		comp_fields_panel_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.comp_fields_panel_ref_label = wx.StaticText( self.panel_comp_fields, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.comp_fields_panel_ref_label.Wrap( -1 )
		self.comp_fields_panel_ref_label.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		
		comp_fields_panel_sizer.Add( self.comp_fields_panel_ref_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.comp_fields_panel_grid = wx.grid.Grid( self.panel_comp_fields, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		
		# Grid
		self.comp_fields_panel_grid.CreateGrid( 0, 2 )
		self.comp_fields_panel_grid.EnableEditing( False )
		self.comp_fields_panel_grid.EnableGridLines( True )
		self.comp_fields_panel_grid.SetGridLineColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
		self.comp_fields_panel_grid.EnableDragGridSize( True )
		self.comp_fields_panel_grid.SetMargins( 0, 0 )
		
		# Columns
		self.comp_fields_panel_grid.SetColSize( 0, 150 )
		self.comp_fields_panel_grid.SetColSize( 1, 150 )
		self.comp_fields_panel_grid.EnableDragColMove( False )
		self.comp_fields_panel_grid.EnableDragColSize( True )
		self.comp_fields_panel_grid.SetColLabelSize( 1 )
		self.comp_fields_panel_grid.SetColLabelValue( 0, u" " )
		self.comp_fields_panel_grid.SetColLabelValue( 1, u" " )
		self.comp_fields_panel_grid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.comp_fields_panel_grid.EnableDragRowSize( False )
		self.comp_fields_panel_grid.SetRowLabelSize( 50 )
		self.comp_fields_panel_grid.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.comp_fields_panel_grid.SetDefaultCellBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )
		self.comp_fields_panel_grid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		self.comp_fields_panel_grid.Hide()
		
		comp_fields_panel_sizer.Add( self.comp_fields_panel_grid, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.comp_fields_panel_file_label = wx.StaticText( self.panel_comp_fields, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.comp_fields_panel_file_label.Wrap( -1 )
		comp_fields_panel_sizer.Add( self.comp_fields_panel_file_label, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.panel_comp_fields.SetSizer( comp_fields_panel_sizer )
		self.panel_comp_fields.Layout()
		comp_fields_panel_sizer.Fit( self.panel_comp_fields )
		self.splitter_main.SplitVertically( self.panel_components, self.panel_comp_fields, 0 )
		sizer_main.Add( self.splitter_main, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( sizer_main )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.on_exit )
		self.Bind( wx.EVT_MENU, self.on_open_sch, id = self.menuitem_open_sch.GetId() )
		self.Bind( wx.EVT_MENU, self.on_save_sch, id = self.menuitem_save_sch.GetId() )
		self.Bind( wx.EVT_MENU, self.on_save_sch_as, id = self.menuitem_save_sch_as.GetId() )
		self.Bind( wx.EVT_MENU, self.on_open_lib, id = self.menuitem_open_lib.GetId() )
		self.Bind( wx.EVT_MENU, self.on_save_lib, id = self.menuitem_save_lib.GetId() )
		self.Bind( wx.EVT_MENU, self.on_save_lib_as, id = self.menuitem_save_lib_as.GetId() )
		self.Bind( wx.EVT_MENU, self.on_complist, id = self.menuitem_complist.GetId() )
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
		self.Bind( wx.EVT_MENU, self.on_settings_import, id = self.menuItem_settings_import.GetId() )
		self.Bind( wx.EVT_MENU, self.on_settings_export, id = self.menuItem_settings_export.GetId() )
		self.Bind( wx.EVT_MENU, self.on_tool, id = self.menuitem_tool.GetId() )
		self.Bind( wx.EVT_MENU, self.on_comp_fields_panel, id = self.menuitem_comp_fields_panel.GetId() )
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
	
	def on_save_sch_as( self, event ):
		event.Skip()
	
	def on_open_lib( self, event ):
		event.Skip()
	
	def on_save_lib( self, event ):
		event.Skip()
	
	def on_save_lib_as( self, event ):
		event.Skip()
	
	def on_complist( self, event ):
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
	
	def on_settings_import( self, event ):
		event.Skip()
	
	def on_settings_export( self, event ):
		event.Skip()
	
	def on_tool( self, event ):
		event.Skip()
	
	def on_comp_fields_panel( self, event ):
		event.Skip()
	
	def on_help( self, event ):
		event.Skip()
	
	def on_about( self, event ):
		event.Skip()
	
	def splitter_mainOnIdle( self, event ):
		self.splitter_main.SetSashPosition( 0 )
		self.splitter_main.Unbind( wx.EVT_IDLE )
	

###########################################################################
## Class EditorDialog
###########################################################################

class EditorDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Редактор полей", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER )
		
		self.SetSizeHintsSz( wx.Size( -1,-1 ), wx.DefaultSize )
		
		sizer_editor = wx.BoxSizer( wx.VERTICAL )
		
		self.panel_editor = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_fields = wx.BoxSizer( wx.VERTICAL )
		
		self.checkbox = wx.CheckBox( self.panel_editor, wx.ID_ANY, u"Включить в перечень элементов", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox.SetValue(True) 
		sizer_fields.Add( self.checkbox, 1, wx.ALL, 5 )
		
		sizer_field_1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_1 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Группа:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_LEFT )
		self.statictext_1.Wrap( -1 )
		sizer_field_1.Add( self.statictext_1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.editor_ctrl_1 = controls.EditorCtrl( self.panel_editor )
		sizer_field_1.Add( self.editor_ctrl_1, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_fields.Add( sizer_field_1, 0, wx.EXPAND, 5 )
		
		sizer_field_3 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_3 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Марка:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_LEFT )
		self.statictext_3.Wrap( -1 )
		sizer_field_3.Add( self.statictext_3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.editor_ctrl_3 = controls.EditorCtrl( self.panel_editor )
		sizer_field_3.Add( self.editor_ctrl_3, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_fields.Add( sizer_field_3, 0, wx.EXPAND, 5 )
		
		sizer_field_4 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_4 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Значение:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_LEFT )
		self.statictext_4.Wrap( -1 )
		sizer_field_4.Add( self.statictext_4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.editor_ctrl_4 = controls.EditorCtrl( self.panel_editor )
		sizer_field_4.Add( self.editor_ctrl_4, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_fields.Add( sizer_field_4, 0, wx.EXPAND, 5 )
		
		sizer_field_5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_5 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Класс точности:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_LEFT )
		self.statictext_5.Wrap( -1 )
		sizer_field_5.Add( self.statictext_5, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.editor_ctrl_5 = controls.EditorCtrl( self.panel_editor )
		sizer_field_5.Add( self.editor_ctrl_5, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_fields.Add( sizer_field_5, 0, wx.EXPAND, 5 )
		
		sizer_field_6 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_6 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Тип:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_LEFT )
		self.statictext_6.Wrap( -1 )
		sizer_field_6.Add( self.statictext_6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.editor_ctrl_6 = controls.EditorCtrl( self.panel_editor )
		sizer_field_6.Add( self.editor_ctrl_6, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_fields.Add( sizer_field_6, 0, wx.EXPAND, 5 )
		
		sizer_field_7 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_7 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Стандарт:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_LEFT )
		self.statictext_7.Wrap( -1 )
		sizer_field_7.Add( self.statictext_7, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.editor_ctrl_7 = controls.EditorCtrl( self.panel_editor )
		sizer_field_7.Add( self.editor_ctrl_7, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_fields.Add( sizer_field_7, 0, wx.EXPAND, 5 )
		
		sizer_field_8 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_8 = wx.StaticText( self.panel_editor, wx.ID_ANY, u"Примечание:", wx.DefaultPosition, wx.Size( 120,-1 ), wx.ALIGN_LEFT )
		self.statictext_8.Wrap( -1 )
		sizer_field_8.Add( self.statictext_8, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.editor_ctrl_8 = controls.EditorCtrl( self.panel_editor )
		sizer_field_8.Add( self.editor_ctrl_8, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_fields.Add( sizer_field_8, 0, wx.EXPAND, 5 )
		
		
		self.panel_editor.SetSizer( sizer_fields )
		self.panel_editor.Layout()
		sizer_fields.Fit( self.panel_editor )
		sizer_editor.Add( self.panel_editor, 0, wx.EXPAND, 5 )
		
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
		
		sizer_options = wx.BoxSizer( wx.HORIZONTAL )
		
		self.checkbox_case_sensitive = wx.CheckBox( self.panel_find, wx.ID_ANY, u"С учетом регистра", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_options.Add( self.checkbox_case_sensitive, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.checkbox_whole_word = wx.CheckBox( self.panel_find, wx.ID_ANY, u"Слово целиком", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_options.Add( self.checkbox_whole_word, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_find_common.Add( sizer_options, 1, wx.EXPAND, 5 )
		
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
		
		self.statictext_about = wx.StaticText( self.panel_about_dialog, wx.ID_ANY, u"kicadbom2spec - приложение для создания\nперечня элементов, оформленного согласно ЕСКД, для схем,\nвыполненных с помощью САПР KiCad.", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
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
		sizer_email.Add( self.statictext_email, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.hyperlink_email = wx.HyperlinkCtrl( self.panel_about_dialog, wx.ID_ANY, u"baranovskiykonstantin@gmail.com", u"mailto:baranovskiykonstantin@gmail.com?subject=kicadbom2spec", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		sizer_email.Add( self.hyperlink_email, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sizer_about.Add( sizer_email, 0, wx.EXPAND, 5 )
		
		sizer_homepage = wx.BoxSizer( wx.HORIZONTAL )
		
		self.statictext_homepage = wx.StaticText( self.panel_about_dialog, wx.ID_ANY, u"Домашняя страница:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.statictext_homepage.Wrap( -1 )
		sizer_homepage.Add( self.statictext_homepage, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.hyperlink_homepage = wx.HyperlinkCtrl( self.panel_about_dialog, wx.ID_ANY, u"https://launchpad.net/kicadbom2spec", u"https://launchpad.net/kicadbom2spec", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		sizer_homepage.Add( self.hyperlink_homepage, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sizer_about.Add( sizer_homepage, 0, wx.EXPAND, 5 )
		
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
## Class CompListDialog
###########################################################################

class CompListDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Создание перечня элементов", pos = wx.DefaultPosition, size = wx.Size( 400,480 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER )
		
		self.SetSizeHintsSz( wx.Size( -1,-1 ), wx.DefaultSize )
		
		sizer_complist_dialog = wx.BoxSizer( wx.VERTICAL )
		
		self.complist_notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.panel_file = wx.Panel( self.complist_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_file = wx.BoxSizer( wx.VERTICAL )
		
		sizer_filepicker = wx.StaticBoxSizer( wx.StaticBox( self.panel_file, wx.ID_ANY, u"Файл" ), wx.HORIZONTAL )
		
		self.filepicker_complist = wx.FilePickerCtrl( sizer_filepicker.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Выбор файла перечня элементов", u"Все файлы (*.*)|*.*|Текстовый документ (*.odt)|*.odt|Электронная таблица (*.ods)|*.ods", wx.DefaultPosition, wx.DefaultSize, wx.FLP_OVERWRITE_PROMPT|wx.FLP_SAVE|wx.FLP_USE_TEXTCTRL )
		sizer_filepicker.Add( self.filepicker_complist, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		sizer_file.Add( sizer_filepicker, 0, wx.EXPAND|wx.ALL, 5 )
		
		sizer_format = wx.StaticBoxSizer( wx.StaticBox( self.panel_file, wx.ID_ANY, u"Формат документа" ), wx.VERTICAL )
		
		self.rbutton_odt = wx.RadioButton( sizer_format.GetStaticBox(), wx.ID_ANY, u"Текстовый документ (*.odt)", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_format.Add( self.rbutton_odt, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, 5 )
		
		self.rbutton_ods = wx.RadioButton( sizer_format.GetStaticBox(), wx.ID_ANY, u"Электронная таблица (*.ods)", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_format.Add( self.rbutton_ods, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		sizer_file.Add( sizer_format, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		self.panel_file.SetSizer( sizer_file )
		self.panel_file.Layout()
		sizer_file.Fit( self.panel_file )
		self.complist_notebook.AddPage( self.panel_file, u"Файл", True )
		self.panel_options = wx.Panel( self.complist_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_options = wx.BoxSizer( wx.VERTICAL )
		
		sizer_options_comp = wx.StaticBoxSizer( wx.StaticBox( self.panel_options, wx.ID_ANY, u"Элементы" ), wx.VERTICAL )
		
		self.checkbox_all_components = wx.CheckBox( sizer_options_comp.GetStaticBox(), wx.ID_ANY, u"Все элементы", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_all_components.SetToolTipString( u"Если данная функция включена, в перечень элементов будут включены все элементы, не зависимо от того установлен флажок для элемента или нет." )
		
		sizer_options_comp.Add( self.checkbox_all_components, 0, wx.EXPAND|wx.ALL, 5 )
		
		self.checkbox_add_units = wx.CheckBox( sizer_options_comp.GetStaticBox(), wx.ID_ANY, u"Добавить единицы измерения", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_add_units.SetToolTipString( u"Если для резисторов, конденсаторов или индуктивностей указаны только значения и данная опция включена, то к значениям будут добавлены соответствующие единицы измерения (Ом, Ф, Гн)." )
		
		sizer_options_comp.Add( self.checkbox_add_units, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		sizer_options.Add( sizer_options_comp, 0, wx.EXPAND|wx.ALL, 5 )
		
		sizer_options_format = wx.StaticBoxSizer( wx.StaticBox( self.panel_options, wx.ID_ANY, u"Формат" ), wx.VERTICAL )
		
		self.checkbox_first_usage = wx.CheckBox( sizer_options_format.GetStaticBox(), wx.ID_ANY, u"Добавить графы первичной применяемости", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_first_usage.SetToolTipString( u"Если данная опция включена, то форматная рамка будет содержать графы первичной применяемости (24, 25 по ГОСТ2.104-2006)" )
		
		sizer_options_format.Add( self.checkbox_first_usage, 0, wx.EXPAND|wx.ALL, 5 )
		
		sizer_first_usage = wx.BoxSizer( wx.HORIZONTAL )
		
		
		sizer_first_usage.AddSpacer( ( 20, 0), 0, wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.checkbox_first_usage_fill = wx.CheckBox( sizer_options_format.GetStaticBox(), wx.ID_ANY, u"Указать первичную применяемость", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_first_usage_fill.SetToolTipString( u"Если данная опция включена, то графа Перв. примен. будет заполнена значением децимального номера без кода документа" )
		
		sizer_first_usage.Add( self.checkbox_first_usage_fill, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		sizer_options_format.Add( sizer_first_usage, 0, wx.EXPAND, 5 )
		
		self.checkbox_customer_fields = wx.CheckBox( sizer_options_format.GetStaticBox(), wx.ID_ANY, u"Добавить графы заказчика", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_customer_fields.SetToolTipString( u"Если данная опция включена, то над основной надписью будут показаны графы заказчика (27-30 по ГОСТ2.104-2006)" )
		
		sizer_options_format.Add( self.checkbox_customer_fields, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		self.checkbox_changes_sheet = wx.CheckBox( sizer_options_format.GetStaticBox(), wx.ID_ANY, u"Добавить лист регистрации изменений", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_changes_sheet.SetToolTipString( u"Если данная опция включена, то в конец перечня элементов будет добавлен лист регистрации изменений." )
		
		sizer_options_format.Add( self.checkbox_changes_sheet, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		self.checkbox_italic = wx.CheckBox( sizer_options_format.GetStaticBox(), wx.ID_ANY, u"Курсив", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_italic.SetToolTipString( u"Использовать курсив для оформления перечня элементов.\nЕсли отметка отсутствует, будет использован прямой шрифт." )
		
		sizer_options_format.Add( self.checkbox_italic, 0, wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		sizer_options.Add( sizer_options_format, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		sizer_options_other = wx.StaticBoxSizer( wx.StaticBox( self.panel_options, wx.ID_ANY, u"Прочее" ), wx.VERTICAL )
		
		self.checkbox_open = wx.CheckBox( sizer_options_other.GetStaticBox(), wx.ID_ANY, u"Открыть перечень элементов", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_open.SetToolTipString( u"Если этот параметр установлен, то после создания перечня элементов он будет открыт в редакторе по умолчанию." )
		
		sizer_options_other.Add( self.checkbox_open, 0, wx.EXPAND|wx.ALL, 5 )
		
		
		sizer_options.Add( sizer_options_other, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		self.panel_options.SetSizer( sizer_options )
		self.panel_options.Layout()
		sizer_options.Fit( self.panel_options )
		self.complist_notebook.AddPage( self.panel_options, u"Параметры", False )
		self.panel_stamp = wx.Panel( self.complist_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_stamp = wx.BoxSizer( wx.VERTICAL )
		
		sizer_title = wx.StaticBoxSizer( wx.StaticBox( self.panel_stamp, wx.ID_ANY, u"Наименование" ), wx.VERTICAL )
		
		self.stamp_title_text = wx.TextCtrl( sizer_title.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.TE_MULTILINE )
		sizer_title.Add( self.stamp_title_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.stamp_title_converted = wx.StaticText( sizer_title.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stamp_title_converted.Wrap( -1 )
		self.stamp_title_converted.SetToolTipString( u"Наименование автоматически корректируется\nсогласно ЕСКД.\nДанное значение будет указано в основной надписи\nперечня элементов." )
		
		sizer_title.Add( self.stamp_title_converted, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_stamp.Add( sizer_title, 0, wx.ALL|wx.EXPAND, 5 )
		
		sizer_decimal_num = wx.StaticBoxSizer( wx.StaticBox( self.panel_stamp, wx.ID_ANY, u"Децимальный номер" ), wx.VERTICAL )
		
		self.stamp_decimal_num_text = wx.TextCtrl( sizer_decimal_num.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_decimal_num.Add( self.stamp_decimal_num_text, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, 5 )
		
		self.stamp_decimal_num_converted = wx.StaticText( sizer_decimal_num.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stamp_decimal_num_converted.Wrap( -1 )
		self.stamp_decimal_num_converted.SetToolTipString( u"Децимальный номер автоматически корректируется\nсогласно ЕСКД.\nДанное значение будет указано в основной надписи\nперечня элементов." )
		
		sizer_decimal_num.Add( self.stamp_decimal_num_converted, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		
		sizer_stamp.Add( sizer_decimal_num, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		sizer_comp = wx.StaticBoxSizer( wx.StaticBox( self.panel_stamp, wx.ID_ANY, u"Организация" ), wx.VERTICAL )
		
		self.stamp_comp_text = wx.TextCtrl( sizer_comp.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_comp.Add( self.stamp_comp_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		sizer_stamp.Add( sizer_comp, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		sizer2_spamp = wx.BoxSizer( wx.HORIZONTAL )
		
		sizer21_stamp = wx.BoxSizer( wx.VERTICAL )
		
		sizer_developer = wx.StaticBoxSizer( wx.StaticBox( self.panel_stamp, wx.ID_ANY, u"Разработал" ), wx.VERTICAL )
		
		self.stamp_developer_text = wx.TextCtrl( sizer_developer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_developer.Add( self.stamp_developer_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		sizer21_stamp.Add( sizer_developer, 0, wx.EXPAND|wx.ALL, 5 )
		
		sizer_verifer = wx.StaticBoxSizer( wx.StaticBox( self.panel_stamp, wx.ID_ANY, u"Проверил" ), wx.VERTICAL )
		
		self.stamp_verifier_text = wx.TextCtrl( sizer_verifer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_verifer.Add( self.stamp_verifier_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		sizer21_stamp.Add( sizer_verifer, 0, wx.EXPAND|wx.ALL, 5 )
		
		
		sizer2_spamp.Add( sizer21_stamp, 1, wx.EXPAND, 5 )
		
		sizer22_stamp = wx.BoxSizer( wx.VERTICAL )
		
		sizer_approver = wx.StaticBoxSizer( wx.StaticBox( self.panel_stamp, wx.ID_ANY, u"Утвердил" ), wx.VERTICAL )
		
		self.stamp_approver_text = wx.TextCtrl( sizer_approver.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_approver.Add( self.stamp_approver_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		sizer22_stamp.Add( sizer_approver, 0, wx.EXPAND|wx.ALL, 5 )
		
		sizer_inspector = wx.StaticBoxSizer( wx.StaticBox( self.panel_stamp, wx.ID_ANY, u"Нормоконтролер" ), wx.VERTICAL )
		
		self.stamp_inspector_text = wx.TextCtrl( sizer_inspector.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_inspector.Add( self.stamp_inspector_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		sizer22_stamp.Add( sizer_inspector, 0, wx.EXPAND|wx.ALL, 5 )
		
		
		sizer2_spamp.Add( sizer22_stamp, 1, wx.EXPAND, 5 )
		
		
		sizer_stamp.Add( sizer2_spamp, 0, wx.EXPAND, 5 )
		
		
		self.panel_stamp.SetSizer( sizer_stamp )
		self.panel_stamp.Layout()
		sizer_stamp.Fit( self.panel_stamp )
		self.complist_notebook.AddPage( self.panel_stamp, u"Основная надпись", False )
		
		sizer_complist_dialog.Add( self.complist_notebook, 1, wx.EXPAND |wx.ALL, 5 )
		
		dialog_buttons = wx.StdDialogButtonSizer()
		self.dialog_buttonsOK = wx.Button( self, wx.ID_OK )
		dialog_buttons.AddButton( self.dialog_buttonsOK )
		self.dialog_buttonsCancel = wx.Button( self, wx.ID_CANCEL )
		dialog_buttons.AddButton( self.dialog_buttonsCancel )
		dialog_buttons.Realize();
		
		sizer_complist_dialog.Add( dialog_buttons, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( sizer_complist_dialog )
		self.Layout()
		
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
		self.general_panel = wx.Panel( self.settings_tabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		general_tab_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.space_as_dot_checkbox = wx.CheckBox( self.general_panel, wx.ID_ANY, u"Отображать пробелы в виде точек \"·\"", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.space_as_dot_checkbox.SetToolTipString( u"Если этот параметр установлен, то в таблице и в полях ввода пробелы будут отображаться в виде специальных символов." )
		
		general_tab_sizer.Add( self.space_as_dot_checkbox, 0, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.remember_selection_checkbox = wx.CheckBox( self.general_panel, wx.ID_ANY, u"Запоминать выбор элементов", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.remember_selection_checkbox.SetToolTipString( u"Если этот параметр установлен, то при сохранении схемы элементам, которые не отмечены для вывода в перечень элементов, будет добавлено поле \"Исключен из ПЭ\". \nПри открытии схемы для элементов с полем \"Исключен из ПЭ\" будет автоматически снята отметка о выводе в перечень элементов." )
		
		general_tab_sizer.Add( self.remember_selection_checkbox, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.show_need_adjust_mark_checkbox = wx.CheckBox( self.general_panel, wx.ID_ANY, u"Показывать метку \"*\" возле обозначения на схеме", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.show_need_adjust_mark_checkbox.SetToolTipString( u"Если этот параметр установлен, то на схеме, возле обозначения компонента, номинал которого \"Подбирают при регулировании\", будет отображаться метка \"*\"." )
		
		general_tab_sizer.Add( self.show_need_adjust_mark_checkbox, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5 )
		
		self.staticline2 = wx.StaticLine( self.general_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		general_tab_sizer.Add( self.staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.auto_groups_statictext = wx.StaticText( self.general_panel, wx.ID_ANY, u"Автоматически заполнять поле \"Группа\" для:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.auto_groups_statictext.Wrap( -1 )
		self.auto_groups_statictext.SetToolTipString( u"Если элементам не назначено значие поля \"Группа\", то при загрузке элементов из файла схемы/библиотеки для выбранных типов они будут сформированны автоматически." )
		
		general_tab_sizer.Add( self.auto_groups_statictext, 0, wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		auto_groups_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		
		auto_groups_sizer.AddSpacer( ( 20, 0), 0, 0, 5 )
		
		self.auto_group_scrolledwindow = wx.ScrolledWindow( self.general_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.VSCROLL )
		self.auto_group_scrolledwindow.SetScrollRate( 5, 5 )
		auto_group_scrolledwindow_sizer = wx.BoxSizer( wx.VERTICAL )
		
		auto_groups_checklistboxChoices = []
		self.auto_groups_checklistbox = wx.CheckListBox( self.auto_group_scrolledwindow, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,100 ), auto_groups_checklistboxChoices, wx.LB_NEEDED_SB|wx.LB_SORT )
		auto_group_scrolledwindow_sizer.Add( self.auto_groups_checklistbox, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.auto_group_scrolledwindow.SetSizer( auto_group_scrolledwindow_sizer )
		self.auto_group_scrolledwindow.Layout()
		auto_group_scrolledwindow_sizer.Fit( self.auto_group_scrolledwindow )
		auto_groups_sizer.Add( self.auto_group_scrolledwindow, 1, wx.EXPAND |wx.ALL, 5 )
		
		auto_groups_buttons_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.auto_groups_add_button = wx.Button( self.general_panel, wx.ID_ANY, u"Добавить", wx.DefaultPosition, wx.DefaultSize, 0 )
		auto_groups_buttons_sizer.Add( self.auto_groups_add_button, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		self.auto_groups_edit_button = wx.Button( self.general_panel, wx.ID_ANY, u"Изменить", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.auto_groups_edit_button.Enable( False )
		
		auto_groups_buttons_sizer.Add( self.auto_groups_edit_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		self.auto_groups_remove_button = wx.Button( self.general_panel, wx.ID_ANY, u"Удалить", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.auto_groups_remove_button.Enable( False )
		
		auto_groups_buttons_sizer.Add( self.auto_groups_remove_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		
		auto_groups_sizer.Add( auto_groups_buttons_sizer, 0, 0, 5 )
		
		
		general_tab_sizer.Add( auto_groups_sizer, 1, wx.EXPAND, 5 )
		
		
		self.general_panel.SetSizer( general_tab_sizer )
		self.general_panel.Layout()
		general_tab_sizer.Fit( self.general_panel )
		self.settings_tabs.AddPage( self.general_panel, u"Основные", True )
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
		self.separators_panel = wx.Panel( self.settings_tabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		separators_common_sizer = wx.BoxSizer( wx.VERTICAL )
		
		header_sizer = wx.GridSizer( 1, 3, 0, 0 )
		
		self.prefix_header_label = wx.StaticText( self.separators_panel, wx.ID_ANY, u"Префикс", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.prefix_header_label.Wrap( -1 )
		self.prefix_header_label.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		
		header_sizer.Add( self.prefix_header_label, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.field_header_label = wx.StaticText( self.separators_panel, wx.ID_ANY, u"Поле", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.field_header_label.Wrap( -1 )
		self.field_header_label.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		
		header_sizer.Add( self.field_header_label, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.suffix_header_label = wx.StaticText( self.separators_panel, wx.ID_ANY, u"Суффикс", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.suffix_header_label.Wrap( -1 )
		self.suffix_header_label.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		
		header_sizer.Add( self.suffix_header_label, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		separators_common_sizer.Add( header_sizer, 0, wx.EXPAND|wx.TOP, 5 )
		
		self.m_staticline14 = wx.StaticLine( self.separators_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		separators_common_sizer.Add( self.m_staticline14, 0, wx.EXPAND |wx.ALL, 5 )
		
		separators_sizer = wx.GridSizer( 5, 3, 0, 0 )
		
		self.separator1_prefix_text = wx.TextCtrl( self.separators_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_RIGHT )
		separators_sizer.Add( self.separator1_prefix_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 5 )
		
		self.separator1_label = wx.StaticText( self.separators_panel, wx.ID_ANY, u"Марка", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.separator1_label.Wrap( -1 )
		separators_sizer.Add( self.separator1_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.separator1_suffix_text = wx.TextCtrl( self.separators_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		separators_sizer.Add( self.separator1_suffix_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 5 )
		
		self.separator2_prefix_text = wx.TextCtrl( self.separators_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_RIGHT )
		separators_sizer.Add( self.separator2_prefix_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 5 )
		
		self.separator2_label = wx.StaticText( self.separators_panel, wx.ID_ANY, u"Значение", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.separator2_label.Wrap( -1 )
		separators_sizer.Add( self.separator2_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.separator2_suffix_text = wx.TextCtrl( self.separators_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		separators_sizer.Add( self.separator2_suffix_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 5 )
		
		self.separator3_prefix_text = wx.TextCtrl( self.separators_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_RIGHT )
		separators_sizer.Add( self.separator3_prefix_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 5 )
		
		self.separator3_label = wx.StaticText( self.separators_panel, wx.ID_ANY, u"Класс точности", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.separator3_label.Wrap( -1 )
		separators_sizer.Add( self.separator3_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.separator3_suffix_text = wx.TextCtrl( self.separators_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		separators_sizer.Add( self.separator3_suffix_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 5 )
		
		self.separator4_prefix_text = wx.TextCtrl( self.separators_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_RIGHT )
		separators_sizer.Add( self.separator4_prefix_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 5 )
		
		self.separator4_label = wx.StaticText( self.separators_panel, wx.ID_ANY, u"Тип", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.separator4_label.Wrap( -1 )
		separators_sizer.Add( self.separator4_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.separator4_suffix_text = wx.TextCtrl( self.separators_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		separators_sizer.Add( self.separator4_suffix_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 5 )
		
		self.separator5_prefix_text = wx.TextCtrl( self.separators_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_RIGHT )
		separators_sizer.Add( self.separator5_prefix_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 5 )
		
		self.separator5_label = wx.StaticText( self.separators_panel, wx.ID_ANY, u"Стандарт", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.separator5_label.Wrap( -1 )
		separators_sizer.Add( self.separator5_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.separator5_suffix_text = wx.TextCtrl( self.separators_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		separators_sizer.Add( self.separator5_suffix_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 5 )
		
		
		separators_common_sizer.Add( separators_sizer, 0, wx.EXPAND, 5 )
		
		self.m_staticline9 = wx.StaticLine( self.separators_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		separators_common_sizer.Add( self.m_staticline9, 0, wx.EXPAND |wx.ALL, 5 )
		
		separators_note_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.separators_note_statictext = wx.StaticText( self.separators_panel, wx.ID_ANY, u"Примечание:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.separators_note_statictext.Wrap( -1 )
		self.separators_note_statictext.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		
		separators_note_sizer.Add( self.separators_note_statictext, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.separators_notetext_statictext = wx.StaticText( self.separators_panel, wx.ID_ANY, u"символом \"·\" обозначены пробелы.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.separators_notetext_statictext.Wrap( -1 )
		separators_note_sizer.Add( self.separators_notetext_statictext, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		separators_common_sizer.Add( separators_note_sizer, 0, wx.LEFT, 5 )
		
		
		separators_common_sizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		self.separators_panel.SetSizer( separators_common_sizer )
		self.separators_panel.Layout()
		separators_common_sizer.Fit( self.separators_panel )
		self.settings_tabs.AddPage( self.separators_panel, u"Разделители", False )
		self.aliases_panel = wx.Panel( self.settings_tabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		alias_sizer = wx.BoxSizer( wx.VERTICAL )
		
		alias_header_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.alias_field_header_panel = wx.Panel( self.aliases_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		alias_field_header_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.alias_field_header_label = wx.StaticText( self.alias_field_header_panel, wx.ID_ANY, u"Поле", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.alias_field_header_label.Wrap( -1 )
		self.alias_field_header_label.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		
		alias_field_header_sizer.Add( self.alias_field_header_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		self.alias_field_header_panel.SetSizer( alias_field_header_sizer )
		self.alias_field_header_panel.Layout()
		alias_field_header_sizer.Fit( self.alias_field_header_panel )
		alias_header_sizer.Add( self.alias_field_header_panel, 1, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.alias_value_header_panel = wx.Panel( self.aliases_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		alias_value_header_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.alias_value_header_label = wx.StaticText( self.alias_value_header_panel, wx.ID_ANY, u"Псевдоним", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.alias_value_header_label.Wrap( -1 )
		self.alias_value_header_label.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		
		alias_value_header_sizer.Add( self.alias_value_header_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		self.alias_value_header_panel.SetSizer( alias_value_header_sizer )
		self.alias_value_header_panel.Layout()
		alias_value_header_sizer.Fit( self.alias_value_header_panel )
		alias_header_sizer.Add( self.alias_value_header_panel, 2, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		
		alias_sizer.Add( alias_header_sizer, 0, wx.EXPAND, 5 )
		
		self.m_staticline15 = wx.StaticLine( self.aliases_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		alias_sizer.Add( self.m_staticline15, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.alises_scrollpanel = wx.ScrolledWindow( self.aliases_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.alises_scrollpanel.SetScrollRate( 5, 5 )
		aliases_scrollpanel_sizer = wx.BoxSizer( wx.VERTICAL )
		
		alias1_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.alias1_label = wx.StaticText( self.alises_scrollpanel, wx.ID_ANY, u"Группа", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.alias1_label.Wrap( -1 )
		alias1_sizer.Add( self.alias1_label, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.alias1_text = wx.TextCtrl( self.alises_scrollpanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		alias1_sizer.Add( self.alias1_text, 2, wx.ALL, 5 )
		
		
		aliases_scrollpanel_sizer.Add( alias1_sizer, 0, wx.EXPAND, 5 )
		
		alias2_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.alias2_label = wx.StaticText( self.alises_scrollpanel, wx.ID_ANY, u"Марка", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.alias2_label.Wrap( -1 )
		alias2_sizer.Add( self.alias2_label, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.alias2_text = wx.TextCtrl( self.alises_scrollpanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		alias2_sizer.Add( self.alias2_text, 2, wx.ALL, 5 )
		
		
		aliases_scrollpanel_sizer.Add( alias2_sizer, 0, wx.EXPAND, 5 )
		
		alias3_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.alias3_label = wx.StaticText( self.alises_scrollpanel, wx.ID_ANY, u"Значение", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.alias3_label.Wrap( -1 )
		alias3_sizer.Add( self.alias3_label, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.alias3_text = wx.TextCtrl( self.alises_scrollpanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		alias3_sizer.Add( self.alias3_text, 2, wx.ALL, 5 )
		
		
		aliases_scrollpanel_sizer.Add( alias3_sizer, 0, wx.EXPAND, 5 )
		
		alias4_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.alias4_label = wx.StaticText( self.alises_scrollpanel, wx.ID_ANY, u"Класс точности", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.alias4_label.Wrap( -1 )
		alias4_sizer.Add( self.alias4_label, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.alias4_text = wx.TextCtrl( self.alises_scrollpanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		alias4_sizer.Add( self.alias4_text, 2, wx.ALL, 5 )
		
		
		aliases_scrollpanel_sizer.Add( alias4_sizer, 0, wx.EXPAND, 5 )
		
		alias5_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.alias5_label = wx.StaticText( self.alises_scrollpanel, wx.ID_ANY, u"Тип", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.alias5_label.Wrap( -1 )
		alias5_sizer.Add( self.alias5_label, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.alias5_text = wx.TextCtrl( self.alises_scrollpanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		alias5_sizer.Add( self.alias5_text, 2, wx.ALL, 5 )
		
		
		aliases_scrollpanel_sizer.Add( alias5_sizer, 0, wx.EXPAND, 5 )
		
		alias6_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.alias6_label = wx.StaticText( self.alises_scrollpanel, wx.ID_ANY, u"Стандарт", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.alias6_label.Wrap( -1 )
		alias6_sizer.Add( self.alias6_label, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.alias6_text = wx.TextCtrl( self.alises_scrollpanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		alias6_sizer.Add( self.alias6_text, 2, wx.ALL, 5 )
		
		
		aliases_scrollpanel_sizer.Add( alias6_sizer, 0, wx.EXPAND, 5 )
		
		alias7_sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.alias7_label = wx.StaticText( self.alises_scrollpanel, wx.ID_ANY, u"Примечание", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.alias7_label.Wrap( -1 )
		alias7_sizer.Add( self.alias7_label, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.alias7_text = wx.TextCtrl( self.alises_scrollpanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		alias7_sizer.Add( self.alias7_text, 2, wx.ALL, 5 )
		
		
		aliases_scrollpanel_sizer.Add( alias7_sizer, 0, wx.EXPAND, 5 )
		
		
		self.alises_scrollpanel.SetSizer( aliases_scrollpanel_sizer )
		self.alises_scrollpanel.Layout()
		aliases_scrollpanel_sizer.Fit( self.alises_scrollpanel )
		alias_sizer.Add( self.alises_scrollpanel, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		self.aliases_panel.SetSizer( alias_sizer )
		self.aliases_panel.Layout()
		alias_sizer.Fit( self.aliases_panel )
		self.settings_tabs.AddPage( self.aliases_panel, u"Псевдонимы", False )
		
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
## Class SettingsSelector
###########################################################################

class SettingsSelector ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Выбор параметров", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CAPTION|wx.CLOSE_BOX )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		sizer_settings_selector = wx.BoxSizer( wx.VERTICAL )
		
		self.panel_settings_selector = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_settings = wx.BoxSizer( wx.VERTICAL )
		
		self.statictext1 = wx.StaticText( self.panel_settings_selector, wx.ID_ANY, u"В выбраном файле найдены следующие\nпараметры:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.statictext1.Wrap( -1 )
		sizer_settings.Add( self.statictext1, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		self.checkbox_size_position = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Размер и позиция окна", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_size_position.SetToolTipString( u"Размер и положение окна программы на экране." )
		
		sizer_settings.Add( self.checkbox_size_position, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.checkbox_column_sizes = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Размеры колонок таблицы элементов", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_column_sizes.SetToolTipString( u"Размеры колонок таблицы элементов." )
		
		sizer_settings.Add( self.checkbox_column_sizes, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.checkbox_comp_fields_panel = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Параметры панели полей компонента", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_comp_fields_panel.SetToolTipString( u"Размеры панели полей выбранного компонента и его дочерних элементов." )
		
		sizer_settings.Add( self.checkbox_comp_fields_panel, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5 )
		
		self.checkbox_general = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Обшие параметры", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_general.SetToolTipString( u"Значения общих параметров:\n* Отображать пробелы в виде точек \"᛫\"\n* Запоминать выбор элементов\n* Показывать метку \"*\" возле обозначения на схеме" )
		
		sizer_settings.Add( self.checkbox_general, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.checkbox_values = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Стандартные значения полей элементов", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_values.SetToolTipString( u"Наборы часто используемых значений для разных полей элементов." )
		
		sizer_settings.Add( self.checkbox_values, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.checkbox_auto_filling_groups = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Параметры авт. заполнения поля \"Группа\"", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_auto_filling_groups.SetToolTipString( u"Наборы значений и их состояние для\nавтоматического заполенения поля\n\"Группа\" при отрытии файлов схем и\nбиблиотек." )
		
		sizer_settings.Add( self.checkbox_auto_filling_groups, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.checkbox_separators = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Разделители наименования", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_separators.SetToolTipString( u"Разделители - это символы, которые\nдобавляются в виде префиксов или\nсуффиксов к полям при формировании\nнаименования элемента в перечне." )
		
		sizer_settings.Add( self.checkbox_separators, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5 )
		
		self.checkbox_aliases = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Псевдонимы полей", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_aliases.SetToolTipString( u"Псевдонимы позволяют использовать\nлюбые пользователские поля для \nработы с приложением." )
		
		sizer_settings.Add( self.checkbox_aliases, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 5 )
		
		self.checkbox_complist = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Параметры перечня элементов", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_complist.SetToolTipString( u"Параметры из диалогового окна\nсоздания перечня элементов." )
		
		sizer_settings.Add( self.checkbox_complist, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.checkbox_recent_sch = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Недавние схемы", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_recent_sch.SetToolTipString( u"Список недавно используемых файлов схем." )
		
		sizer_settings.Add( self.checkbox_recent_sch, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.checkbox_recent_lib = wx.CheckBox( self.panel_settings_selector, wx.ID_ANY, u"Недавние библиотеки", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkbox_recent_lib.SetToolTipString( u"Список недавно используемых файлов схем." )
		
		sizer_settings.Add( self.checkbox_recent_lib, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		self.panel_settings_selector.SetSizer( sizer_settings )
		self.panel_settings_selector.Layout()
		sizer_settings.Fit( self.panel_settings_selector )
		sizer_settings_selector.Add( self.panel_settings_selector, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_settings_selector.Add( self.staticline, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.statictext2 = wx.StaticText( self, wx.ID_ANY, u"Укажите отметками какие параметры\nнужно применить к программе.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.statictext2.Wrap( -1 )
		sizer_settings_selector.Add( self.statictext2, 0, wx.ALIGN_CENTER|wx.ALL|wx.EXPAND, 5 )
		
		dialog_button = wx.StdDialogButtonSizer()
		self.dialog_buttonOK = wx.Button( self, wx.ID_OK )
		dialog_button.AddButton( self.dialog_buttonOK )
		self.dialog_buttonCancel = wx.Button( self, wx.ID_CANCEL )
		dialog_button.AddButton( self.dialog_buttonCancel )
		dialog_button.Realize();
		
		sizer_settings_selector.Add( dialog_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( sizer_settings_selector )
		self.Layout()
		sizer_settings_selector.Fit( self )
		
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
	

