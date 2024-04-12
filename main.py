print(__name__)
import os, random
from src import player, enemy, map, save
from src.combat import battle
from src.menu import mainMenu

run = True
play = False
safe = True
rules = False
menu_open = True

x_len = len(map.map[0])-1
y_len = len(map.map)-1

def clear():
  os.system('cls||clear')
def draw():
  print("xX--------------------xX")

def runGame():
  global run, menu_open, play, safe
  while run:
    while menu_open:
      mainMenu()

    while play:
      print()
      save.save()
      clear()
      tile = map.biomes[map.map[player.player["y"]][player.player["x"]]]
      if not safe:
        if tile["e"]:
          selectEnemy = enemy.e_list[random.randint(0, len(enemy.e_list)-1)]
          encounterCheck = random.randint(0, 100)
          if encounterCheck < enemy.mobs[selectEnemy]["spawn"]:
            player.player["combat"] = True
            battle(selectEnemy, tile)
            save.save()
      if play:
        draw()
        print("Current location: " + tile['t'])
        draw()

        print("STATS")
        print("  Name - " + player.player["name"])
        print("  HP - " + str(player.player["HP"]) + "/" + str(player.player["MAX_HP"]))
        print("  ATK - " + str(player.player["ATK"]))
        print("  Potion(s) - " + str(player.player["potions"]))
        print("  Elixir(s) - " + str(player.player["elixirs"]))
        print("  Coin(s) - " + str(player.player["money"]))
        draw()

        print("Available actions:")
        if player.player["y"] > 0:
          print("  1 - Move North")
        if player.player["x"] < x_len:
          print("  2 - Move East")
        if player.player["y"] < y_len:
          print("  3 - Move South")
        if player.player["x"] > 0:
          print("  4 - Move West")
        if player.player["potions"] > 0:
          print("  5 - Use Potion")
        print("  quit - Quit")
        draw()
        dest = input("\n#> ")
        match dest:
          case "quit":
            play = False
            menu_open = True
            save.save()
          case "1":
            if player.player["y"] > 0:
              player.player["y"] -= 1
              safe = False
            else :
              print("You can't go that way")
          case "2":
            if player.player["x"] < x_len:
              player.player["x"] += 1
              safe = False
            else:
              print("You can't go that way")
          case "3":
            if player.player["y"] < y_len:
              player.player["y"] += 1
              safe = False
            else:
              print("You can't go that way")
          case "4":
            if player.player["x"] > 0:
              player.player["x"] -= 1
              safe = False
            else:
              print("You can't go that way")
          case "5":
            safe = True
            if player.player["potions"] > 0:
              player.player["potions"] -= 1
              player.player["HP"] += 5
              if player.player["HP"] > player.player["MAX_HP"]:
                player.player["HP"] = player.player["MAX_HP"]
              print("You used a potion and restored 5 HP!")
            else:
              print("You don't have any potions left!")
          case _:
            safe = True

runGame()