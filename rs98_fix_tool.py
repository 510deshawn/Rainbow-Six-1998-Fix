#!/usr/bin/env python3
"""
Rainbow Six (1998) Compatibility Fix Tool for Windows 11 x64
Fixes common crashes and compatibility issues with the GOG version
"""

import os
import sys
import ctypes
import winreg
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json

class RainbowSixFixer:
    def __init__(self):
        self.game_path = None
        self.fixes_applied = []
        
    def find_game_installation(self):
        """Try to automatically find Rainbow Six installation"""
        # Common GOG installation paths
        possible_paths = [
            r"C:\GOG Games\Tom Clancy's Rainbow Six",
            r"C:\Program Files (x86)\GOG Galaxy\Games\Tom Clancy's Rainbow Six",
            r"C:\Program Files\GOG Galaxy\Games\Tom Clancy's Rainbow Six",
            r"D:\GOG Games\Tom Clancy's Rainbow Six",
            r"D:\Games\Tom Clancy's Rainbow Six"
        ]
        
        # Check registry for GOG installation
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\GOG.com\Games") as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                name = winreg.QueryValueEx(subkey, "gameName")[0]
                                if "Rainbow Six" in name:
                                    path = winreg.QueryValueEx(subkey, "path")[0]
                                    if os.path.exists(path):
                                        return path
                            except WindowsError:
                                pass
                        i += 1
                    except WindowsError:
                        break
        except:
            pass
        
        # Check common paths
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "RainbowSix.exe")):
                return path
        
        return None
    
    def apply_compatibility_settings(self):
        """Apply Windows compatibility settings to the executable"""
        if not self.game_path:
            return False
            
        exe_path = os.path.join(self.game_path, "Rainbow Six.exe")
        if not os.path.exists(exe_path):
            return False
        
        try:
            # Set compatibility mode via registry
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
            
            # Open or create the registry key
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS)
            except:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
            
            # Set compatibility flags
            # RUNASADMIN: Run as administrator
            # WIN98: Windows 98 compatibility mode
            # DISABLEDWM: Disable desktop composition
            # 640X480: Run in 640x480 (optional, can be removed if not needed)
            compat_flags = "~ RUNASADMIN WIN98 DISABLEDWM"
            
            winreg.SetValueEx(key, exe_path, 0, winreg.REG_SZ, compat_flags)
            winreg.CloseKey(key)
            
            self.fixes_applied.append("Applied Windows 98 compatibility mode")
            self.fixes_applied.append("Set to run as administrator")
            self.fixes_applied.append("Disabled desktop composition")
            return True
        except Exception as e:
            print(f"Error applying compatibility settings: {e}")
            return False
    
    def fix_audio_issues(self):
        """Fix audio-related crashes by modifying game configuration"""
        if not self.game_path:
            return False
        
        # Look for configuration files
        config_files = ["data\\audio.cfg", "audio.cfg", "sound.cfg"]
        fixed = False
        
        for config_file in config_files:
            cfg_path = os.path.join(self.game_path, config_file)
            if os.path.exists(cfg_path):
                try:
                    # Backup original
                    shutil.copy2(cfg_path, cfg_path + ".backup")
                    
                    # Read and modify configuration
                    with open(cfg_path, 'r') as f:
                        content = f.read()
                    
                    # Common audio fixes
                    modifications = [
                        ("SoundChannels=32", "SoundChannels=16"),
                        ("3DSound=1", "3DSound=0"),
                        ("UseEAX=1", "UseEAX=0"),
                        ("UseSurround=1", "UseSurround=0"),
                        ("SampleRate=44100", "SampleRate=22050")
                    ]
                    
                    for old, new in modifications:
                        content = content.replace(old, new)
                    
                    # Write back
                    with open(cfg_path, 'w') as f:
                        f.write(content)
                    
                    fixed = True
                    self.fixes_applied.append(f"Modified {config_file} for audio compatibility")
                except Exception as e:
                    print(f"Error modifying {config_file}: {e}")
        
        # Create a custom audio configuration if none exists
        if not fixed:
            try:
                custom_cfg = os.path.join(self.game_path, "audio.cfg")
                with open(custom_cfg, 'w') as f:
                    f.write("""[Audio]
SoundChannels=16
3DSound=0
UseEAX=0
UseSurround=0
SampleRate=22050
AudioQuality=Low
DisableHardwareAcceleration=1
""")
                self.fixes_applied.append("Created custom audio configuration")
                fixed = True
            except:
                pass
        
        return fixed
    
    def apply_cpu_affinity_fix(self):
        """Create a batch file to run the game with single CPU affinity"""
        if not self.game_path:
            return False
        
        batch_content = """@echo off
echo Starting Rainbow Six with compatibility fixes...

REM Set single CPU affinity to prevent timing issues
start /affinity 1 /high "Rainbow Six" "RainbowSix.exe"

exit
"""
        
        try:
            batch_path = os.path.join(self.game_path, "RainbowSix_Fixed.bat")
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            self.fixes_applied.append("Created CPU affinity launcher (RainbowSix_Fixed.bat)")
            return True
        except Exception as e:
            print(f"Error creating batch file: {e}")
            return False
    
    def install_dgvoodoo(self):
        """Instructions for dgVoodoo2 (3D acceleration wrapper)"""
        dgvoodoo_info = """
dgVoodoo2 Installation (Manual Step Required):

1. Download dgVoodoo2 from: https://dege.freeweb.hu/dgVoodoo2/dgVoodoo2/
2. Extract the following files to your Rainbow Six game folder:
   - D3D8.dll
   - D3D9.dll
   - D3DImm.dll
   - DDraw.dll
   - dgVoodoo.conf
   - dgVoodooCpl.exe

3. Run dgVoodooCpl.exe and configure:
   - Set resolution to your preference
   - Enable "Force vSync"
   - Set "Videocard" to your GPU
   - Apply and close

This fixes many graphics-related crashes and improves compatibility.
"""
        self.fixes_applied.append("dgVoodoo2 installation instructions provided")
        return dgvoodoo_info
    
    def create_mission_fix(self):
        """Create configuration to fix mission-specific crashes"""
        if not self.game_path:
            return False
        
        # Common mission crash fixes
        mission_cfg = """[MissionFixes]
; Disable problematic features for specific missions
DisableSmoke=1
DisableDynamicLighting=1
ReduceTextureQuality=1
DisableWeatherEffects=1

[MemoryFixes]
; Increase heap size for stability
HeapSize=256
UselargeAddressAware=1
"""
        
        try:
            cfg_path = os.path.join(self.game_path, "mission_fixes.cfg")
            with open(cfg_path, 'w') as f:
                f.write(mission_cfg)
            
            self.fixes_applied.append("Created mission crash fix configuration")
            return True
        except:
            return False

