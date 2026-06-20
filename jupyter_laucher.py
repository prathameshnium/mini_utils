import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import re
import webbrowser

# Regex pattern to catch the Jupyter localhost URL along with its access token
URL_PATTERN = re.compile(r'(http://(?:localhost|127\.0\.0\.1):\d+[^\s]+)')

def open_link(url):
    """Opens the clicked URL in the default system web browser."""
    webbrowser.open(url)

def launch_jupyter_and_get_link(filepath, status_label):
    """Runs Jupyter in the background and reads its terminal output to find the link."""
    try:
        # Launch Jupyter, merging stderr into stdout so we can capture all terminal text
        process = subprocess.Popen(
            ["jupyter", "notebook", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1, # Line-buffered
            universal_newlines=True
        )

        # Read the terminal output line-by-line as it generates
        for line in process.stdout:
            match = URL_PATTERN.search(line)
            if match:
                url = match.group(1)
                
                # Update the GUI label to become a clickable link
                status_label.config(
                    text=f"Notebook Link (Click to open):\n{url}",
                    fg="blue",
                    cursor="hand2"
                )
                # Bind left mouse click to open the URL
                status_label.bind("<Button-1>", lambda e, u=url: open_link(u))
                
                break # We found the link, stop reading output
                
    except FileNotFoundError:
         status_label.config(text="Error: Jupyter not found in your system PATH.", fg="red")
    except Exception as e:
         status_label.config(text=f"Error: {str(e)}", fg="red")

def browse_and_open():
    """Opens a file dialog and starts the background launcher."""
    filepath = filedialog.askopenfilename(
        title="Select a Jupyter Notebook",
        filetypes=[("Jupyter Notebooks", "*.ipynb"), ("All Files", "*.*")]
    )
    
    if filepath:
        # Reset the label text and color while Jupyter is loading
        status_label.config(text="Launching Jupyter... generating link.", fg="black", cursor="")
        status_label.unbind("<Button-1>") # Remove old link bindings if any
        
        # Start the process in a separate thread so the Tkinter GUI doesn't freeze
        threading.Thread(
            target=launch_jupyter_and_get_link, 
            args=(filepath, status_label), 
            daemon=True
        ).start()

# --- GUI Setup ---
root = tk.Tk()
root.title("Jupyter Launcher")
root.geometry("450x200") # Made slightly wider to fit long URLs
root.eval('tk::PlaceWindow . center')

# Instructional Label
instruction = tk.Label(root, text="Select a Jupyter Notebook to open:")
instruction.pack(pady=(20, 10))

# Browse Button
browse_button = tk.Button(root, text="Browse .ipynb File", command=browse_and_open, width=20)
browse_button.pack()

# Status / Link Label (Starts empty, gets populated by the thread)
status_label = tk.Label(root, text="", wraplength=400, justify="center")
status_label.pack(pady=(20, 10))

# Run the application
root.mainloop()