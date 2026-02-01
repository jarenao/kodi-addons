import json
import os
import uuid
import xbmc
import xbmcvfs

DATA_PATH = xbmcvfs.translatePath('special://profile/addon_data/plugin.video.mis.favoritos')
FILE_PATH = os.path.join(DATA_PATH, 'favorites.json')

class JSONStorage:
    def __init__(self):
        self.data = self._load()

    def _load(self):
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)
        
        if not os.path.exists(FILE_PATH):
            # Init empty structure
            return {
                "id": "root",
                "name": "Root",
                "type": "folder",
                "children": []
            }
        
        try:
            with open(FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"id": "root", "name": "Root", "type": "folder", "children": []}

    def save(self):
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_folder_contents(self, folder_id):
        """
        Returns the children list of a folder.
        Uses recursive search.
        """
        node = self._find_node(self.data, folder_id)
        if node and node.get('type') == 'folder':
            return node.get('children', [])
        return []

    def get_all_folders_flat(self):
        """
        Returns a flat list of all folders: [(id, name, depth)]
        """
        folders = []
        self._collect_folders(self.data, folders, 0)
        return folders

    def _collect_folders(self, node, result_list, depth):
        if node.get('type') == 'folder':
            result_list.append((node['id'], node['name'], depth))
            for child in node.get('children', []):
                self._collect_folders(child, result_list, depth + 1)

    def add_folder(self, parent_id, name):
        parent = self._find_node(self.data, parent_id)
        if parent:
            new_folder = {
                "id": str(uuid.uuid4()),
                "name": name,
                "type": "folder",
                "children": []
            }
            parent['children'].append(new_folder)
            self.save()
            return True
        return False

    def add_item(self, parent_id, name, url, thumbnail):
        parent = self._find_node(self.data, parent_id)
        if parent:
            new_item = {
                "id": str(uuid.uuid4()),
                "name": name,
                "type": "item",
                "url": url,
                "thumbnail": thumbnail
            }
            parent['children'].append(new_item)
            self.save()
            return True
        return False

    def _find_node(self, current_node, target_id):
        if current_node['id'] == target_id:
            return current_node
        
        if 'children' in current_node:
            for child in current_node['children']:
                found = self._find_node(child, target_id)
                if found:
                    return found
        return None

    def rename_folder(self, folder_id, new_name):
        """Rename a folder."""
        folder = self._find_node(self.data, folder_id)
        if folder and folder.get('type') == 'folder':
            folder['name'] = new_name
            self.save()
            return True
        return False

    def delete_folder(self, folder_id):
        """Delete a folder (must be empty or user confirms)."""
        if folder_id == 'root':
            return False  # Cannot delete root
        
        parent = self._find_parent(self.data, folder_id)
        if parent:
            parent['children'] = [c for c in parent['children'] if c['id'] != folder_id]
            self.save()
            return True
        return False

    def rename_item(self, item_id, new_name):
        """Rename an item."""
        item = self._find_node(self.data, item_id)
        if item and item.get('type') == 'item':
            item['name'] = new_name
            self.save()
            return True
        return False

    def delete_item(self, item_id):
        """Delete an item."""
        parent = self._find_parent(self.data, item_id)
        if parent:
            parent['children'] = [c for c in parent['children'] if c['id'] != item_id]
            self.save()
            return True
        return False

    def move_item(self, item_id, new_parent_id):
        """Move an item to a different folder."""
        # Find the item and its current parent
        old_parent = self._find_parent(self.data, item_id)
        if not old_parent:
            return False
        
        # Find the item itself
        item = None
        for child in old_parent['children']:
            if child['id'] == item_id:
                item = child
                break
        
        if not item:
            return False
        
        # Find new parent
        new_parent = self._find_node(self.data, new_parent_id)
        if not new_parent or new_parent.get('type') != 'folder':
            return False
        
        # Move the item
        old_parent['children'].remove(item)
        new_parent['children'].append(item)
        self.save()
        return True

    def _find_parent(self, current_node, target_id):
        """Find the parent node of a given node ID."""
        if 'children' in current_node:
            for child in current_node['children']:
                if child['id'] == target_id:
                    return current_node
                found = self._find_parent(child, target_id)
                if found:
                    return found
        return None

    def update_item(self, item_id, name=None, url=None, thumbnail=None):
        """Update item properties."""
        item = self._find_node(self.data, item_id)
        if item and item.get('type') == 'item':
            if name:
                item['name'] = name
            if url:
                item['url'] = url
            if thumbnail is not None:
                item['thumbnail'] = thumbnail
            self.save()
            return True
        return False
