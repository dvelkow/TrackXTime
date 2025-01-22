import json
import os
from datetime import datetime, timedelta
import pytz

class TimeTrackerCore:
    def __init__(self):
        self.data_file = "time_records.json"
        
        # Initialize state variables with default values
        self.current_state = "clocked_out"
        self.clock_in_time = None
        self.break_start_time = None
        self.total_break_time = timedelta()
        self.today_worked_time = timedelta()
        self.total_time = timedelta(hours=16)  # Default total time
        self.time_left = self.total_time
        self.time_records = {}
        self.session_date = None  # Track the date of the current session
        
        # Load data and state
        self.load_data()

    def load_data(self):
        """Load time records and current state from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.time_records = data.get('records', {})
                
                # Load state
                state_data = data.get('current_state', {})
                if state_data:
                    self.current_state = state_data.get('state', 'clocked_out')
                    
                    # Convert stored times back to datetime objects
                    clock_in_str = state_data.get('clock_in_time')
                    self.clock_in_time = datetime.fromisoformat(clock_in_str) if clock_in_str else None
                    
                    break_start_str = state_data.get('break_start_time')
                    self.break_start_time = datetime.fromisoformat(break_start_str) if break_start_str else None
                    
                    # Convert stored timedeltas back to timedelta objects
                    total_break_seconds = state_data.get('total_break_time', 0)
                    self.total_break_time = timedelta(seconds=total_break_seconds)
                    
                    total_time_seconds = state_data.get('total_time', 57600)  # Default to 16 hours in seconds
                    self.total_time = timedelta(seconds=total_time_seconds)
                    
                    time_left_seconds = state_data.get('time_left', total_time_seconds)
                    self.time_left = timedelta(seconds=time_left_seconds)
                    
                    # Load session date
                    session_date = state_data.get('session_date')
                    self.session_date = session_date if session_date else None
        else:
            self.time_records = {}

    def save_data(self):
        """Save time records and current state to JSON file"""
        # Prepare state data
        state_data = {
            'state': self.current_state,
            'clock_in_time': self.clock_in_time.isoformat() if self.clock_in_time else None,
            'break_start_time': self.break_start_time.isoformat() if self.break_start_time else None,
            'total_break_time': self.total_break_time.total_seconds(),
            'total_time': self.total_time.total_seconds(),
            'time_left': self.time_left.total_seconds(),
            'session_date': self.session_date
        }
        
        # Combine records and state
        data = {
            'records': self.time_records,
            'current_state': state_data
        }
        
        # Save to file
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)

    def set_time_goal(self, hours):
        """Set new time goal in hours"""
        if self.current_state == "clocked_out":
            self.total_time = timedelta(hours=hours)
            self.time_left = self.total_time
            self.save_data()
            return True
        return False

    def get_time_goal_hours(self):
        """Get current time goal in hours"""
        return self.total_time.total_seconds() / 3600

    def format_timedelta(self, td):
        """Convert timedelta to hours, minutes and seconds format"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours}h {minutes}m {seconds}s"

    def get_current_time(self):
        """Get current time in EET timezone"""
        return datetime.now(pytz.timezone('EET'))

    def clock_in(self):
        """Handle clock in event"""
        self.current_state = "clocked_in"
        self.clock_in_time = self.get_current_time()
        self.total_break_time = timedelta()
        self.time_left = self.total_time
        # Set the session date to the clock-in date
        self.session_date = self.clock_in_time.strftime("%Y-%m-%d")
        self.save_data()
        return True

    def clock_out(self):
        """Handle clock out event"""
        if self.clock_in_time and self.session_date:
            current_time = self.get_current_time()
            worked_time = current_time - self.clock_in_time - self.total_break_time
            
            # Save to records using the session date
            self.time_records[self.session_date] = {
                "total_time": self.format_timedelta(worked_time),
                "breaks": self.format_timedelta(self.total_break_time),
                "clock_in": self.clock_in_time.strftime("%H:%M"),
                "clock_out": current_time.strftime("%H:%M")
            }
        
        # Reset state
        self.current_state = "clocked_out"
        self.clock_in_time = None
        self.total_break_time = timedelta()
        self.session_date = None  # Clear the session date
        self.save_data()
        return True

    def break_in(self):
        """Handle break start event"""
        self.current_state = "break"
        self.break_start_time = self.get_current_time()
        self.save_data()
        return True

    def break_out(self):
        """Handle break end event"""
        if self.break_start_time:
            current_time = self.get_current_time()
            self.total_break_time += current_time - self.break_start_time
        
        self.current_state = "clocked_in"
        self.break_start_time = None
        self.save_data()
        return True

    def calculate_current_times(self):
        """Calculate current worked time and time left"""
        if self.current_state in ["clocked_in", "break"]:
            current_time = self.get_current_time()
            
            if self.current_state == "clocked_in":
                worked_time = current_time - self.clock_in_time - self.total_break_time
                self.time_left = self.total_time - worked_time
            else:  # On break
                worked_time = current_time - self.clock_in_time - self.total_break_time - (current_time - self.break_start_time)
            
            return worked_time, self.time_left
        else:
            # Return default values if not clocked in or on break
            return timedelta(), self.total_time

    def get_records(self):
        """Get time records"""
        return self.time_records