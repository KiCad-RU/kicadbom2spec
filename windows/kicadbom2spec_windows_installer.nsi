;;; BEGIN LICENSE
; Copyright (C) 2015 Baranovskiy Konstantin (baranovskiykonstantin@gmail.com)
; This program is free software: you can redistribute it and/or modify it
; under the terms of the GNU General Public License version 3, as published
; by the Free Software Foundation.
;
; This program is distributed in the hope that it will be useful, but
; WITHOUT ANY WARRANTY; without even the implied warranties of
; MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
; PURPOSE.  See the GNU General Public License for more details.
;
; You should have received a copy of the GNU General Public License along
; with this program.  If not, see <http://www.gnu.org/licenses/>.
;;; END LICENSE

; Plugins:
; - UnTGZ
; - Inetc
; - NSISunzU

!include MUI2.nsh
!include StrFunc.nsh
${StrRep}

Name "kicadbom2spec"
OutFile "..\..\kicadbom2spec_windows_installer.exe"
InstallDir "$PROGRAMFILES\kicadbom2spec"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\COPYING"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_COMPONENTS
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "Russian"

Function ConnectInternet

	Push $R0

	ClearErrors
	Dialer::AttemptConnect
	IfErrors noie3

	Pop $R0
	StrCmp $R0 "online" connected
		MessageBox MB_OK|MB_ICONSTOP "Невозможно подключиться к интернету."
		Quit

	noie3:

	; IE3 not installed
	MessageBox MB_OK|MB_ICONINFORMATION "Пожалуйста, подключитесь к интернету."

	connected:

	Pop $R0

FunctionEnd

Function VersionCompare
; Compare version numbers.
;
; Syntax:
; ${VersionCompare} "[Version1]" "[Version2]" $var
; 
; "[Version1]"        ; First version
; "[Version2]"        ; Second version
; $var                ; Result:
;                     ;    $var=0  Versions are equal
;                     ;    $var=1  Version1 is newer
;                     ;    $var=2  Version2 is newer

	!define VersionCompare `!insertmacro VersionCompareCall`
 
	!macro VersionCompareCall _VER1 _VER2 _RESULT
		Push `${_VER1}`
		Push `${_VER2}`
		Call VersionCompare
		Pop ${_RESULT}
	!macroend
 
	Exch $1
	Exch
	Exch $0
	Exch
	Push $2
	Push $3
	Push $4
	Push $5
	Push $6
	Push $7
 
	begin:
	StrCpy $2 -1
	IntOp $2 $2 + 1
	StrCpy $3 $0 1 $2
	StrCmp $3 '' +2
	StrCmp $3 '.' 0 -3
	StrCpy $4 $0 $2
	IntOp $2 $2 + 1
	StrCpy $0 $0 '' $2
 
	StrCpy $2 -1
	IntOp $2 $2 + 1
	StrCpy $3 $1 1 $2
	StrCmp $3 '' +2
	StrCmp $3 '.' 0 -3
	StrCpy $5 $1 $2
	IntOp $2 $2 + 1
	StrCpy $1 $1 '' $2
 
	StrCmp $4$5 '' equal
 
	StrCpy $6 -1
	IntOp $6 $6 + 1
	StrCpy $3 $4 1 $6
	StrCmp $3 '0' -2
	StrCmp $3 '' 0 +2
	StrCpy $4 0
 
	StrCpy $7 -1
	IntOp $7 $7 + 1
	StrCpy $3 $5 1 $7
	StrCmp $3 '0' -2
	StrCmp $3 '' 0 +2
	StrCpy $5 0
 
	StrCmp $4 0 0 +2
	StrCmp $5 0 begin newer2
	StrCmp $5 0 newer1
	IntCmp $6 $7 0 newer1 newer2
 
	StrCpy $4 '1$4'
	StrCpy $5 '1$5'
	IntCmp $4 $5 begin newer2 newer1
 
	equal:
	StrCpy $0 0
	goto end
	newer1:
	StrCpy $0 1
	goto end
	newer2:
	StrCpy $0 2
 
	end:
	Pop $7
	Pop $6
	Pop $5
	Pop $4
	Pop $3
	Pop $2
	Pop $1
	Exch $0
