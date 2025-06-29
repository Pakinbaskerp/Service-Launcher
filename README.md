# 🚀 Service Launcher

A Python + Tkinter GUI to build, run, and manage multiple .NET and Angular services — with logs, terminal-style tabs, and simple UI controls.

---

## 📦 Prerequisites

Ensure the following are installed before running:

| Requirement      | Install Guide / Command                 |
|------------------|-----------------------------------------|
| Python 3.9+      | [python.org](https://www.python.org/downloads/) |
| pip              | Comes with Python installation          |
| Node.js & npm    | [nodejs.org](https://nodejs.org)        |
| Angular CLI      | `npm install -g @angular/cli`           |
| .NET SDK 6/7/8+  | [dotnet.microsoft.com](https://dotnet.microsoft.com/download) |
| Windows Terminal | From Microsoft Store (optional)         |

---

## 🧪 How to Run (Development Mode)

```bash
# 1. Clone this repo
git clone https://github.com/yourusername/ServiceLauncher.git
cd ServiceLauncher

# 2. (Optional) Create virtual environment
python -m venv env
env\Scripts\activate  # On Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Launch the application
python ServiceLauncher.py

# 1. Install PyInstaller
pip install pyinstaller

# 2. Build executable with icon and no console
pyinstaller --onefile --windowed --icon=myicon.ico ServiceLauncher.py


ServiceLauncher/
│
├── ServiceLauncher.py       # 🧠 Main launcher script
├── requirements.txt         # 📦 Python dependencies
├── myicon.ico               # 🖼 App icon (optional)
├── .gitignore               # 🔒 Git ignore rules
│
├── build/                   # ⚙️ PyInstaller build files
├── dist/                    # 🚀 Final output .exe lives here
└── README.md                # 📖 This file
