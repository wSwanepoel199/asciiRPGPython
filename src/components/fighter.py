from __future__ import annotations

from typing import TYPE_CHECKING

from src.components.base_component import BaseComponent

if TYPE_CHECKING:
  from src.entity import Actor

class Fighter(BaseComponent):
  parent: Actor
  def __init__(self, HP: int, ATK: int, DEF: int):
    self._HP = HP
    self.MAX_HP = HP
    self.ATK = ATK
    self.DEF = DEF
  
  @property
  def HP(self) -> int:
    return self._HP
  
  @HP.setter
  def HP(self, value: int) -> None:
    self._HP = max(0, min(value, self.MAX_HP))

  def die(self) -> list:
    if self.engine.player is self.parent:
      death_message = "YOU DIED"
      death_message_colour = self.engine.colours['player_dead']
    else:
      death_message = f"The {self.parent.name} has died"
      death_message_colour = self.engine.colours['enemy_dead']
    self.parent.char = "%"
    self.parent.entity_type = "OBJECT"
    self.parent.colour = (191,0,0)
    self.parent.blocks_movement = False
    self.parent.ai = None
    self.parent.name = f"Remains of {self.parent.name}"

    self.engine.message_log.add_message(text=death_message, fg=death_message_colour)
  
  def heal_damage(self, amount: int) -> int:
    if self.HP == self.MAX_HP:
      return 0
    
    if self.HP + amount > self.MAX_HP:
      amount = self.HP+amount - self.MAX_HP

    self.HP += amount
    return amount
  def take_damage(self, amount: int) -> None:
    self.HP -= amount
