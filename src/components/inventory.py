from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional

from src.components.base_component import BaseComponent
from src.utils.equipment_type import EquipmentType

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
  
class Equipment(BaseComponent):
  parent: Actor

  def __init__(
      self,
      weapon: Optional[Item] = None,
      armour: Optional[Item] = None,
      accessory: Optional[Item] = None
  ):
    self.weapon = weapon
    self.armour = armour
    self.accessory = accessory

  @property
  def def_bonus(self) -> int:
    bonus = 0

    if (
      self.weapon is not None
      and self.weapon.equippable is not None
    ):
      bonus += self.weapon.equippable.DEF_bonus

    if (
      self.armour is not None
      and self.armour.equippable is not None
    ):
      bonus += self.armour.equippable.DEF_bonus

    return bonus

  @property
  def atk_bonus(self) -> int:
    bonus = 0

    if (
      self.weapon is not None
      and self.weapon.equippable is not None
    ):
      bonus += self.weapon.equippable.ATK_bonus

    if (
      self.armour is not None
      and self.armour.equippable is not None
    ):
      bonus += self.armour.equippable.ATK_bonus

    return bonus
  
  @property
  def hp_bonus(self) -> int:
    bonus = 0

    if (
      self.weapon is not None
      and self.weapon.equippable is not None
    ):
      bonus += self.weapon.equippable.HP_bonus

    if (
      self.armour is not None
      and self.armour.equippable is not None
    ):
      bonus += self.armour.equippable.HP_bonus

    return bonus
  
  def item_is_equipped(self, item: Item) -> bool:
    return self.weapon == item or self.armour == item or self.accessory == item

  def unequip_message(self, item_name: str) -> None:
    self.parent.gamemap.engine.message_log.add_message(
      text=f"You remove the {item_name}."
    )
  
  def equip_message(self, item_name: str) -> None:
    self.parent.gamemap.engine.message_log.add_message(
      text=f"You equip the {item_name}."
    )

  def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
    current_item = getattr(self, slot)

    if current_item is not None:
      self.unequip_from_slot(slot=slot, add_message=add_message)

    setattr(self, slot, item)

    if add_message:
      self.equip_message(item_name=item.name)

  def unequip_from_slot(self, slot: str, add_message: bool) -> None:
    current_item = getattr(self, slot)

    if add_message:
      self.unequip_message(item_name=current_item.name)

    setattr(self, slot, None)

  def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
    if not equippable_item.equippable:
      return

    if equippable_item.equippable.equipment_type == EquipmentType.WEAPON:
      slot = "weapon"
    elif equippable_item.equippable.equipment_type == EquipmentType.ARMOUR:
      slot = "armour"
    elif equippable_item.equippable.equipment_type == EquipmentType.ACCESSORY:
      slot = "accessory"
    else:
      return

    if getattr(self, slot) == equippable_item:
      self.unequip_from_slot(slot=slot, add_message=add_message)
    else:
      self.equip_to_slot(slot=slot, item=equippable_item, add_message=add_message)