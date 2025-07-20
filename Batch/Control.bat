"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
rc.exe /fo mycpl.res mycpl.rc
cl.exe /LD mycpl.c mycpl.res mycpl.def /Fe file.cpl
"C:\Windows\System32\control.exe" file.cpl
