Set ws = CreateObject("Wscript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentFolder = fso.GetParentFolderName(WScript.ScriptFullName)
ws.CurrentDirectory = currentFolder

pythonwPath = "C:\Users\lzpgood\AppData\Local\Programs\Python\Python313\pythonw.exe"
If Not fso.FileExists(pythonwPath) Then
    pythonwPath = "pythonw.exe"
End If

ws.Run """" & pythonwPath & """ """ & currentFolder & "\main.py""", 0, False
