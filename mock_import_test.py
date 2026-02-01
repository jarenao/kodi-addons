import sys
import os

# Simulate Kodi path structure where root plugin dir is in path
plugin_root = os.path.abspath("plugin.video.mis.favoritos")
sys.path.append(plugin_root)

try:
    from resources.lib.context_menu import main
    print("SUCCESS: Import worked")
except ImportError as e:
    print(f"ERROR: {e}")
    # Fix simulation
    print("Attempting to fix sys.path...")
    
except Exception as e:
    print(f"RUNTIME ERROR: {e}")
