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
  - Assignment: Devices only, NOT users. 
  - Platform: Windows 10 and later
  - Policy Type: Custom
  - Add OMA-URI Settings rule

**OMA-URI**

- The {Grouping} field can be assigned any string value, allowing users to create and define custom groups as needed.

```bash
./Vendor/MSFT/AppLocker/ApplicationLaunchRestrictions/{GROUPING}/EXE/Policy
```

**Basic XML String Value sample**

- The following XML rules represent a basic ruleset and should be carefully reviewed and enhanced to meet your organizational requirements before applying them to your Intune OMA-URI policy.

```xml
  <RuleCollection Type="Exe" EnforcementMode="NotConfigured">
    <FilePathRule Id="{GUID}" Name="(Default Rule) All files located in the Program Files folder" Description="Allows members of the Everyone group to run applications that are located in the Program Files folder." UserOrGroupSid="S-1-1-0" Action="Allow">
      <Conditions>
        <FilePathCondition Path="%PROGRAMFILES%\*" />
      </Conditions>
    </FilePathRule>
    <FilePathRule Id="{GUID}" Name="(Default Rule) All files located in the Windows folder" Description="Allows members of the Everyone group to run applications that are located in the Windows folder." UserOrGroupSid="S-1-1-0" Action="Allow">
      <Conditions>
        <FilePathCondition Path="%WINDIR%\*" />
      </Conditions>
    </FilePathRule>
    <FilePathRule Id="{GUID}" Name="(Default Rule) All files" Description="Allows members of the local Administrators group to run all applications." UserOrGroupSid="S-1-5-32-544" Action="Allow">
      <Conditions>
        <FilePathCondition Path="*" />
      </Conditions>
    </FilePathRule>
    <FilePublisherRule Id="{GUID}" Name="ADDINUTIL.EXE, in MICROSOFT® .NET FRAMEWORK, from O=MICROSOFT CORPORATION, L=REDMOND, S=WASHINGTON, C=US" Description="" UserOrGroupSid="S-1-1-0" Action="Deny">
      <Conditions>
        <FilePublisherCondition PublisherName="O=MICROSOFT CORPORATION, L=REDMOND, S=WASHINGTON, C=US" ProductName="MICROSOFT® .NET FRAMEWORK" BinaryName="ADDINUTIL.EXE">
          <BinaryVersionRange LowSection="*" HighSection="*" />
        </FilePublisherCondition>
      </Conditions>
    </FilePublisherRule>
  </RuleCollection>
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
