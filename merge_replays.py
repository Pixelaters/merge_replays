import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import json
from typing import List, Tuple, Optional

class MergeReplaysApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Merge Replays - MP4/M4A Combiner")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Modern color scheme - refined and polished
        self.colors = {
            'bg': '#f8f9fa',
            'fg': '#212529',
            'accent': '#0d6efd',
            'accent_hover': '#0b5ed7',
            'success': '#198754',
            'success_hover': '#157347',
            'text_secondary': '#6c757d',
            'entry_bg': '#ffffff',
            'frame_bg': '#ffffff',
            'border': '#dee2e6',
            'shadow': '#00000015',
            'card_shadow': '#00000010',
            'hover_bg': '#f8f9fa'
        }
        
        # Set window background
        self.root.configure(bg=self.colors['bg'])
        
        # Config file path - use AppData Local for Windows
        appdata_local = os.getenv('LOCALAPPDATA')
        if appdata_local:
            config_dir = Path(appdata_local) / "MergeReplays"
            config_dir.mkdir(exist_ok=True)  # Create directory if it doesn't exist
            self.config_file = config_dir / "config.json"
        else:
            # Fallback if LOCALAPPDATA not available (shouldn't happen on Windows)
            if getattr(sys, 'frozen', False):
                self.config_file = Path(sys.executable).parent / "config.json"
            else:
                self.config_file = Path(__file__).parent / "config.json"
        
        # Variables
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.delete_originals = tk.BooleanVar(value=False)
        self.is_processing = False
        
        # Load saved settings
        self.load_config()
        
        # Track changes to save config (after loading to avoid saving during load)
        self.source_folder.trace_add("write", lambda *args: self.save_config())
        self.dest_folder.trace_add("write", lambda *args: self.save_config())
        self.delete_originals.trace_add("write", lambda *args: self.save_config())
        
        # Save config when window closes
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Setup modern styling
        self.setup_styles()
        
        self.setup_ui()
    
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Try to use a modern theme
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        
        # Configure button style
        style.configure('Modern.TButton',
                       padding=(20, 10),
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure entry style
        style.configure('Modern.TEntry',
                       padding=8,
                       font=('Segoe UI', 9))
        
        # Configure label style
        style.configure('Modern.TLabel',
                       font=('Segoe UI', 9),
                       background=self.colors['bg'])
        
        # Configure label frame style
        style.configure('Modern.TLabelframe',
                       font=('Segoe UI', 9, 'bold'),
                       background=self.colors['bg'],
                       borderwidth=1)
        
        style.configure('Modern.TLabelframe.Label',
                       font=('Segoe UI', 9, 'bold'),
                       background=self.colors['bg'],
                       foreground=self.colors['fg'])
        
        # Configure progress bar
        style.configure('Modern.Horizontal.TProgressbar',
                        thickness=25,
                        borderwidth=0,
                        background=self.colors['accent'])
    
    def setup_ui(self):
        # Main container with padding
        container = tk.Frame(self.root, bg=self.colors['bg'], padx=30, pady=30)
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        
        # Header section
        header_frame = tk.Frame(container, bg=self.colors['bg'])
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 30))
        
        title_label = tk.Label(header_frame, 
                              text="Merge Replays", 
                              font=('Segoe UI', 24, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['fg'])
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(header_frame,
                                 text="Combine MP4 and M4A files with dual audio tracks",
                                 font=('Segoe UI', 11),
                                 bg=self.colors['bg'],
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Main content card with shadow effect
        card_frame = tk.Frame(container, bg=self.colors['frame_bg'], relief=tk.FLAT, bd=0)
        card_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        container.rowconfigure(1, weight=1)
        
        # Content padding
        content_padding = 30
        content_frame = tk.Frame(card_frame, bg=self.colors['frame_bg'], padx=content_padding, pady=content_padding)
        content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(1, weight=1)
        card_frame.columnconfigure(0, weight=1)
        card_frame.rowconfigure(0, weight=1)
        
        # Source folder section
        source_section = tk.Frame(content_frame, bg=self.colors['frame_bg'])
        source_section.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        source_section.columnconfigure(1, weight=1)
        
        source_label = tk.Label(source_section, 
                               text="Source Folder", 
                               font=('Segoe UI', 10, 'bold'),
                               bg=self.colors['frame_bg'],
                               fg=self.colors['fg'],
                               anchor='w')
        source_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        source_entry = tk.Entry(source_section, 
                               textvariable=self.source_folder,
                               font=('Segoe UI', 10),
                               bg=self.colors['entry_bg'],
                               fg=self.colors['fg'],
                               relief=tk.SOLID,
                               bd=1,
                               highlightthickness=2,
                               highlightbackground=self.colors['border'],
                               highlightcolor=self.colors['accent'],
                               insertbackground=self.colors['fg'])
        source_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10))
        
        source_btn = tk.Button(source_section,
                              text="Browse",
                              command=self.select_source_folder,
                              font=('Segoe UI', 10),
                              bg=self.colors['accent'],
                              fg='white',
                              activebackground=self.colors['accent_hover'],
                              activeforeground='white',
                              relief=tk.FLAT,
                              bd=0,
                              padx=24,
                              pady=10,
                              cursor='hand2')
        source_btn.grid(row=1, column=2, sticky=tk.E)
        
        # Destination folder section
        dest_section = tk.Frame(content_frame, bg=self.colors['frame_bg'])
        dest_section.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 25))
        dest_section.columnconfigure(1, weight=1)
        
        dest_label = tk.Label(dest_section,
                             text="Destination Folder",
                             font=('Segoe UI', 10, 'bold'),
                             bg=self.colors['frame_bg'],
                             fg=self.colors['fg'],
                             anchor='w')
        dest_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        dest_entry = tk.Entry(dest_section,
                             textvariable=self.dest_folder,
                             font=('Segoe UI', 10),
                             bg=self.colors['entry_bg'],
                             fg=self.colors['fg'],
                             relief=tk.SOLID,
                             bd=1,
                             highlightthickness=2,
                             highlightbackground=self.colors['border'],
                             highlightcolor=self.colors['accent'],
                             insertbackground=self.colors['fg'])
        dest_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10))
        
        dest_btn = tk.Button(dest_section,
                            text="Browse",
                            command=self.select_dest_folder,
                            font=('Segoe UI', 10),
                            bg=self.colors['accent'],
                            fg='white',
                            activebackground=self.colors['accent_hover'],
                            activeforeground='white',
                            relief=tk.FLAT,
                            bd=0,
                            padx=24,
                            pady=10,
                            cursor='hand2')
        dest_btn.grid(row=1, column=2, sticky=tk.E)
        
        # Options section
        options_section = tk.Frame(content_frame, bg=self.colors['frame_bg'])
        options_section.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 25))
        
        delete_check = tk.Checkbutton(options_section,
                                      text="Delete original files after merge",
                                      variable=self.delete_originals,
                                      font=('Segoe UI', 10),
                                      bg=self.colors['frame_bg'],
                                      fg=self.colors['fg'],
                                      activebackground=self.colors['frame_bg'],
                                      activeforeground=self.colors['fg'],
                                      selectcolor=self.colors['frame_bg'],
                                      anchor='w',
                                      cursor='hand2')
        delete_check.pack(anchor='w', pady=(0, 8))
        
        # Config file location info
        config_info_frame = tk.Frame(options_section, bg=self.colors['frame_bg'])
        config_info_frame.pack(fill=tk.X, pady=(5, 0))
        
        config_info_label = tk.Label(config_info_frame,
                                    text="Config file:",
                                    font=('Segoe UI', 8),
                                    bg=self.colors['frame_bg'],
                                    fg=self.colors['text_secondary'],
                                    anchor='w')
        config_info_label.pack(side=tk.LEFT)
        
        config_path_label = tk.Label(config_info_frame,
                                     text=str(self.config_file),
                                     font=('Segoe UI', 8),
                                     bg=self.colors['frame_bg'],
                                     fg=self.colors['text_secondary'],
                                     anchor='w',
                                     cursor='hand2')
        config_path_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Make config path clickable to open folder
        def open_config_folder(event):
            import subprocess
            folder = str(self.config_file.parent)
            subprocess.Popen(f'explorer /select,"{self.config_file}"' if self.config_file.exists() else f'explorer "{folder}"')
        
        config_path_label.bind('<Button-1>', open_config_folder)
        
        # Progress section
        progress_section = tk.Frame(content_frame, bg=self.colors['frame_bg'])
        progress_section.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_section.columnconfigure(0, weight=1)
        
        progress_header = tk.Frame(progress_section, bg=self.colors['frame_bg'])
        progress_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        progress_title = tk.Label(progress_header,
                                 text="Progress",
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.colors['frame_bg'],
                                 fg=self.colors['fg'],
                                 anchor='w')
        progress_title.pack(side=tk.LEFT)
        
        self.progress_label = tk.Label(progress_header,
                                      text="Ready to merge files",
                                      font=('Segoe UI', 9),
                                      bg=self.colors['frame_bg'],
                                      fg=self.colors['text_secondary'],
                                      anchor='e')
        self.progress_label.pack(side=tk.RIGHT)
        
        # Progress bar with rounded container
        progress_container = tk.Frame(progress_section, bg='#e9ecef', height=10, relief=tk.FLAT, bd=0)
        progress_container.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 0))
        progress_container.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_container,
                                            mode='determinate',
                                            style='Modern.Horizontal.TProgressbar',
                                            length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        
        # Status log section
        status_section = tk.Frame(content_frame, bg=self.colors['frame_bg'])
        status_section.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        status_section.columnconfigure(0, weight=1)
        status_section.rowconfigure(1, weight=1)
        content_frame.rowconfigure(4, weight=1)
        
        status_title = tk.Label(status_section,
                               text="Status Log",
                               font=('Segoe UI', 10, 'bold'),
                               bg=self.colors['frame_bg'],
                               fg=self.colors['fg'],
                               anchor='w')
        status_title.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Status text container
        status_container = tk.Frame(status_section, bg='#1e1e1e', relief=tk.FLAT, bd=0)
        status_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_container.columnconfigure(0, weight=1)
        status_container.rowconfigure(0, weight=1)
        
        self.status_text = tk.Text(status_container,
                                   height=8,
                                   wrap=tk.WORD,
                                   font=('Consolas', 9),
                                   bg='#1e1e1e',
                                   fg='#d4d4d4',
                                   insertbackground='#ffffff',
                                   relief=tk.FLAT,
                                   bd=0,
                                   padx=15,
                                   pady=15,
                                   selectbackground=self.colors['accent'],
                                   selectforeground='white')
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(status_container,
                                  orient=tk.VERTICAL,
                                  command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Action button section
        button_container = tk.Frame(container, bg=self.colors['bg'])
        button_container.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 0))
        
        self.process_button = tk.Button(button_container,
                                       text="Start Merging",
                                       command=self.start_processing,
                                       font=('Segoe UI', 11, 'bold'),
                                       bg=self.colors['success'],
                                       fg='white',
                                       activebackground=self.colors['success_hover'],
                                       activeforeground='white',
                                       relief=tk.FLAT,
                                       bd=0,
                                       padx=50,
                                       pady=14,
                                       cursor='hand2')
        self.process_button.pack()
    
    def load_config(self):
        """Load saved configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if 'source_folder' in config and os.path.isdir(config['source_folder']):
                        self.source_folder.set(config['source_folder'])
                    if 'dest_folder' in config and os.path.isdir(config['dest_folder']):
                        self.dest_folder.set(config['dest_folder'])
                    if 'delete_originals' in config:
                        self.delete_originals.set(config['delete_originals'])
        except Exception as e:
            # If config file is corrupted, just continue with defaults
            pass
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config = {
                'source_folder': self.source_folder.get(),
                'dest_folder': self.dest_folder.get(),
                'delete_originals': self.delete_originals.get()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            # Silently fail if we can't save config
            pass
    
    def on_closing(self):
        """Handle window closing - save config and destroy"""
        self.save_config()
        self.root.destroy()
    
    def select_source_folder(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_folder.set(folder)
    
    def select_dest_folder(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_folder.set(folder)
    
    def log_status(self, message):
        """Add message to status text"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def find_file_pairs(self, folder: str) -> List[Tuple[str, str]]:
        """Find matching mp4 and m4a file pairs"""
        pairs = []
        folder_path = Path(folder)
        
        # Get all mp4 and m4a files
        mp4_files = {f.stem: f for f in folder_path.glob("*.mp4")}
        m4a_files = {f.stem: f for f in folder_path.glob("*.m4a")}
        
        # Find matching pairs
        for name in mp4_files.keys():
            if name in m4a_files:
                pairs.append((str(mp4_files[name]), str(m4a_files[name])))
        
        return pairs
    
    def merge_files(self, mp4_path: str, m4a_path: str, output_path: str) -> bool:
        """Merge mp4 and m4a files into a single file with 2 audio tracks"""
        try:
            # FFmpeg command to merge files with 2 audio tracks
            # -i: input files
            # -map 0:v:0: video from first input (mp4)
            # -map 0:a:0: audio from first input (mp4)
            # -map 1:a:0: audio from second input (m4a)
            # -c:v copy: copy video without re-encoding
            # -c:a copy: copy audio without re-encoding
            # -metadata:s:a:0 title: set name for first audio track (Game Audio)
            # -metadata:s:a:1 title: set name for second audio track (Microphone Track)
            # -disposition:a:0 default: set first audio track as default
            # -disposition:a:1 none: set second audio track as non-default
            
            cmd = [
                'ffmpeg',
                '-i', mp4_path,
                '-i', m4a_path,
                '-map', '0:v:0',      # Video from mp4
                '-map', '0:a:0',      # Audio track 1 from mp4
                '-map', '1:a:0',      # Audio track 2 from m4a
                '-c:v', 'copy',       # Copy video (no re-encode)
                '-c:a', 'copy',       # Copy audio (no re-encode)
                '-metadata:s:a:0', 'title=Game Audio',  # Name for MP4 audio track
                '-metadata:s:a:1', 'title=Microphone Track',  # Name for M4A audio track
                '-disposition:a:0', 'default',  # First audio track is default
                '-disposition:a:1', 'none',     # Second audio track is optional
                '-y',                 # Overwrite output file
                output_path
            ]
            
            # Run ffmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.log_status(f"Error merging {Path(mp4_path).name}: {stderr}")
                return False
            
            return True
            
        except Exception as e:
            self.log_status(f"Exception merging {Path(mp4_path).name}: {str(e)}")
            return False
    
    def check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True
        except FileNotFoundError:
            return False
    
    def start_processing(self):
        """Start the merging process in a separate thread"""
        if self.is_processing:
            return
        
        # Validate inputs
        source = self.source_folder.get()
        dest = self.dest_folder.get()
        
        if not source or not os.path.isdir(source):
            messagebox.showerror("Error", "Please select a valid source folder.")
            return
        
        if not dest or not os.path.isdir(dest):
            messagebox.showerror("Error", "Please select a valid destination folder.")
            return
        
        # Check ffmpeg
        if not self.check_ffmpeg():
            messagebox.showerror("Error", 
                "FFmpeg not found! Please install FFmpeg and add it to your PATH.\n\n"
                "Download from: https://ffmpeg.org/download.html")
            return
        
        # Disable button and start processing
        self.is_processing = True
        self.process_button.config(state='disabled', 
                                  bg='#adb5bd', 
                                  text="Processing...",
                                  cursor='wait')
        self.status_text.delete(1.0, tk.END)
        
        # Run in separate thread to keep UI responsive
        thread = threading.Thread(target=self.process_files, daemon=True)
        thread.start()
    
    def process_files(self):
        """Process all file pairs"""
        source = self.source_folder.get()
        dest = self.dest_folder.get()
        delete_originals = self.delete_originals.get()
        
        try:
            # Find file pairs
            self.log_status("Scanning for file pairs...")
            pairs = self.find_file_pairs(source)
            
            if not pairs:
                self.log_status("No matching file pairs found!")
                messagebox.showinfo("No Files", "No matching MP4/M4A file pairs found in source folder.")
                return
            
            self.log_status(f"Found {len(pairs)} file pair(s) to merge.\n")
            
            # Process each pair
            total = len(pairs)
            success_count = 0
            
            for idx, (mp4_path, m4a_path) in enumerate(pairs, 1):
                mp4_name = Path(mp4_path).stem
                output_path = os.path.join(dest, f"{mp4_name}.mp4")
                
                # Update progress
                progress = int((idx - 1) / total * 100)
                self.progress_bar['value'] = progress
                self.progress_label.config(text=f"Processing {idx}/{total}: {Path(mp4_path).name}")
                self.log_status(f"[{idx}/{total}] Merging: {Path(mp4_path).name}...")
                
                # Merge files
                if self.merge_files(mp4_path, m4a_path, output_path):
                    self.log_status(f"✓ Successfully merged: {mp4_name}.mp4")
                    success_count += 1
                    
                    # Delete originals if requested
                    if delete_originals:
                        try:
                            os.remove(mp4_path)
                            os.remove(m4a_path)
                            self.log_status(f"  Deleted original files")
                        except Exception as e:
                            self.log_status(f"  Warning: Could not delete originals: {str(e)}")
                else:
                    self.log_status(f"✗ Failed to merge: {mp4_name}.mp4")
                
                self.log_status("")  # Empty line for readability
            
            # Final update
            self.progress_bar['value'] = 100
            self.progress_label.config(text=f"Complete! {success_count}/{total} files merged successfully.")
            
            messagebox.showinfo("Complete", 
                f"Processing complete!\n\n"
                f"Successfully merged: {success_count}/{total} files")
            
        except Exception as e:
            self.log_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            # Re-enable button
            self.is_processing = False
            self.process_button.config(state='normal',
                                      bg=self.colors['success'],
                                      text="Start Merging",
                                      cursor='hand2')

def main():
    root = tk.Tk()
    app = MergeReplaysApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

