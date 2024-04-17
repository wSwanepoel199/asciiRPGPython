


from _collections_abc import dict_items
from typing import Any


class Player:
  def __init__(self, name, HP, ATK, potions, elixirs, money, x, y, key, combat) -> None:
    self.name = name
    self.HP = HP
    self.MAX_HP= HP
    self.ATK= ATK
    self.inventory = {
      "potions": potions,
      "elixirs": elixirs,
    }
    self.money=money
    self.x= x
    self.y= y
    self.location = "overworld"
    self.safe = True
    self.key= key
    self.combat= combat

  def __str__(self) -> str:
    return f"{self.__dict__}"

  def __setitem__(self, key, value) -> None:
    setattr(self, key, value)

  def __getitem__(self, key):# -> Any:
    return getattr(self, key)

  def items(self) -> dict_items[str, Any]:
    return self.__dict__.items()

  def heal(self, player) -> None:
    if player["potions"] > 0:
      player["potions"] -= 1
      player["HP"] += 5
      if player["HP"] > player["MAX_HP"]:
        player["HP"] = player["MAX_HP"]
        print("You used a potion and restored 5 HP!")
    else:
      print("You don't have any potions!")