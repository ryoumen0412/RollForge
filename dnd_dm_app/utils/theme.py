"""
============================================================
SISTEMA DE ESTILOS - D&D DUNGEON MASTER APP
============================================================

PALETA DE COLORES:
- Background principal: Negro #000000
- Tarjetas: Gris oscuro #4A4A4A con transparencia
- Texto: Blanco #FFFFFF
- Botones: Gris muy oscuro #212121

TRANSPARENCIAS:
- Grid Container: rgba(0, 0, 0, 153) = 60% opacidad
- Character Cards: rgba(74, 74, 74, 51) = 20% opacidad

NOTAS IMPORTANTES:
1. Qt 6+ soporta rgba() en StyleSheets (funciona correctamente)
2. El grid container usa TransparentWidget con estilo inline
3. Las tarjetas aplican transparencia directamente en CSS
4. Los estilos inline se aplican DESPUÉS del tema global

============================================================
"""

# Colores del tema - PLANOS SIN GRADIENTES
THEME_COLORS = {
    # Colores principales
    'background': '#000000',        # Negro plano para todos los fondos
    'grid_background': '#000000',   # Negro plano para área del grid
    'card_background': '#4A4A4A',   # Gris para tarjetas (usado con rgba() para transparencia)
    
    # Colores de texto
    'text_primary': '#FFFFFF',      # Texto blanco principal
    'text_secondary': '#FFFFFF',    # Texto blanco secundario
    'text_accent': '#FFFFFF',       # Texto blanco para acentos
    
    # Colores de botones  
    'button_primary': '#212121',    # Gris oscuro para botones principales
    'button_secondary': '#212121',  # Mismo gris para botones secundarios
    'button_hover': '#333333',      # Gris un poco más claro para hover
    'button_text': '#FFFFFF',       # Texto blanco en botones
    
    # Colores de acento (mantenemos algunos para elementos especiales)
    'accent_primary': '#666666',    # Gris medio para acentos
    'accent_secondary': '#555555',  # Gris para highlights
    
    # Colores de estado
    'success': '#10B981',           # Verde para éxito
    'warning': '#F59E0B',           # Naranja para advertencias
    'danger': '#EF4444',            # Rojo para errores
    
    # Bordes
    'border_dark': '#333333',       # Borde oscuro
    'border_light': '#555555',      # Borde claro
}


