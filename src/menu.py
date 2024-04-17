from src.save import Save
from src.entity import Entity

print(__name__)

class Menu:
  def __init__(self):
    self.mainmenu = True
    self.rules = False
    self.choice = ''

  def __str__(self):
    return f"{self.__dict__}"

  def __setitem__(self, key, value):
        setattr(self, key, value)

  def __getitem__(self, key):
    return getattr(self, key)

  def mainMenu(self, player, game):

    print("1: New Game")
    print("2: Load Game")
    print("3: Rules")
    print("4: Quit/Exit")

    if self.rules:
      print("I'm the creator and here are my rules MUAHAHAHA")
      self.rules = False
      self.choice = ""
      input('> ')
    else:
      self.choice = input("#> ")

    match self.choice:
      case "1":
        # player = Player("", 50, 3, 1, 0, 0, 0, 0, False, False)
        name = input("Enter your hero's name: ")

        player = Entity({
          "enitityType": "PLAYER",
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
        Save().load(player)
        print("Hero " + player["name"] + " was successfully loaded with HP: "+str(player["HP"])+" and ATK: "+str(player["ATK"])+". They had "+str(player["potions"])+" potion(s), "+ str(player["elixirs"])+" elixir(s) and "+str(player["money"])+" coin(s) on them.")
        input('> ')
        self.mainmenu = False
        game['play'] = True
        return player
      case "3":
        self.rules = True
      case "4":
        quit()
