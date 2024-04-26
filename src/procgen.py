from __future__ import annotations
import random, tcod
import src.factory.actor_factory as actor_factory
import src.factory.item_factory as item_factory
from typing import Tuple, Iterator, List, TYPE_CHECKING
from src.map import GameMap
if TYPE_CHECKING:
  from src.engine import Engine

max_items_by_floor = [
  (1,1),
  (4,2),
]

max_enemies_by_floor = [
  (1,2),
  (4,3),
  (6,5)
]

available_enemies = {
  0: [
    (actor_factory.goblin, 70)
    ],
  3: [
    (actor_factory.slime, 80)
    ],
  5: [
    (actor_factory.orc, 50)
    ],
  10: [
    (actor_factory.dragon, 10)
    ],
}

available_items = {
  0 : [
    (item_factory.healing_potion, 80),
    (item_factory.lightning_bolt_scroll, 70),
    (item_factory.fireball_scroll, 60),
    (item_factory.dagger, 60),
    (item_factory.leather_armour, 30)
    ],
  2 : [
    (item_factory.cure_wounds_scroll, 40),
    (item_factory.sword, 30)
    ],
  4 : [
    (item_factory.confusion_scroll, 40),
    (item_factory.teleport_scroll, 40),
    (item_factory.chain_mail, 20)
    ],
}

def get_max_value_for_floor(max_value_by_floor, floor):
  current_value = 0
  for floor_minimum, value in max_value_by_floor:
    if floor_minimum > floor:
      break
    else:
      current_value = value
  return current_value

def get_entities_at_random(list_of_entities: dict, number_of_entities: int, floor: int) -> list:
  entity_weighted_chances = {}
  for key, values in list_of_entities.items():
    if key > floor:
      break
    else:
      for value in values:
        entity = value[0]
        weighted_chance = value[1]
        entity_weighted_chances[entity] = weighted_chance

  chosen_entities = random.choices(
    population=list(entity_weighted_chances.keys()), 
    weights=list(entity_weighted_chances.values()), 
    k=number_of_entities
  )
  return chosen_entities

class RecRoom:
  def __init__(self, x: int, y: int, width: int, height) -> None:
    self.x1 = x
    self.y1 = y
    self.x2 = x + width
    self.y2 = y + height

    # self.point1 = (x, y)
    # self.point2 = (x+w, y+h)

  @property
  def center(self) -> Tuple[int,int]:
    center_x = int((self.x1 + self.x2) / 2)
    center_y = int((self.y1 + self.y2) / 2)

    return center_x, center_y
  
  @property
  def inner(self) -> Tuple[int,int]:
    """Return the inner area of this room as a 2D array index."""
    return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)
  @property
  def outer(self) -> Tuple[int,int]:
    """Return the outer area of this room as a 2D array index."""
    return slice(self.x1, self.x2+1), slice(self.y1, self.y2+1)
  
  def intersects(self, other: RecRoom) -> bool:
    """Return True if this room overlaps with another RectangularRoom."""
    return (self.x1 <= other.x2 and
            self.x2 >= other.x1 and
            self.y1 <= other.y2 and
            self.y2 >= other.y1)

