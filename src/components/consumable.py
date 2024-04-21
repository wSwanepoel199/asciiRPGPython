from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import src.actions as actions
import src.components.ai as ai
import src.event_handler as event_handler
from src.components.inventory import Inventory
from src.components.base_component import BaseComponent

if TYPE_CHECKING:
  from src.entity import Actor, Item

class Consumable(BaseComponent):
  parent: Item

  def get_action(self, entity: Actor) -> Optional[actions.Action]:
    return actions.ItemAction(entity=entity, item=self.parent)
  
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
     

class LineDamageConsumable(Consumable):
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
    entity.target = target
    self.consume()

class TeleportConsumable(Consumable):
  # def __init__(self) -> None:
  
  def get_action(self, entity: Actor) -> Optional[actions.Action]:
    self.engine.message_log.add_message(
      text="Select a target location.", 
      fg=self.engine.colours['needs_target']
    )
    self.engine.event_handler = event_handler.SingleTargetSelectHandler(
      engine=self.engine, 
      callback=lambda xy: actions.ItemAction(entity=entity, item=self.parent, target_xy=xy)
    )
    return None

  def action(self, action: actions.ItemAction) -> None:
    entity = action.entity
    target = action.target_actor

    if not target:
      target = action.item
    if target.entity_type == "ACTOR":
      raise self.engine.exceptions.Impossible("Another creature has blocked the Teleport.")
    if target is entity:
      raise self.engine.exceptions.Impossible("You can't teleport onto yourself!")
    if not entity.gamemap.tiles[action.target_xy]["walkable"]:
      raise self.engine.exceptions.Impossible("You can't teleport to a location you can't walk on!")
    dx = action.target_xy[0] - entity.x
    dy = action.target_xy[1] - entity.y
    distance = max(abs(dx), abs(dy))
    if distance > 10:
      raise self.engine.exceptions.Impossible("You can't teleport more than 10 tiles away!")
    self.engine.message_log.add_message(
      text=f"You feel your very being evaporate as you are teleported!",
      fg=self.engine.colours['status_effect_applied']
    )
    entity.x, entity.y = action.target_xy
    self.consume()

class ConfusionConsumable(Consumable):
  def __init__(self, turns:int):
    self.turns = turns
  
  def get_action(self, entity: Actor) -> Optional[actions.Action]:
    self.engine.message_log.add_message(
      text="Select a target location.", 
      fg=self.engine.colours['needs_target']
    )
    self.engine.event_handler = event_handler.SingleTargetSelectHandler(
      engine=self.engine, 
      callback=lambda xy: actions.ItemAction(entity=entity,item=self.parent, target_xy=xy)
    )
    return None
  
  def action(self, action: actions.ItemAction) -> None:
    entity = action.entity
    target = action.target_actor

    if not self.engine.game_map.seeing[action.target_xy]:
      raise self.engine.exceptions.Impossible("You can't target a location you can't see.")
    if not target:
      raise self.engine.exceptions.Impossible("You must target an enemy.")
    if target is entity:
      raise self.engine.exceptions.Impossible("You can't confuse yourself!")
    
    self.engine.message_log.add_message(
      text=f"The eyes of the {target.name} go vacant, and it starts to stumble!",
      fg=self.engine.colours['status_effect_applied']
    )

    target.ai = ai.ConfusedAi(
      entity=target,
      prev_ai=target.ai,
      turns_remaining=self.turns
    )
    self.consume()

class FireballDamageConsumable(Consumable):
  def __init__(self, damage: int, radius: int):
    self.damage = damage
    self.radius = radius
  
  def get_action(self, entity: Actor) -> Optional[actions.Action]:
    self.engine.message_log.add_message(
      text="Select a target location.", 
      fg=self.engine.colours['needs_target']
    )
    self.engine.event_handler = event_handler.AreaRangedSelectHandler(
      engine=self.engine, 
      radius=self.radius,
      callback=lambda xy: actions.ItemAction(entity=entity, item=self.parent, target_xy=xy)
    )
    return None
  
  def action(self, action: actions.ItemAction) -> None:
    target_xy = action.target_xy

    if not self.engine.game_map.seeing[target_xy]:
      raise self.engine.exceptions.Impossible("You can't target a location you can't see.")
    targets_hit = False
    for actor in self.engine.game_map.actors:
      if actor.distance(*target_xy) <= self.radius:
        self.engine.message_log.add_message(
          text=f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!",
        )
        actor.fighter.take_damage(amount=self.damage)
        targets_hit = True
    if not targets_hit:
      raise self.engine.exceptions.Impossible("There are no targets in the radius.")
    self.consume()