def get_main_window_style():
    """Obtener estilos para la ventana principal"""
    return f"""
        QMainWindow {{
            background-color: {THEME_COLORS['background']};
            color: {THEME_COLORS['text_primary']};
        }}
        
        /* === LABELS === */
        QLabel {{
            color: {THEME_COLORS['text_primary']};
            background: transparent;
        }}
        
        /* === BUTTONS === */
        QPushButton {{
            background-color: {THEME_COLORS['button_primary']};
            border: 1px solid {THEME_COLORS['border_dark']};
            border-radius: 4px;
            color: {THEME_COLORS['button_text']};
            font-weight: bold;
            font-size: 11px;
            padding: 8px 16px;
            min-width: 100px;
            min-height: 30px;
        }}
        
        QPushButton:hover {{
            background-color: {THEME_COLORS['button_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {THEME_COLORS['button_secondary']};
        }}
        
        QPushButton:default {{
            border: 2px solid {THEME_COLORS['accent_primary']};
        }}
        
        QPushButton:disabled {{
            background-color: {THEME_COLORS['border_dark']};
            color: {THEME_COLORS['text_secondary']};
            border-color: {THEME_COLORS['border_dark']};
        }}
        
        /* === HEADER WIDGET === */
        QWidget#headerWidget {{
            background-color: {THEME_COLORS['background']};
            border: none;
            max-height: 80px;
            min-height: 68px;
        }}
        
        QLabel#titleLabel {{
            color: {THEME_COLORS['text_primary']};
            font-weight: bold;
            background: transparent;
        }}
        
        QLabel#countLabel {{
            color: {THEME_COLORS['text_secondary']};
            background: transparent;
        }}
        
        QLabel#logoLabel {{
            background: transparent;
            border: none;
        }}
        
        /* === GRID CONTAINER === */
        /* Estilos aplicados inline en TransparentWidget.apply_transparent_style() */
        
        QPushButton#headerButton {{
            background-color: {THEME_COLORS['button_primary']};
            border: 1px solid {THEME_COLORS['border_dark']};
            border-radius: 4px;
            color: {THEME_COLORS['button_text']};
            font-weight: bold;
            font-size: 11px;
            padding: 8px 16px;
            min-height: 36px;
            max-height: 36px;
        }}
        
        QPushButton#headerButton:hover {{
            background-color: {THEME_COLORS['button_hover']};
            border: 1px solid {THEME_COLORS['border_light']};
        }}
        
        QPushButton#headerButton:pressed {{
            background-color: {THEME_COLORS['button_secondary']};
        }}
        
        /* === MENU BAR === */
        QMenuBar {{
            background-color: {THEME_COLORS['card_background']};
            color: {THEME_COLORS['text_primary']};
            border-bottom: 2px solid {THEME_COLORS['border_dark']};
            padding: 2px;
        }}
        
        QMenuBar::item {{
            background: transparent;
            padding: 6px 12px;
            margin: 2px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {THEME_COLORS['button_primary']};
        }}
        
        QMenuBar::item:pressed {{
            background-color: {THEME_COLORS['button_secondary']};
        }}
        
        /* === MENU === */
        QMenu {{
            background-color: {THEME_COLORS['card_background']};
            color: {THEME_COLORS['text_primary']};
            border: 2px solid {THEME_COLORS['border_dark']};
            border-radius: 6px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 20px;
            border-radius: 4px;
            margin: 1px;
        }}
        
        QMenu::item:selected {{
            background-color: {THEME_COLORS['button_primary']};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {THEME_COLORS['border_dark']};
            margin: 4px 8px;
        }}
        
        /* === TOOLBAR === */
        QToolBar {{
            background-color: {THEME_COLORS['card_background']};
            border: 1px solid {THEME_COLORS['border_dark']};
            border-radius: 4px;
            spacing: 8px;
            padding: 8px;
        }}
        
        QToolBar QToolButton {{
            background-color: {THEME_COLORS['button_primary']};
            border: 1px solid {THEME_COLORS['border_dark']};
            border-radius: 6px;
            color: {THEME_COLORS['text_primary']};
            font-weight: bold;
            padding: 8px;
            min-width: 60px;
            min-height: 40px;
        }}
        
        QToolBar QToolButton:hover {{
            background-color: {THEME_COLORS['button_hover']};
        }}
        
        /* === STATUS BAR === */
        QStatusBar {{
            background-color: {THEME_COLORS['card_background']};
            color: {THEME_COLORS['text_secondary']};
            border-top: 2px solid {THEME_COLORS['border_dark']};
            padding: 4px;
        }}
        
        /* === SCROLL AREAS === */
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        
        QScrollBar:vertical {{
            background-color: {THEME_COLORS['card_background']};
            border: 1px solid {THEME_COLORS['border_dark']};
            border-radius: 6px;
            width: 12px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {THEME_COLORS['button_primary']};
            border-radius: 5px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {THEME_COLORS['button_hover']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            height: 0;
        }}
    """


def get_character_card_style():
    """
    Obtener estilos para las tarjetas de personajes.
    NOTA: La transparencia se aplica directamente con rgba() que funciona en Qt 6+
    """
    return f"""
        /* === TARJETA BASE CON TRANSPARENCIA === */
        CharacterCard {{
            background-color: rgba(74, 74, 74, 51);  /* 20% opacidad */
            border: 1px solid {THEME_COLORS['border_dark']};
            border-radius: 6px;
            margin: 4px;
            padding: 0px;
        }}
        
        CharacterCard:hover {{
            border-color: {THEME_COLORS['accent_primary']};
        }}
        
        /* === CONTENEDORES INTERNOS === */
        QFrame[frameShape="4"] {{  
            /* Stats panel y image container */
            background-color: transparent;
            border: 1px solid {THEME_COLORS['border_light']};
            border-radius: 4px;
        }}
        
        /* === LABELS === */
        QLabel {{
            color: {THEME_COLORS['text_primary']};
            background: transparent;
        }}
        
        /* === BOTONES === */
        QPushButton {{
            background-color: {THEME_COLORS['button_secondary']};
            border: 1px solid {THEME_COLORS['border_light']};
            border-radius: 3px;
            color: {THEME_COLORS['button_text']};
            font-weight: bold;
            font-size: 11px;
            padding: 6px 12px;
        }}
        
        QPushButton:hover {{
            background-color: {THEME_COLORS['button_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {THEME_COLORS['button_primary']};
        }}
    """


