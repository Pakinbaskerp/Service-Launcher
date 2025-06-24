import tkinter as tk
import sys
from input_screen import InputScreen
from ServiceLauncher import ServiceLauncher


if __name__ == "__main__":
    root = tk.Tk()
    if len(sys.argv) > 1 and sys.argv[1] == "launcher":
        ServiceLauncher(root)
    else:
        InputScreen(root)
    root.mainloop()
