Function ConnectInternet

	Push $R0

	ClearErrors
	Dialer::AttemptConnect
	IfErrors noie3

	Pop $R0
	StrCmp $R0 "online" connected
		MessageBox MB_OK|MB_ICONSTOP \
		"Невозможно подключиться к интернету."
		Quit

	noie3:

	; IE3 not installed
	MessageBox MB_OK|MB_ICONINFORMATION \
	"Пожалуйста, подключитесь к интернету."

	connected:

	Pop $R0

FunctionEnd
