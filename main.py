# print(__name__)
# ‎
from unittest import skip
import tcod
import traceback
import os
import sys
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
import src.assets.load_asset as load_asset


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
    resolution169 = [16, 9]
    resolution425 = [4, 2.5]
    width = 800
    height = round(width // resolution169[0] * resolution169[1])
    columns = 80
    rows = round(columns // resolution425[0] * resolution425[1])
    FLAGS = tcod.context.SDL_WINDOW_RESIZABLE
    # | tcod.context.SDL_WINDOW_MAXIMIZED

    tileset = tcod.tileset.load_tilesheet(
        path=load_asset.cheepicus_15x15,
        columns=16, rows=16,
        charmap=tcod.tileset.CHARMAP_CP437
    )

    title = "Rogue But Worse"

    with tcod.context.new(
        width=width,
        height=height,
        tileset=tileset,
        title=title,
        sdl_window_flags=FLAGS
    ) as context:

        handler: event_handler.BaseEventHandler = game_setup.MainMenu(
            columns=columns, rows=rows)

        skip_once = True
        try:
            while True:
                console = context.new_console(
                    *context.recommended_console_size(),
                    order="F")
                console.clear()
                # if hasattr(handler, 'process') and handler.process and handler.process.is_alive():
                #     print("alive")
                if isinstance(handler, event_handler.EventHandler):
                    handler.engine.event_handler = handler
                    handler.engine.context = context
                    handler.engine.console = console

                handler.on_render(console=console)
                context.present(console=console, integer_scaling=True)
                # if hasattr(handler, 'process') and handler.process and not hasattr(handler.engine, 'game_map'):
                #     if handler.process.is_alive():
                #         continue

                #     # tcod.event.Event(
                #     #     type="PROCESS_END"
                #     # )
                #     # handler.process.join()
                #     continue
                try:
                    if (hasattr(handler, 'thread') and handler.thread) and not (hasattr(handler.engine, 'game_map') and handler.engine.game_map):
                        if not handler.map_check():
                            continue
                    # if not hasattr(handler.engine, 'game_map'):
                    #     continue
                    # print(handler.process.map)
                    # if skip_once:
                    #     skip_once = False
                    #     continue
                    for event in tcod.event.get():
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
