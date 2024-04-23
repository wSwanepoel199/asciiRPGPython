from __future__ import annotations
import random, tcod
import src.factory.item_factory as item_factory
from typing import Tuple, Iterator, List, TYPE_CHECKING
from src.map import GameMap
if TYPE_CHECKING:
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

available_items = {
  "Healing Potion" : item_factory.healing_potion,
  "Cure Wounds Scroll": item_factory.cure_wounds_scroll,
  "Lightning Bolt Scroll" : item_factory.lightning_bolt_scroll,
  "Confusion Scroll": item_factory.confusion_scroll,
  "Teleport Scroll": item_factory.teleport_scroll,
  "Fireball Scroll": item_factory.fireball_scroll
}

def genDungeon(
    *,
    width: int,
    height: int,
    columns: int,
    rows: int,
    min_room_size: int,
    max_room_size: int,
    room_limit: int,
    enemy_limit: int,
    item_limit: int,
    engine:Engine
    ) -> GameMap:
  """Generate a new dungeon map."""
  player = engine.player

  dungeon = GameMap(
    engine=engine, 
    x=0,
    y=0,
    width=width, 
    height=height, 
    # columns=columns,
    # rows=rows,
    map_type="dungeon", 
    entities=[player]
  )
  rooms: List[RecRoom] = []

  for r in range(room_limit):
    room_width = random.randint(a=min_room_size, b=max_room_size)
    room_height = random.randint(a=min_room_size, b=max_room_size)

    x = random.randint(a=1+dungeon.x, b=dungeon.columns - room_width - 2)
    y = random.randint(a=1+dungeon.y, b=dungeon.rows - room_height - 2)

    new_room = RecRoom(x=x, y=y, w=room_width, h=room_height)

    if any(new_room.intersects(other=other) for other in rooms):
      continue

    # dungeon.tiles[new_room.outer] = dungeon.tile_types["wall"]
    dungeon.tiles[new_room.inner] = dungeon.tile_types["floor"]

    if len(rooms) == 0:
      player.place(*new_room.center, gamemap=dungeon)
      x = new_room.center[0]
      y = new_room.center[1]
      for item in available_items.values():
        item.spawn(gamemap=dungeon, x=x, y=y)
    else:
      for x, y in genTunnel(start=rooms[-1].center, end=new_room.center):
        dungeon.tiles[x,y] = dungeon.tile_types["floor"]
      dungeon.place_entities(room=new_room, maximum_monsters=enemy_limit, maximum_items=item_limit)

    rooms.append(new_room)

  i = dungeon.y
  j = dungeon.x
  while i < dungeon.rows-dungeon.y:
    if i+1 >= dungeon.rows-dungeon.y:
      break
    while j < dungeon.columns-dungeon.x:
      if dungeon.tiles[j,i] == dungeon.tile_types["mapfill"] or dungeon.tiles[j,i] == dungeon.tile_types["wall"] or not dungeon.tiles[j,i]:
        j += 1
        continue
      if j+1 >= dungeon.columns-dungeon.x:
        break
      dungeon.placeWall(x=j,y=i,dungeon=dungeon)
      j += 1
    j = dungeon.x
    i += 1


  return dungeon