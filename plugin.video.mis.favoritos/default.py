import sys
import urllib.parse
import xbmcgui
import xbmcplugin
import xbmc

from resources.lib.storage import JSONStorage
from resources.lib.kodi_importer import KodiFavoritesImporter

# Constants
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]
STORAGE = JSONStorage()
IMPORTER = KodiFavoritesImporter()

def log(msg):
    xbmc.log(f"[MisFavoritos] {msg}", level=xbmc.LOGINFO)

def main():
    """
    Main plugin dispatcher.
    """
    args = urllib.parse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', [None])[0]
    folder_id = args.get('folder_id', ['root'])[0]
    item_id = args.get('item_id', [None])[0]
    
    log(f"Started. Mode: {mode}, Folder: {folder_id}, Item: {item_id}")

    if mode is None:
        # List root folder
        list_folder(folder_id)
    elif mode == 'folder':
        list_folder(folder_id)
    elif mode == 'add_folder':
        add_new_folder(folder_id)
    elif mode == 'add_item':
        add_new_item_dialog(folder_id)
    elif mode == 'rename_folder':
        rename_folder(item_id)
    elif mode == 'delete_folder':
        delete_folder(item_id)
    elif mode == 'rename_item':
        rename_item(item_id)
    elif mode == 'delete_item':
        delete_item(item_id)
    elif mode == 'move_item':
        move_item(item_id)
    elif mode == 'edit_item':
        edit_item(item_id)
    elif mode == 'import_kodi':
        import_from_kodi(folder_id)
    elif mode == 'multi_move':
        multi_move_items(folder_id)

def list_folder(folder_id):
    """
    List contents of a specific folder from JSON storage.
    """
    # Use 'movies' content to allow Poster/Fanart views
    xbmcplugin.setContent(ADDON_HANDLE, 'movies')
    # Removed sort method to keep Management Items at the bottom!
    # xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    
    # 1. Get contents and Sort them in Python
    items = STORAGE.get_folder_contents(folder_id)
    # Sort: Folders first, then Items. Both alphabetical.
    items.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))
    
    # 2. List Items
    for item in items:
        if item['type'] == 'folder':
            li = xbmcgui.ListItem(label=f"[COLOR dodgerblue]🗂️ {item['name']}[/COLOR]")
            li.setArt({'icon': 'DefaultFolder.png', 'thumb': 'DefaultFolder.png'})
            # Set InfoTag to allow better view types
            li.setInfo('video', {'title': item['name'], 'plot': 'Carpeta'})
            url = build_url({'mode': 'folder', 'folder_id': item['id']})
            is_folder = True
            
            # Context menu for folders
            context_menu = [
                ('Renombrar', f'RunPlugin({build_url({"mode": "rename_folder", "item_id": item["id"]})})')
            ]
            if item['id'] != 'root':  # Can't delete root
                context_menu.append(('Eliminar', f'RunPlugin({build_url({"mode": "delete_folder", "item_id": item["id"]})})'))
            li.addContextMenuItems(context_menu)
        else:
            # It's an item/file
            li = xbmcgui.ListItem(label=item['name'])
            thumb = item.get('thumbnail', 'DefaultShortcut.png')
            li.setArt({'icon': 'DefaultShortcut.png', 'thumb': thumb, 'poster': thumb, 'fanart': thumb})
            # Set InfoTag to allow better view types
            li.setInfo('video', {'title': item['name'], 'mediatype': 'video'})
            # CRITICAL: Set IsPlayable property so Kodi knows to play it
            li.setProperty('IsPlayable', 'true')
            url = item['url']
            is_folder = False
            
            # Context menu for items
            context_menu = [
                ('Renombrar', f'RunPlugin({build_url({"mode": "rename_item", "item_id": item["id"]})})'),
                ('Editar', f'RunPlugin({build_url({"mode": "edit_item", "item_id": item["id"]})})'),
                ('Mover a...', f'RunPlugin({build_url({"mode": "move_item", "item_id": item["id"]})})'),
                ('Eliminar', f'RunPlugin({build_url({"mode": "delete_item", "item_id": item["id"]})})')
            ]
            li.addContextMenuItems(context_menu)
        
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=is_folder)
    
    # 3. Management Menu (Always at the bottom/top?)
    # Create "Add Folder" Item
    li = xbmcgui.ListItem(label="[COLOR lime]➕ Crear Carpeta[/COLOR]")
    li.setArt({'icon': 'DefaultFolderSquare.png', 'thumb': 'DefaultFolderSquare.png', 'poster': 'DefaultFolderSquare.png', 'fanart': 'DefaultFolderSquare.png'})
    li.setInfo('video', {'title': 'Crear Carpeta', 'plot': 'Crear una nueva carpeta'})
    li.setProperty('IsPlayable', 'false')  # Not playable
    url = build_url({'mode': 'add_folder', 'folder_id': folder_id})
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)
    
    # Create "Add Item" Item
    li = xbmcgui.ListItem(label="[COLOR gold]⭐ Añadir Enlace Directo[/COLOR]")
    li.setArt({'icon': 'DefaultAddonVideo.png', 'thumb': 'DefaultAddonVideo.png', 'poster': 'DefaultAddonVideo.png', 'fanart': 'DefaultAddonVideo.png'})
    li.setInfo('video', {'title': 'Añadir Enlace', 'plot': 'Añadir manualmente un enlace'})
    li.setProperty('IsPlayable', 'false')
    url = build_url({'mode': 'add_item', 'folder_id': folder_id})
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)
    
    # Import from Kodi
    li = xbmcgui.ListItem(label="[COLOR cyan]📥 Importar[/COLOR]")
    li.setArt({'icon': 'DefaultAddonService.png', 'thumb': 'DefaultAddonService.png', 'poster': 'DefaultAddonService.png', 'fanart': 'DefaultAddonService.png'})
    li.setInfo('video', {'title': 'Importar', 'plot': 'Importar favoritos nativos'})
    li.setProperty('IsPlayable', 'false')
    url = build_url({'mode': 'import_kodi', 'folder_id': folder_id})
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)
    
    # Multi-select move
    if len(items) > 0:  # Only show if there are items
        li = xbmcgui.ListItem(label="[COLOR orange]📦 Mover[/COLOR]")
        li.setArt({'icon': 'DefaultAddonService.png', 'thumb': 'DefaultAddonService.png', 'poster': 'DefaultAddonService.png', 'fanart': 'DefaultAddonService.png'})
        li.setInfo('video', {'title': 'Mover', 'plot': 'Mover múltiples elementos'})
        li.setProperty('IsPlayable', 'false')
        url = build_url({'mode': 'multi_move', 'folder_id': folder_id})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    
    # Force Poster View (501) for large images
    xbmc.executebuiltin('Container.SetViewMode(501)')

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

