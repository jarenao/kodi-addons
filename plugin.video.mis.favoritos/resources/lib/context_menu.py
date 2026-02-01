import sys
import xbmc
import xbmcgui
import xbmcaddon

import xbmcaddon

# Fix import path for when running as a context menu item
addon_dir = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path'))
if addon_dir not in sys.path:
    sys.path.append(addon_dir)

from resources.lib.storage import JSONStorage

def get_params():
    # Helper to debug params if needed
    return sys.argv

def main():
    # 1. Capture Item Info
    # For global context menu items, xbmc.getInfoLabel refers to the selected item
    label = xbmc.getInfoLabel('ListItem.Label')
    # FilenameAndPath is usually the best bet for playable items
    path = xbmc.getInfoLabel('ListItem.FilenameAndPath')
    if not path:
        path = xbmc.getInfoLabel('ListItem.Path')
    
    thumb = xbmc.getInfoLabel('ListItem.Art(thumb)')
    icon = xbmc.getInfoLabel('ListItem.Art(icon)')
    art = thumb if thumb else icon
    
    if not path:
        xbmcgui.Dialog().notification('Error', 'No se pudo obtener la ruta del item.', xbmcgui.NOTIFICATION_ERROR)
        return

    # 2. Get Folders
    storage = JSONStorage()
    folders = storage.get_all_folders_flat()
    
    if not folders:
        # Should not happen as Root always exists, but just in case
        xbmcgui.Dialog().notification('Error', 'No hay carpetas disponibles.', xbmcgui.NOTIFICATION_ERROR)
        return

    # 3. Create Selection List
    # folders is list of (id, name, depth)
    display_list = []
    ids = []
    
    for f_id, f_name, depth in folders:
        indent = "  " * depth
        prefix = "- " if depth > 0 else "📂 "
        display_list.append(f"{indent}{prefix}{f_name}")
        ids.append(f_id)

    # 4. Show Dialog
    dialog = xbmcgui.Dialog()
    idx = dialog.select(f"Añadir '{label}' a...", display_list)
    
    if idx >= 0:
        target_folder_id = ids[idx]
        if storage.add_item(target_folder_id, label, path, art):
            xbmcgui.Dialog().notification('Guardado', f'Añadido a {display_list[idx].strip()}', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().notification('Error', 'Error al guardar el favorito', xbmcgui.NOTIFICATION_ERROR)

if __name__ == '__main__':
    main()
