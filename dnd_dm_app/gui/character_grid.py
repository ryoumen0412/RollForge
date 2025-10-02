"""
Grid responsivo para mostrar tarjetas de personajes
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                              QFrame, QLabel, QPushButton, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QFont, QResizeEvent

from typing import List, Dict
from models.character import Character
from gui.character_card import CharacterCard
from utils.theme import get_character_grid_style


class FlowLayout(QVBoxLayout):
    """
    Layout personalizado que organiza widgets en un flujo horizontal
    que se ajusta automáticamente al ancho disponible
    """
    
    def __init__(self, parent=None, character_grid=None):
        super().__init__(parent)
        self.setSpacing(15)
        self.setContentsMargins(20, 20, 20, 20)
        self.character_grid = character_grid
        
        # Lista para mantener las filas actuales
        self.rows = []
        self.cards_per_row = 4  # Número inicial de tarjetas por fila
        # Lista para mantener todas las tarjetas
        self.all_cards = []
        
    def addCard(self, card: CharacterCard):
        """Agregar una tarjeta al layout"""
        # Agregar a la lista de todas las tarjetas
        if card not in self.all_cards:
            self.all_cards.append(card)
        
        # Si no hay filas o la fila actual está llena, crear nueva fila
        if not self.rows or self._get_row_count(self.rows[-1]) >= self.cards_per_row:
            self._create_new_row()
        
        # Agregar a la última fila
        current_row = self.rows[-1]
        current_row['layout'].addWidget(card)
    
    def _get_row_count(self, row):
        """Obtener el número de widgets en una fila (excluyendo spacers)"""
        count = 0
        layout = row['layout']
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() is not None:
                count += 1
        return count
    
    def removeCard(self, card: CharacterCard):
        """Remover una tarjeta del layout"""
        # Remover de la lista de todas las tarjetas
        if card in self.all_cards:
            self.all_cards.remove(card)
        
        # Buscar y remover del layout
        for row in self.rows:
            layout = row['layout']
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget() == card:
                    layout.removeWidget(card)
                    card.deleteLater()
                    
                    # Si la fila quedó vacía, removerla
                    if self._get_row_count(row) == 0:
                        self.removeWidget(row['frame'])
                        row['frame'].deleteLater()
                        self.rows.remove(row)
                    return
    
    def clear(self):
        """Limpiar todo el layout"""
        # Limpiar lista de tarjetas
        self.all_cards.clear()
        
        # Remover todas las filas
        for row in self.rows:
            self.removeWidget(row['frame'])
            row['frame'].deleteLater()
        self.rows.clear()
    
    def _create_new_row(self, row_height: int = None):
        """Crear una nueva fila horizontal con altura flexible"""
        # Crear frame contenedor para la fila
        row_frame = QFrame()
        
        # Altura flexible que MAXIMIZA el uso del espacio vertical
        if row_height:
            row_frame.setMinimumHeight(row_height)
            # Sin altura máxima - permitir que crezca tanto como sea necesario
        else:
            row_frame.setMinimumHeight(300)  # Altura mínima más generosa
            # Sin altura máxima fija - ocupará todo el espacio disponible
        
        row_layout = QHBoxLayout(row_frame)
        row_layout.setSpacing(15)
        row_layout.setContentsMargins(0, 5, 0, 5)  # Pequeños márgenes verticales
        
        # Centrar horizontalmente las tarjetas en la fila
        row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        
        # Agregar la fila al layout principal
        self.addWidget(row_frame)
        
        # Guardar referencia
        self.rows.append({
            'frame': row_frame,
            'layout': row_layout
        })
    
    def updateLayout(self, available_width: int, available_height: int = None):
        """Actualizar el layout basado en el espacio disponible - comportamiento flexbox completo"""
        if available_width <= 0 or not self.all_cards:
            return
            
        # Calcular número óptimo de tarjetas por fila con comportamiento flexbox
        min_card_width = 200  # Ancho mínimo de cada tarjeta
        max_card_width = 400  # Ancho máximo de cada tarjeta
        margin = 40  # Márgenes laterales
        spacing = 15  # Espacio entre tarjetas
        
        effective_width = available_width - margin
        
        # Calcular cuántas tarjetas caben con el ancho mínimo
        max_possible_cards = (effective_width + spacing) // (min_card_width + spacing)
        max_possible_cards = min(max_possible_cards, len(self.all_cards))
        
        # Calcular cuántas tarjetas caben con el ancho máximo
        min_possible_cards = max(1, (effective_width + spacing) // (max_card_width + spacing))
        
        # Determinar el número óptimo de tarjetas por fila
        new_cards_per_row = max(min_possible_cards, min(max_possible_cards, 5))
        
        # Guardar dimensiones disponibles para uso futuro
        self._last_available_width = available_width
        self._last_available_height = available_height
        
        # Si cambió el número de tarjetas por fila, reorganizar
        if new_cards_per_row != self.cards_per_row:
            self.cards_per_row = new_cards_per_row
            self._reorganize_cards_flexbox(available_width, available_height)
        else:
            # Aunque no cambie el número de filas, actualizar tamaños para flexbox
            self._update_card_sizes_only(available_width, available_height)
    
    def _reorganize_cards(self):
        """Reorganizar las tarjetas según el nuevo número por fila - método legacy"""
        # Este método ahora redirige al método flexbox completo
        width = getattr(self, '_last_available_width', 800)
        height = getattr(self, '_last_available_height', None)
        
        if not width or width < 100:
            # Fallback si no tenemos las dimensiones disponibles
            if self.character_grid and hasattr(self.character_grid, 'scroll_area'):
                width = self.character_grid.scroll_area.viewport().width()
                height = self.character_grid.scroll_area.viewport().height()
            else:
                width = 800
                height = None
                
        self._reorganize_cards_flexbox(width, height)
    
    def _reorganize_cards_flexbox(self, available_width: int, available_height: int = None):
        """Reorganizar las tarjetas con comportamiento flexbox completo"""
        if not self.all_cards:
            return
        
        # Recopilar todas las tarjetas y removerlas de los layouts actuales
        cards_to_reorganize = self.all_cards.copy()
        
        # Limpiar todas las filas pero mantener las tarjetas
        for row in self.rows:
            layout = row['layout']
            # Remover todos los widgets del layout sin eliminarlos
            while layout.count() > 0:
                item = layout.takeAt(0)
                # No llamar deleteLater() aquí, solo remover del layout
        
        # Limpiar filas
        for row in self.rows:
            self.removeWidget(row['frame'])
            row['frame'].deleteLater()
        self.rows.clear()
        
        # Calcular distribución flexbox
        total_cards = len(cards_to_reorganize)
        cards_per_row = self.cards_per_row
        
        # Calcular altura por fila - MAXIMIZAR uso del espacio vertical
        row_height = None
        if available_height and total_cards > 0:
            total_rows = (total_cards + cards_per_row - 1) // cards_per_row
            # Usar casi todo el espacio disponible (solo 30px de margen total)
            row_height = (available_height - 30) // total_rows
            # Altura mínima más generosa, sin límite máximo estricto
            row_height = max(300, row_height)  # Permitir que crezca tanto como sea necesario
        
        # Reorganizar en filas
        for i in range(0, total_cards, cards_per_row):
            # Crear nueva fila con altura calculada
            self._create_new_row(row_height)
            current_row = self.rows[-1]
            
            # Obtener tarjetas para esta fila
            cards_in_this_row = cards_to_reorganize[i:i + cards_per_row]
            
            # Actualizar tamaño de cada tarjeta para comportamiento flexbox
            for card in cards_in_this_row:
                # Reconectar señales
                if self.character_grid:
                    try:
                        card.edit_requested.disconnect()
                        card.delete_requested.disconnect()
                    except:
                        pass
                    card.edit_requested.connect(self.character_grid.edit_character_requested)
                    card.delete_requested.connect(self.character_grid.delete_character_requested)
                
                # Actualizar tamaño flexbox con altura disponible
                card.update_card_size(available_width, len(cards_in_this_row), row_height)
                
                # Agregar a la fila
                current_row['layout'].addWidget(card)
    
    def _update_card_sizes_only(self, available_width: int, available_height: int = None):
        """Actualizar solo los tamaños de las tarjetas sin reorganizar - flexbox completo"""
        if not self.rows:
            return
        
        # Calcular altura por fila - maximizar espacio vertical
        row_height = None
        if available_height and len(self.rows) > 0:
            row_height = (available_height - 30) // len(self.rows)
            row_height = max(300, row_height)  # Sin límite máximo estricto
            
        for row in self.rows:
            layout = row['layout']
            cards_in_row = []
            
            # Recopilar tarjetas en esta fila
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget() and hasattr(item.widget(), 'update_card_size'):
                    cards_in_row.append(item.widget())
            
            # Actualizar altura del frame de la fila para maximizar espacio
            if row_height:
                row['frame'].setMinimumHeight(row_height)
                # Sin altura máxima - permitir que use todo el espacio necesario
            
            # Actualizar tamaño de cada tarjeta en la fila
            for card in cards_in_row:
                card.update_card_size(available_width, len(cards_in_row), row_height)


class CharacterGrid(QWidget):
    """
    Widget que muestra las tarjetas de personajes en un grid responsivo
    """
    
    # Señales para comunicación con la ventana principal
    edit_character_requested = Signal(str)  # ID del personaje
    delete_character_requested = Signal(str)  # ID del personaje
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Diccionario para mapear IDs a tarjetas
        self.character_cards: Dict[str, CharacterCard] = {}
        
        self._setup_ui()
        
        # Aplicar tema con fondo morado oscuro
        self.setStyleSheet(get_character_grid_style())
        
        # Timer para evitar reorganizar demasiado frecuentemente
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._on_resize_timeout)
        
    def _setup_ui(self):
        """Configurar la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # === ÁREA DE SCROLL ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Widget contenedor para las tarjetas
        self.scroll_widget = QWidget()
        self.flow_layout = FlowLayout(self.scroll_widget, self)
        self.scroll_widget.setLayout(self.flow_layout)
        
        # Configurar el scroll area
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)
        
        # === ÁREA VACÍA (mostrar cuando no hay personajes) ===
        self.empty_state = self._create_empty_state()
        layout.addWidget(self.empty_state)
        
        # Inicialmente mostrar estado vacío
        self._update_visibility()
    
    def _create_empty_state(self) -> QWidget:
        """Crear el widget que se muestra cuando no hay personajes"""
        empty_widget = QFrame()
        empty_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(empty_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Icono grande
        icon_label = QLabel("D&D")
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_font.setBold(True)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Texto principal
        title_label = QLabel("No hay personajes")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Texto descriptivo
        desc_label = QLabel("¡Crea tu primer personaje para empezar la aventura!")
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc_label.setFont(desc_font)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        return empty_widget
    
    def add_character(self, character: Character):
        """
        Agregar un personaje al grid
        
        Args:
            character: Personaje a agregar
        """
        if character.id in self.character_cards:
            # Si ya existe, actualizar
            self.update_character(character)
            return
        
        # Crear nueva tarjeta
        card = CharacterCard(character)
        
        # Conectar señales
        card.edit_requested.connect(self.edit_character_requested)
        card.delete_requested.connect(self.delete_character_requested)
        
        # Agregar al layout
        self.flow_layout.addCard(card)
        
        # Guardar referencia
        self.character_cards[character.id] = card
        
        # Actualizar visibilidad
        self._update_visibility()
    
    def remove_character(self, character_id: str):
        """
        Remover un personaje del grid
        
        Args:
            character_id: ID del personaje a remover
        """
        if character_id in self.character_cards:
            card = self.character_cards[character_id]
            self.flow_layout.removeCard(card)
            del self.character_cards[character_id]
            
            # Actualizar visibilidad
            self._update_visibility()
    
    def update_character(self, character: Character):
        """
        Actualizar la información de un personaje existente
        
        Args:
            character: Personaje con información actualizada
        """
        if character.id in self.character_cards:
            card = self.character_cards[character.id]
            card.update_character(character)
    
    def clear_all(self):
        """Remover todos los personajes del grid"""
        self.flow_layout.clear()
        self.character_cards.clear()
        self._update_visibility()
    
    def set_characters(self, characters: List[Character]):
        """
        Establecer la lista completa de personajes
        
        Args:
            characters: Lista de personajes a mostrar
        """
        # Limpiar grid actual
        self.clear_all()
        
        # Agregar todos los personajes
        for character in characters:
            self.add_character(character)
        
        # Forzar un update del layout después de cargar todos los personajes
        QTimer.singleShot(100, self._force_layout_update)
    
    def _force_layout_update(self):
        """Forzar una actualización del layout con flexibilidad completa"""
        if self.scroll_area.isVisible():
            viewport_width = self.scroll_area.viewport().width()
            viewport_height = self.scroll_area.viewport().height()
            if viewport_width > 100 and viewport_height > 100:
                self.flow_layout.updateLayout(viewport_width, viewport_height)
    
    def get_character_count(self) -> int:
        """Obtener el número de personajes en el grid"""
        return len(self.character_cards)
    
    def _update_visibility(self):
        """Actualizar qué se muestra: grid o estado vacío"""
        has_characters = len(self.character_cards) > 0
        
        self.scroll_area.setVisible(has_characters)
        self.empty_state.setVisible(not has_characters)
    
        # Los estilos ahora se aplican centralizadamente desde el tema
        pass
    
    def resizeEvent(self, event: QResizeEvent):
        """Manejar eventos de redimensionamiento"""
        super().resizeEvent(event)
        
        # Solo procesar si el resize es significativo
        if hasattr(self, '_last_width'):
            width_diff = abs(event.size().width() - self._last_width)
            if width_diff < 50:  # Ignorar cambios menores a 50px
                return
        
        self._last_width = event.size().width()
        
        # Usar timer para evitar reorganizar demasiado frecuentemente
        self.resize_timer.start(200)  # 200ms delay para mayor estabilidad
    
    def _on_resize_timeout(self):
        """Manejar timeout del resize - con altura flexible"""
        if self.scroll_area.isVisible() and hasattr(self, '_last_width'):
            # Usar las dimensiones del viewport del scroll area
            viewport_width = self.scroll_area.viewport().width()
            viewport_height = self.scroll_area.viewport().height()
            
            # Solo actualizar si tenemos dimensiones válidas
            if viewport_width > 100 and viewport_height > 100:
                self.flow_layout.updateLayout(viewport_width, viewport_height)
    
    def sizeHint(self) -> QSize:
        """Sugerir tamaño óptimo para el grid"""
        return QSize(800, 600)