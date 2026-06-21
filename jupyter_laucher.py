import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import re
import webbrowser

# Regex pattern to catch the Jupyter localhost URL along with its access token
URL_PATTERN = re.compile(r"(http://(?:localhost|127\.0\.0\.1):\d+[^\s]+)")


def open_link(url):
    """Opens the clicked URL in the default system web browser."""
    webbrowser.open(url)


def _run_jupyter(command, filepath, status_label):
    """
    Tries to launch a given Jupyter command and read its output for a URL.

    Returns:
        True  -> link was found and GUI updated
        False -> command missing or process died before yielding a link
    """
    try:
        process = subprocess.Popen(
            command + [filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
    except FileNotFoundError:
        # This specific command (e.g. "jupyter notebook") isn't installed
        return False

    for line in process.stdout:
        match = URL_PATTERN.search(line)
        if match:
            url = match.group(1)
            status_label.config(
                text=f"Notebook Link (Click to open):\n{url}",
                fg="blue",
                cursor="hand2",
            )
            status_label.bind("<Button-1>", lambda e, u=url: open_link(u))
            return True  # Success

    # stdout closed without a URL -> process exited (likely an error/missing)
    return False


def launch_jupyter_and_get_link(filepath, status_label):
    """Try `jupyter notebook` first, then fall back to `jupyter lab`."""
    try:
        # 1) Primary attempt: classic Jupyter Notebook
        status_label.config(
            text="Launching Jupyter Notebook...", fg="black", cursor=""
        )
        if _run_jupyter(["jupyter", "notebook"], filepath, status_label):
            return

        # 2) Fallback attempt: JupyterLab
        status_label.config(
            text="Notebook failed. Trying JupyterLab...", fg="black", cursor=""
        )
        if _run_jupyter(["jupyter", "lab"], filepath, status_label):
            return

        # 3) Both failed
        status_label.config(
            text="Error: Could not launch Jupyter Notebook or Lab.\n"
            "Is Jupyter installed and on your PATH?",
            fg="red",
        )
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")


def browse_and_open():
    """Opens a file dialog and starts the background launcher."""
    filepath = filedialog.askopenfilename(
        title="Select a Jupyter Notebook",
        filetypes=[("Jupyter Notebooks", "*.ipynb"), ("All Files", "*.*")],
    )

    if filepath:
        status_label.config(
            text="Launching Jupyter... generating link.",
            fg="black",
            cursor="",
        )
        status_label.unbind("<Button-1>")

        threading.Thread(
            target=launch_jupyter_and_get_link,
            args=(filepath, status_label),
            daemon=True,
        ).start()


# --- GUI Setup ---
root = tk.Tk()
root.title("Jupyter Launcher")
root.geometry("450x200")
root.eval("tk::PlaceWindow . center")

instruction = tk.Label(root, text="Select a Jupyter Notebook to open:")
instruction.pack(pady=(20, 10))

browse_button = tk.Button(
    root, text="Browse .ipynb File", command=browse_and_open, width=20
)
browse_button.pack()

status_label = tk.Label(root, text="", wraplength=400, justify="center")
status_label.pack(pady=(20, 10))

root.mainloop()