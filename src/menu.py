from src.save import Save
from src.entity import Entity

class Menu:
  def __init__(self) -> None:
    self.mainmenu = True
    self.rules = False
    self.choice = ''

  def __str__(self) -> str:
    return f"{self.__dict__}"

  def __setitem__(self, key, value) -> None:
        setattr(self, key, value)

  def __getitem__(self, key):# -> Any:
    return getattr(self, key)

  def mainMenu(self, player, game) -> Entity | None:

    print("1: New Game")
    print("2: Load Game")
    print("3: Rules")
    print("4: Quit/Exit")

    if self.rules:
      print("I'm the creator and here are my rules MUHAHAHAHA")
      self.rules = False
      self.choice = ""
      input(prompt='> ')
    else:
      self.choice = input(prompt="#> ")

    match self.choice:
      case "1":
        # player = Player("", 50, 3, 1, 0, 0, 0, 0, False, False)
        name = input(prompt="Enter your hero's name: ")

        player = Entity(args={
          "entityType": "PLAYER",
          'icon': "@",
          "name": name,
          "HP": 50,
          "ATK": 3,
          'inventory':{
            "potions": 1,
            "elixirs": 0,
          },
          "money": 0
        })
        self.mainmenu = False
        game['play'] = True
        return player

      case "2":
        player = Entity()
        Save().load(player=player)
        print("Hero " + player["name"] + " was successfully loaded with HP: "+str(object=player["HP"])+" and ATK: "+str(object=player["ATK"])+". They had "+str(object=player["potions"])+" potion(s), "+ str(object=player["elixirs"])+" elixir(s) and "+str(object=player["money"])+" coin(s) on them.")
        input(prompt='> ')
        self.mainmenu = False
        game['play'] = True
        return player
      case "3":
        self.rules = True
      case "4":
        quit()
