import sys
import os

print("Verifying imports...")
try:
    from config import settings
    print("Config loaded")
    from utils import registry, system, files
    print("Utils loaded")
    from ui import components, animations, dialogs
    print("UI loaded")
    from features import security, optimization, maintenance
    print("Features loaded")
    from main import CacheCoreApp
    print("Main app class loaded")
    print("ALL IMPORTS SUCCESSFUL")
except Exception as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)
