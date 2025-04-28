import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from ai_detector import AIDetector
import threading
import os

class AIDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Text Detector")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize the AI detector
        self.detector = AIDetector()
        
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
                label, confidence = self.detector.detect(text)
                self.text_result.config(text=f"Result: {label} (Confidence: {confidence:.2%})")
                self.status_var.set("Analysis complete")
            except Exception as e:
                self.text_result.config(text=f"Error: {str(e)}")
                self.status_var.set("Error occurred")
        
        threading.Thread(target=analyze).start()

    def _select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)

    def _analyze_file(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        
        self.status_var.set("Analyzing file...")
        self.file_result.config(text="Analyzing...")
        
        def analyze():
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                label, confidence = self.detector.detect(text)
                self.file_result.config(text=f"Result: {label} (Confidence: {confidence:.2%})")
                self.status_var.set("Analysis complete")
            except Exception as e:
                self.file_result.config(text=f"Error: {str(e)}")
                self.status_var.set("Error occurred")
        
        threading.Thread(target=analyze).start()

    def _select_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.dir_path_var.set(dir_path)

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
                results = []
                for filename in os.listdir(dir_path):
                    if filename.endswith('.txt'):
                        file_path = os.path.join(dir_path, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                text = file.read()
                            label, confidence = self.detector.detect(text)
                            results.append(f"{filename}: {label} (Confidence: {confidence:.2%})\n")
                        except Exception as e:
                            results.append(f"{filename}: Error - {str(e)}\n")
                
                self.batch_result.delete("1.0", tk.END)
                for result in results:
                    self.batch_result.insert(tk.END, result)
                self.status_var.set("Analysis complete")
            except Exception as e:
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