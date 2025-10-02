"""
Modelo de personaje para D&D 5e
Incluye stats, modificadores, clases y sistema de competencias
"""

import uuid
from typing import Dict, Optional, List
import math


class Character:
    """
    Clase que representa un personaje de D&D 5e con sus estadísticas,
    clase, competencias y modificadores calculados automáticamente
    """
    
    # Stats básicos de D&D
    STATS = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    
    # Clases de D&D 5e
    DND_CLASSES = [
        'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 
        'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard'
    ]
    
    # Skills de D&D 5e organizadas por stat
    SKILLS = {
        'STR': ['Athletics'],
        'DEX': ['Acrobatics', 'Sleight of Hand', 'Stealth'],
        'CON': [],  # No hay skills de CON en D&D 5e
        'INT': ['Arcana', 'History', 'Investigation', 'Nature', 'Religion'],
        'WIS': ['Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival'],
        'CHA': ['Deception', 'Intimidation', 'Performance', 'Persuasion']
    }
    
    # Lista plana de todas las skills para validación
    ALL_SKILLS = []
    for stat_skills in SKILLS.values():
        ALL_SKILLS.extend(stat_skills)
    
    # Rango válido para stats en D&D (típicamente 1-20, pero permite hasta 30 para casos especiales)
    MIN_STAT = 1
    MAX_STAT = 30
    
    # Proficiency bonus estándar para niveles bajos (1-4)
    PROFICIENCY_BONUS = 2
    
    def __init__(self, name: str, stats: Dict[str, int], 
                 character_class: str = 'Fighter',
                 proficiencies: Optional[List[str]] = None,
                 image_path: Optional[str] = None, 
                 character_id: Optional[str] = None):
        """
        Inicializar un personaje
        
        Args:
            name: Nombre del personaje
            stats: Diccionario con los 6 stats de D&D
            character_class: Clase del personaje (debe ser una de DND_CLASSES)
            proficiencies: Lista de skills en las que el personaje tiene proficiency
            image_path: Ruta opcional a la imagen del personaje
            character_id: ID único del personaje (se genera automáticamente si no se proporciona)
        """
        self.id = character_id or str(uuid.uuid4())
        self.name = name
        self.image_path = image_path
        self._stats = {}
        
        # Normalizar clase
        self.character_class = self._normalize_class(character_class)
        
        # Asignar proficiencies (ya validadas externamente con validate_character_data)
        self.proficiencies = proficiencies or []
        
        # Validar y establecer stats
        for stat in self.STATS:
            if stat not in stats:
                raise ValueError(f"Falta el stat requerido: {stat}")
            self.set_stat(stat, stats[stat])
    
    @staticmethod
    def _normalize_class(character_class: str) -> str:
        """
        Normalizar el nombre de la clase a Title Case
        
        Args:
            character_class: Nombre de la clase
            
        Returns:
            Nombre normalizado
            
        Raises:
            ValueError: Si la clase no es válida
        """
        normalized = character_class.title()
        if normalized not in Character.DND_CLASSES:
            raise ValueError(f"Clase inválida: {character_class}. Debe ser una de {Character.DND_CLASSES}")
        return normalized
    
    def set_stat(self, stat: str, value: int):
        """
        Establecer el valor de un stat con validación
        
        Args:
            stat: Nombre del stat (STR, DEX, CON, INT, WIS, CHA)
            value: Valor del stat (1-30)
        """
        if stat not in self.STATS:
            raise ValueError(f"Stat inválido: {stat}. Debe ser uno de {self.STATS}")
        
        if not isinstance(value, int):
            raise TypeError(f"El valor del stat debe ser un entero, recibido: {type(value)}")
        
        if not (self.MIN_STAT <= value <= self.MAX_STAT):
            raise ValueError(f"El valor del stat {stat} debe estar entre {self.MIN_STAT} y {self.MAX_STAT}")
        
        self._stats[stat] = value
    
    def get_stat(self, stat: str) -> int:
        """
        Obtener el valor de un stat
        
        Args:
            stat: Nombre del stat
            
        Returns:
            Valor del stat
        """
        if stat not in self.STATS:
            raise ValueError(f"Stat inválido: {stat}")
        return self._stats.get(stat, 10)  # Valor por defecto 10
    
    def get_modifier(self, stat: str) -> int:
        """
        Calcular el modificador de un stat según las reglas de D&D
        Fórmula: mod = (stat - 10) / 2 (redondeo hacia abajo)
        
        Args:
            stat: Nombre del stat
            
        Returns:
            Modificador del stat (-5 a +10 típicamente)
        """
        stat_value = self.get_stat(stat)
        return math.floor((stat_value - 10) / 2)
    
    def get_all_stats(self) -> Dict[str, int]:
        """
        Obtener todos los stats del personaje
        
        Returns:
            Diccionario con todos los stats
        """
        return self._stats.copy()
    
    def get_all_modifiers(self) -> Dict[str, int]:
        """
        Obtener todos los modificadores calculados
        
        Returns:
            Diccionario con todos los modificadores
        """
        return {stat: self.get_modifier(stat) for stat in self.STATS}
    
    def has_proficiency(self, skill: str) -> bool:
        """
        Verificar si el personaje tiene proficiency en una skill
        
        Args:
            skill: Nombre de la skill
            
        Returns:
            True si tiene proficiency, False en caso contrario
        """
        return skill in self.proficiencies
    
    def get_skill_stat(self, skill: str) -> str:
        """
        Obtener el stat base de una skill
        
        Args:
            skill: Nombre de la skill
            
        Returns:
            Nombre del stat base (STR, DEX, etc.)
        """
        for stat, skills in self.SKILLS.items():
            if skill in skills:
                return stat
        raise ValueError(f"Skill inválida: {skill}")
    
    def calculate_roll_total(self, dice_result: int, skill_or_stat: str, 
                           use_expertise: bool = False) -> Dict[str, int]:
        """
        Calcular el total de una tirada con todos los modificadores
        
        Args:
            dice_result: Resultado del dado físico (ingresado por DM)
            skill_or_stat: Nombre de la skill o stat siendo utilizado
            use_expertise: Si aplicar +2 de expertise (solo para Rogue)
            
        Returns:
            Diccionario con el desglose completo de la tirada
        """
        # Determinar si es una skill o un stat directo
        if skill_or_stat in self.ALL_SKILLS:
            # Es una skill
            base_stat = self.get_skill_stat(skill_or_stat)
            is_skill = True
        elif skill_or_stat in self.STATS:
            # Es un stat directo
            base_stat = skill_or_stat
            is_skill = False
        else:
            raise ValueError(f"Skill/Stat inválido: {skill_or_stat}")
        
        # Calcular componentes
        stat_modifier = self.get_modifier(base_stat)
        
        # Proficiency bonus solo aplica a skills donde el personaje tiene proficiency
        proficiency_bonus = 0
        if is_skill and self.has_proficiency(skill_or_stat):
            proficiency_bonus = self.PROFICIENCY_BONUS
        
        # Expertise solo aplica si es Rogue Y tiene proficiency Y se especifica
        expertise_bonus = 0
        if (use_expertise and self.character_class == 'Rogue' and 
            is_skill and self.has_proficiency(skill_or_stat)):
            expertise_bonus = 2
        
        # Calcular total
        total = dice_result + stat_modifier + proficiency_bonus + expertise_bonus
        
        return {
            'dice_result': dice_result,
            'stat_modifier': stat_modifier,
            'proficiency_bonus': proficiency_bonus,
            'expertise_bonus': expertise_bonus,
            'total': total,
            'base_stat': base_stat,
            'is_skill': is_skill,
            'has_proficiency': is_skill and self.has_proficiency(skill_or_stat) if is_skill else False
        }
    
    def to_dict(self) -> Dict:
        """
        Convertir el personaje a un diccionario para serialización
        
        Returns:
            Diccionario con todos los datos del personaje
        """
        return {
            'id': self.id,
            'name': self.name,
            'character_class': self.character_class,
            'proficiencies': self.proficiencies.copy(),
            'image_path': self.image_path,
            'stats': self._stats,
            'modifiers': self.get_all_modifiers()  # Incluimos modificadores para referencia
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Character':
        """
        Crear un personaje desde un diccionario
        
        Args:
            data: Diccionario con los datos del personaje
            
        Returns:
            Instancia de Character
        """
        return cls(
            name=data['name'],
            stats=data['stats'],
            character_class=data.get('character_class', 'Fighter'),
            proficiencies=data.get('proficiencies', []),
            image_path=data.get('image_path'),
            character_id=data.get('id')
        )
    
    def __str__(self) -> str:
        """Representación en string del personaje"""
        stats_str = ', '.join([f"{stat}: {self.get_stat(stat)} ({self.get_modifier(stat):+d})" 
                              for stat in self.STATS])
        return f"{self.name} ({self.character_class}) - {stats_str}"
    
    def __repr__(self) -> str:
        """Representación detallada del personaje"""
        return f"Character(id='{self.id}', name='{self.name}', class='{self.character_class}', stats={self._stats})"


def validate_character_data(name: str, stats: Dict[str, int], 
                          character_class: str = 'Fighter',
                          proficiencies: Optional[List[str]] = None) -> tuple[bool, str]:
    """
    Validar datos de personaje antes de crear la instancia
    
    Args:
        name: Nombre del personaje
        stats: Diccionario con los stats
        character_class: Clase del personaje
        proficiencies: Lista de skills con proficiency
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    # Validar nombre
    if not name or not name.strip():
        return False, "El nombre del personaje no puede estar vacío"
    
    if len(name.strip()) > 50:
        return False, "El nombre del personaje no puede tener más de 50 caracteres"
    
    # Validar clase usando el método de normalización
    try:
        Character._normalize_class(character_class)
    except ValueError as e:
        return False, str(e)
    
    # Validar proficiencies
    if proficiencies:
        for skill in proficiencies:
            if skill not in Character.ALL_SKILLS:
                return False, f"Skill inválida: {skill}. Debe ser una de {Character.ALL_SKILLS}"
    
    # Validar stats
    if not isinstance(stats, dict):
        return False, "Los stats deben ser un diccionario"
    
    # Verificar que todos los stats requeridos estén presentes
    for required_stat in Character.STATS:
        if required_stat not in stats:
            return False, f"Falta el stat requerido: {required_stat}"
    
    # Verificar valores de stats
    for stat, value in stats.items():
        if stat not in Character.STATS:
            return False, f"Stat inválido: {stat}"
        
        if not isinstance(value, int):
            return False, f"El valor del stat {stat} debe ser un número entero"
        
        if not (Character.MIN_STAT <= value <= Character.MAX_STAT):
            return False, f"El stat {stat} debe estar entre {Character.MIN_STAT} y {Character.MAX_STAT}"
    
    return True, "Datos válidos"