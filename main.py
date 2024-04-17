print(__name__)
import random
from src import window
from src.map import Map
# from src.player import Player
from src.entity import Entity, enemy_stats
from src.combat import Combat
from src.menu import Menu
from src.save import Save
from src.game import Game

initialLoad = True

def runGame() -> None:
  global initialLoad
  game = Game()
  player = Entity()
  menu = Menu()
  map = Map()

  while game.run:
    while menu.mainmenu:
      game.clear()
      player = menu.mainMenu(player=player, game=game)

    while game.play:
      Save().save(player=player)
      game.clear()
      tile = map.biomes[map.map[player["y"]][player["x"]]]
      if not player.safe or not initialLoad:
        if tile["e"]:
          selectEnemy = enemy_stats.items()[random.randint(a=0, b=len(enemy_stats)-1)]
          encounterCheck = random.randint(a=0, b=100)
          if encounterCheck < enemy_stats[selectEnemy]["spawn"]:
            player["combat"] = True
            combat = Combat(target=selectEnemy)
            game.play = combat.battle(player=player)
            menu.mainmenu = not game.play
            Save().save(player=player)
            game.clear()
      initialLoad = False
      if game.play:
        match player.location:
          case "TOWN":
            map.town(player=player)
          case "SHOP":
            map.shop(player=player)
          case "MAYOR":
            map.mayor(player=player)
          case "CAVE":
            map.cave(player=player)
          case "BOSS":
            combat = Combat(target="Dragon")
            game.play = combat.battle(player=player)
            menu.mainmenu = not game.play
            if game.play:
              player.location = "CAVE"
            Save().save(player=player)
            game.clear()
          case _:
            game.play = map.overworld(player=player, tile=tile)
            menu.mainmenu = not game.play


if __name__ == "__main__":
  # runGame()
  window.screen()