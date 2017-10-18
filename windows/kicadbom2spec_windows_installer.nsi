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
; - Inetc

!include MUI2.nsh
!include WinMessages.nsh
!include Sections.nsh
!include StrFunc.nsh
${StrRep}
!include VersionCompare.nsh

!define /file VERSION "..\version"
!define PROG_NAME "kicadbom2spec"

!define DEPENDENCIES "..\..\windows_installer_dependencies\"
!define PYTHON "python-2.7.14.msi"
!define PYTHON_NAME "Python 2.7.14"
!define WXPYTHON "wxPython3.0-win32-3.0.2.0-py27.exe"
!define WXPYTHON_NAME "wxPython 3.0"
!define ODFPY "odfpy-1.3.5.tar.gz"
!define ODFPY_NAME "ODFpy 1.3.5"
!define FONT "opengostfont-ttf-0.3.zip"
!define FONT_NAME "Шрифт OpenGOST 0.3"
!define OFFICE "http://www.libreoffice.org/download/download/"
!define OFFICE_NAME "LibreOffice"

Var SETTINGS_DIR
Var KICAD_DIR
Var PYTHON_MODE

Name "kicadbom2spec"
OutFile "..\..\${PROG_NAME}_v${VERSION}_windows_installer.exe"
InstallDir "$PROGRAMFILES\${PROG_NAME}"
ComponentText "" "" "Выберите компоненты для установки (отметками помечены \
					 компоненты, отсутствующие в Вашей системе):"

RequestExecutionLevel admin
ShowInstDetails show
ShowUninstDetails show

!define MUI_COMPONENTSPAGE_SMALLDESC

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\COPYING"
!define MUI_PAGE_CUSTOMFUNCTION_PRE InitComponents
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

; =============================== Installer ===================================

SectionGroup /e "!Необходимые компоненты" secgrp_required
	Section /o "${PYTHON_NAME}" sec_python
		Push $0
		Push $1

		SetOutPath "$TEMP"
		File "${DEPENDENCIES}${PYTHON}"
		ExecWait 'msiexec /i "${PYTHON}" ADDLOCAL=ALL' $1
		IntCmp $1 0 +2
			Abort "Не удалось установить интерпретатор языка Python."
		Delete ${PYTHON}

		Pop $0
		Pop $1
	SectionEnd

	Section /o "Python из KiCad" sec_python_kicad
	SectionEnd

	Section /o "${WXPYTHON_NAME}" sec_wx
		Push $0
		Push $1

		SetOutPath "$TEMP"
		File "${DEPENDENCIES}${WXPYTHON}"
		ExecWait '"${WXPYTHON}"' $1
		IntCmp $1 0 +2
			Abort "Не удалось установоить библиотеку wxWidgets для Python."
		Delete ${WXPYTHON}

		Pop $0
		Pop $1
	SectionEnd

	Section /o "wxPython из KiCad" sec_wx_kicad
	SectionEnd

	Section /o "${ODFPY_NAME}" sec_odf
		Push $0
		Push $1

		!insertmacro SectionFlagIsSet ${sec_python} ${SF_SELECTED} 0 path_ok
		nsExec::ExecToStack 'python -V'
		Pop $1
		StrCmp "error" $1 0 path_ok
			ReadRegStr $1 HKLM \
				"SYSTEM\CurrentControlSet\Control\Session Manager\Environment" \
				"Path"
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
			Abort "Не удалось установоить библиотеку odfpy для Python."
		Delete ${ODFPY}

		Pop $0
		Pop $1
	SectionEnd

	Section /o "${ODFPY_NAME} для KiCad" sec_odf_kicad
		Push $0
		Push $1

		SetOutPath "$TEMP"
		File "${DEPENDENCIES}${ODFPY}"
		ExecWait "$KICAD_DIR\bin\pip --disable-pip-version-check install ./${ODFPY}" $1
		IntCmp $1 0 +2
			Abort "Не удалось установоить библиотеку odfpy для Python из KiCad."
		Delete ${ODFPY}

		Pop $0
		Pop $1
	SectionEnd
SectionGroupEnd

