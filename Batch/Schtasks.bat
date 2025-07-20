schtasks /Create /TN MyTask /TR "cmd /c C:\Windows\System32\calc.exe" /SC DAILY /F

schtasks /Create /TN MyTask /TR "cmd /c C:\Windows\System32\calc.exe" /SC DAILY /F /RL HIGHEST
