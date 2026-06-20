import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import os
import datetime

def select_folder():
    """Opens a dialog to select a folder and updates the entry box."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path_var.set(folder_selected)

def format_size(size_in_bytes):
    """Converts bytes to a human-readable format (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

def scan_folder():
    """Scans the directory and prints the output based on selected toggles."""
    folder = folder_path_var.get()
    
    # Validate the folder
    if not folder or not os.path.isdir(folder):
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "❌ Please select a valid folder first.\n")
        return

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"Scanning Directory: {folder}\n")
    output_text.insert(tk.END, "="*60 + "\n")

    # Get the state of the toggles
    show_cdate = cdate_var.get()
    show_mdate = mdate_var.get()
    show_size = size_var.get()

    # os.walk automatically goes through subfolders and sub-subfolders
    for root, dirs, files in os.walk(folder):
        
        # Determine the relative path to make the output cleaner
        rel_path = os.path.relpath(root, folder)
        if rel_path == '.':
            rel_path = os.path.basename(folder)
            
        output_text.insert(tk.END, f"\n📁 {rel_path}/\n")

        # Process each file in the current directory
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Fetch file statistics
                stats = os.stat(file_path)
                info_string = [f"📄 {file}"]

                # Append requested metadata based on toggles
                if show_size:
                    info_string.append(f"Size: {format_size(stats.st_size)}")
                    
                if show_cdate:
                    # Note: On Linux, st_ctime is the time of most recent metadata change. 
                    # On Windows, it is the creation time.
                    c_time = datetime.datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M')
                    info_string.append(f"Created: {c_time}")
                    
                if show_mdate:
                    m_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                    info_string.append(f"Modified: {m_time}")

                # Combine the file info with a separator and print it
                final_line = "    " + " | ".join(info_string) + "\n"
                output_text.insert(tk.END, final_line)

            except Exception as e:
                # Handle permission errors or locked files gracefully
                output_text.insert(tk.END, f"    📄 {file} | [Error reading file details]\n")

# ==========================================
# GUI Setup
# ==========================================
root = tk.Tk()
root.title("Directory Recursive Scanner")
root.geometry("800x600")
root.configure(padx=15, pady=15)

# --- Top Frame: Folder Selection ---
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, pady=(0, 10))

folder_path_var = tk.StringVar()

tk.Label(top_frame, text="Target Folder:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
tk.Entry(top_frame, textvariable=folder_path_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
tk.Button(top_frame, text="Browse...", command=select_folder).pack(side=tk.LEFT, padx=5)

# --- Middle Frame: Toggles/Options ---
options_frame = tk.LabelFrame(root, text="Metadata Options", padx=10, pady=5)
options_frame.pack(fill=tk.X, pady=(0, 10))

cdate_var = tk.BooleanVar(value=True)
mdate_var = tk.BooleanVar(value=True)
size_var = tk.BooleanVar(value=True)

tk.Checkbutton(options_frame, text="Include Creation Date", variable=cdate_var).pack(side=tk.LEFT, padx=10)
tk.Checkbutton(options_frame, text="Include Modification Date", variable=mdate_var).pack(side=tk.LEFT, padx=10)
tk.Checkbutton(options_frame, text="Include File Size", variable=size_var).pack(side=tk.LEFT, padx=10)

tk.Button(options_frame, text="Scan Directory", command=scan_folder, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=10)

# --- Bottom Frame: Output Area ---
output_frame = tk.Frame(root)
output_frame.pack(fill=tk.BOTH, expand=True)

# Using ScrolledText for easy scrolling through thousands of files
output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=("Consolas", 10))
output_text.pack(fill=tk.BOTH, expand=True)

# Start the application
if __name__ == "__main__":
    root.mainloop()