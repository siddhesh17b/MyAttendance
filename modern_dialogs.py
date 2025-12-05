"""
Modern Dialog System for BunkMeter
Custom styled dialogs to replace plain tkinter messageboxes

Author: Siddhesh Bisen, GitHub: https://github.com/siddhesh17b
"""

import tkinter as tk
from tkinter import ttk

class ModernDialog:
    """
    Custom modern dialog class with themed styling
    
    Dialog types:
    - info: Blue theme with ℹ️ icon
    - success: Green theme with ✅ icon
    - warning: Orange/Yellow theme with ⚠️ icon
    - error: Red theme with ❌ icon
    - confirm: Blue theme with ❓ icon, Yes/No buttons
    """
    
    # Theme colors for different dialog types
    THEMES = {
        "info": {
            "bg": "#e3f2fd",
            "header_bg": "#1976d2",
            "header_fg": "white",
            "text_fg": "#1565c0",
            "icon": "ℹ️",
            "btn_bg": "#1976d2",
            "btn_fg": "white",
            "btn_hover": "#1565c0"
        },
        "success": {
            "bg": "#e8f5e9",
            "header_bg": "#388e3c",
            "header_fg": "white",
            "text_fg": "#2e7d32",
            "icon": "✅",
            "btn_bg": "#388e3c",
            "btn_fg": "white",
            "btn_hover": "#2e7d32"
        },
        "warning": {
            "bg": "#fff8e1",
            "header_bg": "#f57c00",
            "header_fg": "white",
            "text_fg": "#e65100",
            "icon": "⚠️",
            "btn_bg": "#f57c00",
            "btn_fg": "white",
            "btn_hover": "#e65100"
        },
        "error": {
            "bg": "#ffebee",
            "header_bg": "#d32f2f",
            "header_fg": "white",
            "text_fg": "#c62828",
            "icon": "❌",
            "btn_bg": "#d32f2f",
            "btn_fg": "white",
            "btn_hover": "#c62828"
        },
        "confirm": {
            "bg": "#e3f2fd",
            "header_bg": "#1976d2",
            "header_fg": "white",
            "text_fg": "#1565c0",
            "icon": "❓",
            "btn_bg": "#1976d2",
            "btn_fg": "white",
            "btn_hover": "#1565c0"
        }
    }
    
    def __init__(self, parent, title, message, dialog_type="info", buttons=None):
        """
        Create a modern styled dialog
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Message to display
            dialog_type: One of 'info', 'success', 'warning', 'error', 'confirm'
            buttons: List of button configs [{"text": "OK", "command": func, "primary": True}]
        """
        self.result = None
        self.parent = parent
        
        # Get theme
        theme = self.THEMES.get(dialog_type, self.THEMES["info"])
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.configure(bg=theme["bg"])
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Remove window decorations for cleaner look (optional)
        # self.dialog.overrideredirect(True)
        
        # Main container with border
        main_frame = tk.Frame(
            self.dialog, 
            bg=theme["bg"],
            highlightthickness=2,
            highlightbackground=theme["header_bg"]
        )
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header bar
        header = tk.Frame(main_frame, bg=theme["header_bg"], height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=f"{theme['icon']} {title}",
            font=("Segoe UI", 12, "bold"),
            bg=theme["header_bg"],
            fg=theme["header_fg"],
            padx=15
        ).pack(side=tk.LEFT, pady=10)
        
        # Content area
        content = tk.Frame(main_frame, bg=theme["bg"], padx=25, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Message with icon
        msg_frame = tk.Frame(content, bg=theme["bg"])
        msg_frame.pack(fill=tk.X)
        
        tk.Label(
            msg_frame,
            text=theme["icon"],
            font=("Segoe UI", 28),
            bg=theme["bg"]
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(
            msg_frame,
            text=message,
            font=("Segoe UI", 11),
            bg=theme["bg"],
            fg=theme["text_fg"],
            justify=tk.LEFT,
            wraplength=350
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Button area
        btn_frame = tk.Frame(content, bg=theme["bg"])
        btn_frame.pack(fill=tk.X, pady=(20, 5))
        
        # Default buttons if none provided
        if buttons is None:
            buttons = [{"text": "OK", "command": self.close, "primary": True}]
        
        # Create buttons (right-aligned)
        for btn_config in reversed(buttons):
            is_primary = btn_config.get("primary", False)
            btn = tk.Button(
                btn_frame,
                text=btn_config["text"],
                font=("Segoe UI", 10, "bold" if is_primary else "normal"),
                bg=theme["btn_bg"] if is_primary else "#ffffff",
                fg=theme["btn_fg"] if is_primary else theme["btn_bg"],
                activebackground=theme["btn_hover"],
                activeforeground="white",
                relief=tk.FLAT,
                padx=20,
                pady=6,
                cursor="hand2",
                highlightthickness=1 if not is_primary else 0,
                highlightbackground=theme["btn_bg"],
                command=btn_config.get("command", self.close)
            )
            btn.pack(side=tk.RIGHT, padx=(8, 0))
        
        # Center dialog on parent
        self.center_on_parent()
        
        # Handle close button
        self.dialog.protocol("WM_DELETE_WINDOW", self.close)
        
        # Bind escape key
        self.dialog.bind("<Escape>", lambda e: self.close())
        
        # Focus dialog
        self.dialog.focus_set()
    
    def center_on_parent(self):
        """Center the dialog on the parent window"""
        self.dialog.update_idletasks()
        
        # Get sizes
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Ensure minimum size
        if dialog_width < 400:
            dialog_width = 400
            self.dialog.geometry(f"{dialog_width}x{dialog_height}")
        
        # Get parent position
        if self.parent:
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
        else:
            # Center on screen
            screen_width = self.dialog.winfo_screenwidth()
            screen_height = self.dialog.winfo_screenheight()
            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def close(self):
        """Close the dialog"""
        self.dialog.destroy()
    
    def wait(self):
        """Wait for dialog to close and return result"""
        self.dialog.wait_window()
        return self.result


# Convenience functions to replace messagebox calls

def show_info(parent, title, message):
    """Show an info dialog (replaces messagebox.showinfo)"""
    if parent is None:
        parent = tk._default_root
    dialog = ModernDialog(parent, title, message, "info")
    dialog.wait()

def show_success(parent, title, message):
    """Show a success dialog"""
    if parent is None:
        parent = tk._default_root
    dialog = ModernDialog(parent, title, message, "success")
    dialog.wait()

def show_warning(parent, title, message):
    """Show a warning dialog (replaces messagebox.showwarning)"""
    if parent is None:
        parent = tk._default_root
    dialog = ModernDialog(parent, title, message, "warning")
    dialog.wait()

def show_error(parent, title, message):
    """Show an error dialog (replaces messagebox.showerror)"""
    if parent is None:
        parent = tk._default_root
    dialog = ModernDialog(parent, title, message, "error")
    dialog.wait()

def ask_yes_no(parent, title, message):
    """Show a confirmation dialog (replaces messagebox.askyesno)"""
    if parent is None:
        parent = tk._default_root
    result = [False]  # Use list to allow modification in nested function
    
    def on_yes():
        result[0] = True
        dialog.close()
    
    def on_no():
        result[0] = False
        dialog.close()
    
    buttons = [
        {"text": "Yes", "command": on_yes, "primary": True},
        {"text": "No", "command": on_no, "primary": False}
    ]
    
    dialog = ModernDialog(parent, title, message, "confirm", buttons)
    dialog.wait()
    return result[0]


# Drop-in replacement class that mimics tkinter.messagebox API exactly
class messagebox:
    """
    Drop-in replacement for tkinter.messagebox with modern styling.
    
    Usage - just replace the import:
        # OLD: from tkinter import messagebox
        # NEW: from modern_dialogs import messagebox
        
        messagebox.showinfo("Title", "Message")  # Works exactly like before!
    """
    
    @staticmethod
    def showinfo(title, message, **kwargs):
        """Show info dialog - compatible with tkinter.messagebox.showinfo"""
        show_info(None, title, message)
    
    @staticmethod
    def showwarning(title, message, **kwargs):
        """Show warning dialog - compatible with tkinter.messagebox.showwarning"""
        show_warning(None, title, message)
    
    @staticmethod
    def showerror(title, message, **kwargs):
        """Show error dialog - compatible with tkinter.messagebox.showerror"""
        show_error(None, title, message)
    
    @staticmethod
    def askyesno(title, message, **kwargs):
        """Show yes/no dialog - compatible with tkinter.messagebox.askyesno"""
        return ask_yes_no(None, title, message)
    
    @staticmethod
    def showsuccess(title, message, **kwargs):
        """Show success dialog (BunkMeter extension)"""
        show_success(None, title, message)
