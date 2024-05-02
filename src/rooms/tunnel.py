from __future__ import annotations

from typing import Tuple

class Tunnel:
  def __init__(self, start: Tuple[int,int], end: Tuple[int,int], width: int = 2, height: int = 2):
    self.x1, self.y1 = start
    x,y = end
    self.x2, self.y2 = x + width, y + height
    self.width = width
  
  @property
  def center(self) -> Tuple[int,int]:
    center_x = (self.x1 + self.x2) // 2
    center_y = (self.y1 + self.y2) // 2

    return center_x, center_y
  
  @property
  def inner(self) -> Tuple[int,int]:
    """Return the inner area of this room as a 2D array index."""
    return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)
  @property
  def outer(self) -> Tuple[int,int]:
    """Return the outer area of this room as a 2D array index."""
    return slice(self.x1, self.x2+1), slice(self.y1, self.y2+1)