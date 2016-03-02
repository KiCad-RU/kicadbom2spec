;;; BEGIN LICENSE
; Copyright (C) 2016 Baranovskiy Konstantin (baranovskiykonstantin@gmail.com)
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
; - NSISunzU

!include MUI2.nsh
!include WinMessages.nsh
!include StrFunc.nsh
${StrRep}

!define /file VERSION "..\version"
!define PROG_NAME "kicadbom2spec"
!define DEPENDENCIES "..\..\windows_installer_dependencies\"
!define PYTHON "python-2.7.11.msi"
!define WXPYTHON "wxPython3.0-win32-3.0.2.0-py27.exe"
!define ODFPY "odfpy-1.3.2.tar.gz"
!define FONT "opengostfont-ttf-0.3.zip"
Var SETTINGS_DIR

Name "kicadbom2spec"
OutFile "..\..\${PROG_NAME}_v${VERSION}_windows_installer_full.exe"
InstallDir "$PROGRAMFILES\${PROG_NAME}"

RequestExecutionLevel admin
ShowInstDetails show
ShowUninstDetails show

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

	SetOutPath "$TEMP"
	File "${DEPENDENCIES}${PYTHON}"
	ExecWait 'msiexec /i "${PYTHON}" ADDLOCAL=ALL' $1
	IntCmp $1 0 +2
		Abort "Не удалось установить интерпретатор \
		языка Python."
	Delete ${PYTHON}

	skip_install:

	Pop $0
	Pop $1
SectionEnd

Section "" sec_wx
	Push $0
	Push $1

	SectionGetText ${sec_wx} $0
	StrCmp $0 "" skip_install

	SetOutPath "$TEMP"
	File "${DEPENDENCIES}${WXPYTHON}"
	ExecWait '"${WXPYTHON}"' $1
	IntCmp $1 0 +2
		Abort "Не удалось установоить библиотеку \
		wxWidgets для Python."
	Delete ${WXPYTHON}

	skip_install:

	Pop $0
	Pop $1
SectionEnd

Section "" sec_odf
	Push $0
	Push $1

	SectionGetText ${sec_odf} $0
	StrCmp $0 "" skip_install

	SectionGetText ${sec_python} $0
	StrCmp $0 "" path_ok
	nsExec::ExecToStack 'python -V'
	Pop $1
	StrCmp "error" $1 0 path_ok
		ReadRegStr $1 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
		System::Call 'Kernel32::SetEnvironmentVariable(t "PATH", t "$1")i'
		nsExec::ExecToStack 'python -V'
		Pop $1
		StrCmp "error" $1 0 path_ok
			Abort "Невозможно установить odfpy, так как Python \
			не установлен или установлен не верно."

	path_ok:

	nsExec::ExecToStack 'pip --version'
	Pop $1
	StrCmp "error" $1 0 pip_ok
		Abort "Невозможно установить odfpy, так как Python \
		установлен не верно (отсутствует модуль pip)."

	pip_ok:

	SetOutPath "$TEMP"
	File "${DEPENDENCIES}${ODFPY}"
	ExecWait "pip --disable-pip-version-check install ./${ODFPY}" $1
	IntCmp $1 0 +2
		Abort "Не удалось установоить библиотеку \
		odfpy для Python."
	Delete ${ODFPY}

	skip_install:

	Pop $0
	Pop $1
SectionEnd

Section /o "" sec_font
	Push $0
	Push $1
	Push $R0
	Push $R1

	SectionGetText ${sec_font} $0
	StrCmp $0 "" skip_install

	SetOutPath "$TEMP"
	File "${DEPENDENCIES}${FONT}"
	nsisunz::Unzip /noextractpath /file "opengostfont-ttf-0.3\OpenGostTypeA-Regular.ttf" ${FONT} "$FONTS"
	nsisunz::Unzip /noextractpath /file "opengostfont-ttf-0.3\OpenGostTypeB-Regular.ttf" ${FONT} "$FONTS"

	ReadRegStr $R0 HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion" "CurrentVersion"
	IfErrors win-9x win-NT

win-NT:
	StrCpy $R1 "Software\Microsoft\Windows NT\CurrentVersion\Fonts"
	goto font-add

win-9x:
	StrCpy $R1 "Software\Microsoft\Windows\CurrentVersion\Fonts"
	goto font-add

font-add:
	StrCpy $0 "OpenGost Type A TT Regular (TrueType)"
	StrCpy $1 "OpenGost Type B TT Regular (TrueType)"
	System::Call "GDI32::AddFontResource(t '$FONTS\OpenGostTypeA-Regular.ttf')"
	System::Call "GDI32::AddFontResource(t '$FONTS\OpenGostTypeB-Regular.ttf')"
	WriteRegStr HKLM "$R1" "$0" "OpenGostTypeA-Regular.ttf"
	WriteRegStr HKLM "$R1" "$1" "OpenGostTypeB-Regular.ttf"
	SendMessage ${HWND_BROADCAST} ${WM_FONTCHANGE} 0 0 /TIMEOUT=5000
	Delete ${FONT}

	skip_install:

	Pop $0
	Pop $1
	Pop $R0
	Pop $R1
SectionEnd