SectionGroup /e "Дополнительные компоненты" secgrp_optional
	Section /o "${FONT_NAME}" sec_font
		Push $0
		Push $1
		Push $R0
		Push $R1

		SetOutPath "$TEMP"
		File "${DEPENDENCIES}${FONT}"
		nsisunz::Unzip /noextractpath /file "opengostfont-ttf-0.3\OpenGostTypeA-Regular.ttf" ${FONT} "$FONTS"
		nsisunz::Unzip /noextractpath /file "opengostfont-ttf-0.3\OpenGostTypeB-Regular.ttf" ${FONT} "$FONTS"

		ReadRegStr $R0 HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion" "CurrentVersion"
		IfErrors win-9x win-NT

	win-NT:
		StrCpy $R1 "Software\Microsoft\Windows NT\CurrentVersion\Fonts"
		Goto font-add

	win-9x:
		StrCpy $R1 "Software\Microsoft\Windows\CurrentVersion\Fonts"
		Goto font-add

	font-add:
		StrCpy $0 "OpenGost Type A TT Regular (TrueType)"
		StrCpy $1 "OpenGost Type B TT Regular (TrueType)"
		System::Call "GDI32::AddFontResource(t '$FONTS\OpenGostTypeA-Regular.ttf')"
		System::Call "GDI32::AddFontResource(t '$FONTS\OpenGostTypeB-Regular.ttf')"
		WriteRegStr HKLM "$R1" "$0" "OpenGostTypeA-Regular.ttf"
		WriteRegStr HKLM "$R1" "$1" "OpenGostTypeB-Regular.ttf"
		SendMessage ${HWND_BROADCAST} ${WM_FONTCHANGE} 0 0 /TIMEOUT=5000
		Delete ${FONT}

		Pop $0
		Pop $1
		Pop $R0
		Pop $R1
	SectionEnd

	Section /o "${OFFICE_NAME}" sec_office
		Push $0
		Push $1

		MessageBox MB_OKCANCEL \
			"Для просмотра и редактирования перечней \
			элементов рекомендуется использовать свободный пакет офисных \
			приложений - LibreOffice. $\n $\n \
			Чтобы перейти к загрузке и установке LibreOffice нажмите OK." \
			IDCANCEL libreoffice_done
				ExecShell "open" "${OFFICE}"
		libreoffice_done:

		Pop $0
		Pop $1
	SectionEnd
SectionGroupEnd

SectionGroup /e "!${PROG_NAME}" secgrp_main
	Section "${PROG_NAME}" sec_main

		CreateDirectory "$INSTDIR\bitmaps"
		SetOutPath "$INSTDIR\bitmaps"
		File "..\bitmaps\*.*"

		CreateDirectory "$INSTDIR\doc"
		SetOutPath "$INSTDIR\doc"
		File "..\doc\user_manual.html"
		SetOutPath "$INSTDIR\doc\images"
		File "..\doc\images\*.*"

		CreateDirectory "$INSTDIR\sample"
		SetOutPath "$INSTDIR\sample"
		File "..\sample\*.*"

		SetOutPath $INSTDIR
		File "..\COPYING"
		File "..\README"
		File "..\CHANGELOG"
		File "..\complist.py"
		File "..\controls.py"
		File "..\kicadsch.py"
		File "..\settings.ini"
		File "..\pattern.ods"
		File "..\gui.py"
		File "..\kicadbom2spec.pyw"
		File "..\version"

		SetShellVarContext all
		CreateDirectory "$SMPROGRAMS\${PROG_NAME}"
		StrCmp $PYTHON_MODE "SYSTEM" 0 +3
			CreateShortCut \
				"$SMPROGRAMS\${PROG_NAME}\Запустить kicadbom2spec.lnk" \
				"$INSTDIR\kicadbom2spec.pyw" \
				"" \
				"$INSTDIR\bitmaps\icon.ico"
			Goto +2
			CreateShortCut \
				"$SMPROGRAMS\${PROG_NAME}\Запустить kicadbom2spec.lnk" \
				"$KICAD_DIR\bin\pythonw" \
				"$\"$INSTDIR\kicadbom2spec.pyw$\"" \
				"$INSTDIR\bitmaps\icon.ico"
		CreateShortCut \
			"$SMPROGRAMS\${PROG_NAME}\Руководство пользователя.lnk" \
			"$INSTDIR\doc\user_manual.html"
		CreateShortCut \
			"$SMPROGRAMS\${PROG_NAME}\Удалить kicadbom2spec.lnk" \
			"$INSTDIR\uninstall.exe"

		WriteRegStr "HKLM" \
			"Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
			"DisplayName" \
			"${PROG_NAME}"
		WriteRegStr "HKLM" \
			"Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
			"DisplayVersion" \
			"${VERSION}"
		WriteRegStr "HKLM" \
			"Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
			"DisplayIcon" \
			"$INSTDIR\bitmaps\icon.ico"
		WriteRegStr "HKLM" \
			"Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
			"InstallLocation" \
			"$INSTDIR"
		WriteRegStr "HKLM" \
			"Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
			"UninstallString" \
			"$INSTDIR\uninstall.exe"

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

LangString DESC_secgrp_required ${LANG_Russian} \
	"Перечисленные компоненты необходимы для работы программы kicadbom2spec."
LangString DESC_sec_python ${LANG_Russian} \
	"Интерпретатор языка Python."
LangString DESC_sec_python_kicad ${LANG_Russian} \
	"Интерпретатор языка Python из KiCad."
