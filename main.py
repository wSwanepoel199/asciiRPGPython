print(__name__)
import random, tcod, copy
import src.factory.actor_factory as actor_factory
from src.engine import Engine
from src.map import Map, GameMap
# from src.player import Player
from src.entity import Entity
from src.combat import Combat
from src.menu import Menu
from src.save import Save
from src.game import Game
from src.procgen import genDungeon

initialLoad = True

# def runGame() -> None:
#   global initialLoad
#   game = Game()
#   player = Entity()
#   menu = Menu()
#   map = Map()

#   while game.run:
#     while menu.mainmenu:
#       game.clear()
#       player = menu.mainMenu(player=player, game=game)

#     while game.play:
#       Save().save(player=player)
#       game.clear()
#       tile = map.biomes[map.map[player["y"]][player["x"]]]
#       if not player.safe or not initialLoad:
#         if tile["e"]:
#           selectEnemy = enemy_stats.items()[random.randint(a=0, b=len(enemy_stats)-1)]
#           encounterCheck = random.randint(a=0, b=100)
#           if encounterCheck < enemy_stats[selectEnemy]["spawn"]:
#             player["combat"] = True
#             combat = Combat(target=selectEnemy)
#             game.play = combat.battle(player=player)
#             menu.mainmenu = not game.play
#             Save().save(player=player)
#             game.clear()
#       initialLoad = False
#       if game.play:
#         match player.location:
#           case "TOWN":
#             map.town(player=player)
#           case "SHOP":
#             map.shop(player=player)
#           case "MAYOR":
#             map.mayor(player=player)
#           case "CAVE":
#             map.cave(player=player)
#           case "BOSS":
#             combat = Combat(target="Dragon")
#             game.play = combat.battle(player=player)
#             menu.mainmenu = not game.play
#             if game.play:
#               player.location = "CAVE"
#             Save().save(player=player)
#             game.clear()
#           case _:
#             game.play = map.overworld(player=player, tile=tile)
#             menu.mainmenu = not game.play
def main():
  screen_width = 80
  screen_height = 60

  map_width = 80
  map_height = 60

  room_size_min = 6
  room_size_max = 10
  max_rooms = 30

  room_max_enemy = 2
  room_max_item = 2

  player = copy.deepcopy(actor_factory.player)

  engine = Engine(player=player)

  engine.createConsole(width=screen_width, height=screen_height, tileset_image="./src/assets/dejavu10x10_gs_tc.png", tileset_width=32, tileset_height=8)

  # game_map = GameMap(width=80, height=45)
  squareMapDimMin = min(map_width, map_height)
  # squareMapDimMax = max(map_width, map_height)
  # mapDiff = round(abs((map_width - map_height))/2)
  engine.game_map = genDungeon(
    x=0,
    y=0,
    w=squareMapDimMin,
    h=squareMapDimMin,
    min=room_size_min,
    max=room_size_max,
    room_limit=max_rooms,
    max_enemy_per_room=room_max_enemy,
    max_item_per_room=room_max_item,
    engine=engine,
  )
  engine.update_fov()
  engine.message_log.add_message(
    text="Hello and welcome, adventurer, to yet another dungeon!",
    fg=engine.colours['welcome_text']
  )

  while True:
    engine.console.clear()
    # engine.render()
    engine.event_handler.on_render()
    engine.context.present(console=engine.console)
    engine.event_handler.handle_events(context=engine.context)

if __name__ == "__main__":
  main()