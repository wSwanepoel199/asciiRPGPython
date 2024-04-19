from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import tcod
from src.actions import Action, EscapeAction, BumpAction

if TYPE_CHECKING:
  from engine import Engine

class EventHandler(tcod.event.EventDispatch[Action]):
  def __init__(self, engine: Engine) -> None:
    self.engine = engine

  def handle_events(self) -> None:
    for event in tcod.event.wait():
      action = self.dispatch(event=event)

      if action is None:
        continue
      action.perform()
      self.engine.handle_enemy_turn()
      self.engine.update_fov()

  def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
    raise SystemExit()

  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
    action: Optional[Action] = None
    player = self.engine.player
    # print(event.sym)
    match event.sym:
      case tcod.event.KeySym.UP:
        action = BumpAction(entity=player, dx=0, dy=-1)
      case tcod.event.KeySym.DOWN:
        action = BumpAction(entity=player, dx=0, dy=1)
      case tcod.event.KeySym.LEFT:
        action = BumpAction(entity=player, dx=-1, dy=0)
      case tcod.event.KeySym.RIGHT:
        action = BumpAction(entity=player, dx=1, dy=0)
      case tcod.event.KeySym.ESCAPE:
        action = EscapeAction(entity=player)

    return action