print(__name__)
import tcod, traceback
# from src.map import Map, GameMap
# from src.player import Player
# from src.entity import Entity
# from src.combat import Combat
# from src.menu import Menu
# from src.save import Save
# from src.game import Game
import src.event_handler as event_handler
import src.game_setup as game_setup
import src.utils.exceptions as exceptions
from src.engine import Engine
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

def save_game(handler: event_handler.BaseEventHandler, filename: str) -> None:
  if isinstance(handler, event_handler.EventHandler):
    handler.engine.save_as(filename=filename)
    print("Game saved.")

def main():
  resolution = [4,2.5]
  # resolution = [16,9]
  width = 160
  height = round(width // resolution[0] * resolution[1])

  # engine = 

  tileset = tcod.tileset.load_tilesheet(
    path="./src/assets/dejavu10x10_gs_tc.png",
    columns=32, rows=8,
    charmap=tcod.tileset.CHARMAP_TCOD
  )
  title = "Rogue But Worse"

  console: tcod.console.Console = Engine().genConsole(width=width, height=height)
  context: tcod.context.Context = Engine().genContext(
    width=console.width, 
    height=console.height,
    tileset=tileset,
    title=title,
    vsync=True
  )
  handler: event_handler.BaseEventHandler = game_setup.MainMenu()
  
  try:
    while True:
      console.clear()
      handler.on_render(console=console)
      context.present(console=console)

      try:
        for event in tcod.event.wait():
          context.convert_event(event=event)
          handler = handler.handle_events(event=event)
      except Exception:
        traceback.print_exc()
        if isinstance(handler, event_handler.EventHandler):
          handler.engine.message_log.add_message(
            text=traceback.format_exc(), 
            fg=handler.engine.colours['error']
          )
  except exceptions.QuitWithoutSaving:
    raise
  except SystemExit:
    save_game(handler=handler, filename="savegame.sav")
    raise
  except BaseException:
    save_game(handler=handler, filename="savegame.sav")
    raise

if __name__ == "__main__":
  main()