import tkinter as tk
from tkinter import ttk, messagebox
from config import Config
from typing import Callable

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, config: Config, on_save: Callable[[], None]):
        super().__init__(parent)
        self.config = config
        self.on_save = on_save
        
        self.title("Settings")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Create notebook for different setting categories
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.security_tab = ttk.Frame(self.notebook)
        self.models_tab = ttk.Frame(self.notebook)
        self.ui_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.security_tab, text="Security")
        self.notebook.add(self.models_tab, text="Models")
        self.notebook.add(self.ui_tab, text="UI")
        self.notebook.add(self.analysis_tab, text="Analysis")
        
        self._create_security_tab()
        self._create_models_tab()
        self._create_ui_tab()
        self._create_analysis_tab()
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side=tk.LEFT, padx=5)
    
    def _create_security_tab(self):
        frame = ttk.LabelFrame(self.security_tab, text="Security Settings", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Max text length
        ttk.Label(frame, text="Maximum Text Length (characters):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.max_text_length = ttk.Entry(frame)
        self.max_text_length.insert(0, str(self.config.get("security.max_text_length")))
        self.max_text_length.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Max file size
        ttk.Label(frame, text="Maximum File Size (MB):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.max_file_size = ttk.Entry(frame)
        self.max_file_size.insert(0, str(self.config.get("security.max_file_size") // (1024 * 1024)))
        self.max_file_size.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Rate limit
        ttk.Label(frame, text="Rate Limit (requests/minute):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.rate_limit = ttk.Entry(frame)
        self.rate_limit.insert(0, str(self.config.get("security.rate_limit")))
        self.rate_limit.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Log retention
        ttk.Label(frame, text="Log Retention (days):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.log_retention = ttk.Entry(frame)
        self.log_retention.insert(0, str(self.config.get("security.log_retention_days")))
        self.log_retention.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        frame.columnconfigure(1, weight=1)
    
    def _create_models_tab(self):
        frame = ttk.LabelFrame(self.models_tab, text="Model Settings", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # GPT2 Model
        ttk.Label(frame, text="GPT2 Model:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.gpt2_model = ttk.Entry(frame)
        self.gpt2_model.insert(0, self.config.get("models.gpt2.model_name"))
        self.gpt2_model.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Roberta Model
        ttk.Label(frame, text="Roberta Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.roberta_model = ttk.Entry(frame)
        self.roberta_model.insert(0, self.config.get("models.roberta.model_name"))
        self.roberta_model.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Max length
        ttk.Label(frame, text="Maximum Input Length:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.max_length = ttk.Entry(frame)
        self.max_length.insert(0, str(self.config.get("models.gpt2.max_length")))
        self.max_length.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        frame.columnconfigure(1, weight=1)
    
    def _create_ui_tab(self):
        frame = ttk.LabelFrame(self.ui_tab, text="UI Settings", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Theme
        ttk.Label(frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme = ttk.Combobox(frame, values=["light", "dark"])
        self.theme.set(self.config.get("ui.theme"))
        self.theme.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Font size
        ttk.Label(frame, text="Font Size:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.font_size = ttk.Entry(frame)
        self.font_size.insert(0, str(self.config.get("ui.font_size")))
        self.font_size.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        frame.columnconfigure(1, weight=1)
    
    def _create_analysis_tab(self):
        frame = ttk.LabelFrame(self.analysis_tab, text="Analysis Settings", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Confidence threshold
        ttk.Label(frame, text="Confidence Threshold:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.confidence_threshold = ttk.Entry(frame)
        self.confidence_threshold.insert(0, str(self.config.get("analysis.confidence_threshold")))
        self.confidence_threshold.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Min text length
        ttk.Label(frame, text="Minimum Text Length:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.min_text_length = ttk.Entry(frame)
        self.min_text_length.insert(0, str(self.config.get("analysis.min_text_length")))
        self.min_text_length.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Batch size
        ttk.Label(frame, text="Batch Size:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.batch_size = ttk.Entry(frame)
        self.batch_size.insert(0, str(self.config.get("analysis.batch_size")))
        self.batch_size.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        frame.columnconfigure(1, weight=1)
    
    def _save_settings(self):
        try:
            # Security settings
            self.config.set("security.max_text_length", int(self.max_text_length.get()))
            self.config.set("security.max_file_size", int(self.max_file_size.get()) * 1024 * 1024)
            self.config.set("security.rate_limit", int(self.rate_limit.get()))
            self.config.set("security.log_retention_days", int(self.log_retention.get()))
            
            # Model settings
            self.config.set("models.gpt2.model_name", self.gpt2_model.get())
            self.config.set("models.roberta.model_name", self.roberta_model.get())
            self.config.set("models.gpt2.max_length", int(self.max_length.get()))
            self.config.set("models.roberta.max_length", int(self.max_length.get()))
            
            # UI settings
            self.config.set("ui.theme", self.theme.get())
            self.config.set("ui.font_size", int(self.font_size.get()))
            
            # Analysis settings
            self.config.set("analysis.confidence_threshold", float(self.confidence_threshold.get()))
            self.config.set("analysis.min_text_length", int(self.min_text_length.get()))
            self.config.set("analysis.batch_size", int(self.batch_size.get()))
            
            if self.config.validate_config():
                self.on_save()
                self.destroy()
            else:
                messagebox.showerror("Error", "Invalid configuration values")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def _reset_defaults(self):
        if messagebox.askyesno("Reset to Defaults", "Are you sure you want to reset all settings to defaults?"):
            self.config.config = self.config.default_config
            self.config.save_config()
            self.on_save()
            self.destroy() 