import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import json
import pytz
import os
from ui_components import MinimalButton, StyleManager, WeeklySummaryWindow

class TimeTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Time Tracker")
        
        # Make window full screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.configure(bg='white')
        
        # Initialize styles
        StyleManager.setup_styles()
        
        # Initialize data file
        self.data_file = "time_records.json"
        self.load_data()
        
        # Initialize state variables
        self.current_state = "clocked_out"
        self.clock_in_time = None
        self.break_start_time = None
        self.total_break_time = timedelta()
        self.today_worked_time = timedelta()
        self.hours_left = timedelta(hours=16)
        
        self.setup_ui()
        self.update_time_display()
        self.check_new_date()
    
    def load_data(self):
        """Load time records from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.time_records = json.load(f)
        else:
            self.time_records = {}
    
    def save_data(self):
        """Save time records to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.time_records, f, indent=4)
    
    def format_timedelta(self, td):
        """Convert timedelta to hours and minutes format"""
        total_hours = td.total_seconds() / 3600
        hours = int(total_hours)
        minutes = int((total_hours - hours) * 60)
        return f"{hours}h {minutes}m"
    
    def get_current_time(self):
        """Get current time in EET timezone"""
        return datetime.now(pytz.timezone('EET'))
    
    def check_new_date(self):
        """Check and initialize new date entry in records"""
        current_date = self.get_current_time().strftime("%Y-%m-%d")
        if current_date not in self.time_records:
            self.time_records[current_date] = {
                "total_time": "0h 0m",
                "breaks": "0h 0m",
                "clock_in": "-",
                "clock_out": "-"
            }
            self.save_data()
    
    def setup_ui(self):
        """Initialize the user interface"""
        # Main container
        self.main_container = ttk.Frame(self.root, style="Main.TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=60, pady=60)
        
        # Top section
        top_frame = ttk.Frame(self.main_container, style="Main.TFrame")
        top_frame.pack(fill=tk.X, pady=(0, 40))
        
        # Title
        title_label = ttk.Label(top_frame,
                               text="Time Tracker",
                               style="Title.TLabel")
        title_label.pack()
        
        # Separator
        ttk.Separator(self.main_container, orient='horizontal').pack(fill='x')
        
        # Center section for time display
        center_frame = ttk.Frame(self.main_container, style="Main.TFrame")
        center_frame.pack(expand=True, pady=40)
        
        self.time_label = ttk.Label(center_frame,
                                   text="0h 0m",
                                   style="Time.TLabel")
        self.time_label.pack()
        
        self.hours_left_label = ttk.Label(center_frame,
                                         text="16h 0m left",
                                         style="Remaining.TLabel")
        self.hours_left_label.pack()
        
        # Status display
        self.status_label = ttk.Label(center_frame,
                                     text="Status: Clocked Out",
                                     style="Status.TLabel")
        self.status_label.pack(pady=20)
        
        # Separator
        ttk.Separator(self.main_container, orient='horizontal').pack(fill='x')
        
        # Bottom section for buttons
        bottom_frame = ttk.Frame(self.main_container, style="ButtonFrame.TFrame")
        bottom_frame.pack(pady=40)
        
        # Create grid for buttons
        self.setup_buttons(bottom_frame)
        
        # Weekly summary button at the bottom
        self.summary_btn = MinimalButton(self.main_container,
                                       text="Weekly Summary",
                                       command=self.show_weekly_summary)
        self.summary_btn.pack(pady=20)
        
        self.update_button_states()
    
    def setup_buttons(self, button_frame):
        """Setup the control buttons"""
        # First row
        self.clock_in_btn = MinimalButton(button_frame,
                                        text="Clock In",
                                        command=self.clock_in)
        self.clock_in_btn.grid(row=0, column=0, padx=20, pady=20)
        
        self.clock_out_btn = MinimalButton(button_frame,
                                         text="Clock Out",
                                         command=self.clock_out)
        self.clock_out_btn.grid(row=0, column=1, padx=20, pady=20)
        
        # Second row
        self.break_in_btn = MinimalButton(button_frame,
                                        text="Break In",
                                        command=self.break_in)
        self.break_in_btn.grid(row=1, column=0, padx=20, pady=20)
        
        self.break_out_btn = MinimalButton(button_frame,
                                         text="Break Out",
                                         command=self.break_out)
        self.break_out_btn.grid(row=1, column=1, padx=20, pady=20)
    
    def update_time_display(self):
        """Update the time display and countdown"""
        if self.current_state in ["clocked_in", "break"]:
            current_time = self.get_current_time()
            
            if self.current_state == "clocked_in":
                worked_time = current_time - self.clock_in_time - self.total_break_time
                # Only countdown when not on break
                if self.current_state != "break":
                    self.hours_left -= timedelta(seconds=1)
            else:  # On break
                worked_time = current_time - self.clock_in_time - self.total_break_time - (current_time - self.break_start_time)
            
            self.time_label.config(text=self.format_timedelta(worked_time))
            self.hours_left_label.config(text=f"{self.format_timedelta(self.hours_left)} left")
        
        # Schedule next update
        self.root.after(1000, self.update_time_display)
    
    def update_button_states(self):
        """Update button states based on current state"""
        states = {
            "clocked_out": {
                "clock_in": "normal",
                "clock_out": "disabled",
                "break_in": "disabled",
                "break_out": "disabled"
            },
            "clocked_in": {
                "clock_in": "disabled",
                "clock_out": "normal",
                "break_in": "normal",
                "break_out": "disabled"
            },
            "break": {
                "clock_in": "disabled",
                "clock_out": "disabled",
                "break_in": "disabled",
                "break_out": "normal"
            }
        }
        
        current_states = states[self.current_state]
        self.clock_in_btn["state"] = current_states["clock_in"]
        self.clock_out_btn["state"] = current_states["clock_out"]
        self.break_in_btn["state"] = current_states["break_in"]
        self.break_out_btn["state"] = current_states["break_out"]
    
    def clock_in(self):
        """Handle clock in event"""
        self.current_state = "clocked_in"
        self.clock_in_time = self.get_current_time()
        self.total_break_time = timedelta()
        self.hours_left = timedelta(hours=16)  # Reset countdown
        self.status_label.config(text="Status: Clocked In")
        self.update_button_states()
    
    def clock_out(self):
        """Handle clock out event"""
        if self.clock_in_time:
            current_time = self.get_current_time()
            worked_time = current_time - self.clock_in_time - self.total_break_time
            
            # Save to records
            date_str = current_time.strftime("%Y-%m-%d")
            self.time_records[date_str] = {
                "total_time": self.format_timedelta(worked_time),
                "breaks": self.format_timedelta(self.total_break_time),
                "clock_in": self.clock_in_time.strftime("%H:%M"),
                "clock_out": current_time.strftime("%H:%M")
            }
            self.save_data()
        
        # Reset state
        self.current_state = "clocked_out"
        self.clock_in_time = None
        self.total_break_time = timedelta()
        self.status_label.config(text="Status: Clocked Out")
        self.time_label.config(text="0h 0m")
        self.hours_left_label.config(text="16h 0m left")
        self.update_button_states()
    
    def break_in(self):
        """Handle break start event"""
        self.current_state = "break"
        self.break_start_time = self.get_current_time()
        self.status_label.config(text="Status: On Break")
        self.update_button_states()
    
    def break_out(self):
        """Handle break end event"""
        if self.break_start_time:
            current_time = self.get_current_time()
            self.total_break_time += current_time - self.break_start_time
        
        self.current_state = "clocked_in"
        self.break_start_time = None
        self.status_label.config(text="Status: Clocked In")
        self.update_button_states()
    
    def show_weekly_summary(self):
        """Show weekly summary window"""
        WeeklySummaryWindow(self.root, self.time_records, self.get_current_time)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()