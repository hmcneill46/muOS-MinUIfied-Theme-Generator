import os
import tkinter as tk
from tkinter import filedialog, messagebox

def select_source_directory():
    directory = filedialog.askdirectory(title="Select Directory to make dummy from")
    if directory:
        source_directory.set(directory)

def select_destination_directory():
    directory = filedialog.askdirectory(title="Select where the dummy folder should go")
    if directory:
        destination_directory.set(directory)

def create_dummy():
    src_dir = source_directory.get()
    dest_dir = destination_directory.get()

    if not src_dir or not dest_dir:
        messagebox.showwarning("Missing Information", "Please select both the source and destination directories.")
        return
    
    dummy_dir = os.path.join(dest_dir, f'dummy{os.path.basename(src_dir)}')
    create_dummy_files(src_dir, dummy_dir)
    messagebox.showinfo("Success", f"Dummy directory created at: {dummy_dir}")

def create_dummy_files(src, dest):
    os.makedirs(dest, exist_ok=True)
    for item in os.listdir(src):
        src_item_path = os.path.join(src, item)
        dest_item_path = os.path.join(dest, item)
        if os.path.isdir(src_item_path):
            create_dummy_files(src_item_path, dest_item_path)
        elif os.path.isfile(src_item_path):
            open(dest_item_path, 'w').close()

root = tk.Tk()
root.title("Dummy Directory Creator")
root.geometry("700x200")

source_directory = tk.StringVar()
destination_directory = tk.StringVar()

class GridHelper:
    def __init__(self, master):
        self.master = master
        self.row = 0
        self.column = 0

    def add(self, widget, next_row=False, sticky="w"):
        widget.grid(row=self.row, column=self.column, padx=10, pady=5, sticky=sticky)
        if next_row:
            self.row += 1
            self.column = 0
        else:
            self.column += 1

grid_helper = GridHelper(root)

grid_helper.add(tk.Label(root, text="Select Directory to make dummy from:"), next_row=True)
grid_helper.add(tk.Entry(root, textvariable=source_directory, width=50))
grid_helper.add(tk.Button(root, text="Browse...", command=select_source_directory), next_row=True)

grid_helper.add(tk.Label(root, text="Select where the dummy folder should go:"), next_row=True)
grid_helper.add(tk.Entry(root, textvariable=destination_directory, width=50))
grid_helper.add(tk.Button(root, text="Browse...", command=select_destination_directory), next_row=True)

grid_helper.add(tk.Button(root, text="Create Dummy Directory", command=create_dummy), sticky="e", next_row=True)

root.mainloop()
