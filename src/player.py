

player = {
  "name": '',
  "HP": 10,
  "MAX_HP": 10,
  "ATK": 2,
  "potions": 1,
  "elixirs": 0,
  "money": 0,
  "x": 0,
  "y": 0,
  "key": False,
  "combat": False,
}

class Player:
  def __init__(self, name, HP, ATK, potions, elixirs, money, x, y, key, combat):
    self.name = name
    self.HP = HP
    self.MAX_HP= HP
    self.ATK= ATK
    self.potions= potions
    self.elixirs= elixirs
    self.money=money
    self.x= x
    self.y= y
    self.key= key
    self.combat= combat

  def __str__(self):
    return f"{self.__dict__}"

  def __setitem__(self, key, value):
    setattr(self, key, value)

  def __getitem__(self, key):
    return getattr(self, key)

  def items(self):
    return self.__dict__.items()


  def heal(self):
    if self["potions"] > 0:
      self["potions"] -= 1
      self["HP"] += 5
      if self["HP"] > self["MAX_HP"]:
        self["HP"] = self["MAX_HP"]
        print("You used a potion and restored 5 HP!")
    else:
      print("You don't have any potions!")