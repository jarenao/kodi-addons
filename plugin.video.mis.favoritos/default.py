import sys
import urllib.parse
import xbmcgui
import xbmcplugin
import xbmc

from resources.lib.storage import JSONStorage

# Constants
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]
STORAGE = JSONStorage()

def log(msg):
    xbmc.log(f"[MisFavoritos] {msg}", level=xbmc.LOGINFO)

def main():
    """
    Main plugin dispatcher.
    """
    args = urllib.parse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', [None])[0]
    folder_id = args.get('folder_id', ['root'])[0]
    
    log(f"Started. Mode: {mode}, Folder: {folder_id}")

    if mode is None:
        # List root folder
        list_folder(folder_id)
    elif mode == 'folder':
        list_folder(folder_id)
    elif mode == 'add_folder':
        add_new_folder(folder_id)
    elif mode == 'add_item':
        add_new_item_dialog(folder_id)
        
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_folder(folder_id):
    """
    List contents of a specific folder from JSON storage.
    """
    xbmcplugin.setContent(ADDON_HANDLE, 'videos')
    
    # 1. Get contents
    items = STORAGE.get_folder_contents(folder_id)
    
    # 2. List Items
    for item in items:
        if item['type'] == 'folder':
            li = xbmcgui.ListItem(label=f"[COLOR blue]{item['name']}[/COLOR]")
            url = build_url({'mode': 'folder', 'folder_id': item['id']})
            is_folder = True
        else:
            # It's an item/file
            li = xbmcgui.ListItem(label=item['name'])
            li.setArt({'thumb': item.get('thumbnail', '')})
            url = item['url']
            is_folder = False
        
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=is_folder)
    
    # 3. Management Menu (Always at the bottom/top?)
    # Create "Add Folder" Item
    li = xbmcgui.ListItem(label="[COLOR green]+ Crear Carpeta[/COLOR]")
    url = build_url({'mode': 'add_folder', 'folder_id': folder_id})
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)
    
    # Create "Add Item" Item
    li = xbmcgui.ListItem(label="[COLOR yellow]+ Añadir Favorito (Manual)[/COLOR]")
    url = build_url({'mode': 'add_item', 'folder_id': folder_id})
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)

def add_new_folder(parent_id):
    kbd = xbmc.Keyboard('', 'Nombre de la carpeta')
    kbd.doModal()
    if kbd.isConfirmed():
        name = kbd.getText()
        if name:
            log(f"Creating folder '{name}' in '{parent_id}'")
            if STORAGE.add_folder(parent_id, name):
                xbmc.executebuiltin('Container.Refresh')
            else:
                xbmcgui.Dialog().notification('Error', 'No se pudo crear la carpeta', xbmcgui.NOTIFICATION_ERROR)

def add_new_item_dialog(parent_id):
    # Dialog for Name
    kbd = xbmc.Keyboard('', 'Nombre del favorito')
    kbd.doModal()
    if not kbd.isConfirmed(): return
    name = kbd.getText()
    
    # Dialog for URL
    kbd = xbmc.Keyboard('', 'URL / plugin://...')
    kbd.doModal()
    if not kbd.isConfirmed(): return
    url_link = kbd.getText()
    
    if name and url_link:
        log(f"Creating item '{name}' -> '{url_link}'")
        if STORAGE.add_item(parent_id, name, url_link, ''):
            xbmc.executebuiltin('Container.Refresh')
        else:
            xbmcgui.Dialog().notification('Error', 'No se pudo añadir el item', xbmcgui.NOTIFICATION_ERROR)

def build_url(query):
    return BASE_URL + '?' + urllib.parse.urlencode(query)

if __name__ == '__main__':
    main()
