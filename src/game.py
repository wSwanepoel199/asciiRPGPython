import os

class Game:
  def __init__(self) -> None:
    self.run = True
    self.play = False
    self.safe = True

  def __setitem__(self, key, value) -> None:
    setattr(self, key, value)

  def __getitem__(self, key):# -> Any:
    return getattr(self, key)

  def clear(self) -> None:
    os.system('cls||clear')
  def draw(self) -> None:
    print("xX--------------------xX")