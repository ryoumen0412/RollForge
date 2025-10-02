"""
Utilidades para el manejo de imágenes en la aplicación
"""

import os
from typing import Optional, Tuple
from PIL import Image, ImageQt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
import logging


class ImageUtils:
    """Utilidades para manejo de imágenes"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    DEFAULT_SIZE = (200, 200)
    THUMBNAIL_SIZE = (150, 150)
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def is_valid_image(file_path: str) -> bool:
        """
        Verificar si un archivo es una imagen válida
        
        Args:
            file_path: Ruta del archivo a verificar
            
        Returns:
            True si es una imagen válida
        """
        if not os.path.exists(file_path):
            return False
        
        # Verificar extensión
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ImageUtils.SUPPORTED_FORMATS:
            return False
        
        # Verificar que se puede abrir como imagen
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_pixmap(file_path: str, size: Optional[Tuple[int, int]] = None) -> Optional[QPixmap]:
        """
        Cargar una imagen como QPixmap redimensionado
        
        Args:
            file_path: Ruta de la imagen
            size: Tamaño deseado (ancho, alto) o None para tamaño original
            
        Returns:
            QPixmap o None si hay error
        """
        try:
            if not ImageUtils.is_valid_image(file_path):
                return None
            
            # Cargar y procesar imagen
            with Image.open(file_path) as img:
                # Convertir a RGB si es necesario
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                
                # Redimensionar si se especifica tamaño
                if size:
                    img = ImageUtils._resize_with_aspect_ratio(img, size)
                
                # Convertir a QPixmap
                qt_image = ImageQt.ImageQt(img)
                pixmap = QPixmap.fromImage(qt_image)
                
                return pixmap
                
        except Exception as e:
            logging.error(f"Error cargando imagen {file_path}: {e}")
            return None
    
    @staticmethod
    def _resize_with_aspect_ratio(img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """
        Redimensionar imagen manteniendo proporción
        
        Args:
            img: Imagen PIL
            target_size: Tamaño objetivo (ancho, alto)
            
        Returns:
            Imagen redimensionada
        """
        target_width, target_height = target_size
        img_width, img_height = img.size
        
        # Calcular ratio para mantener proporción
        ratio = min(target_width / img_width, target_height / img_height)
        
        # Nuevas dimensiones
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # Redimensionar
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crear imagen final centrada en el tamaño objetivo
        final_img = Image.new('RGBA', target_size, (0, 0, 0, 0))
        
        # Calcular posición para centrar
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2
        
        final_img.paste(img_resized, (x, y))
        
        return final_img
    
    @staticmethod
    def create_placeholder_pixmap(size: Tuple[int, int], text: str = "Sin Imagen") -> QPixmap:
        """
        Crear un placeholder cuando no hay imagen
        
        Args:
            size: Tamaño del placeholder
            text: Texto a mostrar
            
        Returns:
            QPixmap placeholder
        """
        try:
            # Intentar cargar el placeholder desde assets
            placeholder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "pfp_placeholder.png")
            
            if os.path.exists(placeholder_path):
                # Cargar la imagen placeholder
                img = Image.open(placeholder_path)
                
                # Redimensionar manteniendo proporción
                img = ImageUtils._resize_with_aspect_ratio(img, size)
                
                # Convertir a QPixmap
                qt_image = ImageQt.ImageQt(img)
                pixmap = QPixmap.fromImage(qt_image)
                return pixmap
            
            # Si no existe el archivo, crear placeholder con gradiente
            from PIL import ImageDraw, ImageFont
            
            # Crear imagen placeholder con gradiente
            img = Image.new('RGB', size, color=(45, 52, 72))
            draw = ImageDraw.Draw(img)
            
            # Crear un gradiente simple
            width, height = size
            for i in range(height):
                shade = int(45 + (i / height) * 20)
                color = (shade, shade + 7, shade + 27)
                draw.line([(0, i), (width, i)], fill=color)
            
            # Dibujar borde
            border_color = (74, 77, 90)
            draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=2)
            
            # Intentar agregar texto
            try:
                # Usar fuente por defecto
                font_size = max(10, min(size) // 8)
                
                # Calcular posición del texto
                lines = text.split('\n')
                line_height = font_size + 2
                total_text_height = len(lines) * line_height
                start_y = (height - total_text_height) // 2
                
                for i, line in enumerate(lines):
                    # Calcular ancho del texto aproximado
                    text_width = len(line) * (font_size * 0.6)
                    text_x = (width - text_width) // 2
                    text_y = start_y + (i * line_height)
                    
                    # Dibujar texto con sombra
                    shadow_color = (20, 20, 20)
                    text_color = (200, 200, 210)
                    
                    draw.text((text_x + 1, text_y + 1), line, fill=shadow_color)
                    draw.text((text_x, text_y), line, fill=text_color)
                    
            except Exception:
                # Si falla el texto, continuar sin él
                pass
            
            # Convertir a QPixmap
            qt_image = ImageQt.ImageQt(img)
            pixmap = QPixmap.fromImage(qt_image)
            
            return pixmap
            
        except Exception:
            # Fallback: crear QPixmap básico con patrón
            pixmap = QPixmap(*size)
            pixmap.fill(Qt.GlobalColor.darkGray)
            
            # Dibujar patrón simple
            from PySide6.QtGui import QPainter, QPen
            painter = QPainter(pixmap)
            pen = QPen(Qt.GlobalColor.gray)
            pen.setWidth(1)
            painter.setPen(pen)
            
            # Dibujar líneas diagonales
            for i in range(0, max(size), 20):
                painter.drawLine(i, 0, 0, i)
                painter.drawLine(size[0], i, i, size[1])
            
            painter.end()
            return pixmap
    
    @staticmethod
    def get_image_info(file_path: str) -> Optional[dict]:
        """
        Obtener información de una imagen
        
        Args:
            file_path: Ruta de la imagen
            
        Returns:
            Diccionario con información o None si hay error
        """
        try:
            if not ImageUtils.is_valid_image(file_path):
                return None
            
            with Image.open(file_path) as img:
                info = {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'size_mb': os.path.getsize(file_path) / (1024 * 1024)
                }
                return info
                
        except Exception as e:
            logging.error(f"Error obteniendo info de imagen {file_path}: {e}")
            return None


def get_default_character_icon() -> QIcon:
    """
    Obtener icono por defecto para personajes
    
    Returns:
        QIcon por defecto
    """
    # Crear un icono placeholder simple
    pixmap = ImageUtils.create_placeholder_pixmap((32, 32), "")
    return QIcon(pixmap)