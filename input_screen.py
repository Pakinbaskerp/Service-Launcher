import json
import tkinter as tk
from tkinter import messagebox
from ServiceLauncher import ServiceLauncher  # ✅ ensure this is in the same folder

JSON_FILE = "services.json"
FIELDS = ["name", "path", "runnable", "port"]

class InputScreen:
    def __init__(self, master):
        self.master = master
        master.title("Service Configuration Input")
        master.state("zoomed")
        master.configure(bg="#f4f4f4")
        

        self.entry_rows = []

        tk.Label(master, text="Service Configuration", font=("Segoe UI", 16, "bold"), bg="#f4f4f4").pack(pady=10)
        self.form_frame = tk.Frame(master, bg="#f4f4f4")
        self.form_frame.pack(pady=10)

        headers = ["Name", "Path", "Runnable", "Port"]
        for col, h in enumerate(headers):
            tk.Label(self.form_frame, text=h, font=("Segoe UI", 10, "bold"), bg="#f4f4f4").grid(row=0, column=col, padx=5, pady=5)

        self.services = self.load_services()
        if self.services:
            for s in self.services:
                self.add_row_with_data(s)
        else:
            for _ in range(3):
                self.add_row()

        self.add_buttons()

    def load_services(self):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except:
            return []

    def add_row(self):
        self.add_row_with_data({})

    def add_row_with_data(self, data):
        row_entries = {}
        row = len(self.entry_rows) + 1

        name_entry = tk.Entry(self.form_frame, width=20)
        name_entry.insert(0, data.get("name", ""))
        name_entry.grid(row=row, column=0, padx=5, pady=5)

        path_entry = tk.Entry(self.form_frame, width=40)
        path_entry.insert(0, data.get("path", ""))
        path_entry.grid(row=row, column=1, padx=5, pady=5)

        runnable_var = tk.BooleanVar(value=data.get("runnable", True))
        tk.Checkbutton(self.form_frame, variable=runnable_var, bg="#f4f4f4").grid(row=row, column=2, padx=5, pady=5)

        port_entry = tk.Entry(self.form_frame, width=10)
        port_entry.insert(0, data.get("port", ""))
        port_entry.grid(row=row, column=3, padx=5, pady=5)

        row_entries["name"] = name_entry
        row_entries["path"] = path_entry
        row_entries["runnable"] = runnable_var
        row_entries["port"] = port_entry

        self.entry_rows.append(row_entries)

    def save_all(self):
        valid_rows = []
        for row in self.entry_rows:
            name = row["name"].get().strip()
            path = row["path"].get().strip()
            runnable = row["runnable"].get()
            port = row["port"].get().strip()

            if not name or not path:
                continue
            if port and not port.isdigit():
                messagebox.showerror("Invalid Port", f"Port must be a number. Invalid value: {port}")
                return

            valid_rows.append({"name": name, "path": path, "runnable": runnable, "port": port})

        if not valid_rows:
            messagebox.showwarning("No Data", "No valid entries to save.")
            return

        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(valid_rows, file, indent=2)

        messagebox.showinfo("Saved", "All valid service entries saved.")

    def reset_csv(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to reset?"):
            with open(JSON_FILE, "w", encoding="utf-8") as file:
                json.dump([], file)
            for row in self.entry_rows:
                row["name"].delete(0, tk.END)
                row["path"].delete(0, tk.END)
                row["port"].delete(0, tk.END)
                row["runnable"].set(True)
            messagebox.showinfo("Reset", "All services cleared.")

    def launch_ui(self):
        self.master.destroy()
        root = tk.Tk()
        ServiceLauncher(root)
        root.mainloop()

    def add_buttons(self):
        btn_frame = tk.Frame(self.master, bg="#f4f4f4")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="➕ Add Row", width=15, command=self.add_row,
                  bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=8)

        tk.Button(btn_frame, text="💾 Save All", width=15, command=self.save_all,
                  bg="#28a745", fg="white", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, padx=8)

        tk.Button(btn_frame, text="🗑 Reset All", width=15, command=self.reset_csv,
                  bg="#dc3545", fg="white", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, padx=8)

        tk.Button(btn_frame, text="🚀 Launch UI", width=15, command=self.launch_ui,
                  bg="#007bff", fg="white", font=("Segoe UI", 10, "bold")).grid(row=0, column=3, padx=8)
