"""
Componente de tarjeta de personaje para mostrar información individual
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QGridLayout, QPushButton, QFrame, QSpinBox,
                              QComboBox, QCheckBox, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QFont, QPainter, QColor

from models.character import Character
from utils.image_utils import ImageUtils
from utils.theme import get_character_card_style


class CharacterCard(QFrame):
    """
    Widget que representa una tarjeta individual de personaje
    Muestra imagen, nombre, stats y modificadores
    """
    
    # Señales para comunicación con el widget padre
    edit_requested = Signal(str)  # Emite el ID del personaje
    delete_requested = Signal(str)  # Emite el ID del personaje
    roll_calculated = Signal(dict)  # Emite el resultado completo del cálculo
    
    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character
        self.image_utils = ImageUtils()
        
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        # Configurar tamaño completamente flexible - flexbox verdadero
        self.setMinimumSize(200, 250)
        # Sin altura máxima fija - se ajustará según el contenido y espacio disponible
        # Permitir que la tarjeta crezca y se contraiga tanto horizontal como verticalmente
        
        self._setup_ui()
        
        # Aplicar tema de tarjetas oscuras
        self.setStyleSheet(get_character_card_style())
    
    def _setup_ui(self):
        """Configurar la interfaz de usuario de la tarjeta"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)  # Espaciado más generoso
        layout.setContentsMargins(12, 12, 12, 12)  # Márgenes ligeramente más grandes
        
        # === IMAGEN DEL PERSONAJE ===
        self.image_container = QFrame()
        # Imagen completamente flexible - se ajusta al tamaño disponible
        self.image_container.setMinimumSize(60, 60)
        # Sin tamaño máximo fijo - se escalará proporcionalmente
        self.image_container.setFrameStyle(QFrame.Shape.StyledPanel)
        image_container_layout = QVBoxLayout(self.image_container)
        image_container_layout.setContentsMargins(4, 4, 4, 4)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(50, 50)
        self.image_label.setScaledContents(True)
        self._load_character_image()
        
        image_container_layout.addWidget(self.image_label)
        
        # Centrar imagen en la tarjeta
        image_layout = QHBoxLayout()
        image_layout.addStretch()
        image_layout.addWidget(self.image_container)
        image_layout.addStretch()
        layout.addLayout(image_layout)
        
        # === NOMBRE DEL PERSONAJE ===
        self.name_label = QLabel(self.character.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setMaximumHeight(40)  # Limitar altura
        
        # Configurar fuente del nombre
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        
        layout.addWidget(self.name_label)
        
        # === CLASE Y STATS ===
        class_label = QLabel(f"Clase: {getattr(self.character, 'character_class', 'Fighter')}")
        class_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        class_font = QFont()
        class_font.setPointSize(9)
        class_font.setItalic(True)
        class_label.setFont(class_font)
        layout.addWidget(class_label)
        
        # === STATS Y MODIFICADORES ===
        stats_widget = self._create_stats_widget()
        layout.addWidget(stats_widget)
        
        # === SECCIÓN DE TIRADAS ===
        roll_widget = self._create_roll_widget()
        layout.addWidget(roll_widget)
        
        # Espaciador flexible para empujar los botones hacia abajo
        layout.addStretch(1)
        
        # === BOTONES DE ACCIÓN (PEGADOS AL FONDO) ===
        buttons_layout = self._create_buttons_layout()
        layout.addLayout(buttons_layout)
    
    def update_card_size(self, available_width: int, cards_in_row: int, available_height: int = None):
        """Actualizar el tamaño de la tarjeta basado en el espacio disponible - flexbox completo"""
        if cards_in_row <= 0:
            return
            
        # Calcular ancho disponible por tarjeta
        spacing = 15  # Espacio entre tarjetas
        margin = 40   # Márgenes laterales total
        
        total_spacing = (cards_in_row - 1) * spacing
        card_width = (available_width - margin - total_spacing) // cards_in_row
        
        # Limitar el ancho mínimo y máximo
        card_width = max(200, min(400, card_width))
        
        # Calcular altura flexible - MAXIMIZAR espacio vertical disponible
        base_height = max(300, int(card_width * 1.2))  # Altura base más generosa
        
        # Si se proporciona altura disponible, usar TODO el espacio posible
        if available_height and available_height > 200:
            # Usar casi todo el espacio disponible (solo 20px de margen total)
            card_height = max(base_height, available_height - 20)
        else:
            # Sin limitación de altura, usar un tamaño generoso
            card_height = max(base_height, min(600, int(card_width * 1.6)))
        
        # Actualizar tamaño de la tarjeta
        self.setFixedWidth(card_width)
        self.setMaximumHeight(card_height)
        self.setMinimumHeight(min(250, card_height))
        
        # Actualizar tamaño de imagen proporcionalmente
        image_size = max(50, min(150, card_width * 0.3))
        self.image_label.setFixedSize(int(image_size), int(image_size))
        
        # También actualizar el contenedor de imagen
        container_size = image_size + 8  # 4px padding en cada lado
        if hasattr(self, 'image_container'):
            self.image_container.setFixedSize(int(container_size), int(container_size))
        
        # Los botones ahora tienen altura fija (40px) y se expanden horizontalmente
        # Solo necesitamos actualizar el ancho mínimo si es necesario
        if hasattr(self, 'edit_button') and hasattr(self, 'delete_button'):
            # Ancho mínimo adaptativo pero manteniendo altura fija
            min_button_width = max(60, min(120, card_width * 0.25))  # 25% del ancho cada uno
            self.edit_button.setMinimumWidth(int(min_button_width))
            self.delete_button.setMinimumWidth(int(min_button_width))
        
        # Recargar imagen con nuevo tamaño
        self._load_character_image()
    
    def _load_character_image(self):
        """Cargar la imagen del personaje o mostrar placeholder"""
        # Tamaño dinámico basado en el tamaño actual del contenedor
        current_size = self.image_label.size()
        target_size = (max(72, current_size.width()), max(72, current_size.height()))
        
        if self.character.image_path:
            pixmap = ImageUtils.load_pixmap(
                self.character.image_path, 
                target_size
            )
        else:
            pixmap = None
        
        if pixmap:
            self.image_label.setPixmap(pixmap)
        else:
            # Crear placeholder responsivo
            placeholder = ImageUtils.create_placeholder_pixmap(
                target_size, 
                "D&D\nSin Imagen"
            )
            self.image_label.setPixmap(placeholder)
    
    def _create_stats_widget(self) -> QWidget:
        """
        Crear el widget que muestra los stats y modificadores
        
        Returns:
            Widget con la información de stats
        """
        stats_widget = QFrame()
        stats_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        stats_widget.setFrameShadow(QFrame.Shadow.Sunken)
        stats_widget.setFixedHeight(80)  # Altura fija para consistencia
        
        layout = QGridLayout(stats_widget)
        layout.setSpacing(2)
        layout.setContentsMargins(6, 4, 6, 4)
        
        # Organizar stats en 3 columnas x 2 filas para mejor uso del espacio
        positions = [
            (0, 0), (0, 1), (0, 2),  # Primera fila: STR, DEX, CON
            (1, 0), (1, 1), (1, 2)   # Segunda fila: INT, WIS, CHA
        ]
        
        for i, stat in enumerate(Character.STATS):
            row, col = positions[i]
            
            # Contenedor para cada stat
            stat_container = QFrame()
            stat_layout = QVBoxLayout(stat_container)
            stat_layout.setSpacing(0)
            stat_layout.setContentsMargins(2, 2, 2, 2)
            
            # Label del stat (ej: "STR")
            stat_label = QLabel(stat)
            stat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_font = QFont()
            stat_font.setBold(True)
            stat_font.setPointSize(8)
            stat_label.setFont(stat_font)
            
            # Label del valor y modificador (ej: "16" y "(+3)")
            value = self.character.get_stat(stat)
            modifier = self.character.get_modifier(stat)
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            
            value_label = QLabel(str(value))
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_font = QFont()
            value_font.setPointSize(10)
            value_font.setBold(True)
            value_label.setFont(value_font)
            
            mod_label = QLabel(f"({modifier_str})")
            mod_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            mod_font = QFont()
            mod_font.setPointSize(8)
            mod_label.setFont(mod_font)
            
            # Ensamblar
            stat_layout.addWidget(stat_label)
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(mod_label)
            
            layout.addWidget(stat_container, row, col)
        
        return stats_widget
    
    def _create_roll_widget(self) -> QGroupBox:
        """Crear widget para el sistema de tiradas"""
        roll_group = QGroupBox("Tiradas D&D")
        roll_layout = QVBoxLayout(roll_group)
        roll_layout.setSpacing(6)
        roll_layout.setContentsMargins(6, 6, 6, 6)
        
        # Form layout para los controles
        form_layout = QFormLayout()
        form_layout.setSpacing(4)
        
        # Input para el resultado del dado
        self.dice_input = QSpinBox()
        self.dice_input.setRange(1, 20)
        self.dice_input.setValue(10)
        self.dice_input.setToolTip("Ingresa el resultado del dado físico")
        form_layout.addRow("Dado d20:", self.dice_input)
        
        # Dropdown para skill/stat
        self.skill_combo = QComboBox()
        # Agregar stats directos
        for stat in Character.STATS:
            self.skill_combo.addItem(f"{stat} (Stat)", stat)
        
        # Agregar separador visual y skills
        self.skill_combo.insertSeparator(len(Character.STATS))
        
        # Agregar skills organizadas
        for stat in Character.STATS:
            skills = Character.SKILLS[stat]
            for skill in skills:
                self.skill_combo.addItem(f"{skill} ({stat})", skill)
        
        form_layout.addRow("Skill/Stat:", self.skill_combo)
        
        # Checkbox de expertise (solo para Rogue)
        self.expertise_checkbox = QCheckBox("+2 Expertise")
        self.expertise_checkbox.setToolTip("Solo disponible para clase Rogue")
        # Habilitar solo si es Rogue
        is_rogue = getattr(self.character, 'character_class', 'Fighter') == 'Rogue'
        self.expertise_checkbox.setEnabled(is_rogue)
        if not is_rogue:
            self.expertise_checkbox.setVisible(False)
        
        form_layout.addRow("", self.expertise_checkbox)
        
        roll_layout.addLayout(form_layout)
        
        # Botón calcular
        calculate_button = QPushButton("Calcular Tirada")
        calculate_button.clicked.connect(self._calculate_roll)
        roll_layout.addWidget(calculate_button)
        
        # Label para mostrar resultado
        self.result_label = QLabel("Resultado aparecerá aquí...")
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setMinimumHeight(60)
        self.result_label.setFrameStyle(QFrame.Shape.StyledPanel)
        self.result_label.setStyleSheet("padding: 4px; margin: 2px;")
        roll_layout.addWidget(self.result_label)
        
        return roll_group
    
    def _calculate_roll(self):
        """Calcular el resultado de la tirada con todos los modificadores"""
        try:
            # Obtener valores de la interfaz
            dice_result = self.dice_input.value()
            skill_or_stat = self.skill_combo.currentData()
            use_expertise = self.expertise_checkbox.isChecked() if self.expertise_checkbox.isVisible() else False
            
            # Calcular usando el modelo
            result = self.character.calculate_roll_total(dice_result, skill_or_stat, use_expertise)
            
            # Formatear resultado para mostrar
            skill_name = self.skill_combo.currentText().split(' (')[0]
            result_text = f"🎯 TIRADA: {skill_name}\n"
            result_text += f"Dado: {result['dice_result']}\n"
            result_text += f"Modificador {result['base_stat']}: {result['stat_modifier']:+d}\n"
            
            if result['proficiency_bonus'] > 0:
                result_text += f"Proficiency: {result['proficiency_bonus']:+d}\n"
            
            if result['expertise_bonus'] > 0:
                result_text += f"Expertise: {result['expertise_bonus']:+d}\n"
                
            result_text += f"\n🎲 TOTAL: {result['total']}"
            
            self.result_label.setText(result_text)
            
            # Emitir señal con resultado completo
            result['character_name'] = self.character.name
            result['skill_used'] = skill_name
            self.roll_calculated.emit(result)
            
        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")
    
    def _create_buttons_layout(self) -> QHBoxLayout:
        """
        Crear los botones de acción - flexbox horizontal con altura fija
        
        Returns:
            Layout con los botones que se expanden horizontalmente
        """
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)  # Espaciado entre botones
        buttons_layout.setContentsMargins(0, 8, 0, 0)  # Margen superior
        
        # Botón Editar - flexbox horizontal con altura fija
        self.edit_button = QPushButton("Editar")
        self.edit_button.setFixedHeight(40)  # Altura fija razonable
        self.edit_button.setMinimumWidth(60)  # Ancho mínimo
        # El ancho se expandirá automáticamente (flexbox)
        self.edit_button.setToolTip("Editar personaje")
        self.edit_button.clicked.connect(self._on_edit_clicked)
        
        # Botón Eliminar - flexbox horizontal con altura fija
        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setFixedHeight(40)  # Altura fija razonable
        self.delete_button.setMinimumWidth(60)  # Ancho mínimo
        # El ancho se expandirá automáticamente (flexbox)
        self.delete_button.setToolTip("Eliminar personaje")
        self.delete_button.clicked.connect(self._on_delete_clicked)
        
        # Layout flexbox - los botones se expanden horizontalmente
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        
        return buttons_layout
    
        # Los estilos ahora se aplican centralizadamente desde el tema
        pass
    
    def _on_edit_clicked(self):
        """Manejar clic en botón editar"""
        self.edit_requested.emit(self.character.id)
    
    def _on_delete_clicked(self):
        """Manejar clic en botón eliminar"""
        self.delete_requested.emit(self.character.id)
    
    def update_character(self, character: Character):
        """
        Actualizar la tarjeta con nueva información del personaje
        
        Args:
            character: Nueva instancia del personaje
        """
        self.character = character
        
        # Actualizar nombre
        self.name_label.setText(character.name)
        
        # Recargar imagen
        self._load_character_image()
        
        # Recrear widget de stats
        # Primero remover el widget anterior
        layout = self.layout()
        stats_widget = layout.itemAt(2).widget()  # El widget de stats está en posición 2
        if stats_widget:
            stats_widget.deleteLater()
            layout.removeWidget(stats_widget)
        
        # Crear nuevo widget de stats
        new_stats_widget = self._create_stats_widget()
        layout.insertWidget(2, new_stats_widget)
    
    def get_character_id(self) -> str:
        """
        Obtener el ID del personaje de esta tarjeta
        
        Returns:
            ID único del personaje
        """
        return self.character.id
    
    def sizeHint(self) -> QSize:
        """Sugerir tamaño óptimo para la tarjeta"""
        return QSize(240, 320)
        
    def minimumSizeHint(self) -> QSize:
        """Tamaño mínimo de la tarjeta"""
        return QSize(240, 320)