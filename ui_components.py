import tkinter as tk
from tkinter import ttk
from datetime import timedelta

class MinimalButton(ttk.Button):
    def __init__(self, master, **kwargs):
        style = ttk.Style()
        style.configure("Minimal.TButton",
                       padding=(30, 20),
                       font=('Helvetica', 12),
                       background='white',
                       foreground='black')
        
        style.map("Minimal.TButton",
                 background=[('active', '#f8f8f8')],
                 foreground=[('active', 'black')])
        
        super().__init__(master, style="Minimal.TButton", **kwargs)
        self.bind('<Enter>', lambda e: self.configure(cursor='hand2'))

class StyleManager:
    @staticmethod
    def setup_styles():
        style = ttk.Style()
        
        # Light mode styles (default)
        style.configure(".",
                       font=('Helvetica', 12),
                       background='white',
                       foreground='black')
        
        style.configure("Title.TLabel",
                       font=('Helvetica', 36, 'bold'),
                       background='white',
                       foreground='black',
                       padding=20)
        
        style.configure("Status.TLabel",
                       font=('Helvetica', 14),
                       background='white',
                       foreground='black',
                       padding=10)
        
        style.configure("Time.TLabel",
                       font=('Helvetica', 72, 'bold'),
                       background='white',
                       foreground='black',
                       padding=20)
        
        style.configure("Remaining.TLabel",
                       font=('Helvetica', 24),
                       background='white',
                       foreground='#333333',
                       padding=10)
        
        style.configure("Clickable.TLabel",
                       font=('Helvetica', 24),
                       background='white',
                       foreground='#0066cc',
                       padding=10)
        
        style.configure("Main.TFrame",
                       background='white')
        
        style.configure("ButtonFrame.TFrame",
                       background='white',
                       padding=20)
        
        style.configure("TSeparator",
                       background='#e0e0e0')
        
        style.configure("Minimal.Treeview",
                       background="white",
                       foreground="black",
                       rowheight=50,
                       fieldbackground="white",
                       font=('Helvetica', 12))
        
        style.configure("Minimal.Treeview.Heading",
                       background="white",
                       foreground="black",
                       font=('Helvetica', 14, 'bold'),
                       padding=15)
        
        style.map("Minimal.Treeview",
                 background=[('selected', '#f0f0f0')],
                 foreground=[('selected', 'black')])
    
    @staticmethod
    def toggle_dark_mode(enable_dark_mode):
        style = ttk.Style()
        
        if enable_dark_mode:
            # Dark mode styles
            style.configure(".",
                           background='#2d2d2d',
                           foreground='white')
            
            style.configure("Title.TLabel",
                           background='#2d2d2d',
                           foreground='white')
            
            style.configure("Status.TLabel",
                           background='#2d2d2d',
                           foreground='white')
            
            style.configure("Time.TLabel",
                           background='#2d2d2d',
                           foreground='white')
            
            style.configure("Remaining.TLabel",
                           background='#2d2d2d',
                           foreground='#cccccc')
            
            style.configure("Clickable.TLabel",
                           background='#2d2d2d',
                           foreground='#4dabf7')
            
            style.configure("Main.TFrame",
                           background='#2d2d2d')
            
            style.configure("ButtonFrame.TFrame",
                           background='#2d2d2d')
            
            style.configure("TSeparator",
                           background='#444444')
            
            style.configure("Minimal.Treeview",
                           background="#2d2d2d",
                           foreground="white",
                           fieldbackground="#2d2d2d")
            
            style.configure("Minimal.Treeview.Heading",
                           background="#2d2d2d",
                           foreground="white")
            
            style.map("Minimal.Treeview",
                     background=[('selected', '#444444')],
                     foreground=[('selected', 'white')])
        else:
            # Revert to light mode
            StyleManager.setup_styles()

class TimeGoalDialog:
    def __init__(self, parent, current_hours):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Set Time Goal")
        
        # Center the dialog
        window_width = 400
        window_height = 200
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.dialog.configure(bg='white')
        
        # Make dialog modal
        self.dialog.transient(parent)
        
        # Wait for the window to be visible before setting the grab
        self.dialog.wait_visibility()
        self.dialog.grab_set()
        
        # Create message
        message = ttk.Label(self.dialog,
                          text="Set daily time goal (hours):",
                          style="Status.TLabel")
        message.pack(pady=20)
        
        # Entry for hours
        self.hours_var = tk.StringVar(value=str(current_hours))
        self.entry = ttk.Entry(self.dialog, 
                             textvariable=self.hours_var,
                             justify='center',
                             font=('Helvetica', 14))
        self.entry.pack(pady=10)
        
        # Button frame
        button_frame = ttk.Frame(self.dialog, style="Main.TFrame")
        button_frame.pack(pady=20)
        
        # Save button
        self.save_button = MinimalButton(button_frame,
                                      text="Save",
                                      command=self._on_save)
        self.save_button.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        self.cancel_button = MinimalButton(button_frame,
                                     text="Cancel",
                                     command=self._on_cancel)
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        
        self.result = None
        
    def _on_save(self):
        try:
            hours = float(self.hours_var.get())
            if hours > 0:
                self.result = hours
                self.dialog.destroy()
        except ValueError:
            pass
        
    def _on_cancel(self):
        self.dialog.destroy()

class WeeklySummaryWindow:
    def __init__(self, parent, time_records, get_current_time):
        self.window = tk.Toplevel(parent)
        self.window.title("Weekly Summary")
        
        # Make window full screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}")
        self.window.configure(bg='white')
        
        self.time_records = time_records
        self.get_current_time = get_current_time
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.window, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Title
        title = ttk.Label(main_frame,
                         text="Weekly Summary",
                         style="Title.TLabel")
        title.pack(pady=(0, 30))
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Create Treeview with custom style
        self.tree = ttk.Treeview(main_frame,
                                columns=("Date", "Total Time", "Breaks", "Clock In", "Clock Out"),
                                show="headings",
                                style="Minimal.Treeview")
        
        # Configure columns
        column_widths = {
            "Date": 300,
            "Total Time": 300,
            "Breaks": 300,
            "Clock In": 200,
            "Clock Out": 200
        }
        
        for col, width in column_widths.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        self.populate_data()
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame,
                                orient="vertical",
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack everything
        self.tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add close button at the bottom
        close_button = MinimalButton(main_frame,
                                   text="Close Summary",
                                   command=self.window.destroy)
        close_button.pack(pady=30)

    def populate_data(self):
        from datetime import timedelta
        
        current_date = self.get_current_time().date()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        
        for i in range(7):
            date = start_of_week + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            if date_str in self.time_records:
                record = self.time_records[date_str]
                self.tree.insert("", "end", values=(
                    date_str,
                    record["total_time"],
                    record["breaks"],
                    record["clock_in"],
                    record["clock_out"]
                ))
            else:
                self.tree.insert("", "end", values=(
                    date_str,
                    "0h 0m 0s",
                    "0h 0m 0s",
                    "-",
                    "-"
                ))