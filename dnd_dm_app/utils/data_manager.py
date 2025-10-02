"""
Gestor de datos para persistencia de personajes en JSON
Maneja carga, guardado y gestión de archivos de personajes
"""

import json
import os
import shutil
from typing import Dict, List, Optional
from pathlib import Path
import logging

from models.character import Character


class DataManager:
    """
    Clase responsable de la persistencia de datos de personajes
    Utiliza archivos JSON para almacenar la información
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Inicializar el gestor de datos
        
        Args:
            data_dir: Directorio donde se almacenan los datos. Si es None, usa el directorio del usuario.
        """
        # Configurar logging PRIMERO
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Si no se especifica directorio, usar el directorio de datos del usuario
        if data_dir is None:
            # En Windows: C:\Users\USERNAME\AppData\Local\RollForge\data
            # En Linux/Mac: ~/.local/share/RollForge/data
            if os.name == 'nt':  # Windows
                app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
                self.data_dir = Path(app_data) / "RollForge" / "data"
            else:  # Linux/Mac
                self.data_dir = Path.home() / ".local" / "share" / "RollForge" / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.characters_file = self.data_dir / "characters.json"
        self.images_dir = self.data_dir / "character_images"
        
        self.logger.info(f"Directorio de datos: {self.data_dir}")
        
        # Crear directorios si no existen (ahora que logger está disponible)
        self._setup_directories()
    
    def _setup_directories(self):
        """Crear directorios necesarios si no existen"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.images_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Directorios creados/verificados: {self.data_dir}")
            
            # Crear archivo de personajes si no existe
            if not self.characters_file.exists():
                self._save_characters_file({})
                self.logger.info(f"Archivo de personajes creado: {self.characters_file}")
                
        except PermissionError as e:
            error_msg = (
                f"Error: No hay permisos para crear directorios en '{self.data_dir}'.\n"
                f"Detalles: {e}\n"
                f"La aplicación necesita permisos de escritura en esta ubicación."
            )
            self.logger.error(error_msg)
            raise PermissionError(error_msg) from e
        except OSError as e:
            error_msg = f"Error creando directorios en '{self.data_dir}': {e}"
            self.logger.error(error_msg)
            raise OSError(error_msg) from e
    
    def _save_characters_file(self, characters_data: Dict):
        """
        Guardar el archivo principal de personajes
        
        Args:
            characters_data: Diccionario con todos los personajes
        """
        try:
            with open(self.characters_file, 'w', encoding='utf-8') as f:
                json.dump(characters_data, f, indent=2, ensure_ascii=False)
        except (IOError, json.JSONEncodeError) as e:
            self.logger.error(f"Error guardando archivo de personajes: {e}")
            raise
    
    def _load_characters_file(self) -> Dict:
        """
        Cargar el archivo principal de personajes
        
        Returns:
            Diccionario con todos los personajes
        """
        try:
            if not self.characters_file.exists():
                return {}
            
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(f"Error cargando archivo de personajes: {e}")
            # Crear backup del archivo corrupto
            if self.characters_file.exists():
                backup_path = self.characters_file.with_suffix('.json.backup')
                shutil.copy2(self.characters_file, backup_path)
                self.logger.info(f"Backup creado en: {backup_path}")
            return {}
    
    def save_character(self, character: Character) -> bool:
        """
        Guardar un personaje individual
        
        Args:
            character: Instancia del personaje a guardar
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            characters_data = self._load_characters_file()
            characters_data[character.id] = character.to_dict()
            self._save_characters_file(characters_data)
            
            self.logger.info(f"Personaje guardado: {character.name} (ID: {character.id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando personaje {character.name}: {e}")
            return False
    
    def load_character(self, character_id: str) -> Optional[Character]:
        """
        Cargar un personaje específico por ID
        
        Args:
            character_id: ID único del personaje
            
        Returns:
            Instancia del personaje o None si no se encuentra
        """
        try:
            characters_data = self._load_characters_file()
            
            if character_id not in characters_data:
                return None
            
            character_dict = characters_data[character_id]
            return Character.from_dict(character_dict)
            
        except Exception as e:
            self.logger.error(f"Error cargando personaje {character_id}: {e}")
            return None
    
    def load_all_characters(self) -> List[Character]:
        """
        Cargar todos los personajes guardados
        
        Returns:
            Lista de todos los personajes
        """
        try:
            characters_data = self._load_characters_file()
            characters = []
            
            for character_dict in characters_data.values():
                try:
                    character = Character.from_dict(character_dict)
                    characters.append(character)
                except Exception as e:
                    self.logger.warning(f"Error cargando personaje individual: {e}")
                    continue
            
            self.logger.info(f"Cargados {len(characters)} personajes")
            return characters
            
        except Exception as e:
            self.logger.error(f"Error cargando personajes: {e}")
            return []
    
    def delete_character(self, character_id: str) -> bool:
        """
        Eliminar un personaje por ID
        
        Args:
            character_id: ID único del personaje a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            characters_data = self._load_characters_file()
            
            if character_id not in characters_data:
                self.logger.warning(f"Personaje no encontrado para eliminar: {character_id}")
                return False
            
            # Eliminar imagen asociada si existe
            character_dict = characters_data[character_id]
            if character_dict.get('image_path'):
                self._delete_character_image(character_dict['image_path'])
            
            # Eliminar del archivo de datos
            del characters_data[character_id]
            self._save_characters_file(characters_data)
            
            self.logger.info(f"Personaje eliminado: {character_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error eliminando personaje {character_id}: {e}")
            return False
    
    def save_character_image(self, image_path: str, character_id: str) -> Optional[str]:
        """
        Copiar y guardar la imagen de un personaje en el directorio de datos
        
        Args:
            image_path: Ruta original de la imagen
            character_id: ID del personaje
            
        Returns:
            Nueva ruta de la imagen o None si hay error
        """
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"Archivo de imagen no encontrado: {image_path}")
                return None
            
            # Obtener extensión del archivo
            file_extension = Path(image_path).suffix.lower()
            if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                self.logger.error(f"Formato de imagen no soportado: {file_extension}")
                return None
            
            # Crear nombre único para la imagen
            new_filename = f"{character_id}{file_extension}"
            new_path = self.images_dir / new_filename
            
            # Copiar archivo
            shutil.copy2(image_path, new_path)
            
            self.logger.info(f"Imagen guardada: {new_path}")
            return str(new_path)
            
        except Exception as e:
            self.logger.error(f"Error guardando imagen: {e}")
            return None
    
    def _delete_character_image(self, image_path: str):
        """
        Eliminar imagen de personaje
        
        Args:
            image_path: Ruta de la imagen a eliminar
        """
        try:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
                self.logger.info(f"Imagen eliminada: {image_path}")
        except Exception as e:
            self.logger.warning(f"Error eliminando imagen {image_path}: {e}")
    
    def get_characters_count(self) -> int:
        """
        Obtener el número total de personajes guardados
        
        Returns:
            Número de personajes
        """
        try:
            characters_data = self._load_characters_file()
            return len(characters_data)
        except Exception:
            return 0
    
    def export_characters(self, export_path: str) -> bool:
        """
        Exportar todos los personajes a un archivo JSON
        
        Args:
            export_path: Ruta donde guardar la exportación
            
        Returns:
            True si se exportó correctamente
        """
        try:
            characters_data = self._load_characters_file()
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(characters_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Personajes exportados a: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando personajes: {e}")
            return False
    
    def import_characters(self, import_path: str) -> bool:
        """
        Importar personajes desde un archivo JSON
        
        Args:
            import_path: Ruta del archivo a importar
            
        Returns:
            True si se importó correctamente
        """
        try:
            if not os.path.exists(import_path):
                self.logger.error(f"Archivo de importación no encontrado: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # Validar estructura de datos
            if not isinstance(imported_data, dict):
                self.logger.error("El archivo de importación no tiene el formato correcto")
                return False
            
            # Cargar datos existentes
            existing_data = self._load_characters_file()
            
            # Fusionar datos (los importados tienen prioridad)
            existing_data.update(imported_data)
            
            # Guardar datos fusionados
            self._save_characters_file(existing_data)
            
            self.logger.info(f"Personajes importados desde: {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importando personajes: {e}")
            return False