FunctionEnd

; =============================== Installer ===================================

Section "" sec_python
	Push $0
	Push $1

	SectionGetText ${sec_python} $0
	StrCmp $0 "" skip_install

	Call ConnectInternet
	StrCpy $1 "$TEMP\python_installer.msi"
	inetc::get "https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi" $1 /END
	Pop $0
	StrCmp $0 "OK" success
		SetDetailsView show
		DetailPrint "Не удалось загрузить установочный файл интерпретатора языка Python."
		Abort
	success:
		ExecWait 'msiexec /i "$1"'
		Delete $1

	skip_install:

	Pop $0
	Pop $1
SectionEnd

Section "" sec_wx
	Push $0
	Push $1

	SectionGetText ${sec_wx} $0
	StrCmp $0 "" skip_install

	Call ConnectInternet
	StrCpy $1 "$TEMP\wx_installer.exe"
	inetc::get "http://downloads.sourceforge.net/wxpython/wxPython3.0-win32-3.0.2.0-py27.exe" $1 /END
	Pop $0
	StrCmp $0 "OK" success
		SetDetailsView show
		DetailPrint "Не удалось загрузить установочный файл библиотеки wxWidgets для Python."
		Abort
	success:
		ExecWait '"$1"'
		Delete $1

	skip_install:

	Pop $0
	Pop $1
SectionEnd

Section "" sec_odf
	Push $0
	Push $1

	SectionGetText ${sec_odf} $0
	StrCmp $0 "" skip_install

	Call ConnectInternet
	StrCpy $1 "$TEMP\odfpy_sources.tar.gz"
	inetc::get "https://pypi.python.org/packages/source/o/odfpy/odfpy-0.9.6.tar.gz" $1 /END
	Pop $0
	StrCmp $0 "OK" success
		SetDetailsView show
		DetailPrint "Не удалось загрузить файлы, необходимые для сборки и установки odfpy."
		Abort
	success:
		StrCpy $0 "$TEMP\odfpy"
		CreateDirectory $0
		untgz::extract -d $0 $1
		SetOutPath "$0\odfpy-0.9.6"
		ExecWait "python setup.py build"
		ExecWait "python setup.py install"
		SetOutPath "$INSTDIR"
		RMDir $0
		Delete $1

	skip_install:

	Pop $0
	Pop $1
SectionEnd

Section /o "" sec_font
	Push $0
	Push $1

	SectionGetText ${sec_font} $0
	StrCmp $0 "" skip_install

	Call ConnectInternet
	StrCpy $1 "$TEMP\opengostfont.zip"
	inetc::get "https://bitbucket.org/fat_angel/opengostfont/downloads/opengostfont-ttf-0.3.zip" $1 /END
	Pop $0
	StrCmp $0 "OK" success
		SetDetailsView show
		DetailPrint "Не удалось загрузить чертежные шрифты."
		Abort
	success:
		nsisunz::Unzip /noextractpath /file "opengostfont-ttf-0.3\OpenGostTypeA-Regular.ttf" $1 "$FONTS"
		nsisunz::Unzip /noextractpath /file "opengostfont-ttf-0.3\OpenGostTypeB-Regular.ttf" $1 "$FONTS"
		Delete $1

	skip_install:

	Pop $0
	Pop $1
SectionEnd