SectionGroup /e "!${PROG_NAME}" secgrp_main
	Section "${PROG_NAME}" sec_main

		CreateDirectory "$INSTDIR\bitmaps"
		SetOutPath "$INSTDIR\bitmaps"
		File "..\bitmaps\*.*"

		CreateDirectory "$INSTDIR\doc"
		SetOutPath "$INSTDIR\doc"
		File "..\doc\help_windows.pdf"

		CreateDirectory "$INSTDIR\sample"
		SetOutPath "$INSTDIR\sample"
		File "..\sample\*.*"

		SetOutPath $INSTDIR
		File "..\COPYING"
		File "..\README"
		File "..\CHANGELOG"
		File "..\complist.py"
		File "..\kicadsch.py"
		File "..\settings.ini"
		File "..\pattern.ods"
		File "..\gui.py"
		File "..\kicadbom2spec.pyw"
		File "..\version"

		SetShellVarContext all
		CreateDirectory "$SMPROGRAMS\${PROG_NAME}"
		CreateShortCut \
			"$SMPROGRAMS\${PROG_NAME}\Запустить kicadbom2spec.lnk" "$INSTDIR\kicadbom2spec.pyw" \
			"" \
			"$INSTDIR\bitmaps\icon.ico"
		CreateShortCut \
			"$SMPROGRAMS\${PROG_NAME}\Руководство пользователя.lnk" \
			"$INSTDIR\doc\help_windows.pdf"
		CreateShortCut \
			"$SMPROGRAMS\${PROG_NAME}\Удалить kicadbom2spec.lnk" \
			"$INSTDIR\uninstall.exe"

		WriteRegStr "HKLM" "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" "DisplayName" "${PROG_NAME}"
		WriteRegStr "HKLM" "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" "DisplayVersion" "${VERSION}"
		WriteRegStr "HKLM" "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" "DisplayIcon" "$INSTDIR\bitmaps\icon.ico"
		WriteRegStr "HKLM" "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" "InstallLocation" "$INSTDIR"
		WriteRegStr "HKLM" "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"

		WriteUninstaller "uninstall.exe"
	SectionEnd

	Section /o "settings.ini" sec_settings
		SetOutPath "$SETTINGS_DIR"
		RMDir /r "${PROG_NAME}"
		CreateDirectory "${PROG_NAME}"
		SetOutPath "$SETTINGS_DIR\${PROG_NAME}"
		File "..\settings.ini"
	SectionEnd
SectionGroupEnd

LangString DESC_sec_python ${LANG_Russian} \
	"Интерпретатор языка Python."
LangString DESC_sec_wx ${LANG_Russian} \
	"Обёртка библиотеки кроссплатформенного графического интерфейса \
	пользователя wxWidgets для Python."
LangString DESC_sec_odf ${LANG_Russian} \
	"Библиотека для записи и чтения документов в формате OpenDocument \
	для Python."
LangString DESC_sec_font ${LANG_Russian} \
	"Чертежные шрифты."
LangString DESC_secgrp_main ${LANG_Russian} \
	"Программа создания перечней элементов для схем выполненных \
	в САПР KiCAD."
LangString DESC_sec_main ${LANG_Russian} \
	"Установить программу создания перечней элементов для схем \
	выполненных в САПР KiCAD."
LangString DESC_sec_settings ${LANG_Russian} \
	"Установить файл параметров со значениями по умолчанию."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_python} $(DESC_sec_python)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_wx} $(DESC_sec_wx)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_odf} $(DESC_sec_odf)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_font} $(DESC_sec_font)
	!insertmacro MUI_DESCRIPTION_TEXT ${secgrp_main} $(DESC_secgrp_main)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_main} $(DESC_sec_main)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_settings} $(DESC_sec_settings)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Function .onInit
	Push $0
	Push $1
	Push $2

	StrCpy $SETTINGS_DIR "$APPDATA"

	IntOp $0 ${SF_RO} | ${SF_SELECTED}
	SectionSetFlags ${sec_main} $0

	IfFileExists "$SETTINGS_DIR\${PROG_NAME}\settings.ini" +2
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
		SectionSetText ${sec_python} "Python 2.7.11"
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
		SectionSetText ${sec_odf} "Odfpy 1.3.2"
	odf_ok:

	ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion" "CurrentVersion"
	IfErrors win-9x win-NT

win-NT:
	StrCpy $1 "Software\Microsoft\Windows NT\CurrentVersion\Fonts"
	goto font-check

win-9x:
	StrCpy $1 "Software\Microsoft\Windows\CurrentVersion\Fonts"
	goto font-check

font-check:
	ClearErrors
	ReadRegStr $0 HKLM $1 "OpenGost Type A TT Regular (TrueType)"
	ReadRegStr $0 HKLM $1 "OpenGost Type B TT Regular (TrueType)"
	IfErrors 0 font_ok
		SectionSetText ${sec_font} "OpenGostFont 0.3"
	font_ok:

	Pop $0
	Pop $1
	Pop $2
FunctionEnd

; ================================= Uninstaller ===============================

Section "un.kicadbom2spec" un_sec_main
	RMDir /r "$INSTDIR"
	SetShellVarContext all
	RMDir /r "$SMPROGRAMS\${PROG_NAME}"
	DeleteRegKey "HKLM" "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}"
SectionEnd

Section /o "un.settings.ini" un_sec_settings
	RMDir /r "$SETTINGS_DIR\${PROG_NAME}"
SectionEnd


LangString DESC_un_sec_main ${LANG_Russian} \
	"Удалить файлы программы."
LangString DESC_un_sec_settings ${LANG_Russian} \
	"Удалить файл параметров программы."

!insertmacro MUI_UNFUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT ${un_sec_main} $(DESC_un_sec_main)
	!insertmacro MUI_DESCRIPTION_TEXT ${un_sec_settings} $(DESC_un_sec_settings)
!insertmacro MUI_UNFUNCTION_DESCRIPTION_END

Function un.onInit
	push $0

	StrCpy $SETTINGS_DIR "$APPDATA"

	IntOp $0 ${SF_RO} | ${SF_SELECTED}
	SectionSetFlags ${un_sec_main} $0
	pop $0
FunctionEnd
