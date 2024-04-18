import random, tcod
from typing import Tuple, Iterator
from src.map import GameMap

class RecRoom:
  def __init__(self, x: int, y: int, w: int, h: int) -> None:
    self.point1 = (x, y)
    self.point2 = (x+w, y+h)

  @property
  def center(self) -> Tuple[int,int]:
    center_x = int((self.point1[0] + self.point2[0]) / 2)
    center_y = int((self.point1[1] + self.point2[1]) / 2)

    return center_x, center_y
  
  @property
  def inner(self) -> Tuple[int,int]:
    """Return the inner area of this room as a 2D array index."""
    return slice(self.point1[0]+1, self.point2[0]), slice(self.point1[1]+1, self.point2[1])
  @property
  def outer(self) -> Tuple[int,int]:
    """Return the outer area of this room as a 2D array index."""
    return slice(self.point1[0], self.point2[0]+1), slice(self.point1[1], self.point2[1]+1)
  
def genTunnel(start: Tuple[int,int], end: Tuple[int,int]) -> Iterator[Tuple[int,int], Tuple[int,int]]:
  """Return an L-shaped tunnel between these two points."""
  x1, y1 = start
  x2, y2 = end

  if(random.random() < 0.5):
    corner_x = x2
    corner_y = y1
  else:
    corner_x = x1
    corner_y = y2
  
  for x, y in tcod.los.bresenham((x1, y1), (corner_x,corner_y)).tolist():
    yield x, y
  for x,y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
    yield x, y


def genDungeon(w: int, h: int) -> GameMap:
  dungeon = GameMap(width=w, height=h, map_type="dungeon")

  room_1 = RecRoom(x=20, y=15, w=10, h=15)
  room_2 = RecRoom(x=35, y=25, w=10, h=15)

  dungeon.tiles[room_1.outer] = dungeon.tile_types["wall"]
  dungeon.tiles[room_2.outer] = dungeon.tile_types["wall"]
  dungeon.tiles[room_1.inner] = dungeon.tile_types["floor"]
  dungeon.tiles[room_2.inner] = dungeon.tile_types["floor"]

  for x, y in genTunnel(start=room_2.center, end=room_1.center):
    dungeon.tiles[x,y] = dungeon.tile_types["floor"]

  return dungeon