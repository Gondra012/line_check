Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c uvicorn main:app --host 0.0.0.0 --port 8080", 0, False
WScript.Sleep 2000
WshShell.Run "cmd.exe /c start http://localhost:8080/", 0
