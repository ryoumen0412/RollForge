#!/usr/bin/env python3
"""
RollForge - Character Management Application
Aplicación de escritorio para gestión de personajes de juegos de rol
Author: RollForge Team
"""

import sys
import os

# Añadir el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dnd_dm_app'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from gui.main_window import MainWindow


def main():
    """Función principal de la aplicación"""
    # Configurar variables de entorno para DPI alto ANTES de Qt
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    # Establecer atributos de DPI ANTES de crear QApplication
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # En Windows, establecer el AppUserModelID para que use nuestro ícono en la barra de tareas
    if sys.platform == 'win32':
        import ctypes
        myappid = 'rollforge.charactermanager.v1.0'  # ID único de la aplicación
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    # Configurar la aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("RollForge")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("RollForge Tools")
    
    # Establecer el ícono de la aplicación (para barra de tareas y ventana)
    dragon_icon_path = os.path.join(os.path.dirname(__file__), "assets", "dragon.png")
    if os.path.exists(dragon_icon_path):
        icon = QIcon()
        pixmap = QPixmap(dragon_icon_path)
        # Agregar múltiples tamaños para mejor calidad en diferentes contextos
        for size in [16, 32, 48, 64, 128, 256]:
            scaled = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, 
                                  Qt.TransformationMode.SmoothTransformation)
            icon.addPixmap(scaled)
        app.setWindowIcon(icon)
    
    # Crear y mostrar la ventana principal
    main_window = MainWindow()
    main_window.show()
    
    # Ejecutar la aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()