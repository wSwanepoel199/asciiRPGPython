print(__name__)
import random
from src import enemy
from src.map import Map
from src.player import Player
from src.combat import Combat
from src.menu import Menu
from src.save import Save
from src.game import Game

def runGame():
  game = Game()
  player = Player("", 10, 2, 1, 0, 0, 0, 0, False, False)
  menu = Menu()
  map = Map()

  while game.run:
    while menu.mainmenu:
      game.clear()
      menu.mainMenu(player, game)

    while game.play:
      Save().save(player)
      game.clear()
      tile = map.biomes[map.map[player["y"]][player["x"]]]
      if not game.safe:
        if tile["e"]:
          selectEnemy = enemy.enemy_list[random.randint(0, len(enemy.enemy_list)-1)]
          encounterCheck = random.randint(0, 100)
          if encounterCheck < enemy.enemy_stats[selectEnemy]["spawn"]:
            player["combat"] = True
            combat = Combat(selectEnemy)
            game.play =combat.battle(player, tile, game)
            menu.mainmenu = not game.play
            Save().save(player)
      if game.play:
        game.draw()
        print("Current location: " + tile['t'])
        game.draw()

        print("STATS")
        print("  Name - " + player["name"])
        print("  HP - " + str(player["HP"]) + "/" + str(player["MAX_HP"]))
        print("  ATK - " + str(player["ATK"]))
        print("  Potion(s) - " + str(player["potions"]))
        print("  Elixir(s) - " + str(player["elixirs"]))
        print("  Coin(s) - " + str(player["money"]))
        game.draw()

        print("Available actions:")
        if player["y"] > 0:
          print("  1 - Move North")
        if player["x"] < map.x_len:
          print("  2 - Move East")
        if player["y"] < map.y_len:
          print("  3 - Move South")
        if player["x"] > 0:
          print("  4 - Move West")
        if player["potions"] > 0:
          print("  5 - Use Potion")
        print("  quit - Quit")
        game.draw()
        dest = input("\n#> ")
        match dest:
          case "quit":
            game.play = False
            menu.mainmenu = True
            Save().save(player)
          case "1":
            if player["y"] > 0:
              player["y"] -= 1
              game.safe = False
            else :
              print("You can't go that way")
          case "2":
            if player["x"] < map.x_len:
              player["x"] += 1
              game.safe = False
            else:
              print("You can't go that way")
          case "3":
            if player["y"] < map.y_len:
              player["y"] += 1
              game.safe = False
            else:
              print("You can't go that way")
          case "4":
            if player["x"] > 0:
              player["x"] -= 1
              game.safe = False
            else:
              print("You can't go that way")
          case "5":
            game.safe = True
            player.heal()
          case _:
            game.safe = True


if __name__ == "__main__":
  runGame()