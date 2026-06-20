import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def browse_and_open():
    """Opens a file dialog to select a notebook and launches it."""
    # Open file dialog filtering for .ipynb files
    filepath = filedialog.askopenfilename(
        title="Select a Jupyter Notebook",
        filetypes=[("Jupyter Notebooks", "*.ipynb"), ("All Files", "*.*")]
    )
    
    # If a file was selected (user didn't click cancel)
    if filepath:
        try:
            # Use subprocess.Popen to run the command in the background
            # This prevents the GUI from freezing while Jupyter runs
            subprocess.Popen(["jupyter", "notebook", filepath])
            
            # Optional: Show a success message
            filename = os.path.basename(filepath)
            messagebox.showinfo("Success", f"Launching {filename} in Jupyter Notebook...")
            
        except FileNotFoundError:
            messagebox.showerror(
                "Error", 
                "Jupyter Notebook is not installed or not found in your system PATH. "
                "Please ensure it is installed in your current environment."
            )
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Jupyter Launcher")
root.geometry("350x150")
root.eval('tk::PlaceWindow . center') # Center the window on the screen

# Instructional Label
label = tk.Label(root, text="Select a Jupyter Notebook to open:")
label.pack(pady=(20, 10))

# Browse Button
browse_button = tk.Button(root, text="Browse .ipynb File", command=browse_and_open, width=20)
browse_button.pack()

# Run the application
root.mainloop()