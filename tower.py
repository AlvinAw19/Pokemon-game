"""
This module implements the BattleTower class, which represents the battle tower, where the player (with a team of Pokemon), faces a gauntlet of teams of Pokemon to battle.
Each team, including the player's team and the enemy teams, has a certain number of lives. The battle tower ends when there are no enemy trainer lives left, or no lives left for the player team, or both.

The BattleTower class provides functionality for initializing the tower, setting up the player's team, generating enemy teams, simulating battles, and tracking progress.

__author__ = "Aw Shen Yang"
"""

from poke_team import Trainer
from enum import Enum
from battle import Battle, BattleMode
from data_structures.queue_adt import CircularQueue
from typing import Tuple
import random

class BattleTower:
    MIN_LIVES = 1   # Setting the maximum and minimum number of lives for both player trainer and enemy
    MAX_LIVES = 3
    def __init__(self) -> None:
        """
        Initializes the BattleTower class.

        :complexity: Best and Worst case: O(1) as initialisation process take constant time
        """
        self.player_trainer_lives = None # This variable will be a tuple of (trainer, lives) after it being initiated by the user
        self.enemy_trainer_lives = None # This variable will be a circular queue of enemy in a form of tuples, (enemy, lives)
        self.enemy_defeated_count = 0 # the number of enemy the trainer defeated

    def set_my_trainer(self, trainer: Trainer) -> None:
        """
        Sets the player's team for the battle tower and generates between MIN_LIVES and MAX_LIVES lives.

        :param trainer (Trainer): The Trainer object representing the player.
        :post: self.player_trainer_lives will be initialised with a tuple of the trainer and his lives
        :complexity: 
        O(1) for generating random lives. 
        O(1) for initialisation
        Best and worst case: O(1)
        """
        lives = random.randint(BattleTower.MIN_LIVES, BattleTower.MAX_LIVES) #O(1)
        self.player_trainer_lives = (trainer, lives) #O(1)

    def generate_enemy_trainers(self, num_teams: int) -> None:
        """
        randomly generates a specified number of enemy teams for the battle tower, each with a random
        number of lives between MIN_LIVES and MAX_LIVES.

        :param num_teams (int): The number of enemy teams to generate.
        :post: self.enemy_trainer_lives will become circular queue and initialised with tuples of the enemy and his lives
        :complexity: 
        Let N = the number of team to be generated
        Let M = the complexity of the method _generate_enemy_trainer where the best and worst case is O(N)

        Best Case: O(N*M)
        The loop iterates N times to generate N number of teams,O(N) inside the loop, _generate_eneny_trainer is called, O(M)
        generating random trainer lives have the complexity of O(1), and appending trainer lives into circular queue have the complexity of O(1)
        Therefore, the total complexity is O(N) * (O(M)+O(1)+O(1)) = O(N*M).

        Worst case:
        same as the best case, O(N*M)
        """
        self.enemy_trainer_lives = CircularQueue(num_teams) 
        for _ in range(num_teams): #O(N)
            bad_trainer = self._generate_enemy_trainer() #O(M)
            bad_lives = random.randint(self.MIN_LIVES, self.MAX_LIVES) #O(1)
            self.enemy_trainer_lives.append((bad_trainer, bad_lives)) #O(1)

    def _generate_enemy_trainer(self) -> Trainer:
        """
        Generates a random enemy trainer for the battle tower and assembling them using ROTATE battlemode.

        :return: A randomly generated enemy trainer.
        :rtype: Trainer
        :complexity: 
        Let R = the complexity of pick team ("random") where the best and worst case is O(N), N is the length of the team
        Let A = the complexity of assembling the team with BattleMode.ROTATE, where the best and worst case is O(N), N is the length of the team
        Therefore, the total complexity for the best and worst case is O(N) + O(N) = O(N)
        """
        trainer = Trainer('Enemy')
        trainer.pick_team("random")
        trainer.get_team().assemble_team(BattleMode.ROTATE)
        return trainer

    def battles_remaining(self) -> bool:
        """
        checks if there are more battles remaining in the battle tower by verifying if the player or
        any enemy team has remaining lives.

        :return: True if there are more battles remaining, False otherwise.
        :rtype: bool

        :complexity: Best and Worst case is O(1), as it is just accessing the length of the the queue which is just constant time operation
        """
        return self.player_trainer_lives[1] > 0 and (len(self.enemy_trainer_lives) > 0)

    def next_battle(self) -> Tuple[Trainer, Trainer, Trainer, int, int]:
        """
        simulates a battle between the player team and the next enemy team in the tower.
        It retrieves the player and enemy trainers and their respective remaining lives from the class attributes.
        After simulating the battle, it updates the remaining lives of both teams, increments the enemy defeated count,
        and regenerates the player team and enemy team if it has remaining lives.

        :return: A tuple containing the battle result, player trainer, enemy trainer, player lives remaining after the battle, and enemy lives remaining after the battle.
        :rtype: Tuple[Trainer, Trainer, Trainer, int, int]
        :complexity: 
        Let A = the complexity of commence_battle for ROTATE battlemode where the best case is O(N(P+Q)) and the worst case is O((N+M)(P+Q))
        Let B = the complexity of regenerate_team for ROTATE battlemode where the best case is O(N) and the worst case is O(N*M)

        Best case: O(N(P+Q))
        when the player trainer pokemon too strong and one hit all enemy pokemon, the complexity will be O(N(P+Q))
        and when regenerate the team, all the pokemon of the trainer team is at front part of POKE_LIST and assembling the team using circular queue has
        the complexity of O(N), therefore the total complexity for best case is O(A_best) + O(B_worst) = O(N(P+Q)) where the complexity of commence_battle
        dominated the function.
        
        Worst case: O((N+M)(P+Q))
        when player trainer and enemy team have similar strength and they fight till all pokemon fainted and draw at last, the complexity will be 
        O((N+M)(P+Q))and when regenerate the team, all the pokemon of the trainer team is at back part of POKE_LIST and contributed to a complexity
        of O(NM), therefore the total complexity for worst case is O(A_worst) + O(B_worst) = O((N+M)(P+Q)) where the complexity of commence_battle
        dominated the function.
        """
        player_trainer, player_lives = self.player_trainer_lives #O(1)
        enemy_trainer, enemy_lives = self.enemy_trainer_lives.serve() #O(1)

        tower_battle = Battle(player_trainer, enemy_trainer, BattleMode.ROTATE)
        winner_trainer = tower_battle.commence_battle() # best case is O(N(P+Q)) and the worst case is O((N+M)(P+Q)

        if winner_trainer == None:
            player_lives -= 1
            enemy_lives -= 1
            self.enemy_defeated_count += 1
        elif winner_trainer == player_trainer:
            enemy_lives -= 1
            self.enemy_defeated_count += 1
        elif winner_trainer == enemy_trainer:
            player_lives -= 1
        if enemy_lives != 0:
            enemy_trainer.get_team().regenerate_team(BattleMode.ROTATE) # the best case is O(N) and the worst case is O(N*M)
            self.enemy_trainer_lives.append((enemy_trainer, enemy_lives)) # O(1)
        if player_lives != 0:
            player_trainer.get_team().regenerate_team(BattleMode.ROTATE)
        self.player_trainer_lives = (player_trainer, player_lives)

        return winner_trainer, player_trainer, enemy_trainer, player_lives, enemy_lives


    def enemies_defeated(self) -> int:
        """
        returns the total number of enemy lives taken by the player during battles in the tower.
        
        :return: The number of enemy lives taken by the player.
        :rtype: int
        :complexity: 
        Best case is O(1) 
        as the method directly returns the value of 'self.enemy_defeated_count'.
        Getting the count is a constant-time operation (O(1)) because it doesn't depend on any data structures' size.

        The worst case is the same as best case, o(1)
        """
        return self.enemy_defeated_count
    

if __name__ == "__main__":
    player_trainer = Trainer('Som')
    player_trainer.pick_team("Random")
    # print(player_trainer.get_team())
    player_trainer.get_team().assemble_team(BattleMode.ROTATE)
    player_trainer.get_team().special(BattleMode.ROTATE)

    bt = BattleTower()
    bt.set_my_trainer(player_trainer)
    # print(bt.player_trainer)
    # print(bt.player_lives)
    bt.generate_enemy_trainers(2)
    # # Check number of enemies defeated
    # self.assertEqual(self.bt.enemies_defeated(), 0, "Battle tower not set up correctly")
    while bt.battles_remaining():
        bt.next_battle()
        print(bt.battles_remaining())
    player_trainer.get_team().regenerate_team(battle_mode= BattleMode.OPTIMISE, criterion= "defence")
    print(player_trainer.get_team())
