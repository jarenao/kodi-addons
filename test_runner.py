import sys
import mock_kodi # Inyecta los mocks

# Añadir la ruta del plugin al path para poder importarlo
import os
sys.path.append(os.path.join(os.getcwd(), 'plugin.video.mis.favoritos'))

# PATCH: default.py lee sys.argv al importar, así que debemos falsificarlo antes
sys.argv = ['plugin://plugin.video.mis.favoritos/', '1', '?mode=None']

# Importar el plugin
import default
from resources.lib.storage import JSONStorage

def run_test():
    print("=== SIMULACIÓN DE KODI ===")
    
    # 1. Simular inicio (Root)
    print("\n--- Navegando a ROOT ---")
    # Ya seteado arriba, pero lo llamamos explícitamente
    sys.argv = ['plugin://plugin.video.mis.favoritos/', '1', '?mode=None']
    default.main()

    # 2. Simular creación de carpeta
    print("\n--- Intentando crear carpeta 'TestFolder' ---")
    # Mockeamos el input del teclado para que no se detenga
    original_input = builtins.input
    builtins.input = lambda prompt: "TestFolder"
    
    sys.argv = ['plugin://plugin.video.mis.favoritos/', '1', '?mode=add_folder&folder_id=root']
    default.main()
    
    # 3. Listar de nuevo para ver si aparece
    print("\n--- Listando Root de nuevo ---")
    sys.argv = ['plugin://plugin.video.mis.favoritos/', '1', '?mode=folder&folder_id=root']
    default.main()
    
    builtins.input = original_input # Restaurar input

    # 4. Inspeccionar el JSON generado
    print("\n--- Verificando JSON Storage ---")
    storage = JSONStorage()
    folders = storage.get_all_folders_flat()
    print("Carpetas encontradas:", folders)

import builtins
if __name__ == '__main__':
    run_test()
