Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the project folder (where this script is)
scriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Get Desktop path
desktopPath = objShell.SpecialFolders("Desktop")

' Create shortcut
Set objLink = objShell.CreateShortcut(desktopPath & "\📊 Fraud Detection Dashboard.lnk")
objLink.TargetPath = scriptPath & "\RUN_DASHBOARD.bat"
objLink.WorkingDirectory = scriptPath
objLink.Description = "Launch Financial Fraud Detection Dashboard"
objLink.IconLocation = "C:\Windows\System32\imageres.dll,71"  ' Shield icon
objLink.Save

' Show confirmation
objShell.Popup "✅ Desktop shortcut created!" & vbCrLf & vbCrLf & _
    "Now you can double-click '📊 Fraud Detection Dashboard' on your Desktop to launch it.", _
    5, "Success", 64
