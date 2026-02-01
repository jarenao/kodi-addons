import xml.etree.ElementTree as ET
import xbmcvfs
import xbmc

class KodiFavoritesImporter:
    """Import favorites from Kodi's native favourites.xml file."""
    
    def __init__(self):
        self.favourites_path = xbmcvfs.translatePath('special://profile/favourites.xml')
    
    def get_kodi_favorites(self):
        """
        Read and parse Kodi's favourites.xml file.
        Returns a list of dicts: [{'name': str, 'url': str, 'thumbnail': str}, ...]
        """
        favorites = []
        
        if not xbmcvfs.exists(self.favourites_path):
            xbmc.log("[MisFavoritos] No favourites.xml found", level=xbmc.LOGINFO)
            return favorites
        
        try:
            # Read the file
            file_handle = xbmcvfs.File(self.favourites_path)
            content = file_handle.read()
            file_handle.close()
            
            # Parse XML
            root = ET.fromstring(content)
            
            for fav in root.findall('favourite'):
                name = fav.get('name', 'Sin nombre')
                thumb = fav.get('thumb', '')
                url = fav.text if fav.text else ''
                
                if url:  # Only add if there's a valid URL
                    favorites.append({
                        'name': name,
                        'url': url.strip(),
                        'thumbnail': thumb
                    })
            
            xbmc.log(f"[MisFavoritos] Found {len(favorites)} Kodi favorites", level=xbmc.LOGINFO)
            
        except Exception as e:
            xbmc.log(f"[MisFavoritos] Error reading favourites.xml: {str(e)}", level=xbmc.LOGERROR)
        
        return favorites
    
    def import_to_folder(self, storage, folder_id, selected_favorites):
        """
        Import selected favorites into a specific folder.
        
        Args:
            storage: JSONStorage instance
            folder_id: Target folder ID
            selected_favorites: List of favorite dicts to import
        
        Returns:
            Number of successfully imported favorites
        """
        count = 0
        for fav in selected_favorites:
            if storage.add_item(folder_id, fav['name'], fav['url'], fav['thumbnail']):
                count += 1
        return count
