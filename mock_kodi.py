import sys
import logging

# Configure logging to print to console
logging.basicConfig(level=logging.INFO, format='%(message)s')

class MockXBMC:
    LOGINFO = 1
    LOGERROR = 2
    
    @staticmethod
    def log(msg, level=1):
        prefix = "INFO" if level == 1 else "ERROR"
        logging.info(f"[{prefix}] {msg}")
    
    @staticmethod
    def executebuiltin(cmd):
        logging.info(f"[EXEC] {cmd}")

    @staticmethod
    def getInfoLabel(label):
        return "" # Return empty string by default

    class Keyboard:
        def __init__(self, default='', heading=''):
            self.text = default
            self.heading = heading
            self.confirmed = False
        
        def doModal(self):
            # Simulate user input
            val = input(f"[INPUT] {self.heading} (Default: '{self.text}'): ")
            if val:
                self.text = val
            self.confirmed = True
        
        def isConfirmed(self):
            return self.confirmed
        
        def getText(self):
            return self.text

class MockXBMCGUI:
    NOTIFICATION_INFO = 'info'
    NOTIFICATION_ERROR = 'error'

    class ListItem:
        def __init__(self, label=''):
            self.label = label
            self.art = {}
        
        def setArt(self, art_dict):
            self.art.update(art_dict)

    class Dialog:
        def notification(self, heading, message, icon):
            logging.info(f"[NOTIFY] {heading}: {message}")

class MockXBMCPlugin:
    @staticmethod
    def setContent(handle, content):
        logging.info(f"[PLUGIN] Set Content: {content}")
    
    @staticmethod
    def addDirectoryItem(handle, url, listitem, isFolder):
        logging.info(f"[ITEM] {'[FOLDER]' if isFolder else '[FILE]'} {listitem.label} -> {url}")
    
    @staticmethod
    def endOfDirectory(handle):
        logging.info("[PLUGIN] End of Directory")

class MockXBMCAddon:
    class Addon:
        def getSetting(self, id):
            return ""

import builtins

# Inject Mocks into sys.modules
# This allows 'import xbmc' to work in other files
from types import ModuleType

m_xbmc = ModuleType('xbmc')
for attr in dir(MockXBMC):
    if not attr.startswith('__'):
        setattr(m_xbmc, attr, getattr(MockXBMC, attr))
sys.modules['xbmc'] = m_xbmc

m_xbmcgui = ModuleType('xbmcgui')
for attr in dir(MockXBMCGUI):
    if not attr.startswith('__'):
        setattr(m_xbmcgui, attr, getattr(MockXBMCGUI, attr))
sys.modules['xbmcgui'] = m_xbmcgui

m_xbmcplugin = ModuleType('xbmcplugin')
for attr in dir(MockXBMCPlugin):
    if not attr.startswith('__'):
        setattr(m_xbmcplugin, attr, getattr(MockXBMCPlugin, attr))
sys.modules['xbmcplugin'] = m_xbmcplugin

m_xbmcvfs = ModuleType('xbmcvfs')
m_xbmcvfs.translatePath = lambda path: "." # Mock translates special paths to current dir
sys.modules['xbmcvfs'] = m_xbmcvfs

m_xbmcaddon = ModuleType('xbmcaddon')
for attr in dir(MockXBMCAddon):
    if not attr.startswith('__'):
        setattr(m_xbmcaddon, attr, getattr(MockXBMCAddon, attr))
sys.modules['xbmcaddon'] = m_xbmcaddon

print("Mocks inyectados. Listo para simular Kodi.")
