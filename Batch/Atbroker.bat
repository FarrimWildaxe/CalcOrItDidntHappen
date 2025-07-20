reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Accessibility\ATs\Calculator" /v Name /t REG_SZ /d Calculator /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Accessibility\ATs\Calculator" /v CommandLine /t REG_SZ /d "C:\Windows\System32\calc.exe" /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Accessibility\ATs\Calculator" /v Integration /t REG_DWORD /d 1 /f

C:\Windows\System32\AtBroker.exe /start Calculator
