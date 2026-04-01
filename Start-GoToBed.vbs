' Start-GoToBed.vbs - Silent launcher for PowerShell script
Set objShell = CreateObject("WScript.Shell")
strPath = WScript.ScriptFullName
strFolder = Left(strPath, InStrRev(strPath, "\"))
objShell.Run "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & strFolder & "GoToBed.ps1"" -Hidden", 0, False