def get_character_form_style():
    """Obtener estilos para el formulario de personajes"""
    return f"""
        QDialog {{
            background-color: {THEME_COLORS['background']};
            color: {THEME_COLORS['text_primary']};
        }}
        
        /* === GROUP BOXES === */
        QGroupBox {{
            font-weight: bold;
            font-size: 12px;
            border: 2px solid {THEME_COLORS['border_dark']};
            border-radius: 6px;
            margin-top: 1ex;
            padding-top: 15px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px;
            color: {THEME_COLORS['accent_primary']};
            background-color: {THEME_COLORS['card_background']};
            border-radius: 4px;
        }}
        
        /* === INPUT FIELDS === */
        QLineEdit {{
            background-color: {THEME_COLORS['card_background']};
            border: 1px solid {THEME_COLORS['border_light']};
            border-radius: 4px;
            padding: 6px;
            color: {THEME_COLORS['text_primary']};
            font-size: 12px;
            selection-background-color: {THEME_COLORS['accent_primary']};
        }}
        
        QLineEdit:focus {{
            border-color: {THEME_COLORS['accent_primary']};
        }}
        
        QSpinBox {{
            background-color: {THEME_COLORS['card_background']};
            border: 1px solid {THEME_COLORS['border_light']};
            border-radius: 4px;
            padding: 4px 8px;
            color: {THEME_COLORS['text_primary']};
            font-size: 11px;
            font-weight: bold;
        }}
        
        QSpinBox:focus {{
            border-color: {THEME_COLORS['accent_primary']};
        }}
        
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {THEME_COLORS['button_primary']};
            border: 1px solid {THEME_COLORS['border_dark']};
            width: 16px;
        }}
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {THEME_COLORS['button_hover']};
        }}
        
        /* === BUTTONS === */
        QPushButton {{
            background-color: {THEME_COLORS['button_primary']};
            border: 1px solid {THEME_COLORS['border_dark']};
            border-radius: 4px;
            color: {THEME_COLORS['button_text']};
            font-weight: bold;
            font-size: 11px;
            padding: 8px 16px;
            min-height: 35px;
        }}
        
        QPushButton:hover {{
            background-color: {THEME_COLORS['button_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {THEME_COLORS['button_secondary']};
        }}
        
        QPushButton:default {{
            border-color: {THEME_COLORS['accent_primary']};
        }}
        
        /* === LABELS === */
        QLabel {{
            color: {THEME_COLORS['text_primary']};
            background: transparent;
        }}
        
        /* Image preview frame */
        QLabel[frameShape="4"] {{
            background-color: {THEME_COLORS['card_background']};
            border: 2px dashed {THEME_COLORS['border_light']};
            border-radius: 6px;
        }}
    """


def get_character_grid_style():
    """
    Estilos para el grid de personajes.
    IMPORTANTE: Usa fondos transparentes para permitir ver el fondo de la ventana
    """
    return f"""
        /* === GRID PRINCIPAL === */
        CharacterGrid {{
            background: transparent;
        }}
        
        /* === EMPTY STATE === */
        QFrame[frameShape="4"] {{  /* Empty state frame */
            background-color: rgba(0, 0, 0, 102);  /* 40% opacidad */
            border: 2px dashed {THEME_COLORS['border_light']};
            border-radius: 8px;
            margin: 30px;
        }}
        
        QFrame[frameShape="4"]:hover {{
            border-color: {THEME_COLORS['accent_primary']};
        }}
        
        QLabel {{
            color: {THEME_COLORS['text_accent']};
        }}
        
        /* === SCROLL AREA - TRANSPARENTE === */
        QScrollArea {{
            background: transparent;
            border: none;
        }}
        
        QScrollArea > QWidget > QWidget {{
            background: transparent;
        }}
    """


def apply_theme_to_widget(widget, widget_type="main"):
    """
    Aplicar tema a un widget específico
    
    Args:
        widget: Widget al que aplicar el tema
        widget_type: Tipo de widget ('main', 'card', 'form', 'grid')
    """
    styles = {
        'main': get_main_window_style(),
        'card': get_character_card_style(),
        'form': get_character_form_style(),
        'grid': get_character_grid_style()
    }
    
    if widget_type in styles:
        widget.setStyleSheet(styles[widget_type])


# Fuentes personalizadas para el tema
FONTS = {
    'title': {
        'size': 18,
        'weight': 'bold'
    },
    'subtitle': {
        'size': 14,
        'weight': 'bold'
    },
    'body': {
        'size': 11,
        'weight': 'normal'
    },
    'small': {
        'size': 9,
        'weight': 'normal'
    }
}


def get_fantasy_font(font_type='body'):
    """
    Obtener configuración de fuente para el tema fantasy
    
    Args:
        font_type: Tipo de fuente ('title', 'subtitle', 'body', 'small')
        
    Returns:
        Diccionario con configuración de fuente
    """
    from PySide6.QtGui import QFont
    
    font_config = FONTS.get(font_type, FONTS['body'])
    
    font = QFont()
    font.setPointSize(font_config['size'])
    
    if font_config['weight'] == 'bold':
        font.setBold(True)
    
    return font


# Configuraciones adicionales del tema
THEME_CONFIG = {
    'animation_duration': 200,  # ms
    'border_radius': 8,
    'card_spacing': 10,
    'padding': 12,
    'button_height': 35,
    'icon_size': 16
}