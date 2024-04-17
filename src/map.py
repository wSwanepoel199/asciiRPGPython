from src.game import Game
from src.save import Save
class Map:
  def __init__(self, ):
    self.map = [
      ["P","P","P","P","F","M","C"],
      ["F","F","F", "F", "F", "H", "M"],
      ["F","Fl","B", "P", "H", "F", "H"],
      ["P","Fl","T", "Fl", "P", "H", "M"],
      ["P","Fl","Fl", "P", "H", "M", "M"]
    ]
    self.biomes = {
      "P": {
        "t": "PLAINS",
        "e": True},
      "F": {
        "t": "WOODS",
        "e": True},
      "Fl": {
        "t": "FIELDS",
        "e": False},
      "B": {
        "t": "BRIGE",
        "e": True},
      "T": {
        "t": "TOWN",
        "e": False},
      "S": {
        "t": "SHOP",
        "e": False},
      "Ma": {
        "t": "MAYOR",
        "e": False},
      "C": {
        "t": "CAVE",
        "e": False},
      "M": {
        "t": "MOUNTAIN",
        "e": True},
      "H": {
        "t": "HILLS",
        "e": True,
      }
    }
    self.x_len = len(self.map[0])-1
    self.y_len = len(self.map)-1
    self.boss = False

  def __str__(self):
    return f"{self.__dict__}"
  
  def __setitem__(self, key, value):
    setattr(self, key, value)

  def __getitem__(self, key):
    return getattr(self, key)
  
  def overworld(self, player, tile):
    Game().draw()
    print("Current location: " + tile['t'])
    Game().draw()

    print("STATS")
    print("  Name - " + player["name"])
    print("  HP - " + str(player["HP"]) + "/" + str(player["MAX_HP"]))
    print("  ATK - " + str(player["ATK"]))
    print("  Potion(s) - " + str(player["potions"]))
    print("  Elixir(s) - " + str(player["elixirs"]))
    print("  Coin(s) - " + str(player["money"]))
    Game().draw()
    print("Available actions:")
    if player["y"] > 0:
      print("  1 - Move North")
    if player["x"] < self.x_len:
      print("  2 - Move East")
    if player["y"] < self.y_len:
      print("  3 - Move South")
    if player["x"] > 0:
      print("  4 - Move West")
    if player["potions"] > 0:
      print("  5 - Use Potion")
    if tile["t"] == "TOWN":
      print('  6 - Enter Town')
    if tile["t"] == "CAVE":
      print('  6 - Enter Cave')
    print('  quit - Exit Game')
    Game().draw()

    choice = input("#> ")

    match choice:
      case 'quit':
        Save().save(player)
        return False
      case "1":
        if player["y"] > 0:
          player["y"] -= 1
          player.safe = False
        else :
          print("You can't go that way")
      case "2":
        if player["x"] < self.x_len:
          player["x"] += 1
          player.safe = False
        else:
          print("You can't go that way")
      case "3":
        if player["y"] < self.y_len:
          player["y"] += 1
          player.safe = False
        else:
          print("You can't go that way")
      case "4":
        if player["x"] > 0:
          player["x"] -= 1
          player.safe = False
        else:
          print("You can't go that way")
      case "5":
        player.safe = True
        player.heal(player)
      case "6":
        if tile["t"] == "TOWN":
          player.location = "TOWN"
        if tile['t'] == "CAVE":
          player.location = "CAVE"
      case _:
        player.safe = True
    return True

  def town(self, player):
    print("Town")
    while player.location == "TOWN":
      Game().clear()
      Game().draw()
      print("Welcome to the Town!")
      Game().draw()
      print("STATS")
      print("  Name - " + player["name"])
      print("  HP - " + str(player["HP"]) + "/" + str(player["MAX_HP"]))
      print("  ATK - " + str(player["ATK"]))
      print("  Potion(s) - " + str(player["potions"]))
      print("  Elixir(s) - " + str(player["elixirs"]))
      print("  Coin(s) - " + str(player["money"]))
      Game().draw()
      print("Available actions:")
      print('  1 - Go Shopping')
      print('  2 - Talk to Mayor')
      print('  3 - Leave Town')
      Game().draw()
      choice = input("#> ")

      match choice:
        case "1":
          player.location = "SHOP"
          print("You enter the local Store")
        case "2":
          player.location = "MAYOR"
          print('You go to the mayor')
        case "3":
          player.location = "OVERWORLD"
          print("You leave town to go exploring")
        case _:
          pass
      input("> ")

  def shop(self, player):
    print("Shop")
    while player.location == "SHOP":
      Game().clear()
      Game().draw()
      print("Welcome to the shop!")
      Game().draw()
      print("INVENTORY:")
      print("  Potions: " + str(player.potions))
      print("  Elixirs: " + str(player.elixirs))
      print("  ATK: " + str(player.ATK))
      print("  Gold: " + str(player.money))
      Game().draw()
      print("Available actions:")
      print("  1 - Buy Potion (+30 HP) - 5 Gold")
      print("  2 - Buy Elixir (+1 ATK) - 8 Gold")
      print("  3 - Upgrade Weapon (+2 ATK) - 10 Gold")
      print("  4 - Exit Shop")
      Game().draw()
      choice = input("#> ")

      match choice:
        case "1":
          if player.money >= 5:
            player.money -= 5
            player.potions += 1
            print("You bought a potion!")
          else:
            print("You don't have enough gold!")
        case "2":
          if player.money >= 8:
            player.money -= 8
            player.elixirs += 1
            print("You bought an elixir!")
          else:
            print("You don't have enough gold!")
        case "3":
          if player.money >= 10:
            player.ATK += 2
            player.money -= 10
            print("You improved your weapon!")
          else:
            print("You don't have enough gold!")
        case "4":
          player.location = "TOWN"
        case _:
          pass
      input("> ")


  def mayor(self, player):
    print("Mayor")
    while player.location == "MAYOR":
        Game().clear()
        Game().draw()
        print("Hello there, " + player.name + "!")
        if player.ATK < 10:
          print("You don't look strong enough to face the dragon! Come back once you've grown stronger!")
        else:
          print("You look like you might stand a chance against the dragon! Take this key and go to the cave far north east from here. But be on your guard that beast is dangerious!")
          player.key = True
        Game().draw()
        print("Available actions:")
        print("  1 - Return to the Town")
        Game().draw()

        choice = input("# ")

        if choice == "1":
          player.location = "TOWN"

  def cave(self, player):
    print("Cave")
    while  player.location == 'CAVE':
      Game().clear()
      Game().draw()
      print("Here be Dragons! Unseal the beast to claim its life?")
      Game().draw()
      print("Available actions:")
      if player.key:
        print("  1 - Use key to unseal the Dragon")
        print('  2 - Leave the Cave')
      else:
        print('  1 - Leave the Cave')
      Game().draw()
      choice = input("#> ")

      match choice:
        case "1":
          if player.key:
            print("You unseal the Dragon! Prepare for a FIGHT...")
            player.combat = True
            player.location = "BOSS"
          else:
            player.location = "OVERWORLD"
            print("You decide to leave the Dragon to its sealed slumber!")
        case "2":
          player.location = "OVERWORLD"
          print("You decide to leave the Dragon to its sealed slumber!")
        case _:
          pass
      input("> ")