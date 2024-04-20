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

class HealingConsumable(Consumable):
  def __init__(self, amount: int, on_use:str = ""):
    self.amount = amount
    self.on_use = on_use
  
  def action(self, action: actions.ItemAction) -> None:
    entity = action.entity
    amount_recovered = entity.fighter.heal_damage(amount=self.amount)
    if amount_recovered <= 0:
      raise self.engine.exceptions.Impossible("Your health is already full.")

    if self.on_use:
      self.on_use = self.on_use.split("<amount>")
      self.on_use = self.on_use[0] + str(amount_recovered) + self.on_use[1]
    else:
      self.on_use = f"You drink the {self.parent.name}. It restored {amount_recovered} HP!"
    self.engine.message_log.add_message(
      text=self.on_use,
      fg=self.engine.colours['health_recovery']
    )
    self.consume()
     

class LineDamageCosumable(Consumable):
  def __init__(self, damage: int, range:int, on_hit_message: str = ""):
    self.damage = damage
    self.range = range
    self.on_hit = on_hit_message
  
  def action(self, action: actions.ItemAction) -> None:
    entity = action.entity
    target = None
    closest_distance = self.range + 1.0

    for actor in self.engine.game_map.actors:
      if actor is not entity and self.parent.gamemap.seeing[actor.x, actor.y]:
        distance = entity.distance(x=actor.x, y=actor.y)

        if distance < closest_distance:
          target = actor
          closest_distance = distance
    
    if not target:
      raise self.engine.exceptions.Impossible("No enemies in range.")
    if self.on_hit:
      self.on_hit = self.on_hit.split("<target>")
      self.on_hit = self.on_hit[0] + target.name + self.on_hit[1]
      self.on_hit = self.on_hit.split('<damage>')
      self.on_hit = self.on_hit[0] + str(self.damage) + self.on_hit[1]
    else:
      self.on_hit = f"A lighting bolt strikes the {target.name} with a loud thunder, for {self.damage} damage!"
    self.engine.message_log.add_message(
      text=self.on_hit
    )
    target.fighter.take_damage(amount=self.damage)
    self.consume()