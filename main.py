import os
import json
import random

run = True
menu = True
play = False
rules = False
safe = True

player = {
  "name": '',
  "HP": 10,
  "MAX_HP": 10,
  "ATK": 2,
  "potions": 1,
  "elixirs": 0,
  "money": 0,
  "x": 0,
  "y": 0,
  "key": False,
  "combat": False,
}

map = [["plains","plains","plains","plains","forest","mountain","cave"],
       ["forest","forest","forest", "forest", "forest", "hills", "mountain"],
       ["forest","fields","bridge", "plains", "hills", "forest", "hills"],
       ["plains","shop","town", "major", "plains", "hills", "mountain"],
       ["plains","fields","fields", "plains", "hills", "mountain", "mountain"]]

x_len = len(map[0])-1
y_len = len(map)-1

biomes =  {
  "plains": {
    "t": "PLAINS",
    "e": True},
  "forest": {
    "t": "WOODS",
    "e": True},
  "fields": {
    "t": "FIELDS",
    "e": False},
  "bridge": {
    "t": "BRIGE",
    "e": True},
  "town": {
    "t": "TOWN CENTRE",
    "e": False},
  "shop": {
    "t": "SHOP",
    "e": False},
  "mayor": {
    "t": "MAYOR",
    "e": False},
  "cave": {
    "t": "CAVE",
    "e": False},
  "mountain": {
    "t": "MOUNTAIN",
    "e": True},
  "hills": {
    "t": "HILLS",
    "e": True,
  }
}

e_list = ["Goblin", "Orc", "Slime"]

mobs = {
  "Goblin": {
    "hp": 5,
    "atk": 1,
    "gold": 8,
    "spawn": 30
  },
  "Orc": {
    "hp": 15,
    "atk": 5,
    "gold": 18,
    "spawn": 10
  },
  "Slime": {
    "hp": 13,
    "atk": 2,
    "gold": 12,
    "spawn": 20,
  },
  "Dragon": {
    "hp": 100,
    "atk": 8,
    "gold": 100,
    "spawn": 100
    }
}

def clear ():
  os.system('cls||clear')

def save():
  list = {}
  for key, value in player.items():
    list[key] = value
  json_object = json.dumps(list, indent=2)
  with open("save.json", "w") as outfile:
    outfile.write(json_object)

def load():
  try:
    with open('save.json', 'r') as openfile:
      json_object = json.load(openfile)
      for key, value in json_object.items():
        player[key] = value
  except OSError:
    print("No save file found. Returning to main menu.")

def draw():
    print("xX--------------------xX")

def battle(enemy, tile):
  global play, menu
  print(mobs[enemy])
  hp = mobs[enemy]["hp"]
  max_hp = mobs[enemy]["hp"]
  atk = mobs[enemy]["atk"]
  gold = mobs[enemy]["gold"]
  defend = False
  usedElixir = False

  while player["combat"]:
    clear()
  
    draw()
    print("A wild " + enemy + " has appeared from the " + tile["t"] + "!")
    draw()
    print(enemy+"'s STATS")
    print(enemy + "'s HP: " + str(hp) + "/" + str(max_hp))
    print(enemy + "'s ATK: " + str(atk))
    draw()
    print(player["name"] + "'s STATS")
    print(player["name"] + "'s HP: " + str(player["HP"]) + "/" + str(player["MAX_HP"]))
    print(player["name"] + "'s ATK: " + str(player["ATK"]))
    print('Available Potions: ' + str(player["potions"]))
    print('Available Elixirs: ' + str(player["elixirs"]))
    draw()
    print("Available actions:")
    print("  1 - Attack")
    print("  2 - Defend")
    if player["potions"] > 0:
      print("  3 - Use Potion (+5 HP)")
    if player["elixirs"] > 0:
      print("  4 - Use Elixir (+1 ATK)")
    print('  5 - Run Away')

    action = input('#> ')
    match action:
      case '1':
        hp -= player["ATK"]
        print(str(player['name']) + ' attacked the ' + enemy + ' for ' + str(player["ATK"]) + ' damage!')
        if usedElixir:
            usedElixir = False
            player["ATK"] -= 1
            print("The Elixer wears off, returning your strength to " + str(player["ATK"]))
      case '2':
        defend = True
        atk -= player["ATK"]
        print(str(player['name']) + ' is defending against the ' + enemy + "'s attacks!")
      case '3':
        if player["potions"] > 0:
          player["potions"] -= 1
          player["HP"] += 5
          print(str(player['name']) + ' used a potion and restored 5 HP!')
      case '4':
        if player["elixirs"] > 0:
          usedElixir = True
          player["elixirs"] -= 1
          player["ATK"] += 1
          print(str(player['name']) + ' used an elixir and gained 1 ATK!')
      case '5':
        player["combat"] = False
    input('> ')
    if hp >= 1:
      # if defending
      #   check if able to damage
      if atk >=1:
        player["HP"] -= atk
      if defend:
        if atk <= 0:
          print("The " + enemy + " tried to attack but recoiled against your defences!")
        else:
          print('The '+ enemy + ' attacked you but onlt dealt ' + str(atk) + ' damage because you were defending!')
        atk = mobs[enemy]["atk"]
        defend = False
      else:
        print('The '+ enemy + ' attacked you for ' + str(atk) + ' damage!')
    else:
      clear()
      print('You have defeated the ' + enemy + '!')
      player["money"] += gold
      player["combat"] = False
      if random.randint(0,100) <= 10:
        print('You found a potion after the battle!')
        player["potions"] += 1
      if random.randint(0,100) <= 5:
        print('You found an elixer after the battle!')
        player["elixirs"] += 1
    if player["HP"] <= 0:
      clear()
      player["combat"] = False
      play = False
      menu = True
      draw()
      print("GAME OVER.\nYou have been defeated by the " + enemy + "!")
      if usedElixir:
        usedElixir = False
        player["ATK"] -= 1
      if defend:
        defend = False
      draw()
    input('> ')
    clear()

