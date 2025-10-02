"""
Ventana principal de la aplicación RollForge
"""

from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                              QPushButton, QLabel, QMenuBar, QMenu, QMessageBox,
                              QFileDialog, QStatusBar, QToolBar, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QFont, QIcon, QKeySequence, QPainter, QColor, QPalette, QBrush, QPixmap

from gui.character_grid import CharacterGrid
from gui.character_form import CharacterForm
from models.character import Character
from utils.data_manager import DataManager
from utils.image_utils import get_default_character_icon
from utils.theme import get_main_window_style

import os
import sys
import tempfile


class TransparentWidget(QWidget):
    """Widget con fondo semi-transparente usando StyleSheet inline con !important"""
    def __init__(self, r=0, g=0, b=0, alpha=153, parent=None):
        super().__init__(parent)
        self.r, self.g, self.b, self.alpha = r, g, b, alpha
        # Guardar para aplicar después
        
    def apply_transparent_style(self):
        """Aplicar estilo después de que se haya aplicado el tema global"""
        self.setStyleSheet(f"""
            QWidget#gridContainer {{
                background-color: rgba({self.r}, {self.g}, {self.b}, {self.alpha});
                border-radius: 8px;
            }}
        """)


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación RollForge
    Integra todos los componentes y maneja la lógica principal
    """
    
    def __init__(self):
        super().__init__()
        
        # Variables de estado
        self.characters = []
        self.current_character_form = None
        
        # Cache para la imagen de fondo
        self._background_pixmap = None
        
        # Inicializar gestor de datos con manejo de errores
        try:
            self.data_manager = DataManager()
        except Exception as e:
            # Si falla, mostrar error y usar un directorio temporal como fallback
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), "RollForge", "data")
            QMessageBox.warning(
                None,
                "Advertencia",
                f"No se pudo crear el directorio de datos en la ubicación predeterminada.\n\n"
                f"Error: {str(e)}\n\n"
                f"Se usará un directorio temporal: {temp_dir}"
            )
            try:
                self.data_manager = DataManager(temp_dir)
            except Exception as e2:
                QMessageBox.critical(
                    None,
                    "Error Fatal",
                    f"No se pudo inicializar el gestor de datos.\n\n"
                    f"Error: {str(e2)}\n\n"
                    f"La aplicación no puede continuar."
                )
                sys.exit(1)
        
        self._setup_ui()
        self._create_menus()
        self._create_status_bar()
        self._connect_signals()
        
        # Aplicar tema oscuro plano PRIMERO
        self.setStyleSheet(get_main_window_style())
        
        # DESPUÉS aplicar estilos de transparencia que necesitan sobrescribir el tema
        if hasattr(self, 'grid_container'):
            self.grid_container.apply_transparent_style()
        
        # Cargar personajes guardados
        self._load_characters()
        
        # Timer para guardar automáticamente
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(30000)  # Auto-guardar cada 30 segundos
    
    def _setup_ui(self):
        """Configurar la interfaz de usuario principal"""
        self.setWindowTitle("RollForge - Gestor de Personajes")
        
        # Usar el logo del dragón como ícono de la ventana
        dragon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "dragon.png")
        if os.path.exists(dragon_path):
            # Cargar el ícono y agregar múltiples tamaños para mejor calidad
            icon = QIcon()
            pixmap = QPixmap(dragon_path)
            # Agregar versiones en diferentes tamaños (16x16, 32x32, 48x48, 64x64, 128x128)
            for size in [16, 32, 48, 64, 128]:
                scaled = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
                icon.addPixmap(scaled)
            self.setWindowIcon(icon)
        else:
            self.setWindowIcon(get_default_character_icon())
        
        self.setMinimumSize(1000, 700)
        self.resize(1600, 900)  # Resolución por defecto: 1600x900
        
        # Widget central con fondo de campfire
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Configurar imagen de fondo escalada
        campfire_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "campfire.png")
        if os.path.exists(campfire_path):
            # Cargar imagen ORIGINAL una sola vez y guardar en cache
            self._background_pixmap = QPixmap(campfire_path)
            
            # Escalar para el tamaño inicial
            scaled_pixmap = self._background_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            
            # Configurar como fondo usando palette
            palette = central_widget.palette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_pixmap))
            central_widget.setPalette(palette)
            central_widget.setAutoFillBackground(True)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === ENCABEZADO ===
        header_widget = self._create_header()
        main_layout.addWidget(header_widget)
        
        # === SEPARADOR ===
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #3a3a3a;")
        main_layout.addWidget(separator)
        
        # === CONTENEDOR DEL GRID CON PADDING ===
        # Usar TransparentWidget con 60% de opacidad (alpha=153 de 255)
        self.grid_container = TransparentWidget(r=0, g=0, b=0, alpha=153)
        self.grid_container.setObjectName("gridContainer")
        
        grid_layout = QVBoxLayout(self.grid_container)
        grid_layout.setContentsMargins(40, 30, 40, 30)  # Más padding para que el fondo sea visible
        
        # === GRID DE PERSONAJES ===
        self.character_grid = CharacterGrid()
        grid_layout.addWidget(self.character_grid)
        
        main_layout.addWidget(self.grid_container)
    
    def _create_header(self) -> QWidget:
        """Crear el encabezado con título y botones principales"""
        header_widget = QWidget()
        header_widget.setObjectName("headerWidget")
        header_widget.setMaximumHeight(80)  # Limitar altura máxima del header
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(15)
        
        # === LOGO DEL DRAGÓN ===
        logo_label = QLabel()
        logo_label.setObjectName("logoLabel")
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "dragon.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        logo_label.setFixedSize(48, 48)
        
        # === TÍTULO ===
        title_label = QLabel("RollForge")
        title_label.setObjectName("titleLabel")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # === CONTADOR DE PERSONAJES ===
        self.character_count_label = QLabel("0 personajes")
        self.character_count_label.setObjectName("countLabel")
        count_font = QFont()
        count_font.setPointSize(12)
        self.character_count_label.setFont(count_font)
        
        # === BOTONES PRINCIPALES ===
        # Botón Importar
        self.import_btn = QPushButton("Importar")
        self.import_btn.setObjectName("headerButton")
        self.import_btn.clicked.connect(self._import_characters)
        self.import_btn.setFixedHeight(36)
        self.import_btn.setFixedWidth(100)
        
        # Botón Exportar
        self.export_btn = QPushButton("Exportar")
        self.export_btn.setObjectName("headerButton")
        self.export_btn.clicked.connect(self._export_characters)
        self.export_btn.setFixedHeight(36)
        self.export_btn.setFixedWidth(100)
        
        # Botón Nuevo Personaje
        self.new_character_btn = QPushButton("Nuevo Personaje")
        self.new_character_btn.setObjectName("headerButton")
        self.new_character_btn.clicked.connect(self._show_new_character_form)
        self.new_character_btn.setFixedHeight(36)
        self.new_character_btn.setFixedWidth(150)
        
        # Botón Recargar
        self.reload_btn = QPushButton("Recargar")
        self.reload_btn.setObjectName("headerButton")
        self.reload_btn.clicked.connect(self._load_characters)
        self.reload_btn.setFixedHeight(36)
        self.reload_btn.setFixedWidth(100)
        
        # Ensamblar header
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addWidget(self.character_count_label)
        header_layout.addStretch()
        header_layout.addWidget(self.import_btn)
        header_layout.addWidget(self.export_btn)
        header_layout.addWidget(self.new_character_btn)
        header_layout.addWidget(self.reload_btn)
        
        return header_widget
    
    def _create_menus(self):
        """Crear la barra de menús"""
        menubar = self.menuBar()
        
        # === MENÚ ARCHIVO ===
        file_menu = menubar.addMenu("&Archivo")
        
        # Nuevo Personaje
        new_action = QAction("&Nuevo Personaje", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Crear un nuevo personaje")
        new_action.triggered.connect(self._show_new_character_form)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # Exportar
        export_action = QAction("&Exportar Personajes...", self)
        export_action.setStatusTip("Exportar todos los personajes a un archivo")
        export_action.triggered.connect(self._export_characters)
        file_menu.addAction(export_action)
        
        # Importar
        import_action = QAction("&Importar Personajes...", self)
        import_action.setStatusTip("Importar personajes desde un archivo")
        import_action.triggered.connect(self._import_characters)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Salir
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Salir de la aplicación")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # === MENÚ EDICIÓN ===
        edit_menu = menubar.addMenu("&Edición")
        
        # Recargar
        reload_action = QAction("&Recargar", self)
        reload_action.setShortcut(QKeySequence.StandardKey.Refresh)
        reload_action.setStatusTip("Recargar todos los personajes")
        reload_action.triggered.connect(self._load_characters)
        edit_menu.addAction(reload_action)
        
        # Limpiar Todo
        clear_action = QAction("&Limpiar Todo", self)
        clear_action.setStatusTip("Eliminar todos los personajes (con confirmación)")
        clear_action.triggered.connect(self._clear_all_characters)
        edit_menu.addAction(clear_action)
        
        # === MENÚ AYUDA ===
        help_menu = menubar.addMenu("A&yuda")
        
        # Acerca de
        about_action = QAction("&Acerca de", self)
        about_action.setStatusTip("Información sobre la aplicación")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Crear barra de estado"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Mensaje por defecto
        self.status_bar.showMessage("Listo - RollForge cargado correctamente")
    
    def _connect_signals(self):
        """Conectar señales de los widgets"""
        # Conectar señales del grid
        self.character_grid.edit_character_requested.connect(self._edit_character)
        self.character_grid.delete_character_requested.connect(self._delete_character)
    
    def _load_characters(self):
        """Cargar todos los personajes desde el almacenamiento"""
        try:
            self.characters = self.data_manager.load_all_characters()
            self.character_grid.set_characters(self.characters)
            self._update_character_count()
            
            count = len(self.characters)
            self.status_bar.showMessage(f"Cargados {count} personajes correctamente")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error de Carga", 
                f"Error cargando personajes: {str(e)}"
            )
            self.status_bar.showMessage("Error cargando personajes")
    
    def _show_new_character_form(self):
        """Mostrar formulario para crear nuevo personaje"""
        if self.current_character_form:
            self.current_character_form.close()
        
        self.current_character_form = CharacterForm(self)
        self.current_character_form.character_saved.connect(self._on_character_saved)
        self.current_character_form.show()
    
    def _edit_character(self, character_id: str):
        """Mostrar formulario para editar personaje existente"""
        # Buscar el personaje
        character = self._find_character_by_id(character_id)
        if not character:
            QMessageBox.warning(self, "Error", "Personaje no encontrado")
            return
        
        if self.current_character_form:
            self.current_character_form.close()
        
        self.current_character_form = CharacterForm(self, character)
        self.current_character_form.character_saved.connect(self._on_character_saved)
        self.current_character_form.show()
    
    def _delete_character(self, character_id: str):
        """Eliminar un personaje con confirmación"""
        # Buscar el personaje
        character = self._find_character_by_id(character_id)
        if not character:
            QMessageBox.warning(self, "Error", "Personaje no encontrado")
            return
        
        # Confirmación
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Estás seguro de que quieres eliminar el personaje '{character.name}'?\n\n"
            f"Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Eliminar del almacenamiento
                if self.data_manager.delete_character(character_id):
                    # Remover del grid
                    self.character_grid.remove_character(character_id)
                    
                    # Actualizar lista local
                    self.characters = [c for c in self.characters if c.id != character_id]
                    self._update_character_count()
                    
                    self.status_bar.showMessage(f"Personaje '{character.name}' eliminado correctamente")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar el personaje")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error eliminando personaje: {str(e)}")
    
    def _on_character_saved(self, character: Character):
        """Manejar guardado de personaje (nuevo o editado)"""
        try:
            # Guardar imagen si es necesaria
            if character.image_path and not character.image_path.startswith(str(self.data_manager.images_dir)):
                new_image_path = self.data_manager.save_character_image(
                    character.image_path, 
                    character.id
                )
                if new_image_path:
                    character.image_path = new_image_path
            
            # Guardar personaje
            if self.data_manager.save_character(character):
                # Actualizar grid
                self.character_grid.add_character(character)
                
                # Actualizar lista local
                existing_index = self._find_character_index(character.id)
                if existing_index >= 0:
                    self.characters[existing_index] = character
                    action = "actualizado"
                else:
                    self.characters.append(character)
                    action = "creado"
                
                self._update_character_count()
                self.status_bar.showMessage(f"Personaje '{character.name}' {action} correctamente")
            else:
                QMessageBox.warning(self, "Error", "No se pudo guardar el personaje")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando personaje: {str(e)}")
    
    def _export_characters(self):
        """Exportar personajes a un archivo JSON"""
        if not self.characters:
            QMessageBox.information(self, "Información", "No hay personajes para exportar")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Personajes",
            "personajes_dnd.json",
            "Archivos JSON (*.json);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                if self.data_manager.export_characters(file_path):
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        f"Personajes exportados correctamente a:\\n{file_path}"
                    )
                    self.status_bar.showMessage(f"Personajes exportados a {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Error", "No se pudieron exportar los personajes")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exportando: {str(e)}")
    
    def _import_characters(self):
        """Importar personajes desde un archivo JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Personajes",
            "",
            "Archivos JSON (*.json);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                if self.data_manager.import_characters(file_path):
                    # Recargar personajes
                    self._load_characters()
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        f"Personajes importados correctamente desde:\\n{file_path}"
                    )
                    self.status_bar.showMessage(f"Personajes importados desde {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Error", "No se pudieron importar los personajes")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error importando: {str(e)}")
    
    def _clear_all_characters(self):
        """Eliminar todos los personajes con confirmación"""
        if not self.characters:
            QMessageBox.information(self, "Información", "No hay personajes para eliminar")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación Masiva",
            f"¿Estás seguro de que quieres eliminar TODOS los {len(self.characters)} personajes?\\n\\n"
            f"Esta acción NO se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Eliminar todos los personajes
                for character in self.characters[:]:  # Copia para iterar
                    self.data_manager.delete_character(character.id)
                
                # Limpiar grid y lista
                self.character_grid.clear_all()
                self.characters.clear()
                self._update_character_count()
                
                self.status_bar.showMessage("Todos los personajes han sido eliminados")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error eliminando personajes: {str(e)}")
    
    def _show_about(self):
        """Mostrar información sobre la aplicación"""
        QMessageBox.about(
            self,
            "Acerca de RollForge",
            """
            <h2>RollForge - Gestor de Personajes</h2>
            <p><b>Versión:</b> 1.0.0</p>
            <p><b>Descripción:</b> Aplicación para gestionar personajes de juegos de rol</p>
            
            <h3>Características:</h3>
            <ul>
                <li>Cálculo automático de modificadores D&D</li>
                <li>Gestión de imágenes de personajes</li>
                <li>Interfaz responsive y moderna</li>
                <li>Guardado automático y persistencia de datos</li>
                <li>Exportar/Importar personajes</li>
            </ul>
            
            <p><b>Tecnologías:</b> Python 3, PySide6, Pillow</p>
            <p><b>Autor:</b> RollForge Team</p>
            """
        )
    
    def _update_character_count(self):
        """Actualizar el contador de personajes"""
        count = len(self.characters)
        text = f"{count} personaje" + ("s" if count != 1 else "")
        self.character_count_label.setText(text)
    
    def _find_character_by_id(self, character_id: str) -> Character:
        """Buscar un personaje por ID"""
        for character in self.characters:
            if character.id == character_id:
                return character
        return None
    
    def _find_character_index(self, character_id: str) -> int:
        """Buscar el índice de un personaje por ID"""
        for i, character in enumerate(self.characters):
            if character.id == character_id:
                return i
        return -1
    
    def _auto_save(self):
        """Guardar automáticamente (por si acaso)"""
        # El auto-guardado ya se maneja en el DataManager
        # Este es más para futuras funcionalidades
        pass
    
    def resizeEvent(self, event):
        """Manejar redimensionamiento de la ventana para ajustar el fondo"""
        super().resizeEvent(event)
        
        # Reescalar la imagen de fondo desde el cache
        if self._background_pixmap:
            central_widget = self.centralWidget()
            if central_widget:
                # Usar la imagen cacheada en lugar de recargarla del disco
                scaled_pixmap = self._background_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                
                palette = central_widget.palette()
                palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_pixmap))
                central_widget.setPalette(palette)
    
    def closeEvent(self, event):
        """Manejar cierre de la aplicación"""
        if self.current_character_form:
            self.current_character_form.close()
        
        self.status_bar.showMessage("Cerrando aplicación...")
        event.accept()