from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import random
import threading as mt

from numpy import delete
from src.entity import Actor, Item

if TYPE_CHECKING:
    from src.engine import Engine
    from src.entity import Entity, Actor, Item


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):
    def __init__(self, entity: Actor):
        super().__init__(entity=entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise self.engine.exceptions.Impossible(
                        "Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(
                    text=f"You picked up a {item.name}!")
                return
        raise self.engine.exceptions.Impossible(
            "There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
        self,
        entity: Actor,
        item: Item,
        target_xy: Optional[Tuple[int, int]] = None
    ) -> None:
        super().__init__(entity=entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class ConsumableAction(ItemAction):
    def __init__(
        self,
        entity: Actor,
        item: Item,
        target_xy: Optional[Tuple[int, int]] = None
    ) -> None:
        super().__init__(entity=entity, item=item, target_xy=target_xy)

    def perform(self) -> bool:
        if self.item.consumable:
            return self.item.consumable.action(action=self)
        else:
            raise self.engine.exceptions.Impossible(
                f"The {self.item.name} cannot be used.")


class EquipmentAction(ItemAction):
    def __init__(
        self,
        entity: Actor,
        item: Item,
        target_xy: Optional[Tuple[int, int]] = None
    ) -> None:
        super().__init__(entity=entity, item=item, target_xy=target_xy)

    def perform(self) -> bool:
        if self.item.equippable:
            return self.item.equippable.action(action=self)
        else:
            raise self.engine.exceptions.Impossible(
                f"The {self.item.name} cannot be used.")

# class EscapeAction(Action):
#   def perform(self) -> None:
#     raise SystemExit()


class DropItem(ItemAction):
    def perform(self) -> bool:
        if self.entity.equipment.item_is_equipped(item=self.item):
            self.entity.equipment.toggle_equip(equippable_item=self.item)
        else:
            self.entity.inventory.drop(item=self.item)
        return False


class DirectionalAction(Action):
    def __init__(self, entity: Actor, dx: int, dy: int) -> None:
        super().__init__(entity=entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        return self.engine.game_map.get_blocking_entity(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(DirectionalAction):
    def perform(self) -> None:
        target = self.target_actor
        self.entity['target'] = target
        if not target:
            raise self.engine.exceptions.Impossible("Nothing to attack.")
        if target is self.entity:
            raise self.engine.exceptions.Impossible(
                "You can't attack yourself!")
        hit_chance = random.randint(1, 20)
        hit_check = hit_chance+self.entity.fighter.ACC
        damage = random.sample(
            range(*self.entity.fighter.ATK),
            1)[0]
        if self.entity is self.engine.player:
            attacker_name = self.entity.name.capitalize()
            # attack_desc = f"{self.entity.name.capitalize()} attacked the {target.name}"
            attack_color = self.engine.colours['player_atk']
        else:
            attacker_name = f"The {self.entity.name.capitalize()}"
            # attack_desc = f"The {self.entity.name.capitalize()} attacked {target.name}"
            attack_color = self.engine.colours['enemy_atk']
        attack_desc = f"{attacker_name} attacked the {target.name}"
        if hit_chance == 20:
            attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{self.entity.fighter.ACC} for a {hit_check}. \n{attacker_name} scored a Critical Hit dealing {damage*2} damage."
            target.fighter.take_damage(damage*2)
        elif hit_check >= target.fighter.DEF:
            attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{self.entity.fighter.ACC} for a {hit_check}. \n{attacker_name} dealt {damage} damage."
            target.fighter.take_damage(damage)
        else:
            attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{self.entity.fighter.ACC} for a {hit_check}. \n{attacker_name} missed."
        self.engine.message_log.add_message(
            text=attack_message, fg=attack_color)


class MovementAction(DirectionalAction):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy
        test = False
        if (not self.engine.game_map.in_bounds(x=dest_x, y=dest_y) or not self.engine.game_map.tiles["walkable"][dest_x, dest_y] or self.engine.game_map.get_blocking_entity(x=dest_x, y=dest_y)) and test is False:
            raise self.engine.exceptions.Impossible("That way is blocked.")

        self.entity.move(dx=self.dx, dy=self.dy)


class BumpAction(DirectionalAction):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(entity=self.entity, dx=self.dx, dy=self.dy).perform()
        else:
            return MovementAction(entity=self.entity, dx=self.dx, dy=self.dy).perform()


class WaitAction(Action):
    def perform(self) -> None:
        pass


class UseAction(Action):
    def perform(self):
        for entity in self.engine.game_map.entities - {self.entity}:
            if (self.entity.x, self.entity.y) == self.engine.game_map.stairsdown:
                UseStairsAction(entity=self.entity).perform()
                # self.engine.update_fov()
                return False
            if not entity.x == self.entity.x and not entity.y == self.entity.y:
                raise self.engine.exceptions.Impossible(
                    "There is nothing here to use.")
            if entity.entity_type == "ITEM":
                PickupAction(entity=self.entity).perform()
                return


class UseStairsAction(Action):
    def perform(self) -> None:
        if (self.entity.x, self.entity.y) == self.engine.game_map.stairsdown:
            self.engine.message_log.add_message(
                text="You descend the stairs unto unknown depths.",
                fg=self.engine.colours['descend']
            )
            if hasattr(self.engine.event_handler, "thread"):
                self.engine.event_handler.thread = mt.Thread(
                    target=self.engine.game_world.gen_floor
                )
                self.engine.game_map = None
                self.engine.event_handler.thread.start()
            # self.engine.game_world.gen_floor()
        else:
            raise self.engine.exceptions.Impossible(
                "There are no stairs here.")


class EnemyAction(Action):
    def __init__(
        self,
        entity: Actor,
        actor: Actor,
        target_xy: Optional[Tuple[int, int]] = None,
    ):
        super().__init__(entity=entity)
        self.actor = actor
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        raise NotImplementedError()
