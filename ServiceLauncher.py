import csv
import re
import subprocess
from datetime import datetime
from threading import Thread
import tkinter as tk
from tkinter import ttk, font as tkFont, messagebox
from tokenize import group
import json

class ServiceLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Service Launcher")
        self.root.state("zoomed")
        self.root.configure(bg="#eeeeee")
        self.root.bind_all("<Control-f>", self._global_ctrl_f)
        


        self.default_font = tkFont.Font(family="Segoe UI", size=9)
        self.title_font = tkFont.Font(family="Segoe UI", size=16, weight="bold")
        self.button_font = tkFont.Font(family="Segoe UI", size=9, weight="bold")

        self.services = self.load_services()
        self.running_processes = {}
        self.log_tabs = {}

        self.setup_ui()
    def _global_ctrl_f(self, event):
        current_tab = self.tab_notebook.select()
        tab_index = self.tab_notebook.index(current_tab)
        service_name = self.tab_notebook.tab(tab_index, "text")
        if service_name in self.log_tabs:
            self.show_find_popup(self.log_tabs[service_name])


    # def load_services(self):
    #     services = {}
    #     with open("services.csv", newline='', encoding="utf-8") as csvfile:
    #         reader = csv.DictReader(csvfile)
    #         for row in reader:
    #             name = row["name"]
    #             path = row["path"]
    #             runnable = row["runnable"].strip().lower() == "true"
    #             port = int(row["port"]) if row["port"].strip() else None
    #             services[name] = {"path": path, "runnable": runnable, "port": port}
    #     return services

    def load_services(self):
        try:
            with open("services.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    item["name"]: {
                        "path": item["path"],
                        "runnable": item["runnable"],
                        "port": int(item["port"]) if item["port"] else None
                    } for item in data
                }
        except:
            return {}

    def display_ascii_terminal_intro(self, widget):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)

        # ASCII Logo (editable)
        ascii_logo = r"""
        ___           ___           ___     
        /\__\         /\  \         /\__\    
        /:/  /        /::\  \       /::|  |   
    /:/  /        /:/\:\  \     /:|:|  |   
    /:/  /  ___   /::\~\:\  \   /:/|:|  |__ 
    /:/__/  /\__\ /:/\:\ \:\__\ /:/ |:| /\__\
    \:\  \ /:/  / \:\~\:\ \/__/ \/__|:|/:/  /
    \:\  /:/  /   \:\ \:\__\       |:/:/  / 
    \:\/:/  /     \:\ \/__/       |::/  /  
        \::/  /       \:\__\         /:/  /   
        \/__/         \/__/         \/__/    
        """

        installed_services = sorted(self.services.keys())

        intro_lines = [
            ascii_logo,
            "",
            "🔧 Welcome to Service Launcher Terminal",
            "----------------------------------------",
            "[INFO] Preparing environment...",
            "[INFO] Loading service metadata...",
            "[GIT] ✔ All services are synced with origin/main",
            "",
            "📦 Installed Services:",
        ] + [f"   • {service}" for service in installed_services] + [
            "",
            "💡 Tip: Use ▶ Run, 🔨 Build or ❌ Kill to manage services.",
            f"{chr(0x276F)} Press Ctrl+F to search inside logs.",
            "",
            "🚀 Created by Pakin | v1.0.0"
        ]


        # Optional syntax-style tags
        widget.tag_config("info", foreground="cyan")
        widget.tag_config("git", foreground="magenta")
        widget.tag_config("tip", foreground="yellow")
        widget.tag_config("header", foreground="lime", font=("Courier", 10, "bold"))

        def type_line(line_index=0, char_index=0):
            if line_index < len(intro_lines):
                line = intro_lines[line_index]
                tag = None

                if "[INFO]" in line:
                    tag = "info"
                elif "[GIT]" in line:
                    tag = "git"
                elif "Tip:" in line or "▶" in line:
                    tag = "tip"
                elif "Welcome" in line or "---" in line:
                    tag = "header"

                if char_index < len(line):
                    widget.insert(tk.END, line[char_index], tag)
                    widget.see(tk.END)
                    widget.after(5, lambda: type_line(line_index, char_index + 1))
                else:
                    widget.insert(tk.END, "\n", tag)
                    widget.after(100, lambda: type_line(line_index + 1, 0))
            else:
                widget.config(state="disabled")

        type_line()


    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg="#f5f5f5", pady=8)
        title_frame.pack(fill="x", padx=10)
        tk.Label(title_frame, text="Run Services", font=self.title_font, bg="#f5f5f5", fg="#333").pack(side="left")
        tk.Label(title_frame, text="Created by Pakin", font=self.default_font, fg="gray", bg="#f5f5f5").pack(side="right")

        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=6, bg="#cccccc")
        self.paned_window.pack(fill="both", expand=True, pady=10)

        # Terminal Tabs (Left)
        self.tab_notebook = ttk.Notebook(self.paned_window)
        self.paned_window.add(self.tab_notebook, stretch="always", minsize=1000)


        # ✅ Add a default tab on launch
        welcome_frame = tk.Frame(self.tab_notebook)
        welcome_text = tk.Text(welcome_frame, bg="black", fg="white", font=("Courier", 9), wrap="word")
        welcome_text.insert(tk.END, "🔧 Logs will appear here when you run a service.\n")
        welcome_text.config(state="disabled")
        self.display_ascii_terminal_intro(welcome_text)
        welcome_text.pack(expand=True, fill="both")
        self.tab_notebook.add(welcome_frame, text="Welcome")

        # Right Panel with scrollable canvas
        right_panel = tk.Frame(self.paned_window, bg="#eeeeee")
        self.paned_window.add(right_panel, minsize=350)

        canvas = tk.Canvas(right_panel, bg="#eeeeee", borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#eeeeee")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Independent scroll logic for right panel
        def _on_mousewheel_right(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel_right))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))


        # Scroll with mousewheel
        # Independent scroll logic for right panel
        def _on_mousewheel_right(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel_right))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))


        self.service_frame = self.scrollable_frame
        self.create_service_buttons()
        self.create_nav_buttons(self.scrollable_frame)

        # ✅ Scroll to top on launch
        self.root.after(100, lambda: canvas.yview_moveto(0))



    def create_service_buttons(self):
        for widget in self.service_frame.winfo_children():
            widget.destroy()

        for row, service in enumerate(self.services):
            container = tk.Frame(self.service_frame, bg="#eeeeee")
            container.pack(anchor="center", pady=5)
            group = tk.Frame(container, padx=10, pady=10, bd=1, relief=tk.RIDGE, bg="#ffffff")
            group.pack()
            group.configure(width=280)
 # Adjust width as needed for all buttons to fit


            tk.Label(group, text=service, font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#333333").pack(anchor="w")

            btn_row = tk.Frame(group, bg="#ffffff")
            btn_row.pack(anchor="w", pady=4)

            if self.services[service]["runnable"]:
                tk.Button(btn_row, text="▶ Run", width=8, font=self.button_font,
                        command=lambda s=service: self.run_service(s),
                        bg="#28a745", fg="white", activebackground="#218838", relief=tk.FLAT).pack(side="left", padx=2)

            tk.Button(btn_row, text="🔨 Build", width=8, font=self.button_font,
                    command=lambda s=service: self.build_service(s),
                    bg="#17a2b8", fg="white", activebackground="#117a8b", relief=tk.FLAT).pack(side="left", padx=2)

            tk.Button(btn_row, text="❌ Kill", width=8, font=self.button_font,
                    command=lambda s=service: self.kill_service(s),
                    bg="#dc3545", fg="white", activebackground="#bd2130", relief=tk.FLAT).pack(side="left", padx=2)

    def create_nav_buttons(self, parent):
        spacer = tk.Frame(parent, height=20, bg="#eeeeee")
        spacer.pack()  # Optional spacing before buttons

        btn_nav_frame = tk.Frame(parent, bg="#eeeeee")
        btn_nav_frame.pack(pady=10, anchor="center")  # center-aligned in scrollable area

        tk.Button(btn_nav_frame, text="⬅ Back to Input", font=self.button_font,
                bg="#6c757d", fg="white", command=self.back_to_input_screen,
                width=20).pack(side="left", padx=10)

        tk.Button(btn_nav_frame, text="🗑 Reset & Modify Inputs", font=self.button_font,
                bg="#ffc107", fg="#000", command=self.reset_and_go_to_input,
                width=20).pack(side="left", padx=10)



    def back_to_input_screen(self):
        self.root.destroy()
        import input_screen
        root = tk.Tk()
        input_screen.InputScreen(root)
        root.mainloop()

    def reset_and_go_to_input(self):
        if messagebox.askyesno("Confirm", "This will clear all services and return to input screen. Proceed?"):
            with open("services.csv", "w", newline='', encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=["name", "path", "runnable", "port"])
                writer.writeheader()
            self.back_to_input_screen()

    def log_to_tab(self, service_name, message):
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        text_area = self.get_or_create_log_tab(service_name)
        text_area.insert(tk.END, timestamp + message + "\n")
        text_area.see(tk.END)

    def get_or_create_log_tab(self, service_name):
        if service_name not in self.log_tabs:
            frame = tk.Frame(self.tab_notebook)
            top_bar = tk.Frame(frame, bg="gray20")
            top_bar.pack(fill="x")
            tk.Label(top_bar, text=service_name, fg="white", bg="gray20", font=("Segoe UI", 10, "bold")).pack(side="left", padx=8)
            tk.Button(top_bar, text="✖", command=lambda: self.close_tab(service_name, frame),
                      bg="red", fg="white", font=self.button_font).pack(side="right", padx=5)

            log_frame = tk.Frame(frame)
            log_frame.pack(expand=True, fill='both')

            scrollbar = tk.Scrollbar(log_frame)
            scrollbar.pack(side="right", fill="y")

            text_area = tk.Text(log_frame, height=20, bg="black", fg="lime", font=("Courier", 9),
                                yscrollcommand=scrollbar.set, wrap="word")
            text_area.pack(expand=True, fill='both')
            # Independent scroll logic for left text area
            def _on_mousewheel_left(event):
                text_area.yview_scroll(int(-1 * (event.delta / 120)), "units")

            text_area.bind("<Enter>", lambda e: text_area.bind_all("<MouseWheel>", _on_mousewheel_left))
            text_area.bind("<Leave>", lambda e: text_area.unbind_all("<MouseWheel>"))

            scrollbar.config(command=text_area.yview)

            self.tab_notebook.add(frame, text=service_name)
            self.log_tabs[service_name] = text_area
        text_area = self.log_tabs[service_name]

    # Focus and bind Ctrl+F every time
        text_area.focus_set()
        text_area.bind("<Control-f>", lambda e, text_widget=text_area: self.show_find_popup(text_widget))

        return self.log_tabs[service_name]

    def close_tab(self, service_name, frame):
        index = self.tab_notebook.index(frame)
        self.tab_notebook.forget(index)
        self.log_tabs.pop(service_name, None)

    def clean_ansi(self, text):
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', text)

    def stream_output(self, process, service_name):
        self.log_to_tab(service_name, f"🔁 Started: {service_name}")

        def read_stdout():
            for line in process.stdout:
                cleaned = self.clean_ansi(line.decode("utf-8", errors="ignore").rstrip())
                self.log_to_tab(service_name, cleaned)

        def read_stderr():
            for err in process.stderr:
                cleaned = self.clean_ansi(err.decode("utf-8", errors="ignore").rstrip())
                self.log_to_tab(service_name, f"❌ {cleaned}")

        Thread(target=read_stdout, daemon=True).start()
        Thread(target=read_stderr, daemon=True).start()

    def find_and_kill_port(self, port):
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
    
    def show_find_popup(self, text_widget):
        if hasattr(text_widget, "_find_popup") and text_widget._find_popup.winfo_exists():
            text_widget._find_popup.lift()
            return

        popup = tk.Toplevel(self.root)
        popup.title("Find")
        popup.geometry("320x100")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        text_widget._find_popup = popup

        search_var = tk.StringVar()
        match_count = tk.StringVar(value="0 of 0")
        matches = []
        match_index = [0]

        # UI Elements
        tk.Label(popup, text="Search:").pack(pady=(8, 2))
        entry = tk.Entry(popup, textvariable=search_var, width=35)
        entry.pack()
        entry.focus_set()

        nav_frame = tk.Frame(popup)
        nav_frame.pack(pady=6)

        tk.Label(nav_frame, textvariable=match_count).pack(side="left", padx=(5, 10))
        tk.Button(nav_frame, text="↑", width=3, command=lambda: move(-1)).pack(side="left", padx=2)
        tk.Button(nav_frame, text="↓", width=3, command=lambda: move(1)).pack(side="left", padx=2)
        tk.Button(nav_frame, text="✖", width=3, command=lambda: close()).pack(side="right", padx=5)

        # Highlight tags
        text_widget.tag_config("match", background="yellow", foreground="black")
        text_widget.tag_config("active_match", background="orange", foreground="black")

        def update_matches():
            text_widget.tag_remove("match", "1.0", tk.END)
            text_widget.tag_remove("active_match", "1.0", tk.END)
            matches.clear()

            term = search_var.get().strip()
            if not term:
                match_count.set("0 of 0")
                return

            idx = "1.0"
            while True:
                idx = text_widget.search(term, idx, nocase=True, stopindex=tk.END)
                if not idx:
                    break
                end = f"{idx}+{len(term)}c"
                matches.append((idx, end))
                text_widget.tag_add("match", idx, end)
                idx = end

            if matches:
                match_index[0] = 0
                set_active()
                match_count.set(f"1 of {len(matches)}")
            else:
                match_count.set("0 of 0")

        def set_active():
            text_widget.tag_remove("active_match", "1.0", tk.END)
            if matches:
                idx, end = matches[match_index[0]]
                text_widget.tag_add("active_match", idx, end)
                text_widget.see(idx)
                match_count.set(f"{match_index[0]+1} of {len(matches)}")

        def move(direction):
            if not matches:
                return
            match_index[0] = (match_index[0] + direction) % len(matches)
            set_active()

        def close():
            popup.destroy()
            text_widget.tag_remove("match", "1.0", tk.END)
            text_widget.tag_remove("active_match", "1.0", tk.END)

        # Bind updates on typing
        search_var.trace_add("write", lambda *args: update_matches())

        # Optional: press Enter to jump to next match
        entry.bind("<Return>", lambda e: move(1))


    def run_service(self, name):
    # 🔄 Kill lingering dotnet.exe processes to avoid DLL locks
        if "Frontend" not in name:  # only for .NET services
            try:
                subprocess.run(["taskkill", "/f", "/im", "dotnet.exe"], capture_output=True, text=True)
                self.log_to_tab(name, "🧹 Cleaned up lingering dotnet.exe processes.")
            except Exception as e:
                self.log_to_tab(name, f"⚠️ Failed to kill dotnet processes: {e}")

        # Kill port if needed
        port = self.services[name].get("port")
        if port:
            pid = self.find_and_kill_port(port)
            if pid:
                self.log_to_tab(name, f"⚡ Killed existing process on port {port} (PID: {pid})")

        # Determine command
        path = self.services[name]["path"]
        command = ["cmd", "/c", "ng serve"] if "Frontend" in name else ["dotnet", "run"]

        # Start process
        try:
            process = subprocess.Popen(command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            self.running_processes[name] = process
            Thread(target=self.stream_output, args=(process, name), daemon=True).start()
        except Exception as e:
            self.log_to_tab(name, f"❌ Failed to start process: {e}")


    def build_service(self, name):
        path = self.services[name]["path"]
        command = ["cmd", "/c", "ng build"] if "Frontend" in name else ["dotnet", "build"]

        try:
            self.log_to_tab(name, f"🛠️ Starting build for {name}...")
            process = subprocess.Popen(command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            Thread(target=self.stream_output, args=(process, name), daemon=True).start()
        except Exception as e:
            self.log_to_tab(name, f"❌ Build failed: {e}")

    def kill_service(self, name):
        process = self.running_processes.get(name)
        if process and process.poll() is None:
            process.terminate()
            self.log_to_tab(name, f"❌ Terminated: {name}")
            del self.running_processes[name]
        else:
            self.log_to_tab(name, f"⚠️ No running process found for '{name}'.")

        port = self.services[name].get("port")
        if port:
            pid = self.find_and_kill_port(port)
            if pid:
                self.log_to_tab(name, f"⚡ Also killed process on port {port} (PID: {pid})")
