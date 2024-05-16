from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, Optional

import random

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
        ACC_bonus: int = 0
    ):
        self.equipment_type = equipment_type
        self.ATK_bonus = ATK_bonus
        self.DEF_bonus = DEF_bonus
        self.HP_bonus = HP_bonus
        self.ACC_bonus = ACC_bonus

    def get_action(self, entity: Actor) -> Optional[event_handler.ActionOrHandler]:
        return actions.EquipmentAction(entity=entity, item=self.parent)

    def action(self, action: actions.EquipmentAction) -> None:
        action.entity.equipment.toggle_equip(equippable_item=self.parent)
        # raise NotImplementedError()


class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, ATK_bonus=4)

    def get_action(self, entity: Actor) -> event_handler.WeaponSelectHandler:
        if not entity.equipment.item_is_equipped(item=self.parent):
            return actions.EquipmentAction(entity=entity, item=self.parent)
        if entity.equipment.weapon is self.parent:
            self.engine.message_log.add_message(
                text="Select a target.",
                fg=self.engine.colours['needs_target']
            )
            return event_handler.WeaponSelectHandler(
                engine=self.engine,
                item=self.parent,
                callback=lambda xy: actions.EquipmentAction(
                    entity=entity, item=self.parent, target_xy=xy)
            )

    def action(self, action: actions.EquipmentAction) -> None:
        if not action.entity.equipment.item_is_equipped(item=self.parent):
            action.entity.equipment.toggle_equip(equippable_item=self.parent)
        else:
            entity = action.entity
            target = action.target_actor
            target_xy = action.target_xy
            if target and target is not entity:
                entity.target = target
                hit_chance = random.randint(1, 20)
                hit_check = hit_chance+entity.fighter.ACC
                damage = random.sample(
                    range(*entity.fighter.ATK),
                    1)[0]

                attack_desc = f"{entity.name.capitalize()} attacked the {target.name}"
                attack_color = self.engine.colours['player_atk']

                if hit_chance == 20:
                    attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{entity.fighter.ACC} for a {hit_check}. \n{entity.name.capitalize()} scored a Critical Hit dealing {damage*2} damage."
                    target.fighter.take_damage(damage*2)
                elif hit_check >= target.fighter.DEF:
                    attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{entity.fighter.ACC} for a {hit_check}. \n{entity.name.capitalize()} dealt {damage} damage."
                    target.fighter.take_damage(damage)
                else:
                    attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{entity.fighter.ACC} for a {hit_check}. \n{entity.name.capitalize()} missed."
                self.engine.message_log.add_message(
                    text=attack_message, fg=attack_color)
            elif target and target is entity:
                raise self.engine.exceptions.Impossible(
                    "You can't attack yourself!")
            else:
                raise self.engine.exceptions.Impossible("Nothing to attack.")
                # attack_color = self.engine.colours['enemy_atk']
                # self.engine.message_log.add_message(
                #     text="There was no target to attack.", fg=attack_color)
                # return False
            # raise NotImplementedError()


