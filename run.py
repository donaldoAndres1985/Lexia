"""
Script de inicio para Lee y Juega.
Permite ejecutar la aplicación directamente desde la raíz del proyecto.
"""
import sys
from pathlib import Path

# Agregar la ruta raíz al path de Python
ruta_raiz = Path(__file__).resolve().parent
if str(ruta_raiz) not in sys.path:
    sys.path.insert(0, str(ruta_raiz))

from lee_y_juega.app.main import main

if __name__ == "__main__":
    sys.exit(main())