class FixerGUI:
    def __init__(self):
        self.fixer = RainbowSixFixer()
        self.root = tk.Tk()
        self.root.title("Rainbow Six (1998) Compatibility Fixer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Set admin icon if running as admin
        if ctypes.windll.shell32.IsUserAnAdmin():
            self.root.title("Rainbow Six (1998) Compatibility Fixer [Administrator]")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = ttk.Label(self.root, text="Rainbow Six (1998) Compatibility Fixer", 
                          font=("Arial", 16, "bold"))
        header.pack(pady=10)
        
        # Game path frame
        path_frame = ttk.Frame(self.root)
        path_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(path_frame, text="Game Location:").pack(side="left")
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=40)
        self.path_entry.pack(side="left", padx=5)
        
        ttk.Button(path_frame, text="Browse", command=self.browse_game).pack(side="left")
        ttk.Button(path_frame, text="Auto-Detect", command=self.auto_detect).pack(side="left", padx=5)
        
        # Fixes frame
        fixes_frame = ttk.LabelFrame(self.root, text="Available Fixes", padding=10)
        fixes_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.fix_options = {
            "compatibility": tk.BooleanVar(value=True),
            "audio": tk.BooleanVar(value=True),
            "cpu_affinity": tk.BooleanVar(value=True),
            "mission_fixes": tk.BooleanVar(value=True),
            "dgvoodoo": tk.BooleanVar(value=True)
        }
        
        ttk.Checkbutton(fixes_frame, text="Apply Windows 98 Compatibility Mode", 
                       variable=self.fix_options["compatibility"]).pack(anchor="w", pady=2)
        ttk.Checkbutton(fixes_frame, text="Fix Audio Crashes (Disable EAX/3D Sound)", 
                       variable=self.fix_options["audio"]).pack(anchor="w", pady=2)
        ttk.Checkbutton(fixes_frame, text="Create CPU Affinity Launcher", 
                       variable=self.fix_options["cpu_affinity"]).pack(anchor="w", pady=2)
        ttk.Checkbutton(fixes_frame, text="Apply Mission-Specific Crash Fixes", 
                       variable=self.fix_options["mission_fixes"]).pack(anchor="w", pady=2)
        ttk.Checkbutton(fixes_frame, text="Show dgVoodoo2 Instructions (Graphics Fix)", 
                       variable=self.fix_options["dgvoodoo"]).pack(anchor="w", pady=2)
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready to apply fixes...")
        self.progress_label = ttk.Label(self.root, textvariable=self.progress_var)
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.apply_btn = ttk.Button(button_frame, text="Apply Fixes", 
                                   command=self.apply_fixes, state="disabled")
        self.apply_btn.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side="left", padx=5)
        
        # Output text
        self.output_text = tk.Text(self.root, height=8, width=70)
        self.output_text.pack(padx=20, pady=10)
        
        # Auto-detect on startup
        self.auto_detect()
    
    def browse_game(self):
        folder = filedialog.askdirectory(title="Select Rainbow Six Installation Folder")
        if folder:
            self.path_var.set(folder)
            self.fixer.game_path = folder
            self.apply_btn["state"] = "normal"
    
    def auto_detect(self):
        self.progress_var.set("Auto-detecting game installation...")
        path = self.fixer.find_game_installation()
        if path:
            self.path_var.set(path)
            self.fixer.game_path = path
            self.apply_btn["state"] = "normal"
            self.output_text.insert("end", f"Game found at: {path}\n")
        else:
            self.output_text.insert("end", "Could not auto-detect game. Please browse manually.\n")
    
    def apply_fixes(self):
        if not ctypes.windll.shell32.IsUserAnAdmin():
            messagebox.showwarning("Administrator Required", 
                                 "This tool needs to run as Administrator to apply all fixes.\n"
                                 "Please right-click and select 'Run as administrator'.")
            return
        
        self.apply_btn["state"] = "disabled"
        self.progress_bar.start()
        
        # Run fixes in a separate thread
        thread = threading.Thread(target=self._apply_fixes_thread)
        thread.start()
    
    def _apply_fixes_thread(self):
        self.fixer.fixes_applied = []
        
        if self.fix_options["compatibility"].get():
            self.progress_var.set("Applying compatibility settings...")
            self.fixer.apply_compatibility_settings()
        
        if self.fix_options["audio"].get():
            self.progress_var.set("Fixing audio issues...")
            self.fixer.fix_audio_issues()
        
        if self.fix_options["cpu_affinity"].get():
            self.progress_var.set("Creating CPU affinity launcher...")
            self.fixer.apply_cpu_affinity_fix()
        
        if self.fix_options["mission_fixes"].get():
            self.progress_var.set("Applying mission crash fixes...")
            self.fixer.create_mission_fix()
        
        # Update GUI in main thread
        self.root.after(0, self._fixes_complete)
    
    def _fixes_complete(self):
        self.progress_bar.stop()
        self.progress_var.set("Fixes applied!")
        self.apply_btn["state"] = "normal"
        
        # Show results
        self.output_text.delete(1.0, "end")
        self.output_text.insert("end", "=== Fixes Applied ===\n\n")
        
        for fix in self.fixer.fixes_applied:
            self.output_text.insert("end", f"✓ {fix}\n")
        
        if self.fix_options["dgvoodoo"].get():
            dgvoodoo_info = self.fixer.install_dgvoodoo()
            self.output_text.insert("end", f"\n{dgvoodoo_info}\n")
        
        self.output_text.insert("end", "\n=== Next Steps ===\n")
        self.output_text.insert("end", "1. Use 'RainbowSix_Fixed.bat' to launch the game\n")
        self.output_text.insert("end", "2. If crashes persist, try disabling hardware acceleration\n")
        self.output_text.insert("end", "3. Consider installing dgVoodoo2 for graphics issues\n")
    
    def run(self):
        self.root.mainloop()

def main():
    # Check if running with admin rights
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # Re-run the program with admin rights
        response = messagebox.askyesno("Administrator Required", 
                                     "This tool requires administrator privileges to apply all fixes.\n"
                                     "Would you like to restart with administrator rights?")
        if response:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    
    # Create and run GUI
    app = FixerGUI()
    app.run()

if __name__ == "__main__":
    main()
