"""
This module implements a Pokemon battle simulation system. It provides classes and methods to conduct battles between trainers, each with their own team of Pokemon. 
The module supports various battle modes, including SET, ROTATE, and OPTIMIZE, allowing trainers to compete using different strategies.

Classes:
- Battle: Represents a battle between two trainers, facilitating the commencement and resolution of battles based on specified battle modes.
- Trainer: Represents a Pokemon trainer, containing information about the trainer's name and their team of Pokemon.
- PokeTeam: Represents a team of Pokemon belonging to a trainer, providing methods for assembling, optimizing, and managing the team during battles.
- Pokemon: Represents an individual Pokemon, including attributes such as health, battle_power, level, defense, and speed, along with methods for attacking, defending, leveling up, and determining if the Pokemon is alive.

Battle Modes:
- SET: Both trainer will battle follow a 'King of the Hill' style of combat. In this mode, a particular Pokemon from one trainer's team keeps fighting until its fainted (health <= 0). 
- ROTATE: In this mode, a Pokemon fights a round, and then is sent to the back of the team, making the next pokemon in the party fight the next round. 
- OPTIMIZE: User gets to choose an attribute to order their team. They can choose between Level, HP, Attack, Defence and Speed. This order will be maintained throughout the battle, even when the stats change after each round

The battle simulation system includes methods for conducting battles, calculating attack damage, handling battle rounds, and managing Pokemon teams' status during battles.

__author__ = "Aw Shen Yang"
"""

from __future__ import annotations
from poke_team import Trainer, PokeTeam
from pokemon_base import Pokemon
from typing import Tuple
from battle_mode import BattleMode
from data_structures.array_sorted_list import ArraySortedList, ListItem
from data_structures.stack_adt import ArrayStack
from data_structures.queue_adt import CircularQueue
import math


class Battle:

    def __init__(self, trainer_1: Trainer, trainer_2: Trainer, battle_mode: BattleMode, criterion = "health") -> None:
        """
        Initializes a Battle instance with two trainers and the specified battle mode.

        :param trainer_1 (Trainer): The first trainer participating in the battle.
        :param trainer_2 (Trainer): The second trainer participating in the battle.
        :param battle_mode (BattleMode): The mode of the battle (SET, ROTATE, or OPTIMISE).
        :param criterion (str): The criterion for sorting the teams in OPTIMISE mode (default is "health").
        :complexity: O(1) - Constant time complexity regardless of the number of Pokemon in the team.
        """
        self.trainer_1 = trainer_1
        self.trainer_2 = trainer_2
        self.battle_mode = battle_mode
        self.criterion = criterion
        self.winner_trainer = None

    def commence_battle(self) -> Trainer | None:
        """
        Commences the battle based on the specified battle mode and return the winning trainer or none if draw.

        :return: The winner trainer, or None if it's a draw.
        :rtype: Trainer or None
        :raises ValueError: If an invalid battle mode is provided.
        :complexity: 
        based on the method conduct_battle:
        Best case:  O(N(P+Q))
        attack using SET MODE or ROTATE MODE and player 1's pokemons strength is stronger than player 2 pokemons 

        Worst case: O(N+M)^2 + O((N+M)*(P+Q))
        attack using OPTIMISE MODE and both team pokemons have similar strength and fight until no pokemon left for each team, i.e. draw.
        """
        if self.battle_mode == BattleMode.SET or self.battle_mode == BattleMode.ROTATE or self.battle_mode == BattleMode.OPTIMISE:
            self._conduct_battle(self.battle_mode) #Best case: O(N(P+Q)), Worst case: O(N+M)^2 + O((N+M)*(P+Q))
            return self.winner_trainer
        else:
            raise ValueError("Invalid battle mode")
        
    def _create_teams(self) -> None:
        """
        Creates the teams for both trainers based on the specified battle mode.

        :complexity: 
        Let N = size of the first trainer's team
        Let M = size of the second trainer's team
        Let O = complexity of _pick_team method, where best case is O(N) and worst case is O(Nlog(N))
        As now we are creating two teams, therfore, O(N + M)
        Best Case: O(N+M)
        Worst Case: O(Nlog(N) + Mlog(M))
        """
        self._pick_team(self.trainer_1, self.battle_mode, self.criterion)
        self._pick_team(self.trainer_2, self.battle_mode, self.criterion)

    def _pick_team(self, trainer: Trainer, battle_mode: BattleMode, criterion: str) -> None:
        """
        Picks a team for the trainer and assemble it based on the battle mode and criterion.

        :param trainer (Trainer): The trainer to pick the team for.
        :param battle_mode (BattleMode): The battle mode to use for assembling the team.
        :param criterion (str): The criterion to optimize the team.
        :raises ValueError: If an invalid battle mode is provided.

        :complexity: 
        Let X = complexity of picking a random team, where the best and worst case for choose_randomly is O(N)
        Let Y = complexity of calling assemble team for SET and ROTATE battle mode, where the best and worst case is O(N)
        Let Z = complexity of calling assign team for OPTIMISE battle mode, where best case is O(N) and worst case is O(NlogN)
        
        Best Case: a team is already picken earlier and assembling team using battlemode SET and ROTATE is called, O(N)

        Worst Case: pick a team, follow by creating team using battlemode OPTIMISE, where assign team is called,
                    total complexity = O(N) + O(N) + O(N(logN)) = O(N(log(N)))
        """
        if len(trainer.get_team()) == 0: #Check whether the team is created
            trainer.pick_team("random") 
        if self.battle_mode.value == 0 or self.battle_mode.value == 1: #assemble the team if it is SET or ROTATE battlemode
            trainer.get_team().assemble_team(battle_mode)
        elif self.battle_mode.value == 2:   #assign the team if it is OPTIMISE battlemode
            trainer.get_team().assign_team(criterion)
        else:
            raise ValueError("Invalid battle mode")

    def _conduct_battle(self, battle_type: BattleMode) -> PokeTeam | None:
        """
        Conducts a battle of the specified BattleMode.

        :param battle_type (BattleMode): The type of battle to be conducted.
        :return (PokeTeam or None): The winning team or None if it's a draw.
        :raises ValueError: If an invalid battle mode is provided.
        :complexity: 
        Let N = the length of team 1
        Let M = the length of team 2
        Let O = the complexity of get_next_pokemon, where the best case is O(1) and the worst case is O(N+M) as both trainer is calling it
        Let P = the complexity of battle_round, which the best case and the worst case is O(P+Q) as both trainer is calling it

        Best case for the battle: 
        If team 1 pokemon is stronger than the entire team of team 2 or vice versa, and defeating the other team with one hit and without losing once, 
        therfore the loop only run N or M times. The complexity will be O(N) or O(M).

        Worst Case for the battle: 
        if both team have the similar strength and they fight till all pokemon fainted and draw at last, and it will take multiple rounds, X
        therefore X(N+M). The factor x (number of rounds until the battle end) does not affect the overall complexity, thus it is O(1)
        because it is a constant factor (it does not depend on the input size). Thus, the complexity will be O(N+M).

        Therefore, we can conclude that for each battle mode:
        SET MODE: 
            Best case: O(N) * (O(O_best) + O(P_best)) = O(N) * (O(1) + O(P+Q)) = O(N(P+Q))
            Worst case: O(M+N) * (O(O_worst) + O(P_worst)) = O(N+M) * (O(1) + O(P+Q)) = O((N+M)(P+Q))

        ROTATE MODE:
            Best case: O(N) * (O(O_best) + O(P_best)) = O(N) * (O(1) + O(P+Q)) = O(N(P+Q))
            Worst case: O(M+N) * (O(O_worst) + O(P_worst)) = O(N+M) * (O(1) + O(P+Q)) = O((N+M)(P+Q))

        OPTIMISE MODE:
            Best case: O(N) * (O(O_best) + O(P_best)) = O(N) * (O(N+M) + O(P+Q)) = O(N(N+M+P+Q))
            Worst case: O(M+N) * (O(O_worst) + O(P_worst)) = O(N+M) * (O(N+M) + O(P+Q)) = O((N+M)((N+M)+(P+Q)) = O(N+M)^2 + O((N+M)*(P+Q))
        """
        # Get the team in data structures form
        t1_team, t2_team = self.trainer_1.get_team().team, self.trainer_2.get_team().team
        while len(t1_team) != 0 or len(t2_team) != 0: #Iterates until one of the team have no pokemon left, best case O(N)/O(M) worst case O(M+N)
            if len(t1_team) == 0:            
                self.winner_trainer = self.trainer_2
                return self.trainer_2.get_team()
            elif len(t2_team) == 0:
                self.winner_trainer = self.trainer_1
                return self.trainer_1.get_team()
            
            t1_pokemon, t2_pokemon = self._get_next_pokemon(t1_team), self._get_next_pokemon(t2_team) #Get the next pokemon to battle for both team Best and worst case O(N+M)
            if battle_type.value == 0 or battle_type.value == 1: # if it is SET or ROTATE mode
                self.trainer_1.register_pokemon(t2_pokemon) # register the pokemon to other trainer's pokedex
                self.trainer_2.register_pokemon(t1_pokemon)
                self._battle_round(t1_pokemon, t2_pokemon, t1_team, t2_team) # conduct battle between pokemon of both trainer O(P+Q)
            elif battle_type.value == 2:    # if it is OPTIMISE mode
                self.trainer_1.register_pokemon(t2_pokemon.value)
                self.trainer_2.register_pokemon(t1_pokemon.value)
                self._battle_round(t1_pokemon.value, t2_pokemon.value, t1_team, t2_team)
            else:
                raise ValueError("Invalid battle mode")
        return None
    
    def _get_next_pokemon(self, trainer_team: ArrayStack|CircularQueue|ArraySortedList) -> Pokemon:
        """
        Retrieves the next Pokemon from the team based on different data structure.

        :param trainer_team (ArrayStack or CircularQueue or ArraySortedList): The team of the trainer.
        :return: The next Pokemon in the team.
        :rtype: Pokemon
        :raises TypeError: If an invalid instance is provided.
        :complexity: 
        - Best case: O(1) 
        for stack and queue, as 'pop' and 'serve' are constant-time operations, O(1)
        - Worst case: O(N) 
        for sorted list, as after deleting the index 0, the entire array will shuffle left, where N is the length of the array, O(N)
        """
        if isinstance(trainer_team, ArrayStack):
            return trainer_team.pop()
        elif isinstance(trainer_team, CircularQueue):
            return trainer_team.serve()
        elif isinstance(trainer_team, ArraySortedList):
            return trainer_team.delete_at_index(0)
        else:
            raise TypeError("Invalid instance type: the instance should be of type ArrayStack, CircularQueue or ArraySortedList.")

    def _battle_round(self, t1_pokemon: Pokemon, t2_pokemon: Pokemon, t1_team: ArrayStack|CircularQueue|ArraySortedList, t2_team: ArrayStack|CircularQueue|ArraySortedList) -> None:
        """
        Conducts a single round of battle between two Pokémon.

        :param t1_pokemon (Pokemon): The Pokemon from the first team.
        :param t2_pokemon (Pokemon): The Pokémon from the second team.
        :param t1_team (ArrayStack or CircularQueue or ArraySortedList): The team of the first trainer.
        :param t2_team (ArrayStack or CircularQueue or ArraySortedList): The team of the second trainer.

        :complexity: 
        Let A = the complexity of calculate_attack_damage, where the best and worst case is O(N+M) where M and N is the complexity of the BSet when getting pokedex completion
        Let B = the complexity of attack_defend, where the best case is O(1) and the worst case is O(log(N)) where N is the length of the team
        Let C = the complexity of sudden_death, where the best case is O(1) and the worst case is o(log(N))
        line like get_speed() and is_alive() has the complexity of O(1)

        - Best Case: O(M+N)
        when the pokemon is too strong, and fainted after the first attack, the total complexity will be 
        O(A) + O(B) = O(N+M) + O(1) = O(M+N)

        - Worst Case: O(N+M)
        when the both pokemon attack damage is weak against each other, high health and defense, therefore it will attack until 
        the stage where both pokemon's hp deduct by 1 and send back to the team.
        O(A) + O(B) + O(C) = since O(A) is O(N+M) and is dominating O(B) and O(C), the worst case will be O(N+M)

        we can conclude that the best and worst case is the same, which is O(N+M), where the dominating method is the complexity of calculate attack damage, O(A)
        """
        # If the speed of unit P1 is greater than that of P2, P1 attacks and P2 defends.
        if t1_pokemon.get_speed() > t2_pokemon.get_speed():
            attack_damage = self._calculate_attack_damage(t1_pokemon, t2_pokemon, self.trainer_1.get_pokedex_completion(), self.trainer_2.get_pokedex_completion())
            t2_pokemon.defend(attack_damage)
            self._check_alive(t1_pokemon, t2_pokemon, t1_team, self.trainer_1.get_team())
            # after this initial attack, if the defending Pokemon has not fainted (that is, it still has HP > 0), then they will retort with their own attack to the first Pokemon        
            if t2_pokemon.is_alive():
                attack_damage = self._calculate_attack_damage(t2_pokemon, t1_pokemon, self.trainer_2.get_pokedex_completion(), self.trainer_1.get_pokedex_completion())
                t1_pokemon.defend(attack_damage)
                self._check_alive(t2_pokemon, t1_pokemon, t2_team, self.trainer_2.get_team())
                # if both Pokemon are still alive after they have attacked each other. 
                if t1_pokemon.get_health() > 0 and t2_pokemon.get_health() > 0:
                    self._sudden_death(t1_pokemon, t2_pokemon, t1_team, t2_team)

        # If the speed of unit P2 is greater than that of P1, P2 attacks and P1 defends.
        elif t2_pokemon.get_speed() > t1_pokemon.get_speed():
            attack_damage = self._calculate_attack_damage(t2_pokemon, t1_pokemon, self.trainer_2.get_pokedex_completion(), self.trainer_1.get_pokedex_completion())
            t1_pokemon.defend(attack_damage)
            self._check_alive(t2_pokemon, t1_pokemon, t2_team, self.trainer_2.get_team())
            # after this initial attack, if the defending Pokemon has not fainted (that is, it still has HP > 0), then they will retort with their own attack to the first Pokemon        
            if t1_pokemon.is_alive():
                attack_damage = self._calculate_attack_damage(t1_pokemon, t2_pokemon, self.trainer_1.get_pokedex_completion(), self.trainer_2.get_pokedex_completion())
                t2_pokemon.defend(attack_damage)
                self._check_alive(t1_pokemon, t2_pokemon, t1_team, self.trainer_1.get_team())
                # if both Pokemon are still alive after they have attacked each other. 
                if t1_pokemon.get_health() > 0 and t2_pokemon.get_health() > 0:
                    self._sudden_death(t1_pokemon, t2_pokemon, t1_team, t2_team)

        # If the speeds of P1 and P2 are identical, then both attack and defend simultaneously, regardless of whether one, or both, would faint in combat.
        elif t1_pokemon.get_speed() == t2_pokemon.get_speed():
            attack_damage = self._calculate_attack_damage(t1_pokemon, t2_pokemon, self.trainer_1.get_pokedex_completion(), self.trainer_2.get_pokedex_completion())
            t2_pokemon.defend(attack_damage)
            self._check_alive(t1_pokemon, t2_pokemon, t1_team, self.trainer_1.get_team())
            attack_damage2 = self._calculate_attack_damage(t2_pokemon, t1_pokemon, self.trainer_2.get_pokedex_completion(), self.trainer_1.get_pokedex_completion())
            t1_pokemon.defend(attack_damage2)
            self._check_alive(t2_pokemon, t1_pokemon, t2_team, self.trainer_2.get_team())
            # if both Pokemon are still alive after they have attacked each other. 
            if t1_pokemon.get_health() > 0 and t2_pokemon.get_health() > 0:
                self._sudden_death(t1_pokemon, t2_pokemon, t1_team, t2_team)



    def _calculate_attack_damage(self, attacker: Pokemon, defender: Pokemon, attacker_pokedex_completion: float, defender_pokedex_completion: float) -> int:
        """
        Calculates the attack damage based on the attacker's attack and the defender's defense.

        :param attacker (Pokemon): The Pokémon launching the attack.
        :param defender (Pokemon): The Pokemon defending against the attack.
        :param attacker_pokedex_completion (float): The completion level of the attacker's Pokedex.
        :param defender_pokedex_completion (float): The completion level of the defender's Pokedex.
        :return: The calculated attack damage.
        :rtype: int

        :complexity: 
        Let A = complexity of the attack function, where best and worst case is O(1)
        Let M = complexity of getting the pokedex completion of first trainer, which the best and worst case is O(M) due to the usage of BSet
        Let N = complexity of getting the pokedex completion of second trainer, which the best and worst case is O(N) due to the usage of BSet
        Best Case: total complexity = A + M + N = O(1) + O(M) + O(N) = O(M+N)
        Worst Case: same as best case, O(M+N)
        """
        return math.ceil(attacker.attack(defender) * (attacker_pokedex_completion / defender_pokedex_completion))

    def _check_alive(self, attacker: Pokemon, defender: Pokemon, attacker_team: ArrayStack|CircularQueue|ArraySortedList, attacker_poketeam: PokeTeam) -> None:
        """
        Check whether the pokemon is alive before the next attack, if the pokemon fainted, the opponent pokemon will be level up and
        send back to the team.

        :param attacker (Pokemon): The Pokemon launching the attack.
        :param defender (Pokemon): The Pokemon defending against the attack.
        :param attacker_team (ArrayStack or CircularQueue or ArraySortedList): The team of the attacking Pokemon's trainer.
        :param attacker_poketeam (PokeTeam): The poketeam of the attacking Pokemon's trainer.
        :raises TypeError: If an invalid instance type is provided.

        :complexity: 
        - Best Case:  O(1)
        If 't1_team' and 't2_team' are instances of ArrayStack or CircularQueue, the 'push' and 'append' operations have a complexity of O(1).
        If 't1_team' and 't2_team' are instances of ArraySortedList and the list is well-sorted, adding items with key that equal to the mid also has a complexity of O(1).
        Therefore, the overall best-case complexity is O(1).
        - Worst Case: O(log(N))
        If 't1_team' and 't2_team' are instances of ArraySortedList and the correct position of the key is on the leftmost or rightmost of the array, it will has a complexity of O(log N).
        Therefore, the overall worst-case complexity is O(log N), where N is the length of the team.
        """
        if not defender.is_alive():
            attacker.level_up()
            if isinstance(attacker_team, ArrayStack):
                attacker_team.push(attacker)
            elif isinstance(attacker_team, CircularQueue):
                attacker_team.append(attacker)
            elif isinstance(attacker_team, ArraySortedList):
                if attacker_poketeam.special_counter % 2 == 0:
                    attacker_team.add(ListItem(attacker, getattr(attacker, self.criterion)))
                else:
                    attacker_team.add(ListItem(attacker, (getattr(attacker, self.criterion))*-1))
            else:
                raise TypeError("Invalid instance type: the instance should be of type ArrayStack, CircularQueue or ArraySortedList.")

    def _sudden_death(self, t1_pokemon: Pokemon, t2_pokemon: Pokemon, t1_team: ArrayStack|CircularQueue|ArraySortedList, t2_team: ArrayStack|CircularQueue|ArraySortedList) -> None:
        """
        Handles the scenario when two Pokemon still alive after they have attacked each other.
        In this case, they both lose 1 HP. If they are still alive after losing this 1 HP, they are sent back to their teams according to their battle mode. 
        If a Pokemon faints here due to losing this 1 HP and the other Pokemon is alive, such a Pokemon still gains 1 level.

        :param t1_pokemon (Pokemon): The Pokemon from the first team.
        :param t2_pokemon (Pokemon): The Pokemon from the second team.
        :param t1_team (ArrayStack or CircularQueue or ArraySortedList): The team of the first trainer.
        :param t2_team (ArrayStack or CircularQueue or ArraySortedList): The team of the second trainer.
        :raises TypeError: If an invalid instance type is provided.
        :complexity: 
        Best Case:  O(1)
                    If 't1_team' and 't2_team' are instances of ArrayStack or CircularQueue, the 'push' and 'append' operations have a complexity of O(1).
                    If 't1_team' and 't2_team' are instances of ArraySortedList and the list is well-sorted, adding items with key that equal to the mid also has a complexity of O(1).
                    Therefore, the overall best-case complexity is O(1).
        Worst Case: O(log(N))
                    If 't1_team' and 't2_team' are instances of ArraySortedList and the correct position of the key is on the leftmost or rightmost of the array, it will has a complexity of O(log N).
                    Therefore, the overall worst-case complexity is O(log N), where N is the length of the team.
        """
        t1_pokemon.health -= 1
        t2_pokemon.health -= 1

        if t1_pokemon.is_alive() and t2_pokemon.is_alive():
            if isinstance(t1_team, ArrayStack):
                t1_team.push(t1_pokemon)
                t2_team.push(t2_pokemon)
            elif isinstance(t1_team, CircularQueue):
                t1_team.append(t1_pokemon)
                t2_team.append(t2_pokemon)
            elif isinstance(t1_team, ArraySortedList):
                if self.trainer_1.get_team().special_counter % 2 == 0:
                    t1_team.add(ListItem(t1_pokemon, getattr(t1_pokemon, self.criterion)))
                else:
                    t1_team.add(ListItem(t1_pokemon, (getattr(t1_pokemon, self.criterion))*-1))
                if self.trainer_2.get_team().special_counter % 2 == 0:
                    t2_team.add(ListItem(t2_pokemon, getattr(t2_pokemon, self.criterion)))
                else:
                    t2_team.add(ListItem(t2_pokemon, (getattr(t2_pokemon, self.criterion))*-1))
            else:
                raise TypeError("Invalid instance type: the instance should be of type ArrayStack, CircularQueue or ArraySortedList.")

        elif t1_pokemon.is_alive():
            t1_pokemon.level_up()
            if isinstance(t1_team, ArrayStack):
                t1_team.push(t1_pokemon)
            elif isinstance(t1_team, CircularQueue):
                t1_team.append(t1_pokemon)
            elif isinstance(t1_team, ArraySortedList):
                if self.trainer_1.get_team().special_counter % 2 == 0:
                    t1_team.add(ListItem(t1_pokemon, getattr(t1_pokemon, self.criterion)))
                else:
                    t1_team.add(ListItem(t1_pokemon, (getattr(t1_pokemon, self.criterion))*-1))
            else:
                raise TypeError("Invalid instance type: the instance should be of type ArrayStack, CircularQueue or ArraySortedList.")

        elif t2_pokemon.is_alive():
            t2_pokemon.level_up()
            if isinstance(t1_team, ArrayStack):
                t2_team.push(t2_pokemon)
            elif isinstance(t1_team, CircularQueue):
                t2_team.append(t2_pokemon)
            elif isinstance(t1_team, ArraySortedList):
                if self.trainer_2.get_team().special_counter % 2 == 0:
                    t2_team.add(ListItem(t2_pokemon, getattr(t2_pokemon, self.criterion)))
                else:
                    t2_team.add(ListItem(t2_pokemon, (getattr(t2_pokemon, self.criterion))*-1))
            else:
                raise TypeError("Invalid instance type: the instance should be of type ArrayStack, CircularQueue or ArraySortedList.")

if __name__ == '__main__':
    t1 = Trainer('Ash')
    t2 = Trainer('Gary')
    # t1.pick_team('manual')
    battle_mode = BattleMode.OPTIMISE
    b = Battle(t1, t2, battle_mode, "defence")
    b._create_teams()
    print("before\n", t1.get_team())
    print(f"\n before\n, {t2.get_team()}")
    winner = b.commence_battle()
    print("after battle, t1",t1.get_team(), '\nafter battle, t2')
    print(t2.get_team())
    # print(f"This is after playing before regenerate t1:\n{t1.get_team()}\nThis is after playing before regenerate t2:\n{t2.get_team()}")
    print("Length team 1",len(t1.get_team()))
    print("Length team 2",len(t2.get_team()))

    # t1.get_team().regenerate_team(battle_mode, "health")
    # t2.get_team().regenerate_team(battle_mode, "health")
    # print("after regenerate, t1"'\n',t1.get_team(), '\n after regenerate, t2 \n')
    # print(t2.get_team())