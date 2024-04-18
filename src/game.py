import os
from typing import Any
from src.entity import Entity
from src.menu import Menu

class Game:
  def __init__(self) -> None:
    self.run = True
    self.play = False
    self.safe = True
    self.player = {}
    self.entities = []
    self.menu = {}

  def __setitem__(self, key, value) -> None:
    setattr(self, key, value)

  def __getitem__(self, key) -> Any:
    return getattr(self, key)

  def clear(self) -> None:
    os.system('cls||clear')
  def draw(self) -> None:
    print("xX--------------------xX")

  def setPlayer(self, player) -> None:
    self.player = player
  
  def addEntity(self, entity) -> None:
    # listOfEntities = list(filter(lambda target: target['entityType'] == entity['entityType'], self.entities))
    self.entities.append(Entity(args=entity))
  
  def manageMenu(self) -> None:
    self.menu = Menu()
    self.menu.mainMenu(player=self.player, game=self)