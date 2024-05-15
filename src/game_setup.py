"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import tcod
import lzma
import pickle
import traceback
import tcod.constants
from typing import Optional

import src.factory.actor_factory as actor_factory
import src.factory.item_factory as item_factory
import src.event_handler as event_handler
import src.assets.load_asset as load_asset
from src.engine import Engine
from src.map import GameWorld
from src.utils.colour import loadColours


def new_game(
    title: str,
    width: int,
    height: int,
    map_max_rooms: int,
    room_min_size: int,
    room_max_size: int,
) -> None:
    """Start a new game."""

    room_size_min = room_min_size
    room_size_max = room_max_size
    max_rooms = map_max_rooms
    player = copy.deepcopy(actor_factory.player)

    engine = Engine(player=player)

    engine.title = title

    engine.game_world = GameWorld(
        engine=engine,
        viewport_width=width,
        viewport_height=height,
        room_limit=max_rooms,
        min_room_size=room_size_min,
        max_room_size=room_size_max,
    )

    # engine.game_world.gen_floor()

    # engine.update_fov()

    engine.message_log.add_message(
        text="Hello and welcome, adventurer, to yet another dungeon!",
        fg=engine.colours['welcome_text']
    )

    # dagger = copy.deepcopy(item_factory.dagger)
    # leather_armor = copy.deepcopy(item_factory.leather_armour)

    # dagger.parent = player.inventory
    # leather_armor.parent = player.inventory

    # player.inventory.items.append(dagger)
    # player.equipment.toggle_equip(equippable_item=dagger, add_message=False)

    # player.inventory.items.append(leather_armor)
    # player.equipment.toggle_equip(equippable_item=leather_armor, add_message=False)

    return engine


def load_game(filename: str) -> Engine:
    with open(file=filename, mode="rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(event_handler.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def __init__(self, columns: int, rows: int) -> None:
        self.columns = columns
        self.rows = rows
        self.engine = None

    def on_render(self, console: tcod.console.Console) -> Optional[event_handler.BaseEventHandler]:
        # console = self.engine.console
        self.console = console
        self.colours = loadColours()
        image = tcod.image.Image(
            width=console.width,
            height=console.height,
        ).from_file(load_asset.menu_background)
        image.scale(width=console.width*2, height=console.height*2)

        console.draw_semigraphics(pixels=image, x=0, y=0)
        title = "Rogue But Worse"
        console.print(
            x=console.width // 2,
            y=console.height // 2 - 4,
            string=title,
            fg=self.colours['menu_title'],
            alignment=tcod.constants.CENTER,
        )
        console.print(
            x=console.width // 2,
            y=console.height - 2,
            string="By wSwanepoel",
            fg=self.colours['menu_title'],
            alignment=tcod.constants.CENTER
        )
        if len(title) > 10:
            menu_width = len(title)
        else:
            menu_width = 10

        for i, text in enumerate(
            ["[N]ew game", "[C]ontinue", "[Q]uit"]
        ):
            console.print(
                x=console.width // 2,
                y=console.height // 2 - 2 + i*2,
                string=text.ljust(menu_width),
                fg=self.colours['menu_title'],
                bg=self.colours['black'],
                alignment=tcod.constants.CENTER,
                bg_blend=tcod.constants.BKGND_ALPH
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[event_handler.BaseEventHandler]:
        match event.sym:
            case tcod.event.KeySym.n:

                return event_handler.MainGameEventHandler(engine=new_game(
                    title="Rogue But Worse",
                    width=self.console.width -
                    min((self.console.width // 3), 55),
                    height=self.console.height,
                    map_max_rooms=30,
                    room_min_size=6,
                    room_max_size=10,
                ))
            case tcod.event.KeySym.c:
                try:
                    # create a load game handler that is called instead if main game
                    # handler needs to mimic resize event functionality
                    # then call the on render function once engine has been setup for new instance
                    return event_handler.MainGameEventHandler(engine=load_game(filename="savegame.sav"))
                except FileNotFoundError:
                    return event_handler.PopupMessage(parent=self, text="No saved game to load.")
                except Exception as exc:
                    traceback.print_exc()
                    return event_handler.PopupMessage(parent=self, text=f"Failed to load save:\n{exc}")
            case tcod.event.KeySym.q:
                raise SystemExit()
            case tcod.event.KeySym.ESCAPE:
                raise SystemExit()
            case _:
                return None
