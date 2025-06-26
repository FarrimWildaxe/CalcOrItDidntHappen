# Calc Or It Didn't Happen

This repo showcases practical PoCs using LOLBAS techniques to execute commands without dropping malware. Whether you're a red teamer, researcher, or just here for the chaos, you’ll find "weaponized" LOL moments and harmless-looking binaries doing suspiciously powerful things or not.

💻 Built for demos.

🎩 Powered by misused trust.

🔍 Monitored by defenders (hopefully).

💣 Triggered by AddInUtil, msbuild, certutil, and friends.

---

## RED

### AddinUtil.py

- https://github.com/pwntester/ysoserial.net

```bash
python3 AddinUtil.py
```

---

## BLUE

### Microsoft Intune Configuration - Blocking Unwanted Executables

- Microsoft Intune admin center -> Devices -> Configuration -> New Policy
  - Platform: Windows 10 and later
  - Policy Type: Custom
  - Add OMA-URI Settings rule

**OMA-URI**

```bash
./Vendor/MSFT/AppLocker/ApplicationLaunchRestrictions
```

**String Value sample**

```xml
<AppLockerPolicy Version="1">
  <RuleCollection Type="Exe" EnforcementMode="Enabled">
    <FilePathRule Id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" Name="Block AddInUtil.exe" Description="" UserOrGroupSid="S-1-1-0" Action="Deny">
      <Conditions>
        <FilePathCondition Path="C:\Windows\Microsoft.NET\Framework\v4.0.30319\AddInUtil.exe" />
      </Conditions>
    </FilePathRule>
  </RuleCollection>
</AppLockerPolicy>
```

### Create AppLockerPolicy XML files

*Create your AppLocker policy in a lab machine via secpol.msc or GPO, export to XML, and deploy it.*

- Windows Key + R
- secpol.msc
- Application Control Policies -> AppLocker -> Executable Rules -> Create new Rule
  - Permissions Action: Deny
  - Conditions: Path or File hash
- Right click on AppLocker -> Export Policy

---

## Useful links

- https://lolbas-project.github.io/
- https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/design/applications-that-can-bypass-appcontrol
- https://learn.microsoft.com/en-us/windows/client-management/mdm/applocker-csp
- https://intune.microsoft.com/

---
