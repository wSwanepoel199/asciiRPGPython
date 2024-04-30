from __future__ import annotations
from typing import Tuple, Iterator, List, TYPE_CHECKING, Any

import random, tcod
import multiprocessing as mp

import src.factory.actor_factory as actor_factory
import src.factory.item_factory as item_factory
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
    (item_factory.sword, 20)
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
    self.node = None

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

def place_enemies(
  room: RecRoom, 
  dungeon: GameMap, 
  floor_number: int
) -> None:
    entity_num = max(max(room.x2, room.y2)//10, 1)
    number_of_enemies = random.randint(0, entity_num)

    # number_of_enemies = random.randint(0, get_max_value_for_floor(max_value_by_floor=max_enemies_by_floor, floor=floor_number))

    monsters = get_entities_at_random(
      list_of_entities=available_enemies, 
      number_of_entities=number_of_enemies, 
      floor=floor_number
    )

    for entity in monsters:
      x = random.randint(a=room.x1 + 1, b=room.x2 - 1)
      y = random.randint(a=room.y1 + 1, b=room.y2 - 1)
      # entity = random.choice(list(available_enemies.values()))
      if not any(entity.x == x and entity.y == y for entity in dungeon.actors):
        # entity.fighter.Base_HP += (floor_number//2)
        # entity.fighter.Base_Max_HP += (floor_number//2)
        # entity.fighter.Base_DEF += (floor_number//2)
        # entity.fighter.Base_ATK[0] += (floor_number//2)
        # entity.fighter.Base_ATK[1] += (floor_number//2)
        entity.spawn(x=x, y=y, gamemap=dungeon)

def place_items(
  room: RecRoom, 
  dungeon: GameMap, 
  floor_number: int
) -> None:
  item_num = max(min(room.x2, room.y2)//10, 1)
  number_of_items = random.randint(0, item_num)
  # number_of_items = random.randint(0, get_max_value_for_floor(max_value_by_floor=max_items_by_floor, floor=floor_number))

  items = get_entities_at_random(
    list_of_entities=available_items, 
    number_of_entities=number_of_items, 
    floor=floor_number
  )

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

# def oldgenDungeon(
#     *,
#     map_width: int,
#     map_height: int,
#     min_room_size: int,
#     max_room_size: int,
#     room_limit: int,
#     engine:Engine
#     ) -> GameMap:
#   """Generate a new dungeon map."""
#   player = engine.player
#   dungeon = GameMap(
#     engine=engine, 
#     width=map_width, 
#     height=map_height, 
#     map_type="dungeon", 
#     entities=[player]
#   )
#   rooms: List[RecRoom] = []

#   center_of_last_room = (0, 0)

#   for r in range(room_limit):
#     room_width = random.randint(a=min_room_size, b=max_room_size)
#     room_height = random.randint(a=min_room_size, b=max_room_size)

#     x = random.randint(a=1, b=dungeon.width - room_width - 2)
#     y = random.randint(a=1, b=dungeon.height - room_height - 2)

#     new_room = RecRoom(x=x, y=y, width=room_width, height=room_height)

#     if any(new_room.intersects(other=other) for other in rooms):
#       continue

#     # dungeon.tiles[new_room.outer] = dungeon.tile_types["wall"]
#     dungeon.tiles[new_room.inner] = dungeon.tile_types["floor"]

#     if len(rooms) == 0:
#       player.place(*new_room.center, gamemap=dungeon)
#       x = new_room.center[0]
#       y = new_room.center[1]
#       # for item in available_items.values():
#       #   for i in item:
#       #     i[0].spawn(x=x, y=y, gamemap=dungeon)
#     else:
#       for x, y in genTunnel(start=rooms[-1].center, end=new_room.center):
#         dungeon.tiles[x,y] = dungeon.tile_types["floor"]

#       center_of_last_room = new_room.center

#       place_entities(room=new_room, dungeon=dungeon, floor_number=engine.game_world.current_floor)

#     dungeon.tiles[center_of_last_room] = dungeon.tile_types["stairs_down"]

#     dungeon.stairsdown = center_of_last_room

#     rooms.append(new_room)

#   i = 0
#   j = 0
#   wall_layout = []
#   while i < dungeon.height:
#     if i+1 >= dungeon.height:
#       break
#     while j < dungeon.width:
#       if dungeon.tiles[j,i] == dungeon.tile_types["mapfill"] or dungeon.tiles[j,i] == dungeon.tile_types["wall"] or not dungeon.tiles[j,i]:
#         j += 1
#         continue
#       if j+1 >= dungeon.width:
#         break
#       dungeon.placeWall(x=j,y=i,dungeon=dungeon)
#       j += 1
#     j = 0
#     i += 1

#   i = 0
#   j = 0
#   while i < dungeon.height:
#     if i+1 >= dungeon.height:
#       break
#     while j < dungeon.width:
#       if j+1 >= dungeon.width:
#         break
#       if dungeon.tiles[j,i] == dungeon.tile_types["wall"]:
#         wall_layout += [dungeon.modifyWall(x=j,y=i,dungeon=dungeon)]
#       j += 1
#     j = 0
#     i += 1

#   for wall in list(wall_layout):
#     if wall and len(wall) == 3:
#       dungeon.tiles[wall[0],wall[1]] = dungeon.tile_types[wall[2]]
#     else:
#       continue

#   return dungeon

def genTunnels(queue: mp.Queue, room: RecRoom, prev_room: RecRoom, dungeon: GameMap):
  
  start = prev_room.center
  end = room.center

  for x, y in genTunnel(start=start, end=end):
    if not dungeon.tiles[x-1,y] == dungeon.tile_types["floor"]:
      dungeon.tiles[x-1,y] = dungeon.tile_types["wall"]
    if not dungeon.tiles[x+1,y] == dungeon.tile_types["floor"]:
      dungeon.tiles[x+1,y] = dungeon.tile_types["wall"]
    if not dungeon.tiles[x,y-1] == dungeon.tile_types["floor"]:
      dungeon.tiles[x,y-1] = dungeon.tile_types["wall"]
    if not dungeon.tiles[x,y+1] == dungeon.tile_types["floor"]:
      dungeon.tiles[x,y+1] = dungeon.tile_types["wall"]
    if not dungeon.tiles[x+1,y+1] == dungeon.tile_types["floor"]:
      dungeon.tiles[x+1,y+1] = dungeon.tile_types["wall"]
    if not dungeon.tiles[x+1,y-1] == dungeon.tile_types["floor"]:
      dungeon.tiles[x+1,y-1] = dungeon.tile_types["wall"]
    if not dungeon.tiles[x-1,y-1] == dungeon.tile_types["floor"]:
      dungeon.tiles[x-1,y-1] = dungeon.tile_types["wall"]
    if not dungeon.tiles[x-1,y+1] == dungeon.tile_types["floor"]:
      dungeon.tiles[x-1,y+1] = dungeon.tile_types["wall"]
    dungeon.tiles[x,y] = dungeon.tile_types["floor"]
  queue.put(dungeon.tiles)

# https://roguebasin.com/index.php/Complete_Roguelike_Tutorial,_using_Python%2Blibtcod,_extras#BSP_Dungeon_Generator

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
  tunnels: List[RecRoom] = []
  center_of_last_room = (0, 0)
  bsp = tcod.bsp.BSP(
    x=1,
    y=1,
    width=dungeon.width-2,
    height=dungeon.height-2
  )
  bsp.split_recursive(
    depth=2+(dungeon.game_world.current_floor//2),
    min_width=min_room_size+1,
    min_height=min_room_size+1,
    max_horizontal_ratio=1.5,
    max_vertical_ratio=1.5,
  )

  for node in bsp.inverted_level_order():
    if node.children:
      print("Parent Node:\n %s" % node)
      node1, node2 = node.children
      print('Connect the rooms:\n%s\n%s' % (node1, node2))
      # if node.horizontal:
      #   tunnel = RecRoom(
      #     x=node1.x+node1.width//2,
      #     y=node1.y+node1.height//2,
      #     width=2,
      #     height=node2.y+node2.height//2-(node1.y+node1.height//2)
      #   )
      # else:
      #   tunnel = RecRoom(
      #     x=node1.x+node1.width//2,
      #     y=node1.y+node1.height//2,
      #     width=node2.x+node2.width//2-(node1.x+node1.width//2),
      #     height=2
      #     )

      # dungeon.tiles[tunnel.outer] = dungeon.tile_types["wall"]
      # tunnels.append(tunnel)
      node.x = min(node1.x, node2.x)
      node.y = min(node1.y, node2.y)
      node.width = max(node1.x+node1.width, node2.x+node2.width) - node.x
      node.height = max(node1.y+node1.height, node2.y+node2.height) - node.y
      # node split horizontally
      if node.horizontal:
        tunnel = RecRoom(
          x=node.x+node.width//2,
          y=node.y+node.height//2,
          width=2,
          height=node.height
        )
      else:
        tunnel = RecRoom(
          x=node.x+node.width//2,
          y=node.y+node.height//2,
          width=node.width,
          height=2
        )

      dungeon.tiles[tunnel.outer] = dungeon.tile_types["wall"]
      tunnels.append(tunnel)
    else:
      print('Dig a room for %s.' % node)
      minx = node.x 
      miny = node.y 
      maxx = node.width + node.x - 1
      maxy = node.height + node.y - 1
      
      if maxx >= dungeon.width - 1:
        maxx -= 1
      if maxy >= dungeon.height - 1:
        maxy -= 1
      
      # room_width = random.randint(a=min_room_size, b=node.width)
      # room_height = random.randint(a=min_room_size, b=node.height)
      # room_x = random.randint(a=node.x, b=node.x+node.width-room_width)
      # room_y = random.randint(a=node.y, b=node.y+node.height-room_height)
      # new_room = RecRoom(x=room_x, y=room_y, width=room_width-1, height= room_height-1)

      minx = random.randint(a=minx, b=maxx-min_room_size+1)
      miny = random.randint(a=miny, b=maxy-min_room_size+1)
      maxx = random.randint(a=minx+min_room_size-2, b=maxx)
      maxy = random.randint(a=miny+min_room_size-2, b=maxy)
      
      print(f"minx: {minx}, miny: {miny}, maxx: {maxx}, maxy: {maxy}")
      
      node.x = minx
      node.y = miny
      node.width = maxx-minx
      node.height = maxy-miny

      new_room = RecRoom(x=node.x, y=node.y, width=node.width, height=node.height)

      dungeon.tiles[new_room.outer] = dungeon.tile_types["wall"]
      # dungeon.tiles[new_room.inner] = dungeon.tile_types["floor"]

      new_room.node = node
      if len(rooms)==0:
        player.place(*new_room.center, gamemap=dungeon)
        # x = new_room.center[0]
        # y = new_room.center[1]
        # for item in available_items.values():
        #   for i in item:
        #     i[0].spawn(x=x, y=y, gamemap=dungeon)
      else:
        center_of_last_room = new_room.center

        place_enemies(room=new_room, dungeon=dungeon, floor_number=engine.game_world.current_floor)

      rooms.append(new_room)

  for room in rooms:
    dungeon.tiles[room.inner] = dungeon.tile_types["floor"]
    
    place_items(room=room, dungeon=dungeon, floor_number=engine.game_world.current_floor)

    dungeon.tiles[center_of_last_room] = dungeon.tile_types["stairs_down"]

    dungeon.stairsdown = center_of_last_room
  
  for tunnel in tunnels:
    dungeon.tiles[tunnel.inner] = dungeon.tile_types["floor"]
    
    place_items(room=tunnel, dungeon=dungeon, floor_number=engine.game_world.current_floor)

  wall_layout = []
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
