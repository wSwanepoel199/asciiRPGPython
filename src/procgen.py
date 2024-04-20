from __future__ import annotations
import random, tcod
from typing import Tuple, Iterator, Iterable, List, TYPE_CHECKING
from src.map import GameMap
if TYPE_CHECKING:
  from src.entity import Entity
  from src.engine import Engine

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
  
  def intersects(self, other: RecRoom) -> bool:
    """Return True if this room overlaps with another RectangularRoom."""
    return (
      self.point1[0] <= other.point2[0]
      and self.point2[0] >= other.point1[0]
      and self.point1[1] <= other.point2[1]
      and self.point2[1] >= other.point1[1]
    )

def genTunnel(start: Tuple[int,int], end: Tuple[int,int]) -> Iterator[Tuple[int,int]]:
  """Return an L-shaped tunnel between these two points."""
  x1, y1 = start
  x2, y2 = end

  if(random.random() < 0.5):
    corner_x = x2
    corner_y = y1
  else:
    corner_x = x1
    corner_y = y2
  
  for x, y in tcod.los.bresenham(start=(x1, y1), end=(corner_x,corner_y)).tolist():
    yield x, y
  for x,y in tcod.los.bresenham(start=(corner_x, corner_y), end=(x2, y2)).tolist():
    yield x, y

def genDungeon(
    *,
    x: int,
    y: int,
    w: int,
    h: int,
    min: int,
    max: int,
    room_limit: int,
    max_enemy_per_room: int,
    max_item_per_room: int,
    engine:Engine
    ) -> GameMap:
  """Generate a new dungeon map."""
  player = engine.player
  dungeon = GameMap(
    engine=engine, 
    x=x,
    y=y,
    width=w, 
    height=h, 
    map_type="dungeon", 
    entities=[player]
  )
  rooms: List[RecRoom] = []

  for r in range(room_limit):
    room_width = random.randint(a=min, b=max)
    room_height = random.randint(a=min, b=max)

    x = random.randint(a=1+dungeon.x, b=dungeon.width - room_width - 2)
    y = random.randint(a=1+dungeon.y, b=dungeon.height - room_height - 2)

    new_room = RecRoom(x=x, y=y, w=room_width, h=room_height)

    if any(new_room.intersects(other=other) for other in rooms):
      continue

    # dungeon.tiles[new_room.outer] = dungeon.tile_types["wall"]
    dungeon.tiles[new_room.inner] = dungeon.tile_types["floor"]

    if len(rooms) == 0:
      player.place(*new_room.center, gamemap=dungeon)
    else:
      for x, y in genTunnel(start=rooms[-1].center, end=new_room.center):
        dungeon.tiles[x,y] = dungeon.tile_types["floor"]

    dungeon.place_entities(room=new_room, maximum_monsters=max_enemy_per_room, maximum_items=max_item_per_room)

    rooms.append(new_room)
  i = dungeon.y
  j = dungeon.x
  while i < h-dungeon.y:
    if i+1 >= h-dungeon.y:
      break
    while j < w-dungeon.x:
      if dungeon.tiles[j,i] == dungeon.tile_types["mapfill"] or dungeon.tiles[j,i] == dungeon.tile_types["wall"] or not dungeon.tiles[j,i]:
        j += 1
        continue
      if j+1 >= w-dungeon.x:
        break
      dungeon.placeWall(x=j,y=i,dungeon=dungeon)
      j += 1
    j = dungeon.x
    i += 1


  return dungeon