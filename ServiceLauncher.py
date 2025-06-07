from datetime import datetime
from threading import Thread
import tkinter as tk
from tkinter import ttk, font as tkFont
import subprocess
import re

# Define services and ports
services = {
    "MetaDataService": {"path": r"C:\Users\PakinPaulRaj\Desktop\Forvis Mazars\azure\backend-forvis\src\MetaDataService\MetaDataService.API", "runnable": True, "port": 5080},
    "IdentityService": {"path": r"C:\Users\PakinPaulRaj\Desktop\Forvis Mazars\azure\backend-forvis\src\IdentityService\IdentityService.API", "runnable": True, "port": 5171},
    "ClientService": {"path": r"C:\Users\PakinPaulRaj\Desktop\Forvis Mazars\azure\backend-forvis\src\ClientService\ClientService.API", "runnable": True, "port": 5259},
    "BFFService": {"path": r"C:\Users\PakinPaulRaj\Desktop\Forvis Mazars\azure\backend-forvis\src\BFFService\BFFService.API", "runnable": True, "port": 5258},
    "APIGateway": {"path": r"C:\Users\PakinPaulRaj\Desktop\Forvis Mazars\azure\backend-forvis\src\APIGateway\ForvisMazars.APIGateway", "runnable": True, "port": 5006},
    "Angular Frontend": {"path": r"C:\Users\PakinPaulRaj\Desktop\Forvis Mazars\azure\frontend-forvis", "runnable": True, "port": 4200},
    "Backend Root Build Only": {"path": r"C:\Users\PakinPaulRaj\Desktop\Forvis Mazars\azure\backend-forvis", "runnable": False, "port": None}
}

running_processes = {}

# GUI setup
root = tk.Tk()
root.title("Service Launcher")
root.geometry("1050x900")
root.configure(bg="#eeeeee")

# Fonts
default_font = tkFont.Font(family="Segoe UI", size=9)
title_font = tkFont.Font(family="Segoe UI", size=16, weight="bold")
button_font = tkFont.Font(family="Segoe UI", size=9, weight="bold")

# Title
title_frame = tk.Frame(root, bg="#f5f5f5", pady=8)
title_frame.pack(fill="x", padx=10)
tk.Label(title_frame, text="Run Services", font=title_font, bg="#f5f5f5", fg="#333").pack(side="left")
tk.Label(title_frame, text="Created by Pakin", font=default_font, fg="gray", bg="#f5f5f5").pack(side="right")

tab_notebook = ttk.Notebook(root)
tab_notebook.pack(expand=True, fill='both', pady=10)
log_tabs = {}

# ANSI cleanup
ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
def clean_ansi(text): return ansi_escape.sub('', text)

def get_or_create_log_tab(service_name):
    if service_name not in log_tabs:
        frame = tk.Frame(tab_notebook)
        top_bar = tk.Frame(frame, bg="gray20")
        top_bar.pack(fill="x")
        tk.Label(top_bar, text=service_name, fg="white", bg="gray20", font=("Segoe UI", 10, "bold")).pack(side="left", padx=8)
        tk.Button(top_bar, text="✖", command=lambda: close_tab(service_name, frame), bg="red", fg="white", font=button_font).pack(side="right", padx=5)

        log_frame = tk.Frame(frame)
        log_frame.pack(expand=True, fill='both')

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")

        text_area = tk.Text(log_frame, height=20, bg="black", fg="lime", font=("Courier", 9),
                            yscrollcommand=scrollbar.set, wrap="word")
        text_area.pack(expand=True, fill='both')
        scrollbar.config(command=text_area.yview)

        tab_notebook.add(frame, text=service_name)
        log_tabs[service_name] = text_area
    return log_tabs[service_name]

def close_tab(service_name, frame):
    index = tab_notebook.index(frame)
    tab_notebook.forget(index)
    log_tabs.pop(service_name, None)

def log_to_tab(service_name, message):
    timestamp = datetime.now().strftime("[%H:%M:%S] ")
    text_area = get_or_create_log_tab(service_name)
    text_area.insert(tk.END, timestamp + message + "\n")
    text_area.see(tk.END)

