import tkinter as tk
from tkinter import ttk
from ui_components import MinimalButton, StyleManager, WeeklySummaryWindow, TimeGoalDialog
from time_tracker_core import TimeTrackerCore

class ConfirmationDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Confirm Lock Out")
        
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
        self.dialog.grab_set()
        
        # Create message
        message = ttk.Label(self.dialog,
                          text="Are you sure you want to lock out?",
                          style="Status.TLabel")
        message.pack(pady=30)
        
        # Button frame
        button_frame = ttk.Frame(self.dialog, style="Main.TFrame")
        button_frame.pack(pady=20)
        
        # Yes button
        self.yes_button = MinimalButton(button_frame,
                                      text="Yes",
                                      command=self._on_yes)
        self.yes_button.pack(side=tk.LEFT, padx=10)
        
        # No button
        self.no_button = MinimalButton(button_frame,
                                     text="No",
                                     command=self._on_no)
        self.no_button.pack(side=tk.LEFT, padx=10)
        
        self.result = False
    
    def _on_yes(self):
        self.result = True
        self.dialog.destroy()
    
    def _on_no(self):
        self.dialog.destroy()

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
        
        # Initialize core functionality
        self.core = TimeTrackerCore()
        
        # Dark mode flag
        self.dark_mode = False
        
        self.setup_ui()
        self.update_time_display()
        
        # Bind window closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
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
        
        # Dark mode toggle button
        self.dark_mode_button = MinimalButton(top_frame,
                                             text="Dark Mode",
                                             command=self.toggle_dark_mode)
        self.dark_mode_button.pack(side=tk.RIGHT, padx=10)
        
        # Separator
        ttk.Separator(self.main_container, orient='horizontal').pack(fill='x')
        
        # Center section for time display
        center_frame = ttk.Frame(self.main_container, style="Main.TFrame")
        center_frame.pack(expand=True, pady=40)
        
        self.time_label = ttk.Label(center_frame,
                                   text="0h 0m 0s",
                                   style="Time.TLabel")
        self.time_label.pack()
        
        # Make time left label clickable
        self.time_left_label = ttk.Label(center_frame,
                                       text=f"{self.core.format_timedelta(self.core.total_time)} left",
                                       style="Clickable.TLabel",
                                       cursor="hand2")
        self.time_left_label.pack()
        self.time_left_label.bind('<Button-1>', self.show_time_goal_dialog)
        
        # Status display
        self.status_label = ttk.Label(center_frame,
                                     text=f"Status: {self.core.current_state.replace('_', ' ').title()}",
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
    
    def show_time_goal_dialog(self, event=None):
        """Show dialog to change time goal"""
        if self.core.current_state == "clocked_out":
            current_hours = self.core.get_time_goal_hours()
            dialog = TimeGoalDialog(self.root, current_hours)
            self.root.wait_window(dialog.dialog)
            
            if dialog.result is not None:
                if self.core.set_time_goal(dialog.result):
                    self.time_left_label.config(
                        text=f"{self.core.format_timedelta(self.core.total_time)} left"
                    )
    
    def setup_buttons(self, button_frame):
        """Setup the control buttons"""
        # First row
        self.clock_in_btn = MinimalButton(button_frame,
                                        text="Lock In",
                                        command=self.clock_in)
        self.clock_in_btn.grid(row=0, column=0, padx=20, pady=20)
        
        self.clock_out_btn = MinimalButton(button_frame,
                                         text="Lock Out",
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
        worked_time, time_left = self.core.calculate_current_times()
        
        self.time_label.config(text=self.core.format_timedelta(worked_time))
        self.time_left_label.config(text=f"{self.core.format_timedelta(time_left)} left")
        
        # Update status label
        self.status_label.config(text=f"Status: {self.core.current_state.replace('_', ' ').title()}")
        
        # Schedule next update
        self.root.after(1000, self.update_time_display)
    
    def update_button_states(self):
        """Update button states based on current state"""
        current_state = self.core.current_state
        
        # Reset all buttons to disabled first
        self.clock_in_btn["state"] = "disabled"
        self.clock_out_btn["state"] = "disabled"
        self.break_in_btn["state"] = "disabled"
        self.break_out_btn["state"] = "disabled"
        
        # Enable buttons based on current state
        if current_state == "clocked_out":
            self.clock_in_btn["state"] = "normal"
        elif current_state == "clocked_in":
            self.clock_out_btn["state"] = "normal"
            self.break_in_btn["state"] = "normal"
        elif current_state == "break":
            self.break_out_btn["state"] = "normal"
    
    def clock_in(self):
        """Handle clock in event"""
        if self.core.clock_in():
            self.status_label.config(text="Status: Locked In")
            self.update_button_states()
    
    def clock_out(self):
        """Handle clock out event with confirmation"""
        dialog = ConfirmationDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            if self.core.clock_out():
                self.status_label.config(text="Status: Locked Out")
                self.time_label.config(text="0h 0m 0s")
                self.time_left_label.config(
                    text=f"{self.core.format_timedelta(self.core.total_time)} left"
                )
                self.update_button_states()
    
    def break_in(self):
        """Handle break start event"""
        if self.core.break_in():
            self.status_label.config(text="Status: On Break")
            self.update_button_states()
    
    def break_out(self):
        """Handle break end event"""
        if self.core.break_out():
            self.status_label.config(text="Status: Locked In")
            self.update_button_states()
    
    def show_weekly_summary(self):
        """Show weekly summary window"""
        WeeklySummaryWindow(self.root, self.core.get_records(), self.core.get_current_time)
    
    def toggle_dark_mode(self):
        """Toggle between light and dark mode"""
        self.dark_mode = not self.dark_mode
        StyleManager.toggle_dark_mode(self.dark_mode)
        
        # Update button text
        self.dark_mode_button.config(text="Light Mode" if self.dark_mode else "Dark Mode")
        
        # Update background of the root window
        self.root.configure(bg='#2d2d2d' if self.dark_mode else 'white')
    
    def on_closing(self):
        """Handle window closing event"""
        self.core.save_data()
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()