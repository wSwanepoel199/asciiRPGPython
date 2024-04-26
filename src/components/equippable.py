from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, Optional

from src.components.base_component import BaseComponent
from src.utils.equipment_type import EquipmentType
import src.event_handler as event_handler
import src.actions as actions

if TYPE_CHECKING:
  from src.entity import Item, Actor


class Equippable(BaseComponent):
  parent: Item

  def __init__(
      self,
      equipment_type: EquipmentType,
      ATK_bonus: int = 0,
      DEF_bonus: int = 0,
      HP_bonus: int = 0,
  ):
    self.equipment_type = equipment_type
    self.ATK_bonus = ATK_bonus
    self.DEF_bonus = DEF_bonus
    self.HP_bonus = HP_bonus

  def get_action(self, entity: Actor) -> Optional[event_handler.ActionOrHandler]:
    return actions.ItemAction(entity=entity, item=self.parent)

class Dagger(Equippable):
  def __init__(self) -> None:
    super().__init__(equipment_type=EquipmentType.WEAPON, ATK_bonus=2)

class Sword(Equippable):
  def __init__(self) -> None:
    super().__init__(equipment_type=EquipmentType.WEAPON, ATK_bonus=4)

class LeatherArmour(Equippable):
  def __init__(self) -> None:
    super().__init__(equipment_type=EquipmentType.ARMOUR, DEF_bonus=1)

class ChainMail(Equippable):
  def __init__(self) -> None:
    super().__init__(equipment_type=EquipmentType.ARMOUR, DEF_bonus=3)