def stream_output(process, service_name):
    log_to_tab(service_name, f"🔁 Started: {service_name}")
    def read_stdout():
        for line in process.stdout:
            cleaned = clean_ansi(line.decode("utf-8", errors="ignore").rstrip())
            log_to_tab(service_name, cleaned)
            if "http://" in cleaned or "Local:" in cleaned:
                log_to_tab(service_name, f"🌐 {cleaned}")
    def read_stderr():
        for err in process.stderr:
            cleaned = clean_ansi(err.decode("utf-8", errors="ignore").rstrip())
            log_to_tab(service_name, f"❌ {cleaned}")
    Thread(target=read_stdout, daemon=True).start()
    Thread(target=read_stderr, daemon=True).start()

def find_and_kill_port(port):
    try:
        result = subprocess.run(f'netstat -aon | findstr :{port}', capture_output=True, shell=True, text=True)
        for line in result.stdout.strip().splitlines():
            if "LISTENING" in line:
                pid = re.split(r"\s+", line.strip())[-1]
                subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                return pid
    except Exception as e:
        print(f"[ERROR] Port cleanup failed: {e}")
        return None

def run_service(name):
    port = services[name].get("port")
    if port:
        pid = find_and_kill_port(port)
        if pid:
            log_to_tab(name, f"⚡ Killed existing process on port {port} (PID: {pid})")
    path = services[name]["path"]
    command = ["cmd", "/c", "ng serve"] if "Frontend" in name else ["dotnet", "run"]
    try:
        process = subprocess.Popen(command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        running_processes[name] = process
        Thread(target=stream_output, args=(process, name), daemon=True).start()
    except Exception as e:
        log_to_tab(name, f"❌ Failed to start process: {e}")

def build_service(name):
    path = services[name]["path"]
    command = ["cmd", "/c", "ng build"] if "Frontend" in name else ["dotnet", "build"]
    try:
        log_to_tab(name, f"🛠️ Starting build for {name}...")
        process = subprocess.Popen(command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        Thread(target=stream_output, args=(process, name), daemon=True).start()
    except Exception as e:
        log_to_tab(name, f"❌ Build failed: {e}")

def kill_service(name):
    process = running_processes.get(name)
    if process and process.poll() is None:
        process.terminate()
        log_to_tab(name, f"❌ Terminated: {name}")
        del running_processes[name]
    else:
        log_to_tab(name, f"⚠️ No running process found for '{name}'.")
    port = services[name].get("port")
    if port:
        pid = find_and_kill_port(port)
        if pid:
            log_to_tab(name, f"⚡ Also killed process on port {port} (PID: {pid})")

# Service buttons layout
service_frame = tk.Frame(root, bg="#eeeeee")
service_frame.pack(pady=10)

columns = 4
row = 0
col = 0

for service in services:
    group = tk.Frame(service_frame, padx=10, pady=10, bd=1, relief=tk.RIDGE, bg="#ffffff")
    group.grid(row=row, column=col, padx=10, pady=10)
    tk.Label(group, text=service, font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#333333").pack(pady=(0, 5))

    btn_row = tk.Frame(group, bg="#ffffff")
    btn_row.pack()

    if services[service]["runnable"]:
        tk.Button(btn_row, text="▶ Run", width=6, font=button_font, command=lambda s=service: run_service(s),
                  bg="#28a745", fg="white", activebackground="#218838", relief=tk.FLAT).pack(side="left", padx=4)

    tk.Button(btn_row, text="🔨 Build", width=6, font=button_font, command=lambda s=service: build_service(s),
              bg="#17a2b8", fg="white", activebackground="#117a8b", relief=tk.FLAT).pack(side="left", padx=4)

    tk.Button(btn_row, text="❌ Kill", width=6, font=button_font, command=lambda s=service: kill_service(s),
              bg="#dc3545", fg="white", activebackground="#bd2130", relief=tk.FLAT).pack(side="left", padx=4)

    col += 1
    if col == columns:
        col = 0
        row += 1

print("[UI] Launcher initialized. Ready.")
root.mainloop()
