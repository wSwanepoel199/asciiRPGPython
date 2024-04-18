from __future__ import annotations
import random, tcod
from typing import Tuple, Iterator, Iterable, List, TYPE_CHECKING
from src.map import GameMap
from src.entity import enemy_stats
if TYPE_CHECKING:
  from src.entity import Entity

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

def place_entities(
  room: RecRoom, dungeon: GameMap, maximum_monsters: int,
) -> None:
  number_of_monsters = random.randint(a=0, b=maximum_monsters)
  for i in range(number_of_monsters):
    x = random.randint(a=room.point1[0] + 1, b=room.point2[0] - 1)
    y = random.randint(a=room.point1[1] + 1, b=room.point2[1] - 1)
    selectedEnemy = random.randint(a=1, b=len(enemy_stats))-1
    start = 0
    for key, value in enemy_stats.items():
      if start == selectedEnemy:
        selectedEnemy = value
        break
      else:
        start += 1
    if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
      if random.random() < 0.8:
        selectedEnemy.spawn(dungeon, x, y)
      else:
        pass  # TODO: Place a Troll here

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

def placeWall(x:int, y:int, dungeon: GameMap) -> None:
  if not dungeon.tiles[x+1,y] == dungeon.tile_types["floor"]:
    dungeon.tiles[x+1,y] = dungeon.tile_types["wall"]
  if not dungeon.tiles[x+1,y-1] == dungeon.tile_types["floor"]:
    dungeon.tiles[x+1,y-1] = dungeon.tile_types["wall"]
  if not dungeon.tiles[x,y-1] == dungeon.tile_types["floor"]:
    dungeon.tiles[x,y-1] = dungeon.tile_types["wall"]
  if not dungeon.tiles[x-1,y-1] == dungeon.tile_types["floor"]:
    dungeon.tiles[x-1,y-1] = dungeon.tile_types["wall"]
  if not dungeon.tiles[x-1,y] == dungeon.tile_types["floor"]:
    dungeon.tiles[x-1,y] = dungeon.tile_types["wall"]
  if not dungeon.tiles[x-1,y+1] == dungeon.tile_types["floor"]:
    dungeon.tiles[x-1,y+1] = dungeon.tile_types["wall"]
  if not dungeon.tiles[x,y+1] == dungeon.tile_types["floor"]:
    dungeon.tiles[x,y+1] = dungeon.tile_types["wall"]
  if not dungeon.tiles[x+1,y+1] == dungeon.tile_types["floor"]:
    dungeon.tiles[x+1,y+1] = dungeon.tile_types["wall"]

def genDungeon(
    *,
    w: int,
    h: int,
    min: int,
    max: int,
    room_limit: int,
    max_enemy_per_room: int,
    player: Entity,
    entities: Iterable[Entity],
    ) -> GameMap:
  """Generate a new dungeon map."""
  dungeon = GameMap(width=w, height=h, map_type="dungeon", entities=entities)
  
  rooms: List[RecRoom] = []

  for r in range(room_limit):
    room_width = random.randint(a=min, b=max)
    room_height = random.randint(a=min, b=max)

    x = random.randint(a=0, b=dungeon.width - room_width - 1)
    y = random.randint(a=0, b=dungeon.height - room_height - 1)

    new_room = RecRoom(x=x, y=y, w=room_width, h=room_height)

    if any(new_room.intersects(other=other) for other in rooms):
      continue

    # dungeon.tiles[new_room.outer] = dungeon.tile_types["wall"]
    dungeon.tiles[new_room.inner] = dungeon.tile_types["floor"]

    if len(rooms) == 0:
      player.x, player.y = new_room.center
    else:
      for x, y in genTunnel(start=rooms[-1].center, end=new_room.center):
        dungeon.tiles[x,y] = dungeon.tile_types["floor"]

    place_entities(room=new_room, dungeon=dungeon, maximum_monsters=max_enemy_per_room)

    rooms.append(new_room)
  i = 0
  j = 0
  while i < h:
    if i+1 >= h:
      break
    while j < w:
      if dungeon.tiles[j,i] == dungeon.tile_types["mapfill"] or dungeon.tiles[j,i] == dungeon.tile_types["wall"]:
        j += 1
        continue
      if j+1 >= w:
        break
      placeWall(x=j,y=i,dungeon=dungeon)
      j += 1
    j = 0
    i += 1


  return dungeon