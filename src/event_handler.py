from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Callable, Tuple, Union

import tcod
import os
import time
import tcod.constants
import multiprocessing as mp
import threading as mt

from src import engine
import src.actions as action
import src.utils.constants as constants

if TYPE_CHECKING:
    from src.engine import Engine
    from src.entity import Item, Actor

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
    # Vi keys.
    tcod.event.KeySym.h: (-1, 0),
    tcod.event.KeySym.j: (0, 1),
    tcod.event.KeySym.k: (0, -1),
    tcod.event.KeySym.l: (1, 0),
    tcod.event.KeySym.y: (-1, -1),
    tcod.event.KeySym.u: (1, -1),
    tcod.event.KeySym.b: (-1, 1),
    tcod.event.KeySym.n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER,
}

CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}

ActionOrHandler = Union[action.Action, "BaseEventHandler"]


class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def __init__(self):
        self.console = None,
        self.colours = None,

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        state = self.dispatch(event=event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(
            state, action.Action), f"{self!r} can not handle actions."
        return self

    def ev_windowresized(self, event: tcod.event.WindowResized):
        return self

    def on_render(self, console: tcod.console.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[action.Action]:
        raise SystemExit()


class PopupMessage(BaseEventHandler):
    def __init__(self, parent: BaseEventHandler, text: str) -> None:
        self.parent = parent
        self.text = text

    def on_render(self, console: tcod.console.Console) -> None:
        self.parent.on_render(console=console)
        console.rgb["fg"]
        console.rgb['bg']

        console.print(
            x=console.width//2,
            y=console.height//2,
            string=self.text,
            fg=self.parent.colours['white'],
            bg=self.parent.colours['black'],
            alignment=tcod.constants.CENTER
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        return self.parent


class LoadingHandler(BaseEventHandler):
    def __init__(self, parent: BaseEventHandler, process: Optional[mp.Process], queue: Optional[mp.Queue], text: str) -> None:
        self.parent = parent
        self.process = process
        self.queue = queue
        self.text = text

    def on_render(self, console: tcod.console.Console) -> Optional[BaseEventHandler]:

        self.parent.on_render(console=console)
        console.rgb["fg"]
        console.rgb['bg']

        console.print(
            x=console.width//2,
            y=console.height//2,
            string=self.text,
            fg=self.parent.colours['white'],
            bg=self.parent.colours['black'],
            alignment=tcod.constants.CENTER
        )

        if self.process.is_alive():
            print("Loading...")
            # self.process.join()
        if not self.queue.empty():
            print("engine loaded")

    def on_load(self) -> Optional[BaseEventHandler]:
        if not self.queue.empty() and self.process.is_alive():
            engine = self.queue.get()
            print(engine, "loaded")
            self.process.join()
            print(self.process.is_alive())
            return MainGameEventHandler(engine=engine)

            # MainGameEventHandler(engine=engine)
        else:
            return self


class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        action_or_state = self.dispatch(event=event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action=action_or_state):
            # A valid action was performed
            if not self.engine.player.alive:
                return GameOverEventHandler(engine=self.engine)
            elif self.engine.player.level and self.engine.player.level.can_level_up:
                return LevelUpEventHandler(engine=self.engine)
            elif self.engine.player.inventory and self.engine.player.inventory.open:
                return InventoryActivationHandler(engine=self.engine)
            return MainGameEventHandler(engine=self.engine)
        return self

    def handle_action(self, action: Optional[action.Action]) -> bool:
        if action is None:
            return False
        try:
            res = action.perform()
            if isinstance(res, bool) and res is False:
                return res
            # self.engine.handle_deaths()
        except self.engine.exceptions.Impossible as exc:
            self.engine.message_log.add_message(
                text=exc.args[0],
                fg=self.engine.colours['impossible']
            )
            return False

        # enemy_process = mp.Process(
        #     target=self.engine.handle_enemy_turn,
        # )
        enemy_process = mt.Thread(
            target=self.engine.handle_enemy_turn,
        )
        enemy_process.start()
        enemy_process.join()
        # self.engine.handle_enemy_turn()
        self.engine.update_fov()
        self.engine.handle_deaths()

        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(x=event.tile.x, y=event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def ev_windowresized(self, event: tcod.event.WindowResized) -> None:
        width, height = self.engine.context.recommended_console_size()
        console = self.engine.context.new_console(
            min_columns=width,
            min_rows=height,
            order="F"
        )
        self.engine.game_world.viewport_width = width-min((width // 3), 55)
        self.engine.game_world.viewport_height = height
        self.engine.render(console=console)
        # self.engine.game_map.render(console=console)
        # console = self.engine.context.new_console(
        #   *self.engine.context.recommended_console_size(),
        #   order="F"
        # )
        # self.engine.render(console=console)
        # print(self.engine.console.width, self.engine.console.height, self.engine.game_map.width, self.engine.game_map.height)

        # self.on_render(console=self.engine.console)

    def on_render(self, console: tcod.console.Console) -> None:
        # self.engine.game_map.render(console=console)
        # width, height = self.engine.context.recommended_console_size()
        # self.engine.game_world.viewport_width = width-min((width // 3), 55)
        # self.engine.game_world.viewport_height = height
        width, height = self.engine.context.recommended_console_size()
        self.engine.game_world.viewport_width = width-min((width // 3), 55)
        self.engine.game_world.viewport_height = height
        self.engine.render(console=console)


class AskUserEventHandler(EventHandler):

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        if event.sym in {
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        self.engine.mouse_location = (0, 0)
        self.engine.player.inventory.open = False
        return MainGameEventHandler(engine=self.engine)


class InventoryEventHandler(AskUserEventHandler):
    TITLE = " INVENTORY "

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console=console)
        player = self.engine.player
        viewport = self.engine.game_map.get_viewport()
        if player.x+viewport[0][0]+self.engine.game_map.offset_x <= self.engine.side_console:
            x = self.engine.game_world.viewport_width-self.engine.side_console
        else:
            x = 1
        # ─│┌┐└├┤┬┴┼┘
        number_of_items_in_inventory = len(player.inventory.items)
        height = 0
        y = 0
        width = self.engine.side_console
        offset = 0
        # calculate number of lines wrapped item names use
        if number_of_items_in_inventory > 0:
            lines = []
            for i, item in enumerate(player.inventory.items):
                item_key = chr(ord("a") + i)
                is_equipped = player.equipment.item_is_equipped(item=item)
                item_string = f"[{item_key}]-{item.name}"
                if is_equipped:
                    item_string = f"{item_string} (E)"

                item = list(self.engine.message_log.wrap(
                    string=item_string,
                    width=width-2
                ))
                lines += item + [constants.empty_space]
                height += len(item)

                # height += len(lines)
                if i > 0:
                    height += 1
        else:
            lines = list(self.engine.message_log.wrap(
                string="Inventory is empty.",
                width=width-2
            ))
            height += len(lines)
        # adjust height based on number of lines
        height = min(4+height, console.height)
        # set frame decoration based on height
        # if height == console.height:
        #   decoration = '┌─┐│ │└─┘'
        # else:
        #   decoration = '┌─┐│ │├─┤'
        decoration = '┌─┐│ │└─┘'

        # draw inventory frame
        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
            decoration=decoration
        )
        # draw inventory title
        console.print(
            x=x+1,
            y=y,
            string=self.TITLE,
            bg=(255, 255, 255),
            fg=(0, 0, 0)
        )
        # draw pickup instruction
        console.print(
            x=x+1,
            y=y+height-1,
            string='p-loot',
        )
        # draw drop instruction
        string = 'd-drop'
        console.print(
            x=x+self.engine.side_console - len(string)-1,
            y=y+height-1,
            string=string,
        )
        # print each line
        for line in lines:
            if offset >= height:
                return
            console.print(
                x=x + 1,
                y=1 + y + offset + 1,
                string=line
            )
            offset += 1

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= player.inventory.capacity:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message(
                    text="Invalid entry.",
                    fg=self.engine.colours['invalid']
                )
                return None
            return self.on_item_selected(item=selected_item)
        if key == tcod.event.KeySym.ESCAPE or key == tcod.event.KeySym.BACKSPACE:
            return super().ev_keydown(event=event)
        else:
            return None

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        raise NotImplementedError()


class InventoryActivationHandler(InventoryEventHandler):

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            return item.consumable.get_action(entity=self.engine.player)
        elif item.equippable:
            return item.equippable.get_action(entity=self.engine.player)
        else:
            return None


class InventoryDropHandler(InventoryEventHandler):
    TITLE = "DROP ITEM?"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        return action.DropItem(entity=self.engine.player, item=item)


class SelectIndexHandler(AskUserEventHandler):
    def __init__(self, engine: Engine, target_xy: Optional[Tuple[int, int]] = None):
        super().__init__(engine=engine)
        player = self.engine.player
        self.viewport = self.engine.game_map.get_viewport()
        if target_xy:
            engine.mouse_location = target_xy
        else:
            engine.mouse_location = (player.x, player.y)
        self.valid = True
        self.child = None

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console=console)

        viewport = self.engine.game_map.get_viewport()
        x, y = self.engine.mouse_location
        # dist = self.engine.player.distance(x,y )
        dist = max(abs(self.engine.player.x - x),
                   abs(self.engine.player.y - y))
        x = x - viewport[0][0] + self.engine.game_map.offset_x
        y = y - viewport[0][1] + self.engine.game_map.offset_y
        if self.child and self.child.radius:
            radius = self.child.radius
            if dist > radius:
                console.rgb['fg'][x, y] = self.engine.colours['black']
                console.rgb['bg'][x, y] = self.engine.colours['red']
                self.valid = False
                return
        if self.child and hasattr(self.child, 'item'):
            colour = self.child.item.colour if hasattr(
                self.child.item, 'colour') else self.engine.colours['white']
        else:
            colour = self.engine.colours['white']

        console.rgb['fg'][x, y] = self.engine.colours['black']
        console.rgb['bg'][x, y] = colour

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        key = event.sym
        match key:
            case _:
                if key in MOVE_KEYS:
                    # modify movement based on mod key
                    mod = 1
                    if event.mod & tcod.event.KMOD_SHIFT:
                        mod *= 5
                    if event.mod & tcod.event.KMOD_CTRL:
                        mod *= 10
                    if event.mod & tcod.event.KMOD_ALT:
                        mod *= 20
                    x, y = self.engine.mouse_location
                    dx, dy = MOVE_KEYS[key]
                    x += dx*mod
                    y += dy*mod
                    # clamp x and y to map size
                    x = max(1-self.engine.game_map.offset_x + self.viewport[0][0], min(
                        x, self.viewport[1][0] + self.engine.game_map.offset_x - 1))
                    y = max(1-self.engine.game_map.offset_y + self.viewport[0][1], min(
                        y, self.viewport[1][1] + self.engine.game_map.offset_y - 1))
                    # x=max(1, min(x, self.engine.game_world.viewport_width - 2))
                    # y=max(1, min(y, self.engine.game_world.viewport_height - 2))
                    self.engine.mouse_location = x, y
                    return None
                elif key in CONFIRM_KEYS and self.valid:
                    return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event=event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        raise NotImplementedError()

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        return

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        return MainGameEventHandler(engine=self.engine)


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        performing_action: Optional[action.Action] = None

        player = self.engine.player

        key = event.sym
        modifier = event.mod
        match key:
            case tcod.event.KeySym.ESCAPE:
                # performing_action = action.EscapeAction(entity=self.engine.player)
                raise SystemExit()
            case tcod.event.KeySym.v:
                return HistoryViewer(engine=self.engine)
            case tcod.event.KeySym.i:
                self.engine.player.inventory.open = True
                return InventoryActivationHandler(engine=self.engine)
            case tcod.event.KeySym.d:
                self.engine.player.inventory.open = True
                return InventoryDropHandler(engine=self.engine)
            case tcod.event.KeySym.x:
                return LookHandler(engine=self.engine)
            case tcod.event.KeySym.p:
                return action.PickupAction(entity=player)
            case tcod.event.KeySym.c:
                return CharacterScreenEventHandler(engine=self.engine)
            case tcod.event.KeySym.a:
                if player.equipment.weapon:
                    return player.equipment.weapon.equippable.get_action(entity=player)
                else:
                    return MeleeSelectHandler(
                        engine=self.engine,
                        callback=lambda xy: action.MeleeAction(
                            entity=player,
                            dx=xy[0]-player.x,
                            dy=xy[1]-player.y,
                        )
                    )
            case _:
                if key in MOVE_KEYS:
                    dx, dy = MOVE_KEYS[key]
                    return action.BumpAction(entity=player, dx=dx, dy=dy)
                elif key in WAIT_KEYS:
                    return action.WaitAction(entity=player)
                elif key in CONFIRM_KEYS:
                    return action.UseAction(entity=player)

        return performing_action


class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists(path="savegame.sav"):
            os.remove(path="savegame.sav")
        raise self.engine.exceptions.QuitWithoutSaving(
            "Game exited without saving.")

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.KeySym.ESCAPE:
            # action.EscapeAction(entity=self.engine.player)
            self.on_quit()


class HistoryViewer(EventHandler):
    def __init__(self, engine: Engine):
        super().__init__(engine=engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console=console)

        log_console = tcod.console.Console(
            width=self.engine.console.width - 6, height=self.engine.console.height - 6)

        log_console.draw_frame(
            x=0,
            y=0,
            width=log_console.width,
            height=log_console.height
        )
        log_console.print_box(
            x=0,
            y=0,
            width=log_console.width,
            height=1,
            string="┤Message history├",
            alignment=tcod.constants.CENTER
        )

        self.engine.message_log.render_messages(
            console=log_console,
            x=1,
            y=1,
            width=log_console.width - 2,
            height=log_console.height - 2,
            messages=self.engine.message_log.messages[: self.cursor + 1],
        )

        log_console.blit(
            dest=console,
            dest_x=3,
            dest_y=3,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(
                    0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.KeySym.END:
            # Move directly to the last message.
            self.cursor = self.log_length - 1
        else:  # Any other key moves back to the main game state.
            return MainGameEventHandler(engine=self.engine)
        return None


class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "Level Up!"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console=console)
        x = self.engine.game_world.viewport_width+1
        y = 1
        lines = []
        width = self.engine.side_console-3
        lines += list(self.engine.message_log.wrap(
            string="Congratulations! You level up!",
            width=width,
        ))
        lines += [constants.empty_space]
        lines += list(self.engine.message_log.wrap(
            string="Raise one stat:",
            width=width,
        ))
        lines += [constants.empty_space]
        lines += list(self.engine.message_log.wrap(
            string=f"1)Vitality (+20 HP)",
            width=width,
        ))
        lines += list(self.engine.message_log.wrap(
            string=f"2)Strength (+1 attack)",
            width=width,
        ))
        lines += list(self.engine.message_log.wrap(
            string=f"3)Constitution (+1 defence)",
            width=width,
        ))
        height = len(lines) + 2
        console.draw_frame(
            x=x,
            y=y,
            width=width+1,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        offset = y+1
        for line in lines:
            console.print(x=x+1, y=offset, string=line)
            offset += 1
            if offset > height:
                break

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        match key:
            case tcod.event.KeySym.N1:
                player.level.increase_stat(stat='HP', value=20)
            case tcod.event.KeySym.N2:
                player.level.increase_stat(stat='ATK', value=1)
            case tcod.event.KeySym.N3:
                player.level.increase_stat(stat='DEF', value=1)
            case _:
                self.engine.message_log.add_message(
                    text="Invalid entry.",
                    fg=self.engine.colours['invalid']
                )
                return None
        return super().ev_keydown(event=event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """
        Don't allow the player to click to exit the menu, like normal.
        """
        return None


class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Stats"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console=console)
        x = self.engine.game_world.viewport_width+1
        y = 1
        width = self.engine.side_console-3
        lines = []
        lines += list(self.engine.message_log.wrap(
            string=f"Name: {self.engine.player.name}",
            width=width,
        ))
        lines += [constants.empty_space]
        lines += list(self.engine.message_log.wrap(
            string=f"HP: {self.engine.player.fighter.HP}/{self.engine.player.fighter.MAX_HP}",
            width=width,
        ))
        lines += [constants.empty_space]
        lines += list(self.engine.message_log.wrap(
            string=f"Attack: {self.engine.player.fighter.ATK[0]}-{self.engine.player.fighter.ATK[1]}",
            width=width,
        ))
        lines += [constants.empty_space]
        lines += list(self.engine.message_log.wrap(
            string=f"Defence: {self.engine.player.fighter.DEF}",
            width=width,
        ))
        lines += [constants.empty_space]
        if self.engine.player.level:
            lines += list(self.engine.message_log.wrap(
                string=f"Level: {self.engine.player.level.curr_level}",
                width=width,
            ))
            lines += [constants.empty_space]
            lines += list(self.engine.message_log.wrap(
                string=f"XP: {self.engine.player.level.curr_xp}",
                width=width,
            ))
            lines += [constants.empty_space]
            lines += list(self.engine.message_log.wrap(
                string=f"Next Level: {self.engine.player.level.xp_to_next_level}",
                width=width,
            ))
            lines += [constants.empty_space]
        height = len(lines)+3
        console.draw_frame(
            x=x,
            y=y,
            width=width+1,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        offset = y+2
        for line in lines:
            console.print(x=x+1, y=offset, string=line)
            offset += 1
            if offset > height:
                break


class SingleTargetSelectHandler(SelectIndexHandler):
    def __init__(
        self,
        engine: Engine,
        callback: Callable[[Tuple[int, int]], Optional[action.Action]],
        item: Item,
    ):
        super().__init__(engine=engine)
        self.item = item
        self.callback = callback
        self.radius = 8
        self.child = self

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console=console)
        viewport = self.engine.game_map.get_viewport()
        x, y = self.player_pos = (
            self.engine.player.x +
            self.engine.game_map.offset_x -
            viewport[0][0],
            self.engine.player.y +
            self.engine.game_map.offset_y -
            viewport[0][1]
        )

        if self.item.consumable.range:
            self.radius = self.item.consumable.range
        else:
            self.radius = 8

        x = x - self.radius - 1
        y = y - self.radius - 1
        diameter = self.radius * 2 + 3

        if self.item:
            colour = self.item.colour
        else:
            colour = self.engine.colours['red']

        console.draw_frame(
            x=x,
            y=y,
            width=diameter,
            height=diameter,
            fg=colour,
            clear=False
        )

    def on_index_selected(self, x: int, y: int) -> Optional[action.Action]:

        return self.callback((x, y))


class AreaRangedSelectHandler(SelectIndexHandler):
    def __init__(
        self,
        engine: action.Engine,
        item: Item,
        callback: Callable[[Tuple[int, int]], Optional[action.Action]]
    ):
        super().__init__(engine=engine)
        self.item = item
        self.callback = callback
        self.radius = 8

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console=console)
        viewport = self.engine.game_map.get_viewport()
        x, y = self.engine.mouse_location
        x, y = self.mouse_pos = (
            x +
            self.engine.game_map.offset_x -
            viewport[0][0],
            y +
            self.engine.game_map.offset_y -
            viewport[0][1]
        )

        if hasattr(self.item.consumable, 'radius'):
            self.radius = self.item.consumable.radius
        else:
            self.radius = 8
        x = x - self.radius - 1
        y = y - self.radius - 1
        diameter = self.radius * 2 + 3

        console.draw_frame(
            x=x,
            y=y,
            width=diameter,
            height=diameter,
            fg=self.engine.colours['red'],
            clear=False
        )

    def on_index_selected(self, x: int, y: int) -> Optional[action.Action]:

        return self.callback((x, y))


class LineTargetSelectHandler(SelectIndexHandler):
    def __init__(
        self,
        engine: Engine,
        callback: Callable[[Tuple[int, int]], Optional[action.Action]],
        item: Item,
    ):
        super().__init__(engine=engine)
        self.item = item
        self.callback = callback
        self.radius = 8
        self.child = self

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console=console)
        viewport = self.engine.game_map.get_viewport()
        x, y = self.player_pos = (
            self.engine.player.x +
            self.engine.game_map.offset_x -
            viewport[0][0],
            self.engine.player.y +
            self.engine.game_map.offset_y -
            viewport[0][1]
        )

        if hasattr(self.item.consumable, 'radius'):
            self.radius = self.item.consumable.radius

        x = x - self.radius - 1
        y = y - self.radius - 1
        diameter = self.radius * 2 + 3

        if self.item:
            colour = self.item.colour
        else:
            colour = self.engine.colours['red']

        console.draw_frame(
            x=x,
            y=y,
            width=diameter,
            height=diameter,
            fg=colour,
            clear=False
        )
        radius = self.radius
        mouseX = self.engine.mouse_location[0] - \
            viewport[0][0] + self.engine.game_map.offset_x
        mouseY = self.engine.mouse_location[1] - \
            viewport[0][1] + self.engine.game_map.offset_y
        x, y = self.player_pos = (x + self.radius + 1, y + self.radius + 1)
        line = tcod.los.bresenham(
            start=(x, y),
            end=(mouseX, mouseY)
        ).tolist()

        for pointX, pointY in line:
            if x-radius > pointX or y-radius > pointY:
                self.valid = False
            elif pointX > x+radius or pointY > y+radius:
                self.valid = False
            else:
                console.rgb['fg'][pointX,
                                  pointY] = self.engine.colours['black']
                console.rgb['bg'][pointX,
                                  pointY] = self.item.colour

    def on_index_selected(self, x: int, y: int) -> Optional[action.Action]:

        return self.callback((x, y))


class MeleeSelectHandler(SelectIndexHandler):
    def __init__(
        self,
        engine: Engine,
        callback: Callable[[Tuple[int, int]], Optional[action.Action]],
    ):
        super().__init__(engine=engine)
        if engine.player.target:
            self.target_xy = (engine.player.target.x, engine.player.target.y)
        else:
            self.target_xy = (engine.player.x, engine.player.y)
        super().__init__(
            engine=engine,
            target_xy=(self.target_xy)
        )

        self.callback = callback
        self.radius = 1
        self.child = self

    def on_index_selected(self, x: int, y: int) -> Optional[action.Action]:
        return self.callback((x, y))


class MeleeWeaponSelectHandler(SelectIndexHandler):
    def __init__(
        self,
        engine: Engine,
        callback: Callable[[Tuple[int, int]], Optional[action.Action]],
        item: Item,
        reach: int = 1
    ):
        if engine.player.target:
            self.target_xy = (engine.player.target.x, engine.player.target.y)
        else:
            self.target_xy = (engine.player.x, engine.player.y)
        super().__init__(
            engine=engine,
            target_xy=(self.target_xy)
        )
        self.item = item
        self.callback = callback
        self.radius = reach
        self.child = self

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console=console)
        viewport = self.engine.game_map.get_viewport()
        x, y = self.player_pos = (
            self.engine.player.x +
            self.engine.game_map.offset_x -
            viewport[0][0],
            self.engine.player.y +
            self.engine.game_map.offset_y -
            viewport[0][1]
        )

        if hasattr(self.item.equippable, 'range'):
            self.radius = self.item.equippable.range

        # x = x - self.radius - 1
        # y = y - self.radius - 1

        # if self.item:
        #   colour = self.item.colour
        # else:
        #   colour = self.engine.colours['red']

    def on_index_selected(self, x: int, y: int) -> Optional[action.Action]:
        return self.callback((x, y))


class EnemyActionHandler:
    def __init__(
        self,
        engine: Engine,
        actor: Actor,
        callback: Callable[[Tuple[int, int]], Optional[action.Action]]
    ):
        if engine.player.target:
            self.target_xy = (engine.player.target.x, engine.player.target.y)
        else:
            self.target_xy = (engine.player.x, engine.player.y)
        self.engine = engine
        self.actor = actor
        self.callback = callback
