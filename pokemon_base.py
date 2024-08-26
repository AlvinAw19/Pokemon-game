"""
This module contains PokeType, TypeEffectiveness and an abstract version of the Pokemon Class
1. PokeType defines all the possible types a Pokemon can belong to,
2. TypeEffectiveness provides functionality to determine the effectiveness of one Pokemon type against another.
3. The Pokemon class serves as a base for all specific Pokemon implementations.

__author__ = "Aw Shen Yang"
"""

from abc import ABC
from enum import Enum
from data_structures.referential_array import ArrayR
import math

class PokeType(Enum):
    """
    This class contains all the different types that a Pokemon could belong to

    Attributes:
        FIRE (int): Fire type.
        WATER (int): Water type.
        GRASS (int): Grass type.
        ...
        ROCK (int): Rock type.
    """
    FIRE = 0
    WATER = 1
    GRASS = 2
    BUG = 3
    DRAGON = 4
    ELECTRIC = 5
    FIGHTING = 6
    FLYING = 7
    GHOST = 8
    GROUND = 9
    ICE = 10
    NORMAL = 11
    POISON = 12
    PSYCHIC = 13
    ROCK = 14

class TypeEffectiveness:
    """
    Represents the effectiveness of one Pokemon type against another.

    Complexity: 
        for EFFECT_TABLE:
        Reading the lines: O(m) (where m is the number of lines in the file).
        Skipping the Header Line: O(1).
        The loop assigns effectiveness values to EFFECT_TABLE: O(n) (where n is the number of effectiveness values).
        Best and Worst case: O(m + n).
    """
    EFFECT_TABLE = ArrayR(len(PokeType))

    # Initialize the effect table from a CSV file
    file_path = "type_effectiveness.csv"
    with open(file_path, "r") as file:
        lines = file.readlines() # O(m)
        # Skip the header line as it is the Pokemon Type
        lines = lines[1:] # O(1)
        # Set effectiveness values into the EFFECT TABLE
        for i, line in enumerate(lines):    # O(n)
            EFFECT_TABLE[i] = line.strip()  # O(1)

    @classmethod
    def get_effectiveness(cls, attack_type: PokeType, defend_type: PokeType) -> float:
        """
        Returns the effectiveness of one Pokemon type against another, as a float.

        Args:
            attack_type (PokeType): The type of the attacking Pokemon.
            defend_type (PokeType): The type of the defending Pokemon.

        Returns:
            float: The effectiveness of the attack, as a float value between 0 and 4.
        
        Complexity:
            Best and Worst case: O(1) - Accessing the effectiveness value from the EFFECT TABLE (ArrayR) is a constant-time operation.
        """
        ATTACKER_LINE = cls.EFFECT_TABLE[attack_type.value]  # get the effectiveness values for the attacking type O(1)
        elements = ATTACKER_LINE.split(",")  # Split the line into individual effectiveness value 
        effectiveness = elements[defend_type.value]  # get the effectiveness against the defending type O(1)
        return float(effectiveness)

    def __len__(self) -> int:
        """
        Returns the number of types of Pokemon

        Complexity:
            Best and Worst case: O(1) - because the enumeration maintains an internal count of its members
        """
        return len(PokeType) 


