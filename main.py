print(__name__)
# ‎ 
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
  """If the current event handler has an active Engine then save it."""
  if isinstance(handler, event_handler.EventHandler):
    handler.engine.save_as(filename=filename)
    print("Game saved.")

def main():
  resolution169 = [16,9]
  resolution425 = [4,2.5]
  width = 1600
  height = round(width // resolution169[0] * resolution169[1])
  columns = 80
  rows= round(columns // resolution425[0] * resolution425[1])
  FLAGS = tcod.context.SDL_WINDOW_RESIZABLE
  # | tcod.context.SDL_WINDOW_MAXIMIZED
  

  tileset = tcod.tileset.load_tilesheet(
    # path="./src/assets/dejavu10x10_gs_tc.png",
    # path="./src/assets/rexpaint_cp437_10x10.png",
    path="./src/assets/Cheepicus_15x15.png",
    # path="./src/assets/Aesomatica_16x16.png",
    # path="./src/assets/Runeset_24x24.png",
    columns=16, rows=16,
    charmap=tcod.tileset.CHARMAP_CP437
  )
  title = "Rogue But Worse"
  tcod.tileset.procedural_block_elements(tileset=tileset)
  # context: tcod.context.Context = Engine().genContext(
  #   width= width,
  #   height= height,
  #   columns= columns,
  #   rows= rows,
  #   tileset=tileset,
  #   title=title,
  #   vsync=True,
  # )
  # context.recommended_console_size()


  with tcod.context.new(
    width=width,
    height=height,
    tileset=tileset,
    title=title,
    sdl_window_flags=FLAGS
  ) as context:
    consoleSize = context.recommended_console_size()
    handler: event_handler.BaseEventHandler = game_setup.MainMenu(columns=columns-2, rows=rows)
    # console = context.new_console(
    #   min_columns=columns, 
    #   min_rows=rows, 
    #   order="F"
    # )
    try:
      while True:
        console = context.new_console(
          *context.recommended_console_size(), 
          1, 
          "F")
        console.clear()
        if isinstance(handler, event_handler.EventHandler):
          handler.engine.event_handler = handler
          handler.engine.context = context
          handler.engine.console = console
          # handler.engine.game_map.width = console.width-min((console.width // 4), 55)
          # handler.engine.game_map.height = console.height
          # handler.engine.game_map.console = context.new_console(
          #   *context.recommended_console_size(),
          #   order='F'
          # )
          # handler.engine.game_map.width = console.width
          # handler.engine.game_map.height = console.height-2

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
      context.close()
      pass
    except SystemExit as exc:
      save_game(handler=handler, filename="savegame.sav")
      raise
    except BaseException:
      save_game(handler=handler, filename="savegame.sav")
      raise

if __name__ == "__main__":
  main()