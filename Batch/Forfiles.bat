"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe" /LD "test.c" /link /DEF:"test.def"
"C:\Windows\System32\forfiles.exe" /p "C:\Windows\System32" /m "notepad.exe" /c "cmd /c rundll32 \"C:\Temp\ForFilesExploit\test.dll\",EntryPoint"