class Pokemon(ABC): 
    """
    Represents a base Pokemon class with properties and methods common to all Pokemon.
    """
    def __init__(self):
        """
        Initializes a new instance of the Pokemon class.
        """
        # Attributes common to all Pokemon
        self.health = None
        self.level = None
        self.poketype = None
        self.battle_power = None
        self.evolution_line = None
        self.name = None
        self.experience = None
        self.defence = None
        self.speed = None

    def get_name(self) -> str:
        """
        Returns the name of the Pokemon.

        Returns:
            str: The name of the Pokemon.
        """
        return self.name

    def get_health(self) -> int:
        """
        Returns the current health of the Pokemon.

        Returns:
            int: The current health of the Pokemon.
        """
        return self.health

    def get_level(self) -> int:
        """
        Returns the current level of the Pokemon.

        Returns:
            int: The current level of the Pokemon.
        """
        return self.level

    def get_speed(self) -> int:
        """
        Returns the current speed of the Pokemon.

        Returns:
            int: The current speed of the Pokemon.
        """
        return self.speed

    def get_experience(self) -> int:
        """
        Returns the current experience of the Pokemon.

        Returns:
            int: The current experience of the Pokemon.
        """
        return self.experience

    def get_poketype(self) -> PokeType:
        """
        Returns the type of the Pokemon.

        Returns:
            PokeType: The type of the Pokemon.
        """
        return self.poketype

    def get_defence(self) -> int:
        """
        Returns the defence of the Pokemon.

        Returns:
            int: The defence of the Pokemon.
        """
        return self.defence

    def get_evolution(self) -> list:
        """
        Returns the evolution line of the Pokemon.

        Returns:
            list: The evolution of the Pokemon.
        """
        return self.evolution_line

    def get_battle_power(self) -> int:
        """
        Returns the battle power of the Pokemon.

        Returns:
            int: The battle power of the Pokemon.
        """
        return self.battle_power

    def attack(self, other_pokemon) -> float:
        """
        Calculates and returns the damage that this Pokemon inflicts on the
        other Pokemon during an attack.

        Args:
            other_pokemon (Pokemon): The Pokemon that this Pokemon is attacking.

        Returns:
            float: The damage that this Pokemon inflicts on the other Pokemon during an attack.

        Complexity:
            Best and Worst case: O(1) - as it only involves simple arimethic operations and comparison. 
        """
        if other_pokemon.get_defence() < self.get_battle_power() / 2:
            damage = self.get_battle_power() - other_pokemon.get_defence() 

        elif other_pokemon.get_defence() < self.get_battle_power():
            damage = math.ceil(self.get_battle_power() * 5/8 - other_pokemon.get_defence() / 4)
        
        else:
            damage = math.ceil(self.get_battle_power() / 4)

        return damage * (TypeEffectiveness.get_effectiveness(self.get_poketype(), other_pokemon.get_poketype())) # O(1)

    def defend(self, damage: int) -> None:
        """
        Reduces the health of the Pokemon by the given amount of damage, after taking
        the Pokemon's defence into account.

        Args:
            damage (int): The amount of damage to be inflicted on the Pokemon.
        """
        effective_damage = damage/2 if damage < self.get_defence() else damage
        self.health = self.health - effective_damage

    def level_up(self) -> None:
        """
        Increases the level of the Pokemon by 1, and evolves the Pokemon if it has
        reached the level required for evolution.

        Complexity:
            Best case: O(1) - If the pokemon name is at its final form and does not require to evolve, or the name found at the beginning of the evolution_line list.
            Worst case: O(n+a) - If the pokemon name is located near the end of the list, the complexity is O(n) (linear time, where n is the number of pokemon name in the list).
                        and a is the complexity of _evolve method
        """
        self.level += 1
        if len(self.evolution_line) > 0 and self.evolution_line.index\
            (self.name) != len(self.evolution_line)-1:
            self._evolve()

    def _evolve(self) -> None:
        """
        Evolves the Pokemon to the next stage in its evolution line, and updates
          its attributes accordingly.
        
        Complexity:
            Best case: If the pokemon name is found at the beginning of the evolution_line list, the complexity is O(1) (constant time).
            Worst case: If the pokemon name is not found or is located near the end of the list, the complexity is O(n) (linear time, where n is the number of elements in the list).
        """
        new_name_index = self.evolution_line.index(self.name) + 1   # Best case: O(N) Worst case: O(1)
        self.name = self.evolution_line[new_name_index] # O(1)
        self.evolution_line.pop(0)
        self.apply_multiplier(1.5) # O(1)
        
    def apply_multiplier(self, multiplier: float) -> None:
        """
        Apply a multiplier to all attributes of the Pokemon.

        Args:
            multiplier (float): The multiplier to apply to all attributes.
        """
        self.battle_power *= multiplier
        self.health *= multiplier
        self.speed *= multiplier
        self.defence *= multiplier

    def is_alive(self) -> bool:
        """
        Checks if the Pokemon is still alive (i.e. has positive health).

        Returns:
            bool: True if the Pokemon is still alive, False otherwise.
        """
        return self.get_health() > 0

    def __str__(self):
        """
        Return a string representation of the Pokemon instance in the format:
        <name> (Level <level>) with <health> health and <experience> experience
        """
        return f"{self.name} (Level {self.level}) with {self.get_health()} health and {self.get_experience()} experience"

