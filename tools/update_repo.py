import os
import shutil
import hashlib
import zipfile
import re

# Configuration
PLUGIN_ID = "plugin.video.mis.favoritos"
REPO_DIR = "repository"
TOOLS_DIR = "tools"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_addon_version(addon_xml_path):
    with open(addon_xml_path, 'r') as f:
        content = f.read()
        # Look for the version attribute specifically in the addon tag
        # We search specifically for <addon ... version="..." because other tags like <import> also have version attributes
        match = re.search(r'<addon[^>]+version="([^"]+)"', content)
        if match:
            return match.group(1)
    return None

def create_zip(plugin_path, version, destination_dir):
    zip_name = f"{PLUGIN_ID}-{version}.zip"
    zip_path = os.path.join(destination_dir, zip_name)
    
    print(f"Creating zip: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(plugin_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate relative path from the plugin root, but prepend the plugin ID folder
                rel_path = os.path.relpath(file_path, os.path.dirname(plugin_path))
                zipf.write(file_path, rel_path)
    return zip_name

def generate_addons_xml(repo_path):
    print("Generating addons.xml...")
    addons_xml_content = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
    
    # Find all addon.xml files in the repo structure (we simply copy the one from source for now)
    # But better: read the source addon.xml
    source_addon_xml = os.path.join(PROJECT_ROOT, PLUGIN_ID, "addon.xml")
    
    if os.path.exists(source_addon_xml):
        with open(source_addon_xml, 'r') as f:
            xml_lines = f.readlines()
            # Skip definition lines if we were merging multiple, but here we just embed it
            # Strip standard xml header to avoid duplication if we were looping
            for line in xml_lines:
                if line.strip().startswith('<?xml'): continue
                addons_xml_content += line
    
    addons_xml_content += '</addons>\n'
    
    xml_path = os.path.join(repo_path, "addons.xml")
    with open(xml_path, 'w') as f:
        f.write(addons_xml_content)
        
    return xml_path

def generate_md5(file_path):
    print(f"Generating MD5 for {file_path}")
    with open(file_path, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    
    with open(file_path + ".md5", 'w') as f:
        f.write(md5)

def generate_index_html(directory, title="Kodi Repository"):
    print(f"Generating index.html for {directory}")
    items = sorted(os.listdir(directory))
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: monospace; }}
        a {{ text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <hr>
    <pre>
<a href="../">../</a>
"""
    for item in items:
        if item == "index.html" or item.startswith("."): continue
        is_dir = os.path.isdir(os.path.join(directory, item))
        display_name = item + ("/" if is_dir else "")
        html += f'<a href="{item}">{display_name}</a>\n'

    html += """    </pre>
    <hr>
</body>
</html>
"""
    with open(os.path.join(directory, "index.html"), 'w') as f:
        f.write(html)

def main():
    repo_path = os.path.join(PROJECT_ROOT, REPO_DIR)
    plugin_src = os.path.join(PROJECT_ROOT, PLUGIN_ID)
    addon_xml = os.path.join(plugin_src, "addon.xml")
    
    if not os.path.exists(addon_xml):
        print(f"Error: Could not find {addon_xml}")
        return

    version = get_addon_version(addon_xml)
    print(f"Detected version: {version}")
    
    # 1. Prepare structure
    plugin_dest_dir = os.path.join(repo_path, PLUGIN_ID)
    if os.path.exists(plugin_dest_dir):
        shutil.rmtree(plugin_dest_dir)
    os.makedirs(plugin_dest_dir)
    
    # 2. Copy addon.xml to plugin folder in repo
    shutil.copy(addon_xml, os.path.join(plugin_dest_dir, "addon.xml"))
    
    # 3. Create Zip
    create_zip(plugin_src, version, plugin_dest_dir)
    
    # 4. Generate Root addons.xml and md5
    xml_path = generate_addons_xml(repo_path)
    generate_md5(xml_path)
    
    # 5. Generate index.html files (for root and plugin dir)
    generate_index_html(repo_path, "Kodi Repository Root")
    generate_index_html(plugin_dest_dir, f"Index of {PLUGIN_ID}")
    
    print("\nRepository build complete!")
    print(f"Repository location: {repo_path}")

if __name__ == "__main__":
    main()
