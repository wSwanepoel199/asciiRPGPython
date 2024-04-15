import os

class Game:
  def __init__(self):
    self.run = True
    self.play = False
    self.safe = True

  def __setitem__(self, key, value):
    setattr(self, key, value)

  def __getitem__(self, key):
    return getattr(self, key)

  def clear(self):
    os.system('cls||clear')
  def draw(self):
    print("xX--------------------xX")