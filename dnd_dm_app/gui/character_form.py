"""
Formulario para agregar y editar personajes de D&D
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLineEdit, QSpinBox, QPushButton, QLabel, QFrame,
                              QFileDialog, QMessageBox, QGridLayout, QGroupBox,
                              QComboBox, QCheckBox, QScrollArea, QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap

from models.character import Character, validate_character_data
from utils.image_utils import ImageUtils
from utils.theme import get_character_form_style
import os


class CharacterForm(QDialog):
    """
    Diálogo para crear y editar personajes de D&D
    Incluye validación de datos y selección de imagen
    """
    
    # Señal emitida cuando se guarda un personaje
    character_saved = Signal(Character)
    
    def __init__(self, parent=None, character: Character = None):
        super().__init__(parent)
        self.character = character  # None para nuevo personaje
        self.selected_image_path = None
        self.image_utils = ImageUtils()
        
        self.setWindowTitle("Editar Personaje" if character else "Nuevo Personaje")
        self.setModal(True)
        self.setMinimumSize(600, 800)
        self.resize(650, 850)
        
        self._setup_ui()
        
        # Aplicar tema del formulario
        self.setStyleSheet(get_character_form_style())
        
        # Si estamos editando, cargar datos
        if self.character:
            self._load_character_data()
    
    def _setup_ui(self):
        """Configurar la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título del formulario
        title = QLabel("Editar Personaje" if self.character else "Crear Nuevo Personaje")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # === SECCIÓN INFORMACIÓN BÁSICA ===
        basic_info_group = self._create_basic_info_section()
        layout.addWidget(basic_info_group)
        
        # === SECCIÓN IMAGEN ===
        image_group = self._create_image_section()
        layout.addWidget(image_group)
        
        # === SECCIÓN STATS ===
        stats_group = self._create_stats_section()
        layout.addWidget(stats_group)
        
        # === SECCIÓN COMPETENCIAS ===
        proficiencies_group = self._create_proficiencies_section()
        layout.addWidget(proficiencies_group)
        
        # === BOTONES ===
        buttons_layout = self._create_buttons_layout()
        layout.addLayout(buttons_layout)
    
    def _create_basic_info_section(self) -> QGroupBox:
        """Crear sección de información básica"""
        group = QGroupBox("Información Básica")
        group.setFont(self._get_section_font())
        
        layout = QFormLayout(group)
        layout.setSpacing(10)
        
        # Campo nombre
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ingresa el nombre del personaje")
        self.name_edit.setMaxLength(50)
        layout.addRow("Nombre:", self.name_edit)
        
        # Selector de clase
        self.class_combo = QComboBox()
        self.class_combo.addItems(Character.DND_CLASSES)
        self.class_combo.setCurrentText("Fighter")  # Valor por defecto
        layout.addRow("Clase:", self.class_combo)
        
        return group
    
    def _create_image_section(self) -> QGroupBox:
        """Crear sección de imagen"""
        group = QGroupBox("Imagen del Personaje")
        group.setFont(self._get_section_font())
        
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Imagen actual o placeholder
        image_layout = QHBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(120, 120)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFrameStyle(QFrame.Shape.StyledPanel)
        self.image_label.setScaledContents(False)
        
        # Mostrar placeholder inicial
        placeholder = ImageUtils.create_placeholder_pixmap((120, 120), "Sin Imagen")
        self.image_label.setPixmap(placeholder)
        
        image_layout.addWidget(self.image_label)
        
        # Botones de imagen
        image_buttons_layout = QVBoxLayout()
        
        self.select_image_button = QPushButton("Seleccionar Imagen")
        self.select_image_button.clicked.connect(self._select_image)
        
        self.remove_image_button = QPushButton("Quitar Imagen")
        self.remove_image_button.clicked.connect(self._remove_image)
        self.remove_image_button.setEnabled(False)
        
        image_buttons_layout.addWidget(self.select_image_button)
        image_buttons_layout.addWidget(self.remove_image_button)
        image_buttons_layout.addStretch()
        
        image_layout.addLayout(image_buttons_layout)
        layout.addLayout(image_layout)
        
        return group
    
    def _create_stats_section(self) -> QGroupBox:
        """Crear sección de estadísticas D&D"""
        group = QGroupBox("Estadísticas D&D")
        group.setFont(self._get_section_font())
        
        # Layout principal
        layout = QVBoxLayout(group)
        
        # Descripción
        description = QLabel("Ingresa los valores de las estadísticas (1-30):")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Grid para los stats
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        self.stat_spinboxes = {}
        
        # Crear spinboxes para cada stat
        for i, stat in enumerate(Character.STATS):
            row = i // 2
            col = (i % 2) * 3
            
            # Label del stat
            stat_label = QLabel(f"{stat}:")
            stat_label.setFont(self._get_bold_font())
            
            # SpinBox para el valor
            spinbox = QSpinBox()
            spinbox.setRange(Character.MIN_STAT, Character.MAX_STAT)
            spinbox.setValue(10)  # Valor por defecto
            spinbox.setFixedWidth(80)
            spinbox.valueChanged.connect(lambda value, s=stat: self._update_modifier_preview(s, value))
            
            # Label para mostrar el modificador
            modifier_label = QLabel("(+0)")
            modifier_label.setFixedWidth(40)
            modifier_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Guardar referencias
            self.stat_spinboxes[stat] = {
                'spinbox': spinbox,
                'modifier_label': modifier_label
            }
            
            # Añadir al grid
            stats_layout.addWidget(stat_label, row, col)
            stats_layout.addWidget(spinbox, row, col + 1)
            stats_layout.addWidget(modifier_label, row, col + 2)
        
        layout.addLayout(stats_layout)
        
        # Botón para generar stats aleatorios
        random_button = QPushButton("Generar Stats Aleatorios")
        random_button.clicked.connect(self._generate_random_stats)
        layout.addWidget(random_button)
        
        return group
    
    def _create_proficiencies_section(self) -> QGroupBox:
        """Crear sección de competencias (skills)"""
        group = QGroupBox("Competencias (Skills)")
        group.setFont(self._get_section_font())
        
        layout = QVBoxLayout(group)
        
        # Descripción
        description = QLabel("Selecciona las skills en las que el personaje tiene proficiency (+2 bonus):")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Scroll area para los checkboxes
        scroll_area = QScrollArea()
        scroll_area.setFixedHeight(200)
        scroll_area.setWidgetResizable(True)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self.proficiency_checkboxes = {}
        
        # Crear checkboxes organizados por stat
        for stat in Character.STATS:
            skills = Character.SKILLS[stat]
            if not skills:  # Skip CON ya que no tiene skills
                continue
                
            # Título del stat
            stat_title = QLabel(f"{stat} Skills:")
            stat_title.setFont(self._get_bold_font())
            stat_title.setStyleSheet("color: #FFFFFF; margin-top: 10px;")
            scroll_layout.addWidget(stat_title)
            
            # Checkboxes para las skills de este stat
            for skill in skills:
                checkbox = QCheckBox(skill)
                checkbox.setStyleSheet("margin-left: 20px;")
                self.proficiency_checkboxes[skill] = checkbox
                scroll_layout.addWidget(checkbox)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Botones de ayuda
        buttons_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Seleccionar Todas")
        select_all_btn.clicked.connect(self._select_all_proficiencies)
        select_all_btn.setFixedWidth(120)
        
        clear_all_btn = QPushButton("Limpiar Todas")
        clear_all_btn.clicked.connect(self._clear_all_proficiencies)
        clear_all_btn.setFixedWidth(120)
        
        buttons_layout.addWidget(select_all_btn)
        buttons_layout.addWidget(clear_all_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        return group
    
    def _select_all_proficiencies(self):
        """Seleccionar todas las competencias"""
        for checkbox in self.proficiency_checkboxes.values():
            checkbox.setChecked(True)
    
    def _clear_all_proficiencies(self):
        """Limpiar todas las competencias"""
        for checkbox in self.proficiency_checkboxes.values():
            checkbox.setChecked(False)
    
    def _create_buttons_layout(self) -> QHBoxLayout:
        """Crear botones de acción"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        layout.addStretch()
        
        # Botón Cancelar
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setFixedWidth(120)
        
        # Botón Guardar
        save_text = "Actualizar" if self.character else "Crear"
        self.save_button = QPushButton(save_text)
        self.save_button.clicked.connect(self._save_character)
        self.save_button.setFixedWidth(120)
        self.save_button.setDefault(True)
        
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.save_button)
        
        return layout
    
    def _get_section_font(self) -> QFont:
        """Obtener fuente para títulos de sección"""
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        return font
    
    def _get_bold_font(self) -> QFont:
        """Obtener fuente en negrita"""
        font = QFont()
        font.setBold(True)
        return font
    
    def _select_image(self):
        """Abrir diálogo para seleccionar imagen"""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Imágenes (*.png *.jpg *.jpeg *.gif *.bmp)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                image_path = selected_files[0]
                
                # Verificar que es una imagen válida
                if ImageUtils.is_valid_image(image_path):
                    self.selected_image_path = image_path
                    self._update_image_preview()
                    self.remove_image_button.setEnabled(True)
                else:
                    QMessageBox.warning(self, "Error", "El archivo seleccionado no es una imagen válida.")
    
    def _remove_image(self):
        """Quitar la imagen seleccionada"""
        self.selected_image_path = None
        placeholder = ImageUtils.create_placeholder_pixmap((120, 120), "Sin Imagen")
        self.image_label.setPixmap(placeholder)
        self.remove_image_button.setEnabled(False)
    
    def _update_image_preview(self):
        """Actualizar la vista previa de la imagen"""
        if self.selected_image_path:
            pixmap = ImageUtils.load_pixmap(self.selected_image_path, (120, 120))
            if pixmap:
                self.image_label.setPixmap(pixmap)
    
    def _update_modifier_preview(self, stat: str, value: int):
        """Actualizar la vista previa del modificador"""
        # Calcular modificador usando la fórmula de D&D
        modifier = (value - 10) // 2
        modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        
        # Actualizar label
        self.stat_spinboxes[stat]['modifier_label'].setText(f"({modifier_str})")
    
    def _generate_random_stats(self):
        """Generar estadísticas aleatorias (4d6, drop lowest)"""
        import random
        
        for stat in Character.STATS:
            # Método clásico: 4d6, descartar el menor
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort()
            stat_value = sum(rolls[1:])  # Sumar los 3 más altos
            
            # Actualizar spinbox
            self.stat_spinboxes[stat]['spinbox'].setValue(stat_value)
    
    def _load_character_data(self):
        """Cargar datos del personaje para edición"""
        if not self.character:
            return
        
        # Cargar nombre
        self.name_edit.setText(self.character.name)
        
        # Cargar clase
        if hasattr(self.character, 'character_class'):
            self.class_combo.setCurrentText(self.character.character_class)
        
        # Cargar imagen
        if self.character.image_path and os.path.exists(self.character.image_path):
            self.selected_image_path = self.character.image_path
            self._update_image_preview()
            self.remove_image_button.setEnabled(True)
        
        # Cargar stats
        for stat in Character.STATS:
            value = self.character.get_stat(stat)
            self.stat_spinboxes[stat]['spinbox'].setValue(value)
            self._update_modifier_preview(stat, value)
        
        # Cargar proficiencies
        if hasattr(self.character, 'proficiencies'):
            for skill, checkbox in self.proficiency_checkboxes.items():
                checkbox.setChecked(skill in self.character.proficiencies)
    
    def _save_character(self):
        """Validar y guardar el personaje"""
        # Obtener datos del formulario
        name = self.name_edit.text().strip()
        character_class = self.class_combo.currentText()
        stats = {}
        
        for stat in Character.STATS:
            stats[stat] = self.stat_spinboxes[stat]['spinbox'].value()
        
        # Obtener proficiencies seleccionadas
        proficiencies = []
        for skill, checkbox in self.proficiency_checkboxes.items():
            if checkbox.isChecked():
                proficiencies.append(skill)
        
        # Validar datos
        is_valid, error_message = validate_character_data(name, stats, character_class, proficiencies)
        if not is_valid:
            QMessageBox.warning(self, "Error de Validación", error_message)
            return
        
        try:
            # Crear o actualizar personaje
            if self.character:
                # Actualizar personaje existente
                self.character.name = name
                self.character.character_class = character_class
                self.character.proficiencies = proficiencies.copy()
                
                for stat, value in stats.items():
                    self.character.set_stat(stat, value)
                
                # Actualizar imagen si cambió
                if self.selected_image_path != self.character.image_path:
                    self.character.image_path = self.selected_image_path
                
                character_to_save = self.character
            else:
                # Crear nuevo personaje
                character_to_save = Character(
                    name=name,
                    stats=stats,
                    character_class=character_class,
                    proficiencies=proficiencies,
                    image_path=self.selected_image_path
                )
            
            # Emitir señal de guardado
            self.character_saved.emit(character_to_save)
            
            # Cerrar diálogo
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar el personaje: {str(e)}")