class Sword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, ATK_bonus=6)

    def get_action(self, entity: Actor) -> event_handler.WeaponSelectHandler:
        if not entity.equipment.item_is_equipped(item=self.parent):
            return actions.EquipmentAction(entity=entity, item=self.parent)
        if entity.equipment.weapon is self.parent:
            self.engine.message_log.add_message(
                text="Select a target.",
                fg=self.engine.colours['needs_target']
            )
            return event_handler.WeaponSelectHandler(
                engine=self.engine,
                item=self.parent,
                callback=lambda xy: actions.EquipmentAction(
                    entity=entity, item=self.parent, target_xy=xy),
                reach=1
            )

    def action(self, action: actions.EquipmentAction) -> None:
        if not action.entity.equipment.item_is_equipped(item=self.parent):
            action.entity.equipment.toggle_equip(equippable_item=self.parent)
        else:
            entity = action.entity
            target = action.target_actor
            target_xy = action.target_xy
            if target and target is not entity:
                entity.target = target
                hit_chance = random.randint(1, 20)
                hit_check = hit_chance+entity.fighter.ACC
                damage = random.sample(
                    range(*entity.fighter.ATK),
                    1)[0]
                attack_desc = f"{entity.name.capitalize()} attacked the {target.name}"
                attack_color = self.engine.colours['player_atk']

                if hit_chance == 20:
                    attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{entity.fighter.ACC} for a {hit_check}. \n{entity.name.capitalize()} scored a Critical Hit dealing {damage*2} damage."
                    target.fighter.take_damage(damage*2)
                elif hit_check >= target.fighter.DEF:
                    attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{entity.fighter.ACC} for a {hit_check}. \n{entity.name.capitalize()} dealt {damage} damage."
                    target.fighter.take_damage(damage)
                else:
                    attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{entity.fighter.ACC} for a {hit_check}. \n{entity.name.capitalize()} missed."
                self.engine.message_log.add_message(
                    text=attack_message, fg=attack_color)
            elif target and target is entity:
                raise self.engine.exceptions.Impossible(
                    "You can't attack yourself!")
            else:
                raise self.engine.exceptions.Impossible("Nothing to attack.")
                # attack_color = self.engine.colours['enemy_atk']
                # self.engine.message_log.add_message(
                #     text="There was no target to attack.", fg=attack_color)
                # return False
                # raise NotImplementedError()


class ShortBow(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, ATK_bonus=6)

    def get_action(self, entity: Actor) -> event_handler.WeaponSelectHandler:
        if not entity.equipment.item_is_equipped(item=self.parent):
            return actions.EquipmentAction(entity=entity, item=self.parent)
        if entity.equipment.weapon is self.parent:
            self.engine.message_log.add_message(
                text="Select a target.",
                fg=self.engine.colours['needs_target']
            )
            return event_handler.WeaponSelectHandler(
                engine=self.engine,
                item=self.parent,
                callback=lambda xy: actions.EquipmentAction(
                    entity=entity, item=self.parent, target_xy=xy),
                reach=4
            )

    def action(self, action: actions.EquipmentAction) -> None:
        if not action.entity.equipment.item_is_equipped(item=self.parent):
            action.entity.equipment.toggle_equip(equippable_item=self.parent)
        else:
            entity = action.entity
            target = action.target_actor
            target_xy = action.target_xy
            if target and target is not entity:
                entity.target = target
                hit_chance = random.randint(1, 20)
                hit_check = hit_chance+entity.fighter.ACC
                damage = random.sample(
                    range(*entity.fighter.ATK),
                    1)[0]
                attack_desc = f"{entity.name.capitalize()} shot at the {target.name}"
                attack_color = self.engine.colours['player_atk']
                if hit_chance == 20:
                    attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{entity.fighter.ACC} for a {hit_check}. \n{entity.name.capitalize()} scored a Critical Hit dealing {damage*2} damage."
                    target.fighter.take_damage(damage*2)
                elif hit_check >= target.fighter.DEF:
                    attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{entity.fighter.ACC} for a {hit_check}. \n{entity.name.capitalize()} dealt {damage} damage."
                    target.fighter.take_damage(damage)
                else:
                    attack_message = f"{attack_desc}. \nRolling a {hit_chance}+{entity.fighter.ACC} for a {hit_check}. \n{entity.name.capitalize()} missed."
                self.engine.message_log.add_message(
                    text=attack_message, fg=attack_color)
            elif target and target is entity:
                raise self.engine.exceptions.Impossible(
                    "You can't shoot yourself!")
            else:
                raise self.engine.exceptions.Impossible("Nothing to shoot.")
                # attack_color = self.engine.colours['enemy_atk']
                # self.engine.message_log.add_message(
                #     text="There was no target to attack.", fg=attack_color)
                # return False
                # raise NotImplementedError()


class LeatherArmour(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOUR, DEF_bonus=1)


class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOUR, DEF_bonus=3)


class PlateArmour(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOUR, DEF_bonus=6)