while run:
  while menu:
    clear()
    print("1: New Game")
    print("2: Load Game")
    print("3: Rules")
    print("4: Quit/Exit")

    if rules:
      print("I'm the creator and here are my rules MUAHAHAHA")
      rules = False
      choice = ""
      input('> ')
    else:
      choice = input("#> ")

    match choice:
      case "1":
        player["name"] = input("Enter your hero's name: ")
        clear()
        menu = False
        play = True
      case "2":
        load()
        name = player["name"]
        HP = player["HP"]
        ATK = player["ATK"]
        potions = player["potions"]
        elixirs = player["elixirs"]
        money = player["money"]
        print(f"Hero {name} was successfully loaded with HP: {HP} and ATK: {ATK}. They had { potions} potion(s), {elixirs} elixir(s) and {money} coin(s) on them.")
        input('> ')
        clear()
        menu = False
        play = True
      case "3":
        rules = True
      case "4":
        clear()
        quit()

  while play:
    save()
    clear()
    tile = biomes[map[player["y"]][player["x"]]]
    if not safe:
      if tile["e"]:
        selectEnemy = e_list[random.randint(0, len(e_list)-1)]
        encounterCheck = random.randint(0, 100)
        if encounterCheck < mobs[selectEnemy]["spawn"]:
          player["combat"] = True
          battle(selectEnemy, tile)
          save()
    if play:
      draw()
      print("Current location: " + tile['t'])
      draw()

      print("STATS")
      print("  Name - " + player["name"])
      print("  HP - " + str(player["HP"]) + "/" + str(player["MAX_HP"]))
      print("  ATK - " + str(player["ATK"]))
      print("  Potion(s) - " + str(player["potions"]))
      print("  Elixir(s) - " + str(player["elixirs"]))
      print("  Coin(s) - " + str(player["money"]))
      draw()

      print("Available actions:")
      if player["y"] > 0:
        print("  1 - Move North")
      if player["x"] < x_len:
        print("  2 - Move East")
      if player["y"] < y_len:
        print("  3 - Move South")
      if player["x"] > 0:
        print("  4 - Move West")
      if player["potions"] > 0:
        print("  5 - Use Potion")
      print("  quit - Quit")
      draw()
      dest = input("\n#> ")
      match dest:
        case "quit":
          play = False
          menu = True
          save()
        case "1":
          if player["y"] > 0:
            player["y"] -= 1
            safe = False
          else :
            print("You can't go that way")
        case "2":
          if player["x"] < x_len:
            player["x"] += 1
            safe = False
          else:
            print("You can't go that way")
        case "3":
          if player["y"] < y_len:
            player["y"] += 1
            safe = False
          else:
            print("You can't go that way")
        case "4":
          if player["x"] > 0:
            player["x"] -= 1
            safe = False
          else:
            print("You can't go that way")
        case "5":
          safe = True
          if player["potions"] > 0:
            player["potions"] -= 1
            player["HP"] += 5
            if player["HP"] > player["MAX_HP"]:
              player["HP"] = player["MAX_HP"]
            print("You used a potion and restored 5 HP!")
          else:
            print("You don't have any potions left!")
        case _:
          safe = True