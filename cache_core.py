import sys
import os

# Ensure the current directory is in path to find our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

if __name__ == "__main__":
    try:
        from main import CacheCoreApp
    except ImportError as e:
        print(f"Error importing CacheCoreApp: {e}")
        # Fallback debug info
        print(f"Current path: {sys.path}")
        print(f"Current directory contents: {os.listdir(current_dir)}")
        input("Press Enter to exit...")
        sys.exit(1)

    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
    app = CacheCoreApp()
    app.root.mainloop()
