import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from ai_detector import AIDetector, SecurityError
from config import Config
from settings_dialog import SettingsDialog
import threading
import os
import logging
from datetime import datetime
import shutil
from pathlib import Path

class AIDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.config = Config()
        
        # Apply UI settings
        self.root.title("AI Text Detector")
        self.root.geometry(f"{self.config.get('ui.window_size.width')}x{self.config.get('ui.window_size.height')}")
        self.root.minsize(
            self.config.get('ui.min_window_size.width'),
            self.config.get('ui.min_window_size.height')
        )
        
        # Configure security logging
        self.log_file = f"security_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.security_logger = logging.getLogger('security')
        self.security_logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.security_logger.addHandler(handler)
        
        # Initialize the AI detector with security parameters
        try:
            self.detector = AIDetector(
                max_text_length=self.config.get('security.max_text_length'),
                max_file_size=self.config.get('security.max_file_size')
            )
        except SecurityError as e:
            messagebox.showerror("Security Error", f"Failed to initialize detector: {str(e)}")
            self.root.destroy()
            return
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.text_tab = ttk.Frame(self.notebook)
        self.file_tab = ttk.Frame(self.notebook)
        self.batch_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.text_tab, text="Text Input")
        self.notebook.add(self.file_tab, text="File Input")
        self.notebook.add(self.batch_tab, text="Batch Processing")
        
        self._create_text_tab()
        self._create_file_tab()
        self._create_batch_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Security info
        self.security_info = ttk.Label(root, text="Security: Active", foreground="green")
        self.security_info.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Clean up old logs
        self._cleanup_old_logs()

    def _create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
    
    def _show_settings(self):
        def on_save():
            # Reinitialize detector with new settings
            try:
                self.detector = AIDetector(
                    max_text_length=self.config.get('security.max_text_length'),
                    max_file_size=self.config.get('security.max_file_size')
                )
                # Update UI
                self._update_ui_settings()
            except SecurityError as e:
                messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")
        
        SettingsDialog(self.root, self.config, on_save)
    
    def _update_ui_settings(self):
        # Update theme
        theme = self.config.get('ui.theme')
        if theme == 'dark':
            # Apply dark theme
            self.root.tk_setPalette(background='#2b2b2b', foreground='#ffffff')
        else:
            # Apply light theme
            self.root.tk_setPalette(background='#ffffff', foreground='#000000')
        
        # Update font size
        font_size = self.config.get('ui.font_size')
        style = ttk.Style()
        style.configure('.', font=('TkDefaultFont', font_size))
    
    def _show_about(self):
        about_text = """
AI Text Detector

Version: 1.0.0
Author: Your Name

This tool helps detect AI-generated text using multiple models
and analysis techniques. It provides a user-friendly interface
for analyzing text, files, and directories.

Security features:
- Input validation and sanitization
- Rate limiting
- File type restrictions
- Comprehensive logging
"""
        messagebox.showinfo("About", about_text)
    
    def _show_documentation(self):
        doc_text = """
Documentation

1. Text Input Tab:
   - Enter text directly in the text area
   - Click 'Analyze Text' to process
   - Results show AI/Human classification and confidence

2. File Input Tab:
   - Select a text file to analyze
   - Click 'Analyze File' to process
   - Results show classification for the entire file

3. Batch Processing Tab:
   - Select a directory containing text files
   - Click 'Analyze Directory' to process all files
   - Results show classification for each file

Settings:
- Security: Configure limits and restrictions
- Models: Choose and configure detection models
- UI: Customize appearance and behavior
- Analysis: Adjust detection parameters

For more information, visit the project repository.
"""
        messagebox.showinfo("Documentation", doc_text)
    
    def _cleanup_old_logs(self):
        log_dir = Path(".")
        retention_days = self.config.get('security.log_retention_days')
        current_time = datetime.now()
        
        for log_file in log_dir.glob("security_log_*.log"):
            try:
                # Extract date from filename
                date_str = log_file.stem.split('_')[2:4]  # Get date and time parts
                if len(date_str) == 2:
                    file_date = datetime.strptime('_'.join(date_str), '%Y%m%d_%H%M%S')
                    if (current_time - file_date).days > retention_days:
                        log_file.unlink()
            except Exception as e:
                self._log_security_event("Log Cleanup Error", str(e))

    def _log_security_event(self, event_type: str, details: str):
        """Log security-related events"""
        self.security_logger.info(f"{event_type}: {details}")

    def _create_text_tab(self):
        # Text input area
        ttk.Label(self.text_tab, text="Enter text to analyze:").pack(pady=5)
        self.text_input = scrolledtext.ScrolledText(self.text_tab, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Analyze button
        ttk.Button(self.text_tab, text="Analyze Text", command=self._analyze_text).pack(pady=5)
        
        # Results area
        self.text_result = ttk.Label(self.text_tab, text="")
        self.text_result.pack(pady=5)

    def _create_file_tab(self):
        # File selection
        file_frame = ttk.Frame(self.file_tab)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(file_frame, text="Select File", command=self._select_file).pack(side=tk.LEFT, padx=5)
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Analyze button
        ttk.Button(self.file_tab, text="Analyze File", command=self._analyze_file).pack(pady=5)
        
        # Results area
        self.file_result = ttk.Label(self.file_tab, text="")
        self.file_result.pack(pady=5)

    def _create_batch_tab(self):
        # Directory selection
        dir_frame = ttk.Frame(self.batch_tab)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(dir_frame, text="Select Directory", command=self._select_directory).pack(side=tk.LEFT, padx=5)
        self.dir_path_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.dir_path_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Results area
        self.batch_result = scrolledtext.ScrolledText(self.batch_tab, height=15)
        self.batch_result.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Analyze button
        ttk.Button(self.batch_tab, text="Analyze Directory", command=self._analyze_directory).pack(pady=5)

    def _analyze_text(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to analyze")
            return
        
        self.status_var.set("Analyzing...")
        self.text_result.config(text="Analyzing...")
        
        def analyze():
            try:
                self._log_security_event("Text Analysis", "Starting text analysis")
                label, confidence = self.detector.detect(text)
                self.text_result.config(text=f"Result: {label} (Confidence: {confidence:.2%})")
                self.status_var.set("Analysis complete")
                self._log_security_event("Text Analysis", f"Completed: {label} ({confidence:.2%})")
            except SecurityError as e:
                self._log_security_event("Security Error", str(e))
                self.text_result.config(text=f"Security Error: {str(e)}")
                self.status_var.set("Security error occurred")
                messagebox.showerror("Security Error", str(e))
            except Exception as e:
                self._log_security_event("Error", str(e))
                self.text_result.config(text=f"Error: {str(e)}")
                self.status_var.set("Error occurred")
        
        threading.Thread(target=analyze).start()

    def _select_file(self):
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                self._log_security_event("File Selection", f"Selected file: {file_path}")
                self.file_path_var.set(file_path)
        except Exception as e:
            self._log_security_event("File Selection Error", str(e))
            messagebox.showerror("Error", f"Failed to select file: {str(e)}")

    def _analyze_file(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        
        self.status_var.set("Analyzing file...")
        self.file_result.config(text="Analyzing...")
        
        def analyze():
            try:
                self._log_security_event("File Analysis", f"Starting analysis of {file_path}")
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                label, confidence = self.detector.detect(text)
                self.file_result.config(text=f"Result: {label} (Confidence: {confidence:.2%})")
                self.status_var.set("Analysis complete")
                self._log_security_event("File Analysis", f"Completed: {label} ({confidence:.2%})")
            except SecurityError as e:
                self._log_security_event("Security Error", str(e))
                self.file_result.config(text=f"Security Error: {str(e)}")
                self.status_var.set("Security error occurred")
                messagebox.showerror("Security Error", str(e))
            except Exception as e:
                self._log_security_event("Error", str(e))
                self.file_result.config(text=f"Error: {str(e)}")
                self.status_var.set("Error occurred")
        
        threading.Thread(target=analyze).start()

    def _select_directory(self):
        try:
            dir_path = filedialog.askdirectory()
            if dir_path:
                self._log_security_event("Directory Selection", f"Selected directory: {dir_path}")
                self.dir_path_var.set(dir_path)
        except Exception as e:
            self._log_security_event("Directory Selection Error", str(e))
            messagebox.showerror("Error", f"Failed to select directory: {str(e)}")

    def _analyze_directory(self):
        dir_path = self.dir_path_var.get()
        if not dir_path:
            messagebox.showwarning("Warning", "Please select a directory first")
            return
        
        self.status_var.set("Analyzing directory...")
        self.batch_result.delete("1.0", tk.END)
        self.batch_result.insert(tk.END, "Analyzing...\n")
        
        def analyze():
            try:
                self._log_security_event("Batch Analysis", f"Starting analysis of directory: {dir_path}")
                results = []
                for filename in os.listdir(dir_path):
                    if filename.endswith('.txt'):
                        file_path = os.path.join(dir_path, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                text = file.read()
                            label, confidence = self.detector.detect(text)
                            results.append(f"{filename}: {label} (Confidence: {confidence:.2%})\n")
                            self._log_security_event("File Analysis", f"Completed {filename}: {label} ({confidence:.2%})")
                        except SecurityError as e:
                            self._log_security_event("Security Error", f"{filename}: {str(e)}")
                            results.append(f"{filename}: Security Error - {str(e)}\n")
                        except Exception as e:
                            self._log_security_event("Error", f"{filename}: {str(e)}")
                            results.append(f"{filename}: Error - {str(e)}\n")
                
                self.batch_result.delete("1.0", tk.END)
                for result in results:
                    self.batch_result.insert(tk.END, result)
                self.status_var.set("Analysis complete")
                self._log_security_event("Batch Analysis", "Completed directory analysis")
            except Exception as e:
                self._log_security_event("Error", str(e))
                self.batch_result.delete("1.0", tk.END)
                self.batch_result.insert(tk.END, f"Error: {str(e)}")
                self.status_var.set("Error occurred")

        threading.Thread(target=analyze).start()

def main():
    root = tk.Tk()
    app = AIDetectorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 