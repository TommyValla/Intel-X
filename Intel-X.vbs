Set WshShell = CreateObject("WScript.Shell")

WshShell.CurrentDirectory = "C:\Intel-X-git"

WshShell.Run "cmd.exe /c ""cd /d C:\Intel-X-git && """"C:\Users\tomma\AppData\Local\Python\pythoncore-3.14-64\python.exe"""" """"C:\Intel-X-git\main.py"""" > """"C:\Intel-X-git\launcher.log"""" 2>&1""", 0, True