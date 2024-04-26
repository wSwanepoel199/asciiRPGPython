from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

from src.components.base_component import BaseComponent
from src.utils.render_order import RenderOrder

if TYPE_CHECKING:
  from src.entity import Actor

class Fighter(BaseComponent):
  parent: Actor
  def __init__(self, Base_HP: int, Base_ATK: Tuple[int,int], Base_DEF: int):
    self.Base_HP = Base_HP
    self.Base_Max_HP = Base_HP
    self.Base_ATK = Base_ATK
    self.Base_DEF = Base_DEF
  
  @property
  def HP(self) -> int:
    return self.Base_HP
  
  @property
  def MAX_HP(self) -> int:
    return self.Base_Max_HP + self.HP_Bonus

  @property
  def DEF(self) -> int:
    return self.Base_DEF + self.DEF_Bonus

  @property
  def ATK(self) -> int:
    return [self.Base_ATK[0] + self.ATK_Bonus, self.Base_ATK[1] + self.ATK_Bonus]

  @property
  def DEF_Bonus(self) -> int:
    if self.parent.equipment:
      return self.parent.equipment.def_bonus
    else:
      return 0

  @property
  def ATK_Bonus(self) -> int:
    if self.parent.equipment:
      return self.parent.equipment.atk_bonus
    else:
      return 0
  
  @property
  def HP_Bonus(self) -> int:
    if self.parent.equipment:
      return self.parent.equipment.hp_bonus
    else:
      return 0

  @HP.setter
  def HP(self, value: int) -> None:
    self.Base_HP = max(0, min(value, self.MAX_HP))

  def die(self) -> None:
    if self.engine.player is self.parent:
      death_message = "YOU DIED"
      death_message_colour = self.engine.colours['player_dead']
    else:
      death_message = f"The {self.parent.name} has died"
      death_message_colour = self.engine.colours['enemy_dead']
      if self.engine.player.level and self.parent.level:
        self.engine.player.level.add_xp(xp=self.parent.level.xp_given)

    self.parent.char = "%"
    self.parent.entity_type = "CORPSE"
    self.parent._render_order = RenderOrder.CORPSE
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
