import os
import hashlib
import zipfile
import xml.etree.ElementTree as ET

REPO_DIR = "repository"

def check_md5(file_path):
    if not os.path.exists(file_path):
        print(f"[FAIL] Missing {file_path}")
        return False
    
    md5_path = file_path + ".md5"
    if not os.path.exists(md5_path):
        print(f"[FAIL] Missing MD5 for {file_path}")
        return False
        
    with open(file_path, 'rb') as f:
        calculated = hashlib.md5(f.read()).hexdigest()
        
    with open(md5_path, 'r') as f:
        stored = f.read().strip()
        
    if calculated == stored:
        print(f"[PASS] MD5 matches for {file_path}")
        return True
    else:
        print(f"[FAIL] MD5 mismatch for {file_path}. Stored: {stored}, Calc: {calculated}")
        return False

def check_zip_structure(zip_path, addon_id):
    if not os.path.exists(zip_path):
        print(f"[FAIL] Missing zip {zip_path}")
        return False
        
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Check if all files start with addon_id/
            bad_files = [f for f in zf.namelist() if not f.startswith(addon_id + "/")]
            if bad_files:
                print(f"[FAIL] Zip {zip_path} contains files not under {addon_id}/ directory: {bad_files[:5]}...")
                return False
                
            # Check for addon.xml inside zip
            if f"{addon_id}/addon.xml" not in zf.namelist():
                print(f"[FAIL] Zip {zip_path} missing addon.xml")
                return False
                
            print(f"[PASS] Zip structure correct for {zip_path}")
            return True
    except zipfile.BadZipFile:
        print(f"[FAIL] Bad zip file {zip_path}")
        return False

def main():
    if not os.path.exists(REPO_DIR):
        print(f"Repository directory {REPO_DIR} not found.")
        return

    # 1. Check root addons.xml
    addons_xml = os.path.join(REPO_DIR, "addons.xml")
    if check_md5(addons_xml):
        # 2. Parse addons.xml to find plugins
        try:
            tree = ET.parse(addons_xml)
            root = tree.getroot()
            for addon in root.findall('addon'):
                addon_id = addon.get('id')
                version = addon.get('version')
                print(f"Found addon: {addon_id} v{version}")
                
                # 3. Check if Plugin Zip exists
                zip_name = f"{addon_id}-{version}.zip"
                zip_path = os.path.join(REPO_DIR, addon_id, zip_name)
                
                if check_zip_structure(zip_path, addon_id):
                    print(f"[PASS] Addon {addon_id} passed checks.")
                else:
                    print(f"[FAIL] Addon {addon_id} failed checks.")
                    
        except ET.ParseError as e:
            print(f"[FAIL] Error parsing addons.xml: {e}")

if __name__ == "__main__":
    main()