LangString DESC_sec_wx ${LANG_Russian} \
	"Обёртка библиотеки графического интерфейса пользователя \
	wxWidgets для Python."
LangString DESC_sec_wx_kicad ${LANG_Russian} \
	"Обёртка библиотеки графического интерфейса пользователя \
	wxWidgets для Python из KiCad."
LangString DESC_sec_odf ${LANG_Russian} \
	"Библиотека для записи и чтения документов в формате OpenDocument \
	для Python."
LangString DESC_sec_odf_kicad ${LANG_Russian} \
	"Библиотека для записи и чтения документов в формате OpenDocument \
	для Python из KiCad."
LangString DESC_secgrp_optional ${LANG_Russian} \
	"Перечисленные компоненты нужны для корректного отображения \
	перечней элементов."
LangString DESC_sec_font ${LANG_Russian} \
	"Чертежные шрифты."
LangString DESC_sec_office ${LANG_Russian} \
	"Пакет офисных пргорамм LibreOffice (для установки нужно подключение \
	к интернету)."
LangString DESC_secgrp_main ${LANG_Russian} \
	"Программа создания перечней элементов для схем выполненных \
	в САПР KiCad."
LangString DESC_sec_main ${LANG_Russian} \
	"Файлы программы создания перечней элементов для схем \
	выполненных в САПР KiCad."
LangString DESC_sec_settings ${LANG_Russian} \
	"Файл параметров со значениями по умолчанию."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT ${secgrp_required} $(DESC_secgrp_required)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_python} $(DESC_sec_python)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_python_kicad} $(DESC_sec_python_kicad)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_wx} $(DESC_sec_wx)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_wx_kicad} $(DESC_sec_wx_kicad)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_odf} $(DESC_sec_odf)
	!insertmacro MUI_DESCRIPTION_TEXT ${sec_odf_kicad} $(DESC_sec_odf_kicad)
	!insertmacro MUI_DESCRIPTION_TEXT ${secgrp_optional} $(DESC_secgrp_optional)
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

	StrCpy $SETTINGS_DIR "$APPDATA"

	ClearErrors
	ReadRegStr $0 HKLM \
		"Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
		"UninstallString"
	ReadRegStr $1 HKLM \
		"Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
		"DisplayVersion"
	IfErrors uninstalled 0
		IfFileExists "$0" 0 uninstalled
			MessageBox MB_YESNO|MB_ICONQUESTION \
			"На Вашем ПК уже установлена программа ${PROG_NAME} v$1.\
			$\n\
			Перед началом установки старую версию программы необходимо \
			удалить, чтобы избежать возможных проблем. \
			$\n$\n\
			Хотите удалить ее сейчас?" \
			IDYES uninstall_prev IDNO 0
				Quit
			uninstall_prev:
				ExecWait '"$0" _?=$INSTDIR'
	uninstalled:

	Pop $0
	Pop $1
	Pop $2
FunctionEnd

