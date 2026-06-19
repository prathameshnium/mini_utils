import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import os
from datetime import date

LEAST_COUNT = 0.02  # mm per vernier division
N_DIVISIONS = 50
DEFAULT_FILE = "vernier_measurements_log.csv"


def compute_reading(main_scale, vernier_line):
    """Total = main scale (mm) + vernier line * least count."""
    return main_scale + vernier_line * LEAST_COUNT


class VernierApp:
    def __init__(self, root):
        self.root = root
        root.title("Mitutoyo Vernier Logger (0.02 mm)")

        pad = {"padx": 6, "pady": 4}

        # remembered save location (default = next to the script)
        self.save_path = os.path.join(os.getcwd(), DEFAULT_FILE)

        # --- Sample metadata ---
        meta = ttk.LabelFrame(root, text="Sample Info")
        meta.grid(row=0, column=0, sticky="ew", padx=8, pady=6)

        ttk.Label(meta, text="Sample name *").grid(row=0, column=0, sticky="w", **pad)
        self.name = ttk.Entry(meta, width=24)
        self.name.grid(row=0, column=1, **pad)

        ttk.Label(meta, text="Measurement type *").grid(row=1, column=0, sticky="w", **pad)
        self.mtype = ttk.Combobox(
            meta, values=["thickness", "diameter"], state="readonly", width=21
        )
        self.mtype.current(0)
        self.mtype.grid(row=1, column=1, **pad)

        ttk.Label(meta, text="Sample shape (optional)").grid(row=2, column=0, sticky="w", **pad)
        self.shape = ttk.Entry(meta, width=24)
        self.shape.grid(row=2, column=1, **pad)

        ttk.Label(meta, text="Sample code (optional)").grid(row=3, column=0, sticky="w", **pad)
        self.code = ttk.Entry(meta, width=24)
        self.code.grid(row=3, column=1, **pad)

        ttk.Label(meta, text="Date (optional)").grid(row=4, column=0, sticky="w", **pad)
        self.date = ttk.Entry(meta, width=24)
        self.date.insert(0, str(date.today()))
        self.date.grid(row=4, column=1, **pad)

        # --- Readings ---
        self.rd = ttk.LabelFrame(
            root, text="Readings  (main scale mm  +  vernier line /50)"
        )
        self.rd.grid(row=1, column=0, sticky="ew", padx=8, pady=6)

        ttk.Label(self.rd, text="#").grid(row=0, column=0, **pad)
        ttk.Label(self.rd, text="Main scale (mm)").grid(row=0, column=1, **pad)
        ttk.Label(self.rd, text="Vernier line (0-49)").grid(row=0, column=2, **pad)

        self.main_entries = []
        self.line_entries = []
        self.row_labels = []
        self.pad = pad

        for _ in range(3):  # start with 3 reading rows
            self.add_row()

        # add / remove row buttons
        rowbtns = ttk.Frame(root)
        rowbtns.grid(row=2, column=0, sticky="w", padx=8)
        ttk.Button(rowbtns, text="+ Add reading", command=self.add_row).pack(
            side="left", padx=4, pady=2
        )
        ttk.Button(rowbtns, text="- Remove reading", command=self.remove_row).pack(
            side="left", padx=4, pady=2
        )

        # --- File location ---
        fl = ttk.LabelFrame(root, text="Save file")
        fl.grid(row=3, column=0, sticky="ew", padx=8, pady=6)

        self.path_var = tk.StringVar(value=self.save_path)
        ttk.Entry(fl, textvariable=self.path_var, width=40).grid(
            row=0, column=0, **pad
        )
        ttk.Button(fl, text="Browse...", command=self.browse_existing).grid(
            row=0, column=1, **pad
        )
        ttk.Button(fl, text="Save As...", command=self.browse_new).grid(
            row=0, column=2, **pad
        )

        # --- Buttons ---
        btns = ttk.Frame(root)
        btns.grid(row=4, column=0, sticky="ew", padx=8, pady=4)
        ttk.Button(btns, text="Calculate", command=self.calculate).pack(
            side="left", padx=4
        )
        ttk.Button(btns, text="Save (append)", command=self.save).pack(
            side="left", padx=4
        )
        ttk.Button(btns, text="Clear readings", command=self.clear_readings).pack(
            side="left", padx=4
        )
        ttk.Button(btns, text="Clear all", command=self.clear_all).pack(
            side="left", padx=4
        )

        # --- Result ---
        self.result = tk.Text(root, height=9, width=52, state="disabled")
        self.result.grid(row=5, column=0, padx=8, pady=6)

        self.last = None  # cache last computed dict

    # ---------- dynamic rows ----------
    def add_row(self):
        i = len(self.main_entries)
        r = i + 1  # grid row (row 0 is the header)
        lbl = ttk.Label(self.rd, text=str(r))
        lbl.grid(row=r, column=0, **self.pad)
        e_main = ttk.Entry(self.rd, width=12)
        e_main.grid(row=r, column=1, **self.pad)
        e_line = ttk.Entry(self.rd, width=12)
        e_line.grid(row=r, column=2, **self.pad)
        self.row_labels.append(lbl)
        self.main_entries.append(e_main)
        self.line_entries.append(e_line)

    def remove_row(self):
        if len(self.main_entries) <= 1:
            messagebox.showinfo("Minimum", "At least one reading row is required.")
            return
        self.row_labels.pop().destroy()
        self.main_entries.pop().destroy()
        self.line_entries.pop().destroy()

    # ---------- file pickers ----------
    def browse_existing(self):
        """Pick an existing CSV to append into."""
        path = filedialog.askopenfilename(
            title="Select CSV file to append to",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.path_var.set(path)

    def browse_new(self):
        """Choose location/name for a (new) CSV."""
        path = filedialog.asksaveasfilename(
            title="Choose save location",
            defaultextension=".csv",
            initialfile=DEFAULT_FILE,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.path_var.set(path)

    # ---------- core ----------
    def read_values(self):
        """Parse entered rows; ignore fully empty rows."""
        readings = []
        for e_main, e_line in zip(self.main_entries, self.line_entries):
            m, l = e_main.get().strip(), e_line.get().strip()
            if m == "" and l == "":
                continue
            try:
                m = float(m)
                l = float(l)
            except ValueError:
                raise ValueError("Main scale and vernier line must be numbers.")
            if not (0 <= l < N_DIVISIONS):
                raise ValueError(f"Vernier line must be between 0 and {N_DIVISIONS - 1}.")
            readings.append(compute_reading(m, l))
        if not readings:
            raise ValueError("Enter at least one reading.")
        return readings

    def calculate(self):
        try:
            name = self.name.get().strip()
            if not name:
                raise ValueError("Sample name is required.")
            readings = self.read_values()
        except ValueError as err:
            messagebox.showerror("Input error", str(err))
            return

        mtype = self.mtype.get()
        mean = sum(readings) / len(readings)
        unit = "mm"

        lines = [f"Sample: {name}", f"Type: {mtype}"]
        if self.shape.get().strip():
            lines.append(f"Shape: {self.shape.get().strip()}")
        if self.code.get().strip():
            lines.append(f"Code: {self.code.get().strip()}")
        if self.date.get().strip():
            lines.append(f"Date: {self.date.get().strip()}")

        lines.append(
            f"Readings (n={len(readings)}): "
            + ", ".join(f"{r:.3f}" for r in readings)
            + " mm"
        )
        lines.append(f"Mean: {mean:.3f} {unit}")

        area = None
        if mtype == "diameter":
            area = math.pi * (mean / 2) ** 2  # mm^2
            lines.append(f"Area: {area:.4f} mm^2")

        self.last = {
            "name": name,
            "mtype": mtype,
            "shape": self.shape.get().strip(),
            "code": self.code.get().strip(),
            "date": self.date.get().strip(),
            "readings": readings,
            "mean": mean,
            "area": area,
        }

        self.result.config(state="normal")
        self.result.delete("1.0", "end")
        self.result.insert("1.0", "\n".join(lines))
        self.result.config(state="disabled")

    def save(self):
        if self.last is None:
            self.calculate()
            if self.last is None:
                return
        d = self.last

        path = self.path_var.get().strip()
        if not path:
            messagebox.showerror("No file", "Please choose a save file location.")
            return

        readings = d["readings"]
        n = len(readings)
        area_str = f"{d['area']:.4f}" if d["area"] is not None else ""

        # build dynamic header sized to this row's number of readings
        r_cols = ",".join(f"r{i + 1}_mm" for i in range(n))
        header = (
            "date,sample_name,sample_code,shape,type,n,"
            + r_cols
            + ",mean_mm,area_mm2\n"
        )

        new_file = not os.path.exists(path)
        r_vals = ",".join(f"{x:.3f}" for x in readings)
        row = ",".join(
            [
                d["date"],
                d["name"],
                d["code"],
                d["shape"],
                d["mtype"],
                str(n),
                r_vals,
                f"{d['mean']:.3f}",
                area_str,
            ]
        )

        try:
            with open(path, "a", encoding="utf-8") as f:
                if new_file:
                    f.write(header)
                f.write(row + "\n")
        except OSError as err:
            messagebox.showerror("Save error", str(err))
            return

        messagebox.showinfo("Saved", f"Appended to {os.path.abspath(path)}")

    def clear_readings(self):
        for e in self.main_entries + self.line_entries:
            e.delete(0, "end")

    def clear_all(self):
        # sample info
        self.name.delete(0, "end")
        self.mtype.current(0)
        self.shape.delete(0, "end")
        self.code.delete(0, "end")
        self.date.delete(0, "end")
        self.date.insert(0, str(date.today()))
        # readings
        self.clear_readings()
        # result + cache
        self.last = None
        self.result.config(state="normal")
        self.result.delete("1.0", "end")
        self.result.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    VernierApp(root)
    root.mainloop()