Section /o "" sec_office
	Push $0
	Push $1

	SectionGetText ${sec_office} $0
	StrCmp $0 "" skip_install

	Call ConnectInternet
	StrCpy $1 "$TEMP\libreoffice_installer.msi"
	inetc::get "http://download.documentfoundation.org/libreoffice/stable/4.4.2/win/x86/LibreOffice_4.4.2_Win_x86.msi" $1 /END
	Pop $0
	StrCmp $0 "OK" success
		SetDetailsView show
		DetailPrint "Не удалось загрузить установочный файл офисный пакет LibreOffice."
		Abort
	success:
		ExecWait 'msiexec /i "$1"'
		Delete $1

	skip_install:

	Pop $0
	Pop $1
SectionEnd

SectionGroup /e "!kicadbom2spec" secgrp_main
	Section "kicadbom2spec" sec_main

		CreateDirectory "$INSTDIR\bitmaps"
		SetOutPath "$INSTDIR\bitmaps"
		File "..\bitmaps\*.*"

		CreateDirectory "$INSTDIR\sample"
		SetOutPath "$INSTDIR\sample"
		File "..\sample\*.*"

		SetOutPath $INSTDIR
		File "..\COPYING"
		File "..\README"
		File "..\CHANGELOG"
		File "..\kicadsch.py"
		File "..\spec.py"
		File "..\pattern.ods"
		File "..\gui.py"
		File "..\kicadbom2spec.pyw"
		File "..\doc\help_windows.pdf"
		WriteUninstaller "uninstall.exe"
		CreateDirectory "$SMPROGRAMS\kicadbom2spec"
		CreateShortCut "$SMPROGRAMS\kicadbom2spec\Запустить kicadbom2spec.lnk" "$INSTDIR\kicadbom2spec.pyw" "" "$INSTDIR\bitmaps\icon.ico"
		CreateShortCut "$SMPROGRAMS\kicadbom2spec\Руководство пользователя.lnk" "$INSTDIR\help_windows.pdf"
		CreateShortCut "$SMPROGRAMS\kicadbom2spec\Удалить kicadbom2spec.lnk" "$INSTDIR\uninstall.exe"
	SectionEnd
	
	Section /o "settings.ini" sec_settings
		SetOutPath "$INSTDIR"
		File "..\settings.ini"
	SectionEnd
SectionGroupEnd

LangString DESC_sec_python ${LANG_Russian} "Интерпретатор языка Python."
LangString DESC_sec_wx ${LANG_Russian} "Обёртка библиотеки кросплатформенного графического интерфейса пользователя wxWidgets для Python."
LangString DESC_sec_odf ${LANG_Russian} "Библиотека для записи и чтения документов в формате OpenDocument для Python."
LangString DESC_sec_font ${LANG_Russian} "Чертежные шрифты."
LangString DESC_sec_office ${LANG_Russian} "Пакет офисных пргорамм LibreOffice."
LangString DESC_secgrp_main ${LANG_Russian} "Программа создания перечней элементов для схем выполненных в САПР KiCAD."
LangString DESC_sec_main ${LANG_Russian} "Установить программу создания перечней элементов для схем выполненных в САПР KiCAD."
LangString DESC_sec_settings ${LANG_Russian} "Установить файл параметров со значениями по умолчанию."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_python} $(DESC_sec_python)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_wx} $(DESC_sec_wx)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_odf} $(DESC_sec_odf)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_font} $(DESC_sec_font)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_office} $(DESC_sec_office)
	!insertmacro MUI_DESCRIPTION_TEXT ${secgrp_main} $(DESC_secgrp_main)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_main} $(DESC_sec_main)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_settings} $(DESC_sec_settings)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Function .onInit
	Push $0
	Push $1
	Push $2

	IntOp $0 ${SF_RO} | ${SF_SELECTED}
	SectionSetFlags ${sec_main} $0

	IfFileExists "$INSTDIR\settings.ini" +2
		SectionSetFlags ${sec_settings} ${SF_SELECTED}

	Var /GLOBAL min_python_version
	StrCpy $min_python_version "2.7.0"
	Var /GLOBAL max_python_version
	StrCpy $max_python_version "3.0.0"

	nsExec::ExecToStack 'python -V'
	Pop $1 ; status
	StrCmp "error" $1 enable_python
	Pop $2 ; version
	${StrRep} $1 $2 "Python " ""
	StrCpy $2 $1
	${VersionCompare} $min_python_version $2 $1
	IntCmp $1 1 enable_python python_ok 0
	${VersionCompare} $max_python_version $2 $1
	IntCmp $1 1 python_ok enable_python enable_python
	
	enable_python:
		SectionSetFlags ${sec_python} ${SF_SELECTED}
		SectionSetText ${sec_python} "Python 2.7.9"
	python_ok:

	Var /GLOBAL min_wx_version
	StrCpy $min_wx_version "2.8.0.0"

	nsExec::ExecToStack 'python -c "import wx; print wx.version()"'
	Pop $1 ; status
	StrCmp "error" $1 enable_wx
	Pop $2 ; version
	StrCpy $1 $2 7
	StrCpy $2 $1
	${VersionCompare} $min_wx_version $2 $1
	IntCmp $1 1 enable_wx wx_ok wx_ok
	
	enable_wx:
		SectionSetFlags ${sec_wx} ${SF_SELECTED}
		SectionSetText ${sec_wx} "wxPython 3.0.2.0"
	wx_ok:

	nsExec::ExecToStack 'python -c "import odf"'
	Pop $1 ; status
	StrCmp "error" $1 enable_odf
	Pop $2 ; output
	StrCpy $1 $2 9
	StrCmp "Traceback" $1 enable_odf
	Goto odf_ok
	
	enable_odf:
		SectionSetFlags ${sec_odf} ${SF_SELECTED}
		SectionSetText ${sec_odf} "Odfpy 0.9.6"
	odf_ok:

	IfFileExists "$FONTS\OpenGostTypeB-Regular.*tf" font_ok enable_font

	enable_font:
		SectionSetText ${sec_font} "OpenGostFont 0.3"
	font_ok:

	ClearErrors
	EnumRegKey $0 HKLM "SOFTWARE\LibreOffice" 0
	IfErrors 0 office_ok
		SectionSetText ${sec_office} "LibreOffice 4.4.2"
	office_ok:

	Pop $0
	Pop $1
	Pop $2
FunctionEnd

; ================================== Uninstaller ===============================

Section "un.kicadbom2spec" un_sec_main
	Delete "$INSTDIR\*.pyc"
	RMDir /r "$INSTDIR\bitmaps"
	RMDir /r "$INSTDIR\sample"
	Delete "$INSTDIR\COPYING"
	Delete "$INSTDIR\README"
	Delete "$INSTDIR\CHANGELOG"
	Delete "$INSTDIR\kicadsch.py"
	Delete "$INSTDIR\spec.py"
	Delete "$INSTDIR\pattern.ods"
	Delete "$INSTDIR\gui.py"
	Delete "$INSTDIR\kicadbom2spec.pyw"
	Delete "$INSTDIR\help_windows.pdf"
	Delete "$INSTDIR\uninstall.exe"
	RMDir /r "$SMPROGRAMS\kicadbom2spec"
SectionEnd

Section /o "un.settings.ini" un_sec_settings
	Delete "$INSTDIR\settings.ini"
	RMDir /r "$INSTDIR"
SectionEnd
	

LangString DESC_un_sec_main ${LANG_Russian} "Удалить файлы программы."
LangString DESC_un_sec_settings ${LANG_Russian} "Удалить файл параметров программы."

!insertmacro MUI_UNFUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT ${un_sec_main} $(DESC_un_sec_main)
	!insertmacro MUI_DESCRIPTION_TEXT ${un_sec_settings} $(DESC_un_sec_settings)
!insertmacro MUI_UNFUNCTION_DESCRIPTION_END

Function un.onInit
	push $0
	IntOp $0 ${SF_RO} | ${SF_SELECTED}
	SectionSetFlags ${un_sec_main} $0
	pop $0
FunctionEnd
