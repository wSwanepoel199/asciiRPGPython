from __future__ import annotations
from typing import List, TYPE_CHECKING

from src.components.base_component import BaseComponent

if TYPE_CHECKING:
  from src.entity import Actor, Item

class Inventory(BaseComponent):
  parent: Actor

  def __init__(self, capacity: int):
    self.capacity = capacity
    self.items: List[Item] = []

  def drop(self, item:Item) -> None:
    self.items.remove(item)
    item.place(x=self.parent.x, y=self.parent.y, gamemap=self.gamemap)
    self.engine.message_log.add_message(text=f"You dropped a {item.name}.")