def place_entities(
  room: RecRoom, 
  dungeon: GameMap, 
  floor_number: int
) -> None:
    number_of_enemies = random.randint(0, get_max_value_for_floor(max_value_by_floor=max_enemies_by_floor, floor=floor_number))
    number_of_items = random.randint(0, get_max_value_for_floor(max_value_by_floor=max_items_by_floor, floor=floor_number))

    monsters = get_entities_at_random(
      list_of_entities=available_enemies, 
      number_of_entities=number_of_enemies, 
      floor=floor_number
    )
    items = get_entities_at_random(
      list_of_entities=available_items, 
      number_of_entities=number_of_items, 
      floor=floor_number
    )

    for entity in monsters:
      x = random.randint(a=room.x1 + 1, b=room.x2 - 1)
      y = random.randint(a=room.y1 + 1, b=room.y2 - 1)
      # entity = random.choice(list(available_enemies.values()))
      if not any(entity.x == x and entity.y == y for entity in dungeon.actors):
        entity.fighter.HP += floor_number//2
        entity.fighter.DEF += floor_number//2
        entity.fighter.ATK[0] += floor_number//2
        entity.fighter.ATK[1] += floor_number//2
        entity.spawn(x=x, y=y, gamemap=dungeon)
    
    for item in items:
      x = random.randint(a=room.x1 + 1, b=room.x2 - 1)
      y = random.randint(a=room.y1 + 1, b=room.y2 - 1)
      # entity = random.choice(list(available_items.values()))
      if not any(entity.x == x and entity.y == y for entity in dungeon.items):
        item.spawn(x=x, y=y, gamemap=dungeon)

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
    map_width: int,
    map_height: int,
    min_room_size: int,
    max_room_size: int,
    room_limit: int,
    engine:Engine
    ) -> GameMap:
  """Generate a new dungeon map."""
  player = engine.player
  dungeon = GameMap(
    engine=engine, 
    width=map_width, 
    height=map_height, 
    map_type="dungeon", 
    entities=[player]
  )
  rooms: List[RecRoom] = []

  center_of_last_room = (0, 0)

  for r in range(room_limit):
    room_width = random.randint(a=min_room_size, b=max_room_size)
    room_height = random.randint(a=min_room_size, b=max_room_size)

    x = random.randint(a=1, b=dungeon.width - room_width - 2)
    y = random.randint(a=1, b=dungeon.height - room_height - 2)

    new_room = RecRoom(x=x, y=y, width=room_width, height=room_height)

    if any(new_room.intersects(other=other) for other in rooms):
      continue

    # dungeon.tiles[new_room.outer] = dungeon.tile_types["wall"]
    dungeon.tiles[new_room.inner] = dungeon.tile_types["floor"]

    if len(rooms) == 0:
      player.place(*new_room.center, gamemap=dungeon)
      x = new_room.center[0]
      y = new_room.center[1]
      for item in available_items.values():
        for i in item:
          i[0].spawn(x=x, y=y, gamemap=dungeon)
    else:
      for x, y in genTunnel(start=rooms[-1].center, end=new_room.center):
        dungeon.tiles[x,y] = dungeon.tile_types["floor"]

      center_of_last_room = new_room.center

      place_entities(room=new_room, dungeon=dungeon, floor_number=engine.game_world.current_floor)

    dungeon.tiles[center_of_last_room] = dungeon.tile_types["stairs_down"]

    dungeon.stairsdown = center_of_last_room

    rooms.append(new_room)

  i = 0
  j = 0
  wall_layout = []
  while i < dungeon.height:
    if i+1 >= dungeon.height:
      break
    while j < dungeon.width:
      if dungeon.tiles[j,i] == dungeon.tile_types["mapfill"] or dungeon.tiles[j,i] == dungeon.tile_types["wall"] or not dungeon.tiles[j,i]:
        j += 1
        continue
      if j+1 >= dungeon.width:
        break
      dungeon.placeWall(x=j,y=i,dungeon=dungeon)
      j += 1
    j = 0
    i += 1

  i = 0
  j = 0
  while i < dungeon.height:
    if i+1 >= dungeon.height:
      break
    while j < dungeon.width:
      if j+1 >= dungeon.width:
        break
      if dungeon.tiles[j,i] == dungeon.tile_types["wall"]:
        wall_layout += [dungeon.modifyWall(x=j,y=i,dungeon=dungeon)]
      j += 1
    j = 0
    i += 1

  for wall in list(wall_layout):
    if wall and len(wall) == 3:
      dungeon.tiles[wall[0],wall[1]] = dungeon.tile_types[wall[2]]
    else:
      continue

  return dungeon