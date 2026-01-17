import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)
from . import geometry, api
from ..utils_datastore import outline_from_krm, outline_from_dwba

# TOML handling
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

try:
    import rtoml
except ImportError:
    rtoml = None


class ShapeViewerComboApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shape Viewer V0.2 - J.TONG 2026")
        self.root.geometry("1400x1200")  # Set initial window size

        # --- Global storage ---
        self.all_shapes = {}
        self.current_view_mode = tk.StringVar(value="2D")  # Default to 2D
        self.source_mode = tk.StringVar(value="Web")  # Default to Web source
        self.show_grid_var = tk.BooleanVar(value=True)  # Grid toggle
        self.web_shape_index = {}  # Store for lookups

        # --- Setup UI ---
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left pane
        self.left_pane = ttk.Frame(self.main_frame, width=300)
        self.left_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Source Selection
        ttk.Label(self.left_pane, text="Shape Source:").pack(
            anchor=tk.W, pady=(0, 5)
        )
        source_frame = ttk.Frame(self.left_pane)
        source_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(
            source_frame, text="Web Datastore", variable=self.source_mode,
            value="Web", command=self.toggle_source_ui
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(
            source_frame, text="Load File", variable=self.source_mode,
            value="File", command=self.toggle_source_ui
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(
            source_frame, text="Regular Shape", variable=self.source_mode,
            value="Regular", command=self.toggle_source_ui
        ).pack(side=tk.LEFT)

        # --- File Loading UI ---
        self.file_ui_frame = ttk.Frame(self.left_pane)
        # self.file_ui_frame.pack(fill=tk.X) # Managed by toggle_source_ui

        ttk.Label(self.file_ui_frame, text="Select Shapes File (.toml):").pack(
            anchor=tk.W, pady=(0, 5)
        )
        file_frame = ttk.Frame(self.file_ui_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(
            file_frame, textvariable=self.file_path_var, state='readonly'
        )
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.browse_btn = ttk.Button(
            file_frame, text="Browse...", command=self.browse_file
        )
        self.browse_btn.pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Label(self.file_ui_frame, text="Select Organism:").pack(
            anchor=tk.W, pady=(0, 5)
        )
        self.shape_selector = ttk.Combobox(
            self.file_ui_frame, state="readonly", width=30
        )
        self.shape_selector.pack(fill=tk.X)
        self.shape_selector.bind(
            "<<ComboboxSelected>>", self.refresh_plot
        )

        # --- Web Datastore UI ---
        self.web_ui_frame = ttk.Frame(self.left_pane)

        ttk.Label(self.web_ui_frame, text="Online Shapes Source:").pack(
            anchor=tk.W, pady=(0, 5)
        )
        ttk.Label(
            self.web_ui_frame,
            text="Official EchoSMs Repository (GitHub)",
            font=("", 8, "italic")
        ).pack(anchor=tk.W, pady=(0, 10))

        self.fetch_btn = ttk.Button(
            self.web_ui_frame, text="Connect & Fetch Shapes",
            command=self.fetch_web_shapes
        )
        self.fetch_btn.pack(fill=tk.X, pady=(0, 10))

        self.web_status_var = tk.StringVar(value="Not Connected")
        self.web_status_label = tk.Label(
            self.web_ui_frame, textvariable=self.web_status_var, anchor=tk.W
        )
        self.web_status_label.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(self.web_ui_frame, text="Select Organism (Web):").pack(
            anchor=tk.W, pady=(0, 5)
        )
        self.web_shape_selector = ttk.Combobox(
            self.web_ui_frame, state="readonly", width=30
        )
        self.web_shape_selector.pack(fill=tk.X)
        self.web_shape_selector.bind(
            "<<ComboboxSelected>>", self.on_web_shape_selected
        )

        # --- Regular Shape Generator UI ---
        self.regular_ui_frame = ttk.Frame(self.left_pane)
        # Don't pack initially

        ttk.Label(self.regular_ui_frame, text="Select Shape Type:").pack(
            anchor=tk.W, pady=(0, 5)
        )
        self.reg_shape_type = tk.StringVar()
        self.reg_shape_selector = ttk.Combobox(
            self.regular_ui_frame, textvariable=self.reg_shape_type,
            state="readonly", width=30
        )
        self.reg_shape_selector['values'] = [
            "Sphere", "Prolate Spheroid", "Cylinder", "Bent Cylinder"
        ]
        self.reg_shape_selector.current(0)
        self.reg_shape_selector.pack(fill=tk.X, pady=(0, 10))
        self.reg_shape_selector.bind(
            "<<ComboboxSelected>>", self.update_param_fields
        )

        # Parameters Frame
        self.params_frame = ttk.Frame(self.regular_ui_frame)
        self.params_frame.pack(fill=tk.X, pady=(0, 10))

        self.param_vars = {}  # Store entry vars
        self.update_param_fields()  # Initialize fields

        self.gen_btn = ttk.Button(
            self.regular_ui_frame, text="Generate Shape",
            command=self.generate_regular_shape
        )
        self.gen_btn.pack(fill=tk.X, pady=(0, 5))

        # Save Format Selection
        save_fmt_frame = ttk.Frame(self.regular_ui_frame)
        save_fmt_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(save_fmt_frame, text="Save As:").pack(side=tk.LEFT)
        self.save_format_var = tk.StringVar(value="Auto")
        ttk.Radiobutton(
            save_fmt_frame, text="Auto", variable=self.save_format_var,
            value="Auto"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            save_fmt_frame, text="KRM", variable=self.save_format_var,
            value="KRM"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            save_fmt_frame, text="DWBA", variable=self.save_format_var,
            value="DWBA"
        ).pack(side=tk.LEFT, padx=5)

        # Save Shape Button
        self.save_shape_btn = ttk.Button(
            self.regular_ui_frame, text="Save Shape to TOML",
            command=self.save_generated_shape_to_toml, state=tk.DISABLED
        )
        self.save_shape_btn.pack(fill=tk.X, pady=(2, 0))

        # View Mode Selection
        ttk.Label(self.left_pane, text="View Mode:").pack(
            anchor=tk.W, pady=(20, 5)
        )  # Extra pad
        view_frame = ttk.Frame(self.left_pane)
        view_frame.pack(fill=tk.X)
        ttk.Radiobutton(
            view_frame, text="2D View", variable=self.current_view_mode,
            value="2D", command=self.refresh_plot
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(
            view_frame, text="3D View", variable=self.current_view_mode,
            value="3D", command=self.refresh_plot
        ).pack(side=tk.LEFT)

        # Grid Toggle Checkbox
        ttk.Checkbutton(
            self.left_pane, text="Show Background Grid",
            variable=self.show_grid_var, command=self.refresh_plot
        ).pack(anchor=tk.W, pady=(5, 0))

        # Info
        ttk.Label(self.left_pane, text="Organism Information:").pack(
            anchor=tk.W, pady=(10, 5)
        )
        self.info_text = tk.Text(
            self.left_pane, height=20, wrap=tk.WORD, state=tk.DISABLED,
            width=40
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Right pane (Plot)
        self.right_pane = ttk.Frame(self.main_frame)
        self.right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.toolbar_frame = ttk.Frame(self.right_pane)
        self.toolbar_frame.pack(fill=tk.X, pady=(0, 5))

        # Matplotlib setup
        self.fig = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_pane)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Add NavigationToolbar
        self.toolbar = NavigationToolbar2Tk(
            self.canvas, self.toolbar_frame, pack_toolbar=False
        )
        self.toolbar.update()
        self.toolbar.pack(side=tk.LEFT, fill=tk.X)

        # Context Menu
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(
            label="Toggle Grid", command=self.toggle_grid
        )
        self.context_menu.add_command(
            label="Reset View", command=lambda: self.toolbar.home()
        )

        # Bind Mouse Wheel for Zoom and Right Click for Menu
        self.canvas_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas_widget.bind(
            "<Button-3>", self.show_context_menu
        )  # Right click
        self.canvas_widget.bind(
            "<Button-4>", self.on_mouse_wheel
        )  # Linux scroll up
        self.canvas_widget.bind(
            "<Button-5>", self.on_mouse_wheel
        )  # Linux scroll down

        # Initialize UI state
        self.toggle_source_ui()

    def toggle_source_ui(self):
        mode = self.source_mode.get()
        # Hide all first
        self.file_ui_frame.pack_forget()
        self.regular_ui_frame.pack_forget()
        self.web_ui_frame.pack_forget()

        insert_after = self.left_pane.winfo_children()[1]  # Source frame

        if mode == "File":
            self.file_ui_frame.pack(fill=tk.X, after=insert_after)
        elif mode == "Regular":
            self.regular_ui_frame.pack(fill=tk.X, after=insert_after)
        elif mode == "Web":
            self.web_ui_frame.pack(fill=tk.X, after=insert_after)

    def update_status(self, text, color="black"):
        self.web_status_var.set(text)
        self.web_status_label.config(fg=color)

    def fetch_web_shapes(self):
        self.fetch_btn.config(state=tk.DISABLED)
        self.update_status("Fetching index from Datastore...", "red")
        self.root.update_idletasks()

        def run_fetch():
            try:
                # Returns dict: "Name" -> "ID"
                index = api.fetch_online_shapes_index()
                self.root.after(
                    0, lambda idx=index: self.on_index_success(idx)
                )
            except Exception as e:
                err_msg = str(e)
                self.root.after(
                    0, lambda msg=err_msg: self.on_fetch_error(msg)
                )

        threading.Thread(target=run_fetch, daemon=True).start()

    def on_index_success(self, index):
        self.web_shape_index = index  # Store for lookups
        names = sorted(index.keys())
        self.web_shape_selector['values'] = names
        self.update_status(f"Found {len(names)} specimens.", "green")
        self.fetch_btn.config(state=tk.NORMAL)
        if names:
            self.web_shape_selector.current(0)
            self.on_web_shape_selected()

    def on_fetch_error(self, error_msg):
        self.update_status("Fetch failed.", "red")
        self.fetch_btn.config(state=tk.NORMAL)
        messagebox.showerror("Network Error", f"Failed:\n{error_msg}")

    def on_web_shape_selected(self, event=None):
        display_name = self.web_shape_selector.get()
        if not hasattr(self, 'web_shape_index') or \
           display_name not in self.web_shape_index:
            return

        # Check Cache first
        if display_name in self.all_shapes:
            self.update_status(f"Loaded {display_name} from cache.", "green")
            self.shape_selector.set(display_name)
            self.refresh_plot_with_feedback()
            return

        specimen_id = self.web_shape_index[display_name]
        self.update_status(f"Fetching {specimen_id}...", "red")
        self.root.config(cursor="wait")

        def progress_cb(downloaded, total):
            mb_downloaded = downloaded / (1024 * 1024)
            if total > 0:
                percent = (downloaded / total) * 100
                msg = f"Downloading: {mb_downloaded:.1f}MB ({percent:.0f}%)"
            else:
                msg = f"Downloading: {mb_downloaded:.1f}MB"
            # Thread-safe UI update
            self.root.after(0, lambda: self.update_status(msg, "orange"))

        def run_detail_fetch():
            try:
                shape_entry = api.fetch_shape_data(
                    specimen_id, progress_callback=progress_cb
                )
                self.root.after(
                    0, lambda se=shape_entry, dn=display_name:
                    self.on_detail_success(dn, se)
                )
            except Exception as e:
                err_msg = str(e)
                self.root.after(
                    0, lambda msg=err_msg: self.on_fetch_error(msg)
                )
                self.root.after(0, lambda: self.root.config(cursor=""))

        threading.Thread(target=run_detail_fetch, daemon=True).start()

    def on_detail_success(self, name, shape_entry):
        self.root.config(cursor="")
        self.update_status("Ready.", "green")

        # Cache it
        self.all_shapes[name] = shape_entry

        # Select in main selector and plot
        current_values = list(self.shape_selector['values'])
        if name not in current_values:
            self.shape_selector['values'] = current_values + [name]

        self.shape_selector.set(name)
        self.refresh_plot_with_feedback()

    def update_param_fields(self, event=None):
        # Clear existing params
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self.param_vars = {}

        shape_type = self.reg_shape_type.get()

        # Helper to add field
        def add_field(label_text, var_name, default_val):
            f = ttk.Frame(self.params_frame)
            f.pack(fill=tk.X, pady=2)
            ttk.Label(f, text=label_text).pack(
                side=tk.LEFT, fill=tk.X, expand=True
            )
            var = tk.DoubleVar(value=default_val)
            ttk.Entry(f, textvariable=var, width=16).pack(
                side=tk.RIGHT, padx=5
            )
            self.param_vars[var_name] = var

        if shape_type == "Sphere":
            add_field("Radius a (cm):", "a", 2.0)
        elif shape_type == "Prolate Spheroid":
            add_field("Minor Radius a (cm):", "a", 2.0)
            add_field("Length L (cm):", "L", 10.0)
        elif shape_type == "Cylinder":
            add_field("Radius a (cm):", "a", 2.0)
            add_field("Length L (cm):", "L", 10.0)
        elif shape_type == "Bent Cylinder":
            add_field("Radius a (cm):", "a", 1.0)
            add_field("Arc Length L (cm):", "L", 10.0)
            add_field("Radius Curv. rho_c (cm):", "rho_c", -30.0)

    def generate_regular_shape(self):
        try:
            shape_type = self.reg_shape_type.get()
            # Get params in cm, convert to m for internal logic
            params = {k: v.get() / 100.0 for k, v in self.param_vars.items()}

            shape_data = {}  # Store shape data in meters
            model_type = "KRM"  # Default

            if shape_type == "Sphere":
                shape_data = geometry.generate_sphere(params['a'])
                model_type = "KRM"
            elif shape_type == "Prolate Spheroid":
                shape_data = geometry.generate_prolate_spheroid(
                    params['a'], params['L']
                )
                model_type = "KRM"
            elif shape_type == "Cylinder":
                shape_data = geometry.generate_cylinder(
                    params['a'], params['L']
                )
                model_type = "KRM"
            elif shape_type == "Bent Cylinder":
                shape_data = geometry.generate_bent_cylinder(
                    params['a'], params['L'], params['rho_c']
                )
                model_type = "DWBA"

            # Load into "all_shapes" pseudo-file entry
            self.all_shapes = {
                shape_data['name']: {
                    'data': shape_data, 'model_type': model_type
                }
            }

            # Select it
            self.shape_selector['values'] = [shape_data['name']]
            self.shape_selector.current(0)
            self.refresh_plot()

            # Show info
            self.update_info_display(shape_data)

            # Enable Save
            self.save_shape_btn.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Generation failed:\n{e}")

    def save_generated_shape_to_toml(self):
        if rtoml is None:
            messagebox.showerror(
                "Error", "rtoml library is not installed. Saving is disabled."
            )
            return

        selected_name = self.shape_selector.get()
        if not selected_name or selected_name not in self.all_shapes:
            messagebox.showwarning(
                "No Shape", "Please generate a shape first."
            )
            return

        shape_entry = self.all_shapes[selected_name]
        data = shape_entry['data']
        source_type = shape_entry['model_type']

        target_format = self.save_format_var.get()
        if target_format == "Auto":
            target_format = source_type

        # Construct dictionary for TOML
        output_shape = {
            "name": data.get("name"),
            "aphiaid": 0,
            "vernacular": "Regular Shape",
            "length": 0.0,
            "source": f"Generated by echosms.viewer (from {source_type})",
            "swimbladder_rho": 1.24,
            "swimbladder_c": 345,
            "body_rho": 1070,
            "body_c": 1570
        }

        # --- Conversion Logic ---

        if target_format == "KRM":
            output_shape["data_format"] = "echosms_krm"

            if source_type == "KRM":
                # Direct Copy
                output_shape["x_b"] = data.get("x_b", [])
                output_shape["z_bU"] = data.get("z_bU", [])
                output_shape["z_bL"] = data.get("z_bL", [])
                output_shape["w_b"] = data.get("w_b", [])

            elif source_type == "DWBA":
                # Convert DWBA (Bent) to KRM (Straightened)
                x_dwba = np.array(data.get("x", []))
                y_dwba = np.array(data.get("y", []))
                z_dwba = np.array(data.get("z", []))
                a_dwba = np.array(data.get("a", []))

                # Calculate Arc Length for X axis
                if len(x_dwba) > 1:
                    dist = np.sqrt(
                        np.diff(x_dwba)**2 +
                        np.diff(y_dwba)**2 +
                        np.diff(z_dwba)**2
                    )
                    x_b = np.concatenate(([0], np.cumsum(dist)))
                else:
                    x_b = np.array([0.0])

                output_shape["x_b"] = x_b.tolist()
                output_shape["z_bU"] = a_dwba.tolist()
                output_shape["z_bL"] = (-a_dwba).tolist()
                output_shape["w_b"] = (2 * a_dwba).tolist()

            # Placeholders
            output_shape["x_sb"] = []
            output_shape["z_sbU"] = []
            output_shape["z_sbL"] = []
            output_shape["w_sb"] = []

            if output_shape["x_b"]:
                length = max(output_shape["x_b"]) - min(output_shape["x_b"])
                output_shape["length"] = float(f"{length:.4f}")

        elif target_format == "DWBA":
            output_shape["data_format"] = "echosms_dwba"

            if source_type == "DWBA":
                # Direct Copy
                output_shape["x"] = data.get("x", [])
                output_shape["y"] = data.get("y", [])
                output_shape["z"] = data.get("z", [])
                output_shape["a"] = data.get("a", [])

            elif source_type == "KRM":
                # Convert KRM to DWBA (Straight Centerline)
                x_b = np.array(data.get("x_b", []))
                z_bU = np.array(data.get("z_bU", []))

                # Assume straight centerline on X axis
                output_shape["x"] = x_b.tolist()
                output_shape["y"] = np.zeros_like(x_b).tolist()
                output_shape["z"] = np.zeros_like(x_b).tolist()
                # Radius = z_bU (assuming circular body of revolution)
                output_shape["a"] = z_bU.tolist()

            if output_shape["x"]:
                if source_type == "DWBA":
                    # Recalculate arc length properly if it was bent
                    x_arr = np.array(output_shape["x"])
                    y_arr = np.array(output_shape["y"])
                    z_arr = np.array(output_shape["z"])
                    if len(x_arr) > 1:
                        length = np.sum(
                            np.sqrt(
                                np.diff(x_arr)**2 +
                                np.diff(y_arr)**2 +
                                np.diff(z_arr)**2
                            )
                        )
                    else:
                        length = 0.0
                else:
                    length = (
                        max(output_shape["x"]) - min(output_shape["x"])
                    )

                output_shape["length"] = float(f"{length:.4f}")

        # Wrap in list
        toml_data = {"shape": [output_shape]}

        # Dialog
        default_filename = selected_name.replace(
            " ", "_"
        ).replace("(", "").replace(
            ")", ""
        ).replace("=", "").replace(",", "_") + ".toml"

        file_path = filedialog.asksaveasfilename(
            title="Save Shape to TOML",
            initialfile=default_filename,
            defaultextension=".toml",
            filetypes=[("TOML Files", "*.toml"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    rtoml.dump(toml_data, f)
                messagebox.showinfo(
                    "Success", f"Shape saved to:\n{file_path}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Shapes TOML File",
            filetypes=[("TOML Files", "*.toml"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_shapes_from_file(file_path)

    def load_shapes_from_file(self, file_path):
        self.file_path_var.set(file_path)
        self.all_shapes = {}

        try:
            with open(file_path, 'rb') as f:
                data = tomllib.load(f)

            shapes_list = data.get("shape", [])
            if not shapes_list:
                messagebox.showwarning("No Shapes", "No 'shape' list found.")
                return

            for shape in shapes_list:
                name = shape.get("name", "Unknown")
                data_format = shape.get("data_format", "").lower()
                model_type = None
                if data_format == "echosms_krm":
                    model_type = "KRM"
                elif data_format == "echosms_dwba":
                    model_type = "DWBA"

                if model_type:
                    self.all_shapes[name] = {
                        'data': shape, 'model_type': model_type
                    }

            shape_names = sorted(self.all_shapes.keys())
            self.shape_selector['values'] = shape_names
            if shape_names:
                self.shape_selector.current(0)
                self.refresh_plot()
            else:
                self.shape_selector.set('')
                self.fig.clf()
                self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def refresh_plot_with_feedback(self, event=None):
        self.refresh_plot(event)

    def refresh_plot(self, event=None):
        # Update UI to show activity
        self.root.config(cursor="wait")
        self.update_status("Rendering...", "red")
        self.root.update_idletasks()

        # Defer execution slightly to let UI update
        self.root.after(10, self._refresh_plot_internal)

    def _refresh_plot_internal(self):
        try:
            selected_name = self.shape_selector.get()
            if selected_name in self.all_shapes:
                shape_info = self.all_shapes[selected_name]
                # Safe get
                model_type = shape_info.get('model_type', 'KRM')

                # Auto-switch to 3D for 3D-native models
                if model_type in ['KA', 'FEM', 'PTDWBA']:
                    if self.current_view_mode.get() != '3D':
                        self.current_view_mode.set('3D')

                mode = self.current_view_mode.get()

                if mode == "2D":
                    self.plot_shape_2d(
                        shape_info['data'], shape_info['model_type']
                    )
                else:
                    self.plot_shape_3d(
                        shape_info['data'], shape_info['model_type']
                    )

                self.update_info_display(shape_info['data'])
        except Exception as e:
            print(f"Plotting error: {e}")
            messagebox.showerror("Plotting Error", str(e))
        finally:
            self.root.config(cursor="")
            self.update_status("Ready.", "green")

    def plot_shape_2d(self, shape_data, model_type):
        self.fig.clf()
        ax_top = self.fig.add_subplot(211)
        ax_side = self.fig.add_subplot(212, sharex=ax_top)

        shapes_for_plot = []

        if model_type == 'KRM':
            # Body
            if "x_b" in shape_data and len(shape_data["x_b"]) > 0:
                body = outline_from_krm(
                    shape_data["x_b"],
                    shape_data["z_bU"],
                    shape_data["z_bL"],
                    shape_data["w_b"],
                    anatomical_type="body",
                    boundary="fluid-filled"
                )
                shapes_for_plot.append(body)

            # Swimbladder
            if "x_sb" in shape_data and len(shape_data["x_sb"]) > 0:
                sb = outline_from_krm(
                    shape_data["x_sb"],
                    shape_data["z_sbU"],
                    shape_data["z_sbL"],
                    shape_data["w_sb"],
                    anatomical_type="swimbladder",
                    boundary="pressure-release"
                )
                shapes_for_plot.append(sb)

        elif model_type == 'DWBA':
            if "x" in shape_data and len(shape_data["x"]) > 0:
                dwba_shape = outline_from_dwba(
                    shape_data["x"],
                    shape_data["z"],
                    shape_data["a"],
                    anatomical_type="body",
                    boundary="fluid-filled"
                )
                if "y" in shape_data:
                    dwba_shape["y"] = shape_data["y"]

                shapes_for_plot.append(dwba_shape)

        elif model_type == 'DATASTORE':
            if 'shapes' in shape_data:
                raw_shapes = shape_data['shapes']
                for s in raw_shapes:
                    # Ensure basics
                    if 'boundary' not in s:
                        s['boundary'] = 'fluid-filled'
                    if 'anatomical_type' not in s:
                        s['anatomical_type'] = 'body'

                    shapes_for_plot.append(s)

        if shapes_for_plot:
            # Custom plotting to fix coordinate axis issues
            # We do NOT use plot_shape_outline because it enforces
            # inverted axes

            # 1. Determine Global Coordinate Transform based on Body
            x_mult = 1.0

            # Find body
            body_s = next(
                (s for s in shapes_for_plot
                 if s.get('anatomical_type') == 'body' and 'x' in s),
                shapes_for_plot[0]
            )
            if 'x' in body_s:
                bx = np.array(body_s['x'])
                if len(bx) > 0 and np.mean(bx) < 0:
                    x_mult = -1.0  # Flip negative coordinates to positive

            for s in shapes_for_plot:
                # Determine colors
                c = 'C0' if s.get('boundary') == 'fluid-filled' else 'C1'

                # Check if Outline or Surface
                if 'facets_0' in s:
                    # Surface - Point Cloud Projection
                    x = np.array(s.get('x', [])) * 100
                    y = np.array(s.get('y', [])) * 100
                    z = np.array(s.get('z', [])) * 100

                    # Apply Global Transform
                    x = x * x_mult
                    z = -z  # Always invert Z (Depth -> Height)

                    ax_top.plot(x, y, '.', color=c, markersize=1, alpha=0.5)
                    ax_side.plot(x, z, '.', color=c, markersize=1, alpha=0.5)

                elif 'width' in s and 'height' in s:
                    # Outline - Line Plot
                    x = np.array(s.get('x', [])) * 100
                    y = np.array(s.get('y', [])) * 100
                    z = np.array(s.get('z', [])) * 100
                    w = np.array(s.get('width', [])) * 100
                    h = np.array(s.get('height', [])) * 100

                    # Apply Global Transform
                    if model_type == 'DATASTORE':
                        x = x * x_mult
                        z = -z
                    elif model_type == 'KRM':
                        z = -z
                    elif model_type == 'DWBA':
                        # DWBA Local File Fix:
                        # Head is typically at max X, so flip to 0
                        if len(x) > 0:
                            x = np.max(x) - x

                    # Calculate Edges

                    y_top = y + w / 2.0
                    y_bot = y - w / 2.0
                    z_top = z + h / 2.0
                    z_bot = z - h / 2.0

                    # Plot Dorsal
                    ax_top.plot(x, y, 'k:', linewidth=0.5, alpha=0.5)
                    ax_top.plot(x, y_top, color=c)
                    ax_top.plot(x, y_bot, color=c)
                    # Close loop
                    ax_top.plot(
                        [x[0], x[0]], [y_top[0], y_bot[0]], color=c
                    )
                    ax_top.plot(
                        [x[-1], x[-1]], [y_top[-1], y_bot[-1]], color=c
                    )

                    # Plot Lateral
                    ax_side.plot(x, z, 'k:', linewidth=0.5, alpha=0.5)
                    ax_side.plot(x, z_top, color=c)
                    ax_side.plot(x, z_bot, color=c)
                    # Close loop
                    ax_side.plot(
                        [x[0], x[0]], [z_top[0], z_bot[0]], color=c
                    )
                    ax_side.plot(
                        [x[-1], x[-1]], [z_top[-1], z_bot[-1]], color=c
                    )

                elif ('mass_density' in s or 'categories' in s) \
                        and 'voxel_size' in s:
                    # Voxels
                    try:
                        # Determine data source
                        data = None
                        if 'mass_density' in s:
                            temp = np.array(s['mass_density'])
                            if temp.ndim == 3:
                                data = temp

                        if data is None and 'categories' in s:
                            temp = np.array(s['categories'])
                            if temp.ndim == 3:
                                data = temp

                        if data is None:
                            print(
                                "Skipping voxels: valid 3D data not "
                                "found in mass_density or categories."
                            )
                            continue

                        v_size = np.array(s['voxel_size']) * 100

                        # FEM/PTDWBA Fix: (H, L, W) -> (L, W, H)
                        inner_model = shape_data.get('model_type', '')
                        if inner_model in ['FEM', 'PTDWBA'] or \
                           model_type in ['FEM', 'PTDWBA']:
                            # Transpose: 0->2(H), 1->0(L), 2->1(W)
                            data = np.transpose(data, (1, 2, 0))
                            v_size = v_size[[1, 2, 0]]
                            # Flip Length (Axis 0) to put Head at Left (0)
                            data = np.flip(data, axis=0)

                        nx, ny, nz = data.shape
                        lx = nx * v_size[0]
                        ly = ny * v_size[1]
                        lz = nz * v_size[2]

                        # Projections
                        # Dorsal (Top): Collapse Z (axis 2) -> (X, Y) = (L, W)
                        dorsal_proj = np.max(data, axis=2).T

                        # Lateral: Collapse Y (axis 1) -> (X, Z)=(L, H)
                        lateral_proj = np.max(data, axis=1).T

                        # Extent: Center Y/Z, Start X at 0.
                        extent_top = [0, lx, -ly / 2, ly / 2]
                        extent_side = [0, lx, -lz / 2, lz / 2]

                        ax_top.imshow(
                            dorsal_proj, aspect='equal', origin='lower',
                            extent=extent_top, cmap='viridis'
                        )
                        ax_side.imshow(
                            lateral_proj, aspect='equal', origin='lower',
                            extent=extent_side, cmap='viridis'
                        )

                    except Exception as e:
                        print(f"Error plotting voxels: {e}")

        # Track global bounds
        g_min_x, g_max_x = float('inf'), float('-inf')
        g_min_y, g_max_y = float('inf'), float('-inf')
        g_min_z, g_max_z = float('inf'), float('-inf')

        if shapes_for_plot:
            for s in shapes_for_plot:
                # Re-calculate transform locally for bounds
                tx, ty, tz = np.array([]), np.array([]), np.array([])

                # Align Z-transform with plotting logic
                z_sign = -1.0
                if model_type == 'DWBA':
                    z_sign = 1.0

                if 'facets_0' in s:
                    tx = np.array(s.get('x', [])) * 100 * x_mult
                    ty = np.array(s.get('y', [])) * 100
                    tz = np.array(s.get('z', [])) * 100 * z_sign
                elif 'width' in s:
                    tx = np.array(s.get('x', [])) * 100 * x_mult
                    ty = np.array(s.get('y', [])) * 100
                    tz = np.array(s.get('z', [])) * 100 * z_sign
                    w = np.array(s.get('width', [])) * 100
                    h = np.array(s.get('height', [])) * 100
                    # For outlines, bounds are determined by width/height edges
                    if len(ty) > 0:
                        g_min_y = min(g_min_y, np.min(ty - w / 2))
                        g_max_y = max(g_max_y, np.max(ty + w / 2))
                        g_min_z = min(g_min_z, np.min(tz - h / 2))
                        g_max_z = max(g_max_z, np.max(tz + h / 2))

                elif 'mass_density' in s and 'voxel_size' in s:
                    # Voxel bounds (approx)
                    try:
                        v = np.array(s['mass_density']).shape
                        vs = np.array(s['voxel_size']) * 100

                        # FEM/PTDWBA Fix
                        inner_model = shape_data.get('model_type', '')
                        if inner_model in ['FEM', 'PTDWBA'] or \
                           model_type in ['FEM', 'PTDWBA']:
                            v = (v[1], v[2], v[0])
                            vs = (vs[1], vs[2], vs[0])

                        lx = v[0] * vs[0]
                        ly = v[1] * vs[1]
                        lz = v[2] * vs[2]
                        # Check if x needs shift? In plot loop we use
                        # origin='lower' extent=[0, lx...]
                        # So X bounds are 0 to lx.
                        tx = np.array([0, lx])
                        g_min_y = min(g_min_y, -ly / 2)
                        g_max_y = max(g_max_y, ly / 2)
                        g_min_z = min(g_min_z, -lz / 2)
                        g_max_z = max(g_max_z, lz / 2)
                    except Exception:
                        pass

                if len(tx) > 0:
                    g_min_x = min(g_min_x, np.min(tx))
                    g_max_x = max(g_max_x, np.max(tx))
                    if 'facets_0' in s:  # Surface bounds
                        g_min_y = min(g_min_y, np.min(ty))
                        g_max_y = max(g_max_y, np.max(ty))
                        g_min_z = min(g_min_z, np.min(tz))
                        g_max_z = max(g_max_z, np.max(tz))

            # Apply Limits with Padding
            if g_min_x != float('inf'):
                # Calculate max span to ensure 1:1 ratio fits
                span_x = g_max_x - g_min_x
                span_y = g_max_y - g_min_y
                span_z = g_max_z - g_min_z

                # The shared X axis must be large enough to accommodate the
                # aspect ratio of the "tallest" other axis
                # Matplotlib's 'datalim' might struggle with shared axes.
                # We can try to force a bounding box that is large enough.

                max_span = max(span_x, span_y, span_z * 2.5)

                # Center X
                mid_x = (g_max_x + g_min_x) / 2
                ax_top.set_xlim(
                    [mid_x - max_span / 2 * 1.1, mid_x + max_span / 2 * 1.1]
                )

                # Y and Z set to their own bounds (with padding)
                # We also center them
                mid_y = (g_max_y + g_min_y) / 2
                # Ensure Y view isn't too tight if Y is tiny
                view_h_y = max(span_y, max_span / 5.0)
                ax_top.set_ylim(
                    [mid_y - view_h_y / 2 * 1.2, mid_y + view_h_y / 2 * 1.2]
                )

                mid_z = (g_max_z + g_min_z) / 2
                # Ensure Z view isn't too tight
                view_h_z = max(span_z, max_span / 5.0)
                ax_side.set_ylim(
                    [mid_z - view_h_z / 2 * 1.2, mid_z + view_h_z / 2 * 1.2]
                )

            v_name = shape_data.get(
                "vernacular_name", shape_data.get("name", "Unknown")
            )
            ax_top.set_title(f'{v_name} (Dorsal)')
            ax_top.set_ylabel('Width (cm)', labelpad=10)

            # Smart Grid & Aspect: Disable grid and use 'auto' aspect for
            # Voxel/Surface (CT/Mesh)
            # Enable grid and use 'equal' aspect for Outlines (KRM/SDWBA)
            is_voxel_or_surface = any(
                (('mass_density' in s or 'categories' in s)
                 and 'voxel_size' in s) or
                ('facets_0' in s)
                for s in shapes_for_plot
            )
            show_grid = not is_voxel_or_surface

            ax_top.grid(show_grid)

            # Aspect Ratio & Padding Logic
            if is_voxel_or_surface:
                # Use 'box' adjustment to shrink the axes area to fit the
                # image exactly (no white padding)
                # This makes it look like Figure_2.png where the image IS
                # the frame.
                ax_top.set_aspect('equal', adjustable='box')
                ax_side.set_aspect('equal', adjustable='box')

                # Force tight limits to remove any remaining internal padding
                # Note: lx, ly, lz are calculated in the voxel block above
                if 'lx' in locals():
                    ax_top.set_xlim(0, lx)
                    ax_top.set_ylim(-ly / 2, ly / 2)
                    ax_side.set_ylim(-lz / 2, lz / 2)
            else:
                # For Outlines, use 'datalim' to allow flexible window
                # resizing while keeping 1:1
                ax_top.set_aspect('equal', adjustable='datalim')
                ax_side.set_aspect('equal', adjustable='datalim')

            v_name = shape_data.get(
                "vernacular_name", shape_data.get("name", "Unknown")
            )
            ax_top.set_title(f'{v_name} (Dorsal)')
            ax_top.set_ylabel('Width (cm)', labelpad=10)

            ax_side.set_title('Lateral View')
            ax_side.set_xlabel('Length (cm)', labelpad=10)
            ax_side.set_ylabel('Height (cm)', labelpad=10)
            ax_side.grid(show_grid)

        plt.tight_layout()
        self.canvas.draw()

    def plot_shape_3d(self, shape_data, model_type):
        self.fig.clf()
        self.ax = self.fig.add_subplot(111, projection='3d')

        theta = np.linspace(0, 2 * np.pi, 30)

        if model_type == 'KRM':
            self.ax.set_xlabel('X (Length) [cm]', labelpad=10)
            self.ax.set_ylabel('Y (Width) [cm]', labelpad=10)
            self.ax.set_zlabel('Z (Height) [cm]', labelpad=10)

            x_b = np.array(shape_data.get("x_b", [])) * 100
            z_bU = np.array(shape_data.get("z_bU", [])) * 100
            z_bL = np.array(shape_data.get("z_bL", [])) * 100
            w_b = np.array(shape_data.get("w_b", [])) * 100

            if len(x_b) > 0:
                if len(w_b) != len(x_b):  # Fallback if width not provided
                    w_b = z_bU - z_bL

                z_c = (z_bU + z_bL) / 2.0
                r_z = (z_bU - z_bL) / 2.0
                r_y = w_b / 2.0

                X = np.tile(x_b[:, np.newaxis], (1, len(theta)))
                Y = r_y[:, np.newaxis] * np.cos(theta)
                Z = z_c[:, np.newaxis] + r_z[:, np.newaxis] * np.sin(theta)

                self.ax.plot_surface(
                    X, Y, Z, color='cyan', alpha=0.3, edgecolor='none'
                )
                self.ax.plot_wireframe(
                    X, Y, Z, color='cyan', rstride=5, cstride=5, alpha=0.2,
                    linewidth=0.5
                )

            x_sb = np.array(shape_data.get("x_sb", [])) * 100
            z_sbU = np.array(shape_data.get("z_sbU", [])) * 100
            z_sbL = np.array(shape_data.get("z_sbL", [])) * 100
            w_sb = np.array(shape_data.get("w_sb", [])) * 100

            if len(x_sb) > 0:
                if len(w_sb) != len(x_sb):
                    w_sb = z_sbU - z_sbL

                z_c_sb = (z_sbU + z_sbL) / 2.0
                r_z_sb = (z_sbU - z_sbL) / 2.0
                r_y_sb = w_sb / 2.0

                X_sb = np.tile(x_sb[:, np.newaxis], (1, len(theta)))
                Y_sb = r_y_sb[:, np.newaxis] * np.cos(theta)
                Z_sb = (z_c_sb[:, np.newaxis] +
                        r_z_sb[:, np.newaxis] * np.sin(theta))

                self.ax.plot_surface(
                    X_sb, Y_sb, Z_sb, color='white', alpha=0.9,
                    edgecolor='none'
                )

        elif model_type == 'DWBA':
            self.ax.set_xlabel('X (Length) [mm]', labelpad=10)
            self.ax.set_ylabel('Y (Width) [mm]', labelpad=10)
            self.ax.set_zlabel('Z (Height) [mm]', labelpad=10)

            x = np.array(shape_data.get("x", []))
            if len(x) > 0:
                default_zeros = np.zeros(len(x))
            else:
                default_zeros = []
            y = np.array(shape_data.get("y", default_zeros))
            z = np.array(shape_data.get("z", default_zeros))
            a = np.array(shape_data.get("a", []))

            if len(x) > 0 and len(a) > 0:
                x = x * 1000
                y = y * 1000
                z = z * 1000
                a = a * 1000

                x = np.max(x) - x
                y = -y
                z = -z

                X = np.tile(x[:, np.newaxis], (1, len(theta)))
                Y = y[:, np.newaxis] + a[:, np.newaxis] * np.cos(theta)
                Z = z[:, np.newaxis] + a[:, np.newaxis] * np.sin(theta)

                self.ax.plot_surface(
                    X, Y, Z, color='cyan', alpha=0.4, edgecolor='k',
                    linewidth=0.1
                )

        elif model_type == 'DATASTORE':
            self.ax.set_xlabel('X [cm]', labelpad=10)
            self.ax.set_ylabel('Y [cm]', labelpad=10)
            self.ax.set_zlabel('Z [cm]', labelpad=10)

            # Use user preference for grid visibility
            show_grid = self.show_grid_var.get()
            self.ax.grid(show_grid)
            if not show_grid:
                self.ax.set_facecolor('white')

            shapes = shape_data.get('shapes', [])

            # 1. Determine Global Coordinate Transform based on Body
            x_mult = 1.0
            body_s = next(
                (s for s in shapes
                 if s.get('anatomical_type') == 'body' and 'x' in s), None
            )
            if body_s:
                bx = np.array(body_s['x'])
                if len(bx) > 0 and np.mean(bx) < 0:
                    x_mult = -1.0

            for s in shapes:
                # Color logic: Body is cool cyan, internal organs are
                # warm orange
                is_body = s.get('anatomical_type') == 'body'
                color = 'cyan' if is_body else 'orange'
                alpha = 0.4 if is_body else 0.7

                # Check if Surface (Mesh)
                if 'facets_0' in s:
                    try:
                        facets = np.array(
                            [s['facets_0'], s['facets_1'], s['facets_2']]
                        ).transpose()
                        x = np.array(s['x']) * 100
                        y = np.array(s['y']) * 100
                        z = np.array(s['z']) * 100
                        x = x * x_mult
                        z = -z

                        # Use trisurf for smooth models
                        if len(facets) > 50000:
                            skip = max(1, len(x) // 15000)
                            self.ax.scatter(
                                x[::skip], y[::skip], z[::skip], c=color,
                                alpha=alpha, s=1
                            )
                        else:
                            # Use slightly higher alpha and edgecolor to
                            # reduce "holes" caused by depth sorting
                            self.ax.plot_trisurf(
                                x, y, z, triangles=facets,
                                alpha=alpha, color=color,
                                edgecolor='none', shade=True,
                                antialiased=False
                            )  # Disable antialiased to fill tiny gaps

                    except Exception as e:
                        print(f"Error plotting surface: {e}")
                    continue

                # Check if Voxels
                if ('mass_density' in s or 'categories' in s) \
                        and 'voxel_size' in s:
                    try:
                        # Determine data source
                        data = None
                        if 'mass_density' in s:
                            temp = np.array(s['mass_density'])
                            if temp.ndim == 3:
                                data = temp

                        if data is None and 'categories' in s:
                            temp = np.array(s['categories'])
                            if temp.ndim == 3:
                                data = temp

                        if data is None:
                            continue

                        v_size = np.array(s['voxel_size']) * 100  # cm

                        # FEM/PTDWBA Fix: (H, L, W) -> (L, W, H)
                        inner_model = shape_data.get('model_type', '')
                        if inner_model in ['FEM', 'PTDWBA'] or \
                           model_type in ['FEM', 'PTDWBA']:
                            data = np.transpose(data, (1, 2, 0))
                            v_size = v_size[[1, 2, 0]]
                            data = np.flip(data, axis=0)

                        nx, ny, nz = data.shape

                        # --- Professional Turbo Gradient Reconstruction ---
                        d_min, d_max = np.min(data), np.max(data)
                        if d_max > d_min:
                            # Use 6% threshold to filter background while
                            # keeping flesh
                            thresh_bg = d_min + 0.06 * (d_max - d_min)

                            def get_surface_indices(binary_mask):
                                if np.sum(binary_mask) == 0:
                                    return [], [], []
                                padded = np.pad(
                                    binary_mask, 1, mode='constant',
                                    constant_values=0
                                )
                                n_sum = (
                                    padded[:-2, 1:-1, 1:-1].astype(int) +
                                    padded[2:, 1:-1, 1:-1].astype(int) +
                                    padded[1:-1, :-2, 1:-1].astype(int) +
                                    padded[1:-1, 2:, 1:-1].astype(int) +
                                    padded[1:-1, 1:-1, :-2].astype(int) +
                                    padded[1:-1, 1:-1, 2:].astype(int)
                                )
                                surf = binary_mask & (n_sum < 6)
                                return np.where(surf)

                            mask = data > thresh_bg
                            ix, iy, iz = get_surface_indices(mask)

                            if len(ix) > 0:
                                voxel_values = data[ix, iy, iz]
                                xs = ix * v_size[0]
                                ys = (iy - ny / 2) * v_size[1]
                                zs = (iz - nz / 2) * v_size[2]
                                z_mult = -1.0 if inner_model not in [
                                    'FEM', 'PTDWBA'
                                ] else 1.0

                                # Sampling for GUI performance
                                if len(ix) > 100000:
                                    skip = len(ix) // 100000
                                    xs = xs[::skip]
                                    ys = ys[::skip]
                                    zs = zs[::skip]
                                    voxel_values = voxel_values[::skip]

                                # 2. Map Colors and Alphas
                                norm = plt.Normalize(
                                    vmin=thresh_bg, vmax=d_max
                                )
                                colors = plt.get_cmap('turbo')(
                                    norm(voxel_values)
                                )
                                alphas = (
                                    (voxel_values - thresh_bg) /
                                    (d_max - thresh_bg)
                                ) ** 1.2
                                colors[:, 3] = alphas * 0.6 + 0.1

                                self.ax.scatter(
                                    xs, ys, zs * z_mult, c=colors, s=1,
                                    edgecolors='none', depthshade=True
                                )

                    except Exception as e:
                        print(f"Error plotting 3D voxels: {e}")
                    continue

                # Else assume Outline
                x = np.array(s.get('x', [])) * 100  # cm
                y = np.array(s.get('y', [])) * 100
                z = np.array(s.get('z', [])) * 100
                w = np.array(s.get('width', [])) * 100
                h = np.array(s.get('height', [])) * 100

                # Transform
                x = x * x_mult
                z = -z

                if len(x) > 1 and len(w) > 0:
                    r_y = w / 2.0
                    r_z = h / 2.0

                    X = np.tile(x[:, np.newaxis], (1, len(theta)))
                    Y = (np.tile(y[:, np.newaxis], (1, len(theta))) +
                         r_y[:, np.newaxis] * np.cos(theta))
                    Z = (np.tile(z[:, np.newaxis], (1, len(theta))) +
                         r_z[:, np.newaxis] * np.sin(theta))

                    self.ax.plot_surface(
                        X, Y, Z, color=color, alpha=alpha, edgecolor='none'
                    )

        self.ax.set_title(f'{shape_data.get("name", "Unknown")} (3D View)')
        self.ax.set_xlabel('X [cm]')
        self.ax.set_ylabel('Y [cm]')
        self.ax.set_zlabel('Z [cm]')
        try:
            self.set_axes_equal(self.ax)
        except Exception as e:
            print(f"Warning: set_axes_equal failed: {e}")
        self.canvas.draw()

    def set_axes_equal(self, ax):
        """Make axes of 3D plot have equal scale and force a cubic
        bounding box.
        """
        try:
            # Get current limits
            xlim = ax.get_xlim3d()
            ylim = ax.get_ylim3d()
            zlim = ax.get_zlim3d()

            x_range = abs(xlim[1] - xlim[0])
            y_range = abs(ylim[1] - ylim[0])
            z_range = abs(zlim[1] - zlim[0])

            # Determine maximum range to create a cube
            max_range = max(x_range, y_range, z_range)

            # Add some padding (10%) so data isn't touching the walls
            max_range *= 1.1

            # Calculate centers
            x_mid = np.mean(xlim)
            y_mid = np.mean(ylim)
            z_mid = np.mean(zlim)

            # Set new limits so all axes span the same amount (max_range)
            ax.set_xlim3d([x_mid - max_range / 2, x_mid + max_range / 2])
            ax.set_ylim3d([y_mid - max_range / 2, y_mid + max_range / 2])
            ax.set_zlim3d([z_mid - max_range / 2, z_mid + max_range / 2])

            # Force the display box to be a cube (1:1:1 aspect)
            # This combined with equal limits ensures 1:1 data scaling
            ax.set_box_aspect((1, 1, 1))

        except Exception as e:
            print(f"Warning: set_axes_equal failed: {e}")

    def update_info_display(self, shape_data):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        def summarize(val):
            if isinstance(val, np.ndarray):
                return f"<Array shape={val.shape} dtype={val.dtype}>"
            elif isinstance(val, list):
                if len(val) > 10:
                    return f"<List len={len(val)}>"
                # Check if list contains dicts (e.g. shapes list)
                if len(val) > 0 and isinstance(val[0], dict):
                    return f"<List of {len(val)} Dicts>"
                return str(val)
            return str(val)

        for key, value in shape_data.items():
            self.info_text.insert(tk.END, f"{key}: {summarize(value)}\n")
        self.info_text.config(state=tk.DISABLED)

    def on_mouse_wheel(self, event):
        """Interactive zoom for both 2D and 3D plots."""
        if not self.fig.axes:
            return

        # Zoom factor
        scale_factor = 1.1 if event.num == 5 or event.delta < 0 else 0.9

        for ax in self.fig.axes:
            if hasattr(ax, 'get_zlim'):
                cur_xlim = ax.get_xlim()
                cur_ylim = ax.get_ylim()
                cur_zlim = ax.get_zlim()
                new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
                new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
                new_depth = (cur_zlim[1] - cur_zlim[0]) * scale_factor
                x_mid = sum(cur_xlim) / 2
                y_mid = sum(cur_ylim) / 2
                z_mid = sum(cur_zlim) / 2
                ax.set_xlim([x_mid - new_width / 2, x_mid + new_width / 2])
                ax.set_ylim([y_mid - new_height / 2, y_mid + new_height / 2])
                ax.set_zlim([z_mid - new_depth / 2, z_mid + new_depth / 2])
            else:
                cur_xlim = ax.get_xlim()
                cur_ylim = ax.get_ylim()
                new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
                new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
                ax.set_xlim([cur_xlim[0], cur_xlim[0] + new_width])
                ax.set_ylim([cur_ylim[0], cur_ylim[0] + new_height])
        self.canvas.draw()

    def show_context_menu(self, event):
        """Display the right-click menu."""
        self.context_menu.post(event.x_root, event.y_root)

    def toggle_grid(self):
        """Toggle grid visibility from context menu."""
        self.show_grid_var.set(not self.show_grid_var.get())
        self.refresh_plot()


def main():
    root = tk.Tk()
    ShapeViewerComboApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
