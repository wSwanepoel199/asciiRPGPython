from __future__ import annotations

from typing import TYPE_CHECKING

from src.components.base_component import BaseComponent

if TYPE_CHECKING:
  from src.entity import Actor

class Level(BaseComponent):
  parent: Actor

  def __init__(
    self, 
    curr_level: int = 1,
    curr_xp: int = 0,
    level_up_base:int = 0,
    level_up_factor:int = 25,
    xp_given: int = 0,
  ):
    self.curr_level = curr_level
    self.curr_xp = curr_xp
    self.level_up_base = level_up_base
    self.level_up_factor = level_up_factor
    self.xp_given = xp_given
  
  @property
  def xp_to_next_level(self) -> int:
    return self.level_up_base + (self.curr_level-1) * self.level_up_factor
  
  @property
  def can_level_up(self) -> bool:
    return self.curr_xp >= self.xp_to_next_level

  def add_xp(self, xp: int) -> None:
    if xp <= 0 or self.level_up_base <= 0:
      return
    
    self.curr_xp += xp
    self.engine.message_log.add_message(
      text=f"You gain {xp} experience points.",
      fg=self.engine.colours['green']
    )

    # if self.can_level_up:
    #   self.engine.message_log.add_message(
    #     text=f"You advance to level {self.curr_level+1}!", 
    #     fg="green"
    #   )
  def increase_level(self) -> None:
    self.curr_xp -= self.xp_to_next_level

    self.curr_level += 1

  def increase_stat(self, stat: str, value: int) -> None:
    match stat:
      case "HP":
        hp = self.parent.fighter.HP
        maxhp = self.parent.fighter.MAX_HP
        if hp == maxhp:
          self.parent.fighter.MAX_HP += value
          self.parent.fighter.HP += value
        else:
          self.parent.fighter.MAX_HP += value
        self.engine.message_log.add_message(text="Your health improves!")
        self.increase_level()
      case "ATK":
        (min_atk,max_atk) = self.parent.fighter.ATK
        atk_average = (min_atk + max_atk) // 2
        max_increase = atk_average % value
        min_increase = atk_average % (value+1)
        # print(f"Increase Amount: {value}, Max Increase: {max_increase}, Min Increase: {min_increase}")
        self.engine.message_log.add_message(text="You feel stronger!")
        self.parent.fighter.ATK = (min_atk + min_increase, max_atk + max_increase)
        self.increase_level()
      case "DEF":
        self.engine.message_log.add_message(
          text="You become more resilient to blows!")
        self.parent.fighter.DEF += value
        self.increase_level()