Function InitComponents
	Push $0
	Push $1
	Push $2

	StrCpy $KICAD_DIR ""
	ClearErrors
	ReadRegStr $0 HKLM \
		"Software\Microsoft\Windows\CurrentVersion\Uninstall\KiCad" \
		"InstallLocation"
	IfErrors kicad_no 0
		IfFileExists "$0\bin\pythonw.exe" 0 kicad_no
			StrCpy $KICAD_DIR $0
			MessageBox MB_YESNO|MB_ICONQUESTION \
			"На Вашем ПК установлен KiCad со встроенным интерпретатором \
			языка Python и библиотекой графического пользовательского \
			интерфейса wxWidgets. Эти компоненты необходимы для работы \
			программы kicadbom2spec и могут использоваться совместно. $\n\
			Хотите использовать эти компоненты из KiCad или установить их \
			отдельно? \
			$\n$\n \
			Нажмите ''Да'' чтобы использовать необходимые компоненты из \
			KiCad. \
			$\n$\n \
			Нажмите ''Нет'' чтобы установить необходимые компоненты отдельно." \
			IDYES kicad_yes IDNO kicad_no
			kicad_yes:
				StrCpy $PYTHON_MODE "KICAD"
				Goto kicad_end
			kicad_no:
				StrCpy $PYTHON_MODE "SYSTEM"
	kicad_end:

	IntOp $0 ${SF_RO} | ${SF_SELECTED}
	!insertmacro SetSectionFlag ${sec_main} $0

	IfFileExists "$SETTINGS_DIR\${PROG_NAME}\settings.ini" settings_exists
		!insertmacro SetSectionFlag ${sec_settings} ${SF_SELECTED}
	settings_exists:

	StrCmp $PYTHON_MODE "KICAD" check_required_kicad check_required_system

	check_required_kicad:
		SectionSetText ${sec_python} ""
		SectionSetText ${sec_wx} ""
		SectionSetText ${sec_odf} ""
		!insertmacro SetSectionFlag ${sec_python_kicad} ${SF_SELECTED}
		!insertmacro SetSectionFlag ${sec_python_kicad} ${SF_RO}
		!insertmacro SetSectionFlag ${sec_wx_kicad} ${SF_SELECTED}
		!insertmacro SetSectionFlag ${sec_wx_kicad} ${SF_RO}

		nsExec::ExecToStack '$KICAD_DIR\bin\python -c "import odf"'
		Pop $1 ; status
		StrCmp "error" $1 enable_odf_kicad
		Pop $2 ; output
		StrCpy $1 $2 9
		StrCmp "Traceback" $1 enable_odf_kicad odf_python_ok
		enable_odf_kicad:
			!insertmacro SetSectionFlag ${sec_odf_kicad} ${SF_SELECTED}
			!insertmacro SetSectionFlag ${sec_odf_kicad} ${SF_RO}
		odf_python_ok:

		Goto check_required_done

	check_required_system:
		SectionSetText ${sec_python_kicad} ""
		SectionSetText ${sec_wx_kicad} ""

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
			!insertmacro SetSectionFlag ${sec_python} ${SF_SELECTED}
			!insertmacro SetSectionFlag ${sec_python} ${SF_RO}
		python_ok:

		Var /GLOBAL min_wx_version
		StrCpy $min_wx_version "3.0.0.0"

		nsExec::ExecToStack 'python -c "import wx; print wx.version()"'
		Pop $1 ; status
		StrCmp "error" $1 enable_wx
		Pop $2 ; version
		StrCpy $1 $2 7
		StrCpy $2 $1
		${VersionCompare} $min_wx_version $2 $1
		IntCmp $1 1 enable_wx wx_ok wx_ok
		enable_wx:
			!insertmacro SetSectionFlag ${sec_wx} ${SF_SELECTED}
			!insertmacro SetSectionFlag ${sec_wx} ${SF_RO}
		wx_ok:

		nsExec::ExecToStack 'pip -c "import odf"'
		Pop $1 ; status
		StrCmp "error" $1 enable_odf
		Pop $2 ; output
		StrCpy $1 $2 9
		StrCmp "Traceback" $1 enable_odf odf_ok
		enable_odf:
			!insertmacro SetSectionFlag ${sec_odf} ${SF_SELECTED}
			!insertmacro SetSectionFlag ${sec_odf} ${SF_RO}
		odf_ok:

		# Если присутствует KiCad с интегрированным Pyhton и выбрана установка
		# отдельной версией Python (PYTHON_MODE=SYSTEM) все равно нужно
		# устновить ODFpy для встроенного в KiCad Python'a. Иначе будет
		# невозможно использовать kicadbom2spec в качестве BOM плагина.
		StrCmp KICAD_DIR "" disable_odf_bom 0
			nsExec::ExecToStack '$KICAD_DIR\bin\python -c "import odf"'
			Pop $1 ; status
			StrCmp "error" $1 enable_odf_bom
			Pop $2 ; output
			StrCpy $1 $2 9
			StrCmp "Traceback" $1 enable_odf_bom disable_odf_bom
			enable_odf_bom:
				MessageBox MB_OK|MB_ICONINFORMATION \
					"Для работы программы ${PROG_NAME} в качестве BOM \
					плагина нужно установить модуль ODFpy для Python из KiCad."
				!insertmacro SetSectionFlag ${sec_odf_kicad} ${SF_SELECTED}
				Goto odf_bom_end
			disable_odf_bom:
				SectionSetText ${sec_odf_kicad} ""
			odf_bom_end:

	check_required_done:

	ClearErrors
	ReadRegStr $0 HKLM \
		"SOFTWARE\Microsoft\Windows NT\CurrentVersion" \
		"CurrentVersion"
	IfErrors win-9x win-NT
	win-NT:
		StrCpy $1 "Software\Microsoft\Windows NT\CurrentVersion\Fonts"
		Goto win-ok
	win-9x:
		StrCpy $1 "Software\Microsoft\Windows\CurrentVersion\Fonts"
		Goto win-ok
	win-ok:

	ClearErrors
	ReadRegStr $0 HKLM $1 "OpenGost Type A TT Regular (TrueType)"
	ReadRegStr $0 HKLM $1 "OpenGost Type B TT Regular (TrueType)"
	IfErrors 0 font_ok
		!insertmacro SetSectionFlag ${sec_font} ${SF_SELECTED}
	font_ok:

	ClearErrors
	EnumRegKey $0 HKLM "SOFTWARE\LibreOffice" 0
	IfErrors 0 office_ok
		!insertmacro SetSectionFlag ${sec_office} ${SF_SELECTED}
	office_ok:

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
	!insertmacro SetSectionFlag ${un_sec_main} $0
	pop $0
FunctionEnd
