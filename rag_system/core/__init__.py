# Ce fichier permet à Python de traiter ce répertoire comme un package
from pathlib import Path
import sys

# Assurer que le répertoire parent est dans le chemin de recherche
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir)) 