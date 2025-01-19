import tkinter as tk
from tkinter import ttk, font

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
        
        # Configure the main theme
        style.configure(".",
                       font=('Helvetica', 12),
                       background='white',
                       foreground='black')
        
        # Main title style
        style.configure("Title.TLabel",
                       font=('Helvetica', 36, 'bold'),
                       background='white',
                       foreground='black',
                       padding=20)
        
        # Status indicator style
        style.configure("Status.TLabel",
                       font=('Helvetica', 14),
                       background='white',
                       foreground='black',
                       padding=10)
        
        # Time display style
        style.configure("Time.TLabel",
                       font=('Helvetica', 72, 'bold'),
                       background='white',
                       foreground='black',
                       padding=20)
        
        # Remaining time style
        style.configure("Remaining.TLabel",
                       font=('Helvetica', 24),
                       background='white',
                       foreground='#333333',
                       padding=10)
        
        # Frame styles
        style.configure("Main.TFrame",
                       background='white')
        
        style.configure("ButtonFrame.TFrame",
                       background='white',
                       padding=20)
        
        # Separator style
        style.configure("TSeparator",
                       background='#e0e0e0')
        
        # Configure Treeview
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
                    "0h 0m",
                    "0h 0m",
                    "-",
                    "-"
                ))