def rename_folder(folder_id):
    folder = STORAGE._find_node(STORAGE.data, folder_id)
    if folder:
        kbd = xbmc.Keyboard(folder['name'], 'Nuevo nombre')
        kbd.doModal()
        if kbd.isConfirmed():
            new_name = kbd.getText()
            if new_name and STORAGE.rename_folder(folder_id, new_name):
                xbmc.executebuiltin('Container.Refresh')
            else:
                xbmcgui.Dialog().notification('Error', 'No se pudo renombrar', xbmcgui.NOTIFICATION_ERROR)

def delete_folder(folder_id):
    folder = STORAGE._find_node(STORAGE.data, folder_id)
    if folder:
        # Check if folder has children
        has_children = len(folder.get('children', [])) > 0
        msg = f"¿Eliminar '{folder['name']}'?"
        if has_children:
            msg += "\n\n⚠️ La carpeta contiene elementos que también se eliminarán."
        
        if xbmcgui.Dialog().yesno('Confirmar eliminación', msg):
            if STORAGE.delete_folder(folder_id):
                xbmc.executebuiltin('Container.Refresh')
            else:
                xbmcgui.Dialog().notification('Error', 'No se pudo eliminar', xbmcgui.NOTIFICATION_ERROR)

def rename_item(item_id):
    item = STORAGE._find_node(STORAGE.data, item_id)
    if item:
        kbd = xbmc.Keyboard(item['name'], 'Nuevo nombre')
        kbd.doModal()
        if kbd.isConfirmed():
            new_name = kbd.getText()
            if new_name and STORAGE.rename_item(item_id, new_name):
                xbmc.executebuiltin('Container.Refresh')
            else:
                xbmcgui.Dialog().notification('Error', 'No se pudo renombrar', xbmcgui.NOTIFICATION_ERROR)

def delete_item(item_id):
    item = STORAGE._find_node(STORAGE.data, item_id)
    if item:
        if xbmcgui.Dialog().yesno('Confirmar eliminación', f"¿Eliminar '{item['name']}'?"):
            if STORAGE.delete_item(item_id):
                xbmc.executebuiltin('Container.Refresh')
            else:
                xbmcgui.Dialog().notification('Error', 'No se pudo eliminar', xbmcgui.NOTIFICATION_ERROR)

def move_item(item_id):
    # Get current parent folder
    current_parent = STORAGE._find_parent(STORAGE.data, item_id)
    current_parent_id = current_parent['id'] if current_parent else None
    
    # Get all folders
    folders = STORAGE.get_all_folders_flat()
    folder_names = []
    folder_ids = []
    
    for fid, name, depth in folders:
        indent = '  ' * depth
        # Mark current folder
        if fid == current_parent_id:
            folder_names.append(f"{indent}[COLOR lime]✓ {name} [ACTUAL][/COLOR]")
        else:
            folder_names.append(f"{indent}{name}")
        folder_ids.append(fid)
    
    # Show selection dialog
    selected = xbmcgui.Dialog().select('Mover a carpeta:', folder_names)
    if selected >= 0:
        target_folder_id = folder_ids[selected]
        # Don't move if it's the same folder
        if target_folder_id == current_parent_id:
            xbmcgui.Dialog().notification('Info', 'Ya está en esa carpeta', xbmcgui.NOTIFICATION_INFO)
            return
        
        if STORAGE.move_item(item_id, target_folder_id):
            xbmc.executebuiltin('Container.Refresh')
            xbmcgui.Dialog().notification('Éxito', 'Favorito movido', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().notification('Error', 'No se pudo mover', xbmcgui.NOTIFICATION_ERROR)

def edit_item(item_id):
    item = STORAGE._find_node(STORAGE.data, item_id)
    if not item:
        return
    
    # Name
    kbd = xbmc.Keyboard(item['name'], 'Nombre')
    kbd.doModal()
    if not kbd.isConfirmed(): return
    name = kbd.getText()
    
    # URL
    kbd = xbmc.Keyboard(item.get('url', ''), 'URL')
    kbd.doModal()
    if not kbd.isConfirmed(): return
    url = kbd.getText()
    
    # Thumbnail (optional)
    kbd = xbmc.Keyboard(item.get('thumbnail', ''), 'Thumbnail (opcional)')
    kbd.doModal()
    thumbnail = kbd.getText() if kbd.isConfirmed() else item.get('thumbnail', '')
    
    if STORAGE.update_item(item_id, name, url, thumbnail):
        xbmc.executebuiltin('Container.Refresh')
    else:
        xbmcgui.Dialog().notification('Error', 'No se pudo actualizar', xbmcgui.NOTIFICATION_ERROR)

def import_from_kodi(folder_id):
    # Get Kodi favorites
    kodi_favs = IMPORTER.get_kodi_favorites()
    
    if not kodi_favs:
        xbmcgui.Dialog().ok('Sin favoritos', 'No se encontraron favoritos en Kodi.\n\nPuedes añadir favoritos desde el menú contextual de cualquier elemento en Kodi.')
        return
    
    # Show selection dialog
    fav_names = [f['name'] for f in kodi_favs]
    selected_indices = xbmcgui.Dialog().multiselect('Selecciona favoritos a importar:', fav_names)
    
    if selected_indices:
        selected_favs = [kodi_favs[i] for i in selected_indices]
        count = IMPORTER.import_to_folder(STORAGE, folder_id, selected_favs)
        xbmc.executebuiltin('Container.Refresh')
        xbmcgui.Dialog().notification('Importación completa', f'{count} favoritos importados', xbmcgui.NOTIFICATION_INFO)

def multi_move_items(current_folder_id):
    """Select multiple items and move them to a folder."""
    # Get items in current folder
    items = STORAGE.get_folder_contents(current_folder_id)
    
    # Filter only items (not folders)
    movable_items = [item for item in items if item['type'] == 'item']
    
    if not movable_items:
        xbmcgui.Dialog().ok('Sin elementos', 'No hay favoritos para mover en esta carpeta.')
        return
    
    # Show multi-select dialog
    item_names = [item['name'] for item in movable_items]
    selected_indices = xbmcgui.Dialog().multiselect('Selecciona favoritos a mover:', item_names)
    
    if not selected_indices:
        return
    
    # Get all folders for destination
    folders = STORAGE.get_all_folders_flat()
    folder_names = []
    folder_ids = []
    
    for fid, name, depth in folders:
        indent = '  ' * depth
        # Mark current folder
        if fid == current_folder_id:
            folder_names.append(f"{indent}[COLOR lime]✓ {name} [ACTUAL][/COLOR]")
        else:
            folder_names.append(f"{indent}{name}")
        folder_ids.append(fid)
    
    # Show destination folder selection
    selected_folder = xbmcgui.Dialog().select('Mover a carpeta:', folder_names)
    if selected_folder >= 0:
        target_folder_id = folder_ids[selected_folder]
        
        # Don't move if it's the same folder
        if target_folder_id == current_folder_id:
            xbmcgui.Dialog().notification('Info', 'Ya están en esa carpeta', xbmcgui.NOTIFICATION_INFO)
            return
        
        # Move all selected items
        moved_count = 0
        for idx in selected_indices:
            item_id = movable_items[idx]['id']
            if STORAGE.move_item(item_id, target_folder_id):
                moved_count += 1
        
        xbmc.executebuiltin('Container.Refresh')
        xbmcgui.Dialog().notification('Éxito', f'{moved_count} favoritos movidos', xbmcgui.NOTIFICATION_INFO)

def build_url(query):
    return BASE_URL + '?' + urllib.parse.urlencode(query)

if __name__ == '__main__':
    main()
