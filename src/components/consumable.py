from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import src.actions as actions

from src.components.inventory import Inventory
from src.components.base_component import BaseComponent

if TYPE_CHECKING:
  from src.entity import Actor, Item

class Consumable(BaseComponent):
  parent: Item

  def get_action(self, entity: Actor) -> Optional[actions.Action]:
    return actions.ItemAction(entity, self.parent)
  
  def action(self, action: actions.ItemAction) -> None:
    raise NotImplementedError()
  
  def consume(self) -> None:
    entity = self.parent
    inventory = entity.parent
    if isinstance(inventory, Inventory):
      inventory.items.remove(entity)


class HealingPotion(Consumable):
  def __init__(self, amount: int):
    self.amount = amount
  
  def action(self, action: actions.ItemAction) -> None:
    entity = action.entity
    amount_recovered = entity.fighter.heal_damage(amount=self.amount)

    if amount_recovered > 0:
      self.engine.message_log.add_message(
        text=f"You drink the {self.parent.name}. It restored {amount_recovered} HP!",
        fg=self.engine.colours['health_recovery']
      )
      self.consume()
    else:
      raise self.engine.exceptions.Impossible("Your health is already full.")