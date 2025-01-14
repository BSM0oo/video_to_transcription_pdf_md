import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from app import process_video, get_working_dir
import threading

print("Starting GUI application...")  # Debug print

class App(tk.Tk):
    def __init__(self):
        print("Initializing App...")  # Debug print
        super().__init__()

        self.title("Video to PDF Converter")
        self.geometry("600x400")
        
        # Configure main window
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create main frame
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.columnconfigure(0, weight=1)

        # Create file selection button
        self.select_button = ttk.Button(
            main_frame,
            text="Select Video File",
            command=self.browse_file,
            padding=10
        )
        self.select_button.grid(row=0, column=0, pady=20, sticky="ew")

        # Create options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options")
        options_frame.grid(row=1, column=0, pady=20, sticky="ew")

        # Extraction method
        ttk.Label(options_frame, text="Extraction method:").grid(row=0, column=0, padx=5, pady=5)
        self.method_var = tk.StringVar(value="1")
        
        # Add callback before creating radio buttons
        def on_method_change(*args):
            print(f"Method changed to: {self.method_var.get()}")  # Debug print
            if self.method_var.get() == "1":
                self.param_label.config(text="Interval (seconds):")
                self.param_var.set("0.5")
            else:
                self.param_label.config(text="Scene threshold:")
                self.param_var.set("0.3")

        self.method_var.trace_add("write", on_method_change)
        
        # Create radio buttons
        ttk.Radiobutton(options_frame, text="Fixed intervals", variable=self.method_var, value="1").grid(row=0, column=1, padx=5, pady=5)
        ttk.Radiobutton(options_frame, text="Scene detection", variable=self.method_var, value="2").grid(row=0, column=2, padx=5, pady=5)

        # Interval/threshold
        self.param_label = ttk.Label(options_frame, text="Interval (seconds):")
        self.param_label.grid(row=1, column=0, padx=5, pady=5)
        self.param_var = tk.StringVar(value="0.5")
        self.param_entry = ttk.Entry(options_frame, textvariable=self.param_var, width=10)
        self.param_entry.grid(row=1, column=1, padx=5, pady=5)

        # OCR option
        self.ocr_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Extract text (OCR)", variable=self.ocr_var).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, pady=20)

        # Add Start Processing button
        self.start_button = ttk.Button(
            buttons_frame,
            text="Start Processing",
            command=self.start_processing,
            state='disabled'  # Initially disabled
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(buttons_frame, text="Open Output Folder", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        # Progress bar and label
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_label = ttk.Label(progress_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Store selected file path
        self.selected_file = None

    def update_param_label(self, *args):
        print(f"Updating param label for method: {self.method_var.get()}")  # Debug print
        if self.method_var.get() == "1":
            self.param_label.config(text="Interval (seconds):")
            self.param_var.set("0.5")
        else:
            self.param_label.config(text="Scene threshold:")
            self.param_var.set("0.3")

    def browse_file(self, event=None):
        print("Browse file dialog opened")  # Debug print
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if file_path:
            print(f"Selected file: {file_path}")  # Debug print
            self.selected_file = file_path
            self.start_button.config(state='normal')  # Enable start button
            self.status_label.config(text=f"Selected: {os.path.basename(file_path)}")

    def start_processing(self):
        if self.selected_file:
            self.process_video_file(self.selected_file)
            self.start_button.config(state='disabled')  # Disable during processing

    def update_ui(self, status, is_error=False):
        """Thread-safe UI updates"""
        self.after(0, self._do_update_ui, status, is_error)

    def _do_update_ui(self, status, is_error):
        """Perform UI updates on the main thread"""
        self.status_label.config(text=status)
        if status == "Complete!":
            self.progress.stop()
            self.start_button.config(state='normal')
            messagebox.showinfo("Success", "Processing completed successfully!")
        elif is_error:
            self.progress.stop()
            self.start_button.config(state='normal')
            messagebox.showerror("Error", status)

    def process_video_file(self, file_path):
        def process():
            try:
                self.progress.start(10)
                self.update_ui("Processing...")
                
                process_video(
                    file_path,
                    method=self.method_var.get(),
                    param=float(self.param_var.get()),
                    extract_text=self.ocr_var.get()
                )
                
                self.update_ui("Complete!")
            except Exception as e:
                self.update_ui(str(e), is_error=True)

        thread = threading.Thread(target=process)
        thread.start()

    def open_output_folder(self):
        working_dir = get_working_dir()
        os.system(f'open "{working_dir}"')

if __name__ == "__main__":
    try:
        print("Creating App instance...")  # Debug print
        app = App()
        print("Starting mainloop...")  # Debug print
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")  # Debug print
        raise
