#!/usr/bin/env python3
"""
Folder Scanner GUI
Scan a folder recursively and save a detailed tree listing to a text file.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

class FolderScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Scanner")
        self.root.geometry("500x200")
        self.root.resizable(False, False)

        self.folder_path = tk.StringVar()
        self.include_details = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        # Folder selection
        tk.Label(self.root, text="Select folder to scan:").pack(pady=(10, 0))

        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Entry(frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)

        # Options
        tk.Checkbutton(self.root, text="Include file sizes and modification dates",
                       variable=self.include_details).pack(pady=5)

        # Scan button
        self.scan_btn = tk.Button(self.root, text="Scan and Save", command=self.scan_folder,
                                  bg="#4CAF50", fg="white", padx=20, pady=5)
        self.scan_btn.pack(pady=10)

        # Progress bar (indeterminate)
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=5)

        # Status label
        self.status = tk.Label(self.root, text="", fg="blue")
        self.status.pack()

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def scan_folder(self):
        folder = self.folder_path.get().strip()
        if not folder:
            messagebox.showerror("Error", "Please select a folder.")
            return

        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Selected path is not a valid directory.")
            return

        # Disable button, start progress
        self.scan_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status.config(text="Scanning...")

        # Run the scan in a separate thread to keep GUI responsive
        self.root.after(100, lambda: self.perform_scan(folder))

    def perform_scan(self, folder):
        try:
            # Determine output file path (same directory as this script)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_name = os.path.basename(folder) or "root"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(script_dir, f"folder_structure_{base_name}_{timestamp}.txt")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Folder structure of: {folder}\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                # Walk through the directory
                for root_dir, dirs, files in os.walk(folder):
                    level = root_dir.replace(folder, '').count(os.sep)
                    indent = '  ' * level
                    folder_name = os.path.basename(root_dir) or os.path.basename(folder)

                    # Write folder name
                    if self.include_details.get():
                        # Get folder stats (if possible)
                        try:
                            stat = os.stat(root_dir)
                            size = stat.st_size
                            mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            f.write(f"{indent}[FOLDER] {folder_name} (size: {size} bytes, modified: {mtime})\n")
                        except:
                            f.write(f"{indent}[FOLDER] {folder_name}\n")
                    else:
                        f.write(f"{indent}{folder_name}/\n")

                    # Write files
                    sub_indent = '  ' * (level + 1)
                    for file in files:
                        file_path = os.path.join(root_dir, file)
                        if self.include_details.get():
                            try:
                                stat = os.stat(file_path)
                                size = stat.st_size
                                mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                                f.write(f"{sub_indent}{file} (size: {size} bytes, modified: {mtime})\n")
                            except:
                                f.write(f"{sub_indent}{file}\n")
                        else:
                            f.write(f"{sub_indent}{file}\n")
                    f.write("\n")  # blank line between directories

            self.progress.stop()
            self.status.config(text=f"Scan complete! Saved to:\n{output_file}", fg="green")
            messagebox.showinfo("Success", f"Folder structure saved to:\n{output_file}")
        except Exception as e:
            self.progress.stop()
            self.status.config(text="Error during scan", fg="red")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            self.scan_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderScannerApp(root)
    root.mainloop()