"""
This module contains classes and methods for managing PokeTeams and Trainers in a Pokemon game.

Classes:
- PokeTeam: Represents a team of Pokemon.
- Trainer: Represents a Pokémon Trainer.

Dependencies:
- pokemon.py: Contains classes for different Pokemon.
- battle_mode.py: Enumerates different battle modes.

__author__ = "Aw Shen Yang"
"""
# Importing necessary modules and classes
from pokemon import *
import random
from typing import List
from data_structures.bset import BSet
from data_structures.array_sorted_list import ArraySortedList, ListItem
from data_structures.stack_adt import ArrayStack
from data_structures.referential_array import ArrayR
from data_structures.queue_adt import CircularQueue
from battle_mode import BattleMode


class PokeTeam:
    random.seed(20)
    TEAM_LIMIT = 6                          # Setting the maximum number of Pokemon in a team O(1)
    POKE_LIST = get_all_pokemon_types()     # method from pokemon.py where getting an array of classes for all available Pokemon, O(T) where T is the complexity of get_all_pokemon_types(), which best and worst case is O(N)
    POKE_HEALTH = get_all_pokemon_healths() # method from pokemon.py where getting an array of health values for all available Pokemon, O(H) where H is complexity of get_all_pokemon_healths(), which best and worst case is O(N)
    CRITERION_LIST = ["health", "defence", "battle_power", "speed", "level"]  # List of criteria to assemble the team during OPTIMISE battlemode 



    def __init__(self):
        """ 
        Initializes a PokeTeam instance.
        
        :complexity: 
        - Best Case: O(1) - initialising a variable take constant time.
        - Worst Case: same as the Best Case, O(1)
        """
        self.team = ArrayR(self.TEAM_LIMIT)  # Initializing an ArrayR instance for storing the team O(1)
        self.team_memory = None              # Initializing a variable to keep a memory for the order of the pokemon in a team O(1)
        self.team_count = 0                  # Initializing a variable(counter) to keep track of the number of Pokemon in the team O(1)
        self.special_counter = 0             # Initializing a variable(special counter) to keep track of the number of special called O(1)

    def choose_manually(self) -> None:
        """ 
        Allows the user to manually choose Pokemon for the team.

        :post: the ArrayR, self.team, will be fill up with pokemon inside
        :complexity: 
            Let N = the number of pokemon to choose for a team
            Let M = the total number of pokemon class inside the POKE_LIST
            - Best Case: O(N)
            Occurs when the user enters a valid number of Pokemon (between 1 and PokeTeam.TEAM_LIMIT) and 
            provides Pokemon names that matches the index 0 of Pokemon classes in the array.
            The loop for inputting the number of Pokemon (while True) runs only ONCE.
            The inner loop for entering Pokemon names (for i in range(num_pokemon)) runs exactly N times.
            Within the inner loop, the search for a matching Pokemon class (for pokemon_class in PokeTeam.POKE_LIST) also runs 1 times since the pokemon choosen is the first in the array
            therefore having O(1) complexity.
            Total complexity = O(1) + O(N) * (O(1) + O(1)) = O(N)

            - Worst Case: O(N*M) 
            the user repeatedly enters invalid inputs for both the number of Pokemon and the Pokemon names.
            The loop for inputting the number of Pokemon (while True) may run MULTIPLE times(x).
            The factor x (number of times the while True loop runs until valid input is provided) does not affect the overall complexity, thus it is O(1)
            because it is a constant factor (it does not depend on the input size).
            The inner loop for entering Pokemon names (for i in range(num_pokemon)) runs N times.
            Within the inner loop, the search for a matching Pokemon class (for pokemon_class in PokeTeam.POKE_LIST) also runs M times.
            Total complexity = O(1) + O(N) * (O(1) + O(M)) = O(N*M)
        """
        while True: # O(1) - Constant time operation
            num_pokemon = int(input(f"How many Pokemon do you want in your team (up to {PokeTeam.TEAM_LIMIT})? "))
            if 0 < num_pokemon <= self.TEAM_LIMIT:
                break
            print(f"Invalid number of Pokemon. Please choose a number between 1 and {PokeTeam.TEAM_LIMIT}.")

        print(f"Choose {num_pokemon} Pokemon for your team.")
        manual_team = ArrayR(num_pokemon)
        for i in range(num_pokemon): # O(N) iterations, N = number of pokemon
            while True:
                pokemon_name = input(f"Enter the name of Pokemon {i + 1}: ")
                found = False  # Flag to indicate if the Pokemon was found
                
                # Check if the input Pokemon name matches any Pokemon classes in POKE_LIST
                for pokemon_class in PokeTeam.POKE_LIST: # O(M) where M is the number of pokemon classes
                    if pokemon_name.lower() == pokemon_class.__name__.lower():
                        manual_team[i] = pokemon_class()  # O(1) 
                        found = True
                        break  # break once a match is found
                
                if found:
                    self.team_count += 1  # count increase only if a valid Pokemon was found
                    break  # break once a valid Pokemon was found
                else:
                    print(f"Pokemon '{pokemon_name}' not found. Please enter a valid Pokemon name.")

        print(f"You have chosen {self.team_count} Pokemon for your team.")
        self.team = manual_team         #O(1)
        self.team_memory = self.team    #O(1)

    def choose_randomly(self) -> None:
        """ 
        Generates a team based on the team limit with randomly chosen Pokemon.

        :post: the ArrayR, self.team, will be fill up with pokemon inside
        :complexity: 
            Let N = the number of Pokemon to choose for a team
            Let M = the complexity of get_all_pokemon_types, where the best and worst case is O(M)
            - Best Case: O(M)
            The loop iterates N times, O(N).
            For each iteration, it will generate a random integer using random.randint(0, len(all_pokemon)-1) takes constant time (O(1)).
            Assigning the selected Pokémon class to the team also takes constant time (O(1)).
            Total complexity = O(M) + O(N)*(O(1)+O(1)) = O(M) 
            as M is the total number of pokemon available and N is the number of pokemon in a team, therefore, O(M) is a dominating complexity

            - Worst Case: Same as the Best Case, O(M)
        """
        all_pokemon = get_all_pokemon_types() # O(M), M is the total subclasses of Pokemon
        self.team_count = 0 #O(1)
        for i in range(self.TEAM_LIMIT): #O(N), N is the number of Pokemon to choose for a team
            rand_int = random.randint(0, len(all_pokemon)-1)    #O(1)
            self.team[i] = all_pokemon[rand_int]()              #O(1)
            self.team_count += 1
        self.team_memory = self.team                            #O(1)
    
    def regenerate_team(self, battle_mode: BattleMode, criterion: str = None) -> None:
        """
        Heal all of the pokemon to their original HP while preserving their level and evolution. 
        Assemble the team according to the battle mode 
        If a special is called, it need to be called again after regenerate to maintain the order of the team
        
        :param battle_mode (BattleMode): The battle mode to be used for assembling the team.
        :param criterion (str): The criterion to be used for assembling the team for OPTIMISE battle mode
        :post: the sequence of the pokemon will be maintain based on the order before the battle with health fully regenerated
        :complexity:
            Let N = the total number of pokemon in a team
            Let M = the total number of pokemon class inside the POKE_LIST
            Let A = complexity of assemble team, where best case is O(N) and worst case is O(Nlog(N))
            Let S = complexity of special, where best case is O(N) and worst case is O(Nlog(N))

            - Best case: O(N)
            occurs when regenerate the entire team O(N), and then pokemons' index is at the front of the POKE_LIST, assemble the 
            team with the best case and no special is called, therefore the total complexity is (O(N)*O(1)) + O(A_BEST) = 2 O(N) = O(N)

            - Worst case: O(N*M) 
            occurs when regenerating the entire team O(N), and the pokemons' index is towards the end of POKE_LIST, therefore takes O(M) time (linear search).
            assemble the team in the worst case and calling special in the worst case
            Therefore, the total complexity is O(N*M) + O(A_Worst) + O(S_Worst) = O(N*M) + O(Nlog(N)) + O(Nlog(N)) = O(N*M) (as it is the dominating complexity)
        """
        for pokemon_name in self.team_memory:  # O(N) where N is the number of Pokemon in the team
            pokemon_name_index = self.POKE_LIST.index(type(pokemon_name))   # Best case O(1) when the pokemon is at index 0, Worst case O(M) when the pokemon is at the index -1
            pokemon_name.health = self.POKE_HEALTH[pokemon_name_index]      # Updating the Pokemon's health attribute is a constant-time operation (O(1)).

        self.team = self.team_memory                    # O(1)
        self.assemble_team(battle_mode, criterion)      # Best O(N), worst O(Nlog(N))                         

        if self.special_counter % 2 == 1:
            self.special(battle_mode)                   # Best O(N), worst O(Nlog(N))  

    def assign_team(self, criterion: str = None) -> None:
        """ 
        assign the order of the team based on the chosen attribute using list item and array sorted list.         
        
        :param criterion (str): The criterion to be used for arranging the order of the team
        :raises TypeError: If an invalid instance type is provided.
        :post: the array of pokemon will be sorted in ascending order based on the criteria and self.team will become data structure Array Sorted List.
        :complexity: 
        Let N = the total number of pokemon in a team (ArrayR)
        The loop iterates over the team once, therefore the complexity is O(N) and it sorts the team based on the specified criterion.
        Sorting the elements using a binary search has a time complexity of O(log N) in the worst case and O(1) in the best case.

        - Best case: O(N)
        the key of the pokemon added is always equal to the key in the middle of the array [O(N) * 1] = O(N) 
        - Worst case: O(Nlog(N))
        the correct position of the pokemon added is always in the front or back of the array [O(N) * O(log(N))] = O(N log(N)) 
        """
        if isinstance(self.team, ArrayR):
            optimise_assemble_team = ArraySortedList(len(self.team))

            for pokemon in self.team:
                if criterion in PokeTeam.CRITERION_LIST:
                    key = getattr(pokemon, criterion)
                else:
                    raise ValueError("Criteria not match")  

                list_item = ListItem(pokemon, key)
                optimise_assemble_team.add(list_item)

            self.team = optimise_assemble_team

        else:
            raise TypeError("Invalid instance type: the instance should be of type ArrayR.")

    def assemble_team(self, battle_mode: BattleMode, criterion: str = "health") -> None:
        """ 
        Assembles the team according to the specified battle mode and criterion.
        if it is SET battlemode, the pokemon will be push into the stack.
        if it is ROTATE battlemode, the pokemon will be append into the queue.
        if it is OPTIMISE battlemode, assign team is called to arrange the pokemon according to the criterion.

        :param battle_mode (BattleMode): The battle mode to be used for assembling the team.
        :param criterion (str): The criterion to be used for assembling the team.
        :raises ValueError: If an invalid battlemode is provided.
        :raises TypeError: If an invalid instance type is provided.
        :post: self.team will become other data structure such as array stack, circular queue or array sorted list
        :complexity: 
            By considering each battle mode,
            Battle Mode SET (Stack):
            The loop iterates over the arrayr once, O(N) (linear time).
            Pushing each Pokémon onto the stack is a constant-time operation (O(1).
            Best and Worst case: O(N) where n is the number of pokemon

            Battle Mode ROTATE (Circular Queue):
            The loop iterates over the arrayr once, O(N) (linear time).
            Appending each Pokémon to the circular queue is a constant-time operation (O(1)).
            Best and Worst case: O(N) where n is the number of pokemon

            Battle Mode OPTIMISE (ArraySortedList):
            Based on the method assign team:
            The best case is O(N) and the worst case is O(Nlog(N))
        """
        if isinstance(self.team, ArrayR):
            # push all the pokemon into an array stack
            if battle_mode.value == 0:
                set_assemble_team = ArrayStack(self.team_count)
                for pokemon in self.team:
                    set_assemble_team.push(pokemon)
                self.team = set_assemble_team

            # append all the pokemon into a circular queue
            elif battle_mode.value == 1:
                rotate_assemble_team = CircularQueue(self.team_count)
                for pokemon in self.team:
                    rotate_assemble_team.append(pokemon)
                self.team = rotate_assemble_team

            # add the pokemon into an array sorted list using list item  
            elif battle_mode.value == 2:
                self.assign_team(criterion)
            
            else:
                raise ValueError("Invalid battle mode")

        else:
            raise TypeError("Invalid instance type: the instance should be of type ArrayR.")

    def special(self, battle_mode: BattleMode) -> None:
        """ 
        Applies special effects to the team based on the specified battle mode.

        :param battle_mode (BattleMode): The battle mode specifying the type of special to apply.
        :post: the sequence of the pokemon in the data structure will be arrange according to the battlemode.
        :raises TypeError: If an invalid instance type is provided.
        :complexity: 
            Let N = the length of the team
            for each battle mode:
            BattleMode SET:
                In this effect, we use three stacks (s1, s2, and s3) to reverse the upper half of the Pokemon in self.team.
                The loop runs len(self.team) // 2 times. O(N) // 2 = O(N)
                Each stack operation (push, pop) takes constant time.
                Therefore, the best and worst case is O(N).

            BattleMode ROTATE
                In this effect, we use two stacks (s1 and s2) and a circular queue (s3) to reverse the bottom half of the Pokemon in self.team.
                The loop runs len(self.team) // 2 times. O(N) // 2 = O(N)
                Each stack and queue operation takes constant time.
                Therefore, the best and worst case is O(N).
            
            BattleMode OPTIMISE
                In this effect, we create a temporary sorted list (temp_asl) by negating the keys of the Pokemon in self.team.
                The loop runs len(self.team), N times.
                Each operation (delete at index, add) in the sorted list takes logarithmic time.
                Therefore, the worst case is O(N) * log(N).
                if the array sorted list is already correctly sorted, then the sorting is just O(1)
                Therfore, the best case is O(N) * O(1) = O(N)

            In conclusion:
                Best case for special = all battle mode: O(N)
                Worst case for special = BattleMode.OPTIMISE: O(N log(N))
        """
        # This reverse the first half of the team
        if battle_mode.value == 0:
            s1 = self.team
            s2 = ArrayStack(len(self.team))
            s3 = ArrayStack(len(self.team))
            for _ in range(len(self.team) // 2):
                s2.push(s1.pop())
            while len(s2) > 0:
                s3.push(s2.pop())
            while len(s3) > 0:
                s1.push(s3.pop())
            self.special_counter += 1

        # This reverse the bottom half of the team
        elif battle_mode.value == 1:
            s1 = self.team
            s2 = ArrayStack(len(self.team))
            s3 = CircularQueue(len(self.team))
            for _ in range(len(self.team) // 2):
                s3.append(s1.serve())
            while len(s1) > 0:
                s2.push(s1.serve())
            while len(s2) > 0:
                s3.append(s2.pop())
            while len(s3) > 0:
                s1.append(s3.serve())
            self.special_counter += 1

        # This toggles the sorting order (from ascending to descending and vice-versa) by multiplying the key with negative 1 and add it back
        elif battle_mode.value == 2:
            temp_asl = ArraySortedList(len(self.team))
            for _ in range(len(self.team)):
                update_pokemon = self.team.delete_at_index(0)
                update_pokemon.key *= -1
                temp_asl.add(update_pokemon)
            self.team = temp_asl
            self.special_counter += 1

        else:
            raise ValueError("Invalid battle mode")

    def __getitem__(self, index: int) -> Pokemon:
        """ 
        Retrieves a Pokemon at the specified index in the team.

        :param index: The index of the Pokemon to retrieve.
        :type index: int
        :return: The Pokemon at the specified index.
        :rtype: Pokemon
        :raises TypeError: If an invalid instance type is provided.
        :complexity: 
        Let N = the number of Pokemon in the team. 
        - Best Case: O(1)
            If the instance is an ArrayR or ArraySortedList, we directly access the Pokemon at the specified index without any additional loops or operations.
            therefore the access time is constant O(1).
        - Worst Case: O(N)
            In the worst case, we need to perform additional operations to retrieve the Pokemon at the specified index.
            If the instance is an ArrayStack or CircularQueue, we iterate over the team to find the Pokemon at the specified index.
            The loop runs N times.
        """
        if isinstance(self.team, ArrayStack):
            temp_stack = ArrayStack(index)
            for _ in range(index): #O(N)
                temp_stack.push(self.team.pop())
            item = self.team.peek()
            while len(temp_stack) > 0: #O(N)
                self.team.push(temp_stack.pop())

        elif isinstance(self.team, CircularQueue):
            for i in range(len(self.team)): #O(N)
                serve_item = self.team.serve()
                if i == index:
                    item = serve_item
                self.team.append(serve_item)

        elif isinstance (self.team, ArraySortedList):
            item = self.team[index].value #O(1)
        
        elif isinstance (self.team, ArrayR):
            item = self.team[index] #(1)
        
        else:
            raise TypeError("Invalid instance type: the instance should be of type ArrayR, ArrayStack, CircularQueue or ArraySortedList.")

        return item
    
    def __len__(self) -> int:
        """ Returns the number of Pokemon in the team.

        :return: The number of Pokemon in the team.
        :rtype: int
        :complexity: 
        - Best and Worst Case: O(1) - If the instance is an ArrayR, it directly returns the team_count, which is a constant-time operation and
            instance like Array Sorted List, Circular Queue and ArrayStack can directly get the length.
        """
        if isinstance(self.team, ArrayR):
            return self.team_count
        else:
            return len(self.team)

    def __str__(self) -> str:
        """ 
        Returns a string representation of the team.

        :return: A string representation of the team.
        :rtype: str
        :complexity: 
        - Best and Worst Case: O(N) for all instance, where N is the number of Pokemon in the team. 
            The method iterates over the team to create the string representation.
        """
        if isinstance(self.team, ArrayR):
            string = '\n'.join(str(pokemon) for pokemon in self.team) #O(N)

        elif isinstance(self.team, ArrayStack):
            temp_stack = ArrayStack(self.team_count)
            string = ""
            while not self.team.is_empty(): # 0(N)
                pokemon = self.team.pop()
                string += str(pokemon)
                temp_stack.push(pokemon)
                if not self.team.is_empty():
                    string += "\n"
            while not temp_stack.is_empty(): # O(N)
                self.team.push(temp_stack.pop())

        elif isinstance(self.team, CircularQueue):
            string = ""
            queue_length = len(self.team)  # Store the initial length of the queue
            iterations = 0  # Track the number of iterations
            while not iterations == queue_length: #O(N)
                pokemon = self.team.serve()
                string += str(pokemon)
                iterations += 1
                self.team.append(pokemon)
                if iterations < queue_length:
                    string += "\n"

        elif isinstance(self.team, ArraySortedList):
            string = ""
            for i in range(len(self.team)): #O(N)
                string += str(self.team[i].value)
                if i < (len(self.team)-1):
                    string += "\n"
        else:
            raise TypeError("Invalid instance type: the instance should be type of ArrayR, ArrayStack, CircularQueue or ArraySortedList.")

        return string

class Trainer:

    def __init__(self, name) -> None:
        """
        Initializes the Trainer class with a name.

        :param name (str): The name of the trainer.
        :complexity: O(1) - Constant time complexity regardless of the attributes being initialized.
        """
        self.name = name
        self.poke_team = PokeTeam()
        self.pokedex = BSet()

    def pick_team(self, method: str) -> None:
        """
        Picks a team of Pokemon for the trainer.

        :param selection_mode (str): The selection mode for picking the team.
        :complexity: 
        Depends on the method chosen:
        Let B = the complexity of choose_randomly(), where the Best and Worst case is O(N)
        Let W = the complexity of choose_manually(). where the Best case is O(N) and the Worst case is O(N*M)
        Let N = the number of pokemon in a team

        and looping through the team to register the pokemon, the complexity is N, 
        and also considering the register_pokemon() method, where the best and worst case is O(1)
        the overall best and worst case would be
        Best case = O(B_best) + O(N)*O(1) = O(N) + O(N) = O(N)
        Worst case = O(W_worst) + O(N)*O(1) = O(N*M) + O(N) = O(N*M)
        """
        if method.lower() == 'random':
            self.poke_team.choose_randomly()    #Best and worst O(N)
        elif method.lower() == 'manual':
            self.poke_team.choose_manually()    #Best O(N), Worst O(N*M)
        else:
            raise ValueError("Invalid team selection method")
        
        for pokemon in self.poke_team:  #O(N)
            self.register_pokemon(pokemon)


    def get_team(self) -> PokeTeam:
        """ 
        Returns the PokeTeam of the trainer.

        :return: The PokeTeam of the trainer.
        :rtype: PokeTeam
        :complexity: 
            - Best and Worst Case: O(1) - Constant time complexity as it only returns the PokeTeam attribute of the trainer.
        """
        return self.poke_team

    def get_name(self) -> str:
        """ 
        Returns the name of the trainer.

        :return: The name of the trainer.
        :rtype: str
        :complexity: 
            - Best and Worst Case: O(1) - Constant time complexity as it only returns the name attribute of the trainer.
        """
        return self.name

    def register_pokemon(self, pokemon: Pokemon) -> None:
        """ 
        Registers a Pokemon in the trainer's Pokedex.

        :param pokemon (Pokemon): The Pokemon to register.
        :complexity: 
            adding an item to the BSet data structure has an average time complexity of O(1).
            Best and worst case = O(1)
        """
        self.pokedex.add(pokemon.get_poketype().value + 1) # +1 is added as the add method in bset only accept integer greater than 0

    def get_pokedex_completion(self) -> float:
        """ 
        Returns the completion ratio of the trainer's Pokedex.

        :return: The completion ratio of the trainer's Pokedex.
        :rtype: float
        :complexity: 
        - Best Case: O(N)
            To get the length of PokeType is a constant, O(1) because the enumeration maintains an internal count of its members.
            Accessing the length of 'self.pokedex' is more complex as 'self.pokedex' is a BSet, 
            determining its length requires counting the individual elements. We don't know how many elements we've added 
            or removed using cheap bitwise operations, so the complexity is O(N), where N is the number of elements in the set.
            even though BSet it has higher complexity in length compared to ArrayR, but all operations are extremely cheap due to the use of integers.
            O(N) / O(1) = O(N)
        - Worst Case: same as the best case, O(N)
        """
        completion = len(self.pokedex) / len(PokeType)

        return round(completion,2)

    def __str__(self) -> str:
        """ 
        Returns a string representation of the trainer.

        :return: A string representation of the trainer.
        :rtype: str
        :complexity: 
        - Best Case: O(N)
        The call to the method 'self.get_pokedex_completion()' is O(N) due to counting the elements in 'self.pokedex'.
        and the string method involves simple string formatting and arithmetic operations, O(1)
        Therefore, the total complexity is O(N)
        - Worst Case: same as the best case, O(N)
        """
        completion = self.get_pokedex_completion() 
        
        return f"Trainer {self.name} Pokedex Completion: {round(completion * 100)}%"


if __name__ == '__main__':
    t = Trainer('Ash')
    print(t)
    t.pick_team("Random")
    print(t)
    print(t.get_team())
    t.get_team().assemble_team(battle_mode=BattleMode.SET)
    t.get_team().special(battle_mode=BattleMode.SET)
    print(t.get_team())