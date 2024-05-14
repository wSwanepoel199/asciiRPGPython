from __future__ import annotations
from typing import Tuple, Iterator, List, TYPE_CHECKING, Any, Union

import random
import tcod
import threading as mt
import multiprocessing as mp

import src.factory.actor_factory as actor_factory
import src.factory.item_factory as item_factory
from src.map import GameMap
from src.rooms.recroom import RecRoom
from src.rooms.tunnel import Tunnel

if TYPE_CHECKING:
    from src.engine import Engine

print_console = False

max_items_by_floor = [
    (1, 1),
    (4, 2),
]

max_enemies_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5)
]

available_enemies = {
    0: [
        (actor_factory.goblin, 60)
    ],
    3: [
        (actor_factory.slime, 40)
    ],
    5: [
        (actor_factory.orc, 30)
    ],
    10: [
        (actor_factory.dragon, 10)
    ],
}

available_items = {
    0: [
        (item_factory.healing_potion, 70),
        (item_factory.dagger, 50),
        (item_factory.leather_armour, 20)
    ],
    2: [
        (item_factory.lightning_bolt_scroll, 60),
        (item_factory.fireball_scroll, 50),
    ],
    3: [
        (item_factory.cure_wounds_scroll, 30),
        (item_factory.sword, 20)
    ],
    4: [
        (item_factory.teleport_scroll, 30),
    ],
    5: [
        (item_factory.confusion_scroll, 20),
        (item_factory.chain_mail, 10)
    ]
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


def place_enemies(
    lock: mt.Lock,
    room: Union[RecRoom, Tunnel],
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
        x, y = 0, 0
        if hasattr(room, "floors"):
            valid_spots = []
            if print_console:
                print("placing enemies on floor \n")
            for pos in room.floors:
                for tile in pos:
                    if tile:
                        valid_spots.append(tile)
            x, y = random.choice(valid_spots)
        else:
            if print_console:
                print("placing enemies at coords \n")
            if room.x1+1 >= room.x2-1:
                x = random.randint(a=room.x2-1, b=room.x1+1)
            else:
                x = random.randint(a=room.x1+1, b=room.x2-1)
            if room.y1+1 >= room.y2-1:
                y = random.randint(a=room.y2-1, b=room.y1+1)
            else:
                y = random.randint(a=room.y1+1, b=room.y2-1)
        # entity = random.choice(list(available_enemies.values()))
        lock.acquire()
        if not any(entity.x == x and entity.y == y for entity in dungeon.actors):
            if print_console:
                print("spawning enemy at ", x, " ", y, "\n")
            # entity.fighter.Base_HP += (floor_number//2)
            # entity.fighter.Base_Max_HP += (floor_number//2)
            # entity.fighter.Base_DEF += (floor_number//2)
            # entity.fighter.Base_ATK[0] += (floor_number//2)
            # entity.fighter.Base_ATK[1] += (floor_number//2)
            entity.spawn(x=x, y=y, gamemap=dungeon)
        lock.release()


def place_items(
    lock: mt.Lock,
    room: Union[RecRoom, Tunnel],
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
        x, y = 0, 0
        if hasattr(room, "floors"):
            valid_spots = []
            if print_console:
                print("placing items on floor \n")
            for pos in room.floors:
                for tile in pos:
                    if tile:
                        valid_spots.append(tile)
            x, y = random.choice(valid_spots)
        else:
            if print_console:
                print("placing items at coords \n")
            if room.x1+1 >= room.x2-1:
                x = random.randint(a=room.x2-1, b=room.x1+1)
            else:
                x = random.randint(a=room.x1+1, b=room.x2-1)
            if room.y1+1 >= room.y2-1:
                y = random.randint(a=room.y2-1, b=room.y1+1)
            else:
                y = random.randint(a=room.y1+1, b=room.y2-1)
        # entity = random.choice(list(available_items.values()))
        lock.acquire()
        if not any(entity.x == x and entity.y == y for entity in dungeon.items):
            if print_console:
                print("spawning items at ", x, " ", y, "\n")
            item.spawn(x=x, y=y, gamemap=dungeon)
        lock.release()


def genTunnel(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end

    if (random.random() < 0.5):
        corner_x = x2
        corner_y = y1
    else:
        corner_x = x1
        corner_y = y2

    for x, y in tcod.los.bresenham(start=(x1, y1), end=(corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham(start=(corner_x, corner_y), end=(x2, y2)).tolist():
        yield x, y

# https://roguebasin.com/index.php/Complete_Roguelike_Tutorial,_using_Python%2Blibtcod,_extras#BSP_Dungeon_Generator


def modWalls(wall_layout: list, dungeon: GameMap) -> None:
    i = 0
    j = 0
    while i < dungeon.height:
        if i+1 >= dungeon.height:
            break
        while j < dungeon.width:
            if j+1 >= dungeon.width:
                break
            if dungeon.tiles[j, i] == dungeon.tile_types["wall"]:
                wall_layout += [dungeon.modifyWall(x=j, y=i, dungeon=dungeon)]
            j += 1
        j = 0
        i += 1


def genDungeon(
    *,
    map_width: int,
    map_height: int,
    min_room_size: int,
    max_room_size: int,
    room_limit: int,
    engine: Engine
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
    map_width = dungeon.width-2
    map_height = dungeon.height-3

    bsp = tcod.bsp.BSP(
        x=1,
        y=1,
        width=map_width,
        height=map_height
    )

    bsp.split_recursive(
        depth=2+(dungeon.game_world.current_floor//2),
        min_width=min_room_size+1,
        min_height=min_room_size+1,
        max_horizontal_ratio=1.5,
        max_vertical_ratio=1.5,
    )

    for node in bsp.post_order():
        if not node.children:
            # print('Dig a room for %s.' % node)
            minx = node.x
            miny = node.y
            maxx = node.width + node.x - 1
            maxy = node.height + node.y - 1

            if maxx >= map_width - 1:
                maxx -= 1
            if maxy >= map_height - 1:
                maxy -= 1

            minx = random.randint(a=minx, b=max(maxx-min_room_size, minx+1))
            miny = random.randint(a=miny, b=max(maxy-min_room_size, miny+1))
            maxx = random.randint(a=minx+min_room_size-2, b=maxx)
            maxy = random.randint(a=miny+min_room_size-2, b=maxy)

            # print(f"minx: {minx}, miny: {miny}, maxx: {maxx}, maxy: {maxy}")

            node.x = minx
            node.y = miny
            node.width = maxx-minx
            node.height = maxy-miny

            new_room = RecRoom(
                x=node.x,
                y=node.y,
                width=node.width,
                height=node.height
            )

            new_room.genWalls(gamemap=dungeon)
            dungeon.tiles[new_room.inner] = dungeon.tile_types["floor"]

            new_room.node = node
            if len(rooms) == 0:
                player.place(*new_room.center, gamemap=dungeon)
                x = new_room.center[0]
                y = new_room.center[1]
                for item in available_items.values():
                    for i in item:
                        i[0].spawn(x=x, y=y, gamemap=dungeon)
            else:
                center_of_last_room = new_room.center

                # place_enemies(room=new_room, dungeon=dungeon,
                #               floor_number=engine.game_world.current_floor)

            rooms.append(new_room)

        else:
            # print("Parent Node:\n %s" % node)
            left, right = node.children
            while left.children:
                # left = random.choice(left.children)
                left = left.children[1]
            while right.children:
                # right = random.choice(right.children)
                right = right.children[0]
            # left = bsp.find_node(node1.x, node1.y)
            # right = bsp.find_node(node2.x, node2.y)

            # print('Connect the rooms:\n%s\n%s' % (left, right))
            node.x = min(left.x, right.x)
            node.y = min(left.y, right.y)
            node.width = max(left.x+left.width, right.x+right.width) - node.x
            node.height = max(left.y+left.height, right.y +
                              right.height) - node.y
            tunnel = None
            # tunnel_size = random.randint(a=2, b=4)
            tunnel_size = 3
            x1 = random.randint(
                a=left.x+1, b=max(left.x+left.width-1-tunnel_size, left.x+2)
            )
            y1 = random.randint(
                a=left.y+1, b=max(left.y+left.height-1-tunnel_size, left.y+2)
            )
            x3 = random.randint(
                a=right.x+1, b=max(right.x+right.width-1-tunnel_size, right.x+2)
            )
            y3 = random.randint(
                a=right.y+1, b=max(right.y+right.height-1-tunnel_size, right.y+2)
            )
            z2 = node.position
            # print("dig from (%s, %s) to (%s, %s) via (%s)" % (x1, y1, x3, y3, z2))
            if node.horizontal:
                y1 = left.y+left.height
                y3 = right.y
                z2 = random.randint(a=y1, b=y3)

                tunnel = Tunnel(
                    start=(x1, y1),
                    middle=(z2),
                    end=(x3, y3),
                    horizontal=True,
                    width=tunnel_size,
                    height=tunnel_size
                )
                tunnel.genWalls(dungeon)
                tunnel.genFloors(dungeon)
                tunnels.append(tunnel)

            else:
                x1 = left.x+left.width
                x3 = right.x

                z2 = random.randint(a=x1, b=x3)
                tunnel = Tunnel(
                    start=(x1, y1),
                    middle=(z2),
                    end=(x3, y3),
                    horizontal=False,
                    width=tunnel_size,
                    height=tunnel_size
                )
                tunnel.genWalls(dungeon)
                tunnel.genFloors(dungeon)
                tunnels.append(tunnel)

    dungeon.tiles[center_of_last_room] = dungeon.tile_types["stairs_down"]

    dungeon.stairsdown = center_of_last_room

    lock = mt.Lock()

    def populateRooms(lock: mt.Lock, rooms: list):
        for room in rooms:
            # dungeon.tiles[room.inner] = dungeon.tile_types["floor"]
            # room_spawn_enemies = mt.Thread(
            #     target=place_enemies,
            #     args=(
            #         lock,
            #         room,
            #         dungeon,
            #         engine.game_world.current_floor
            #     ))
            # room_spawn_enemies.start()
            place_enemies(
                lock=lock,
                room=room,
                dungeon=dungeon,
                floor_number=engine.game_world.current_floor
            )
            # room_spawn_items = mt.Thread(
            #     target=place_items,
            #     args=(
            #         lock,
            #         room,
            #         dungeon,
            #         engine.game_world.current_floor
            #     ))
            # room_spawn_items.start()
            place_items(
                lock=lock,
                room=room,
                dungeon=dungeon,
                floor_number=engine.game_world.current_floor
            )
    room_thread = mt.Thread(
        target=populateRooms,
        args=(lock, rooms)
    )

    def populateTunnels(lock: mt.Lock, tunnels: list):
        for tunnel in tunnels:
            # dungeon.tiles[tunnel.inner] = dungeon.tile_types["floor"]
            # if random.random() < 0.3:
            # tunnel_spawn_enemies = mt.Thread(
            #     target=place_enemies,
            #     args=(
            #         lock,
            #         tunnel,
            #         dungeon,
            #         engine.game_world.current_floor
            #     ))
            # tunnel_spawn_enemies.start()
            place_enemies(
                lock=lock,
                room=tunnel,
                dungeon=dungeon,
                floor_number=engine.game_world.current_floor
            )
            # if random.random() < 0.3:
            # tunnel_spawn_items = mt.Thread(
            #     target=place_items,
            #     args=(
            #         lock,
            #         tunnel,
            #         dungeon,
            #         engine.game_world.current_floor
            #     ))
            # tunnel_spawn_items.start()
            place_items(
                lock=lock,
                room=tunnel,
                dungeon=dungeon,
                floor_number=engine.game_world.current_floor
            )

    tunnel_thread = mt.Thread(
        target=populateTunnels,
        args=(lock, tunnels)
    )

    wall_layout = []

    def modifyWall(dungeon: GameMap, wall_layout: list):
        i = 0
        j = 0
        while i < dungeon.height:
            if i+1 >= dungeon.height:
                break
            while j < dungeon.width:
                if j+1 >= dungeon.width:
                    break
                if dungeon.tiles[j, i] == dungeon.tile_types["wall"]:
                    if print_console:
                        print("modding wall at (%s, %s)" % (j, i))
                    dungeon.modifyWall(
                        x=j,
                        y=i,
                        dungeon=dungeon,
                        wall_layout=wall_layout
                    )
                j += 1
            j = 0
            i += 1

    wall_thread = mt.Thread(
        target=modifyWall,
        args=(dungeon, wall_layout)
    )

    def updateWalls(wall_layout: list, dungeon: GameMap):
        for wall in list(wall_layout):
            if wall and len(wall) == 3:
                if print_console:
                    print("updating wall at (%s, %s)" % (wall[0], wall[1]))

                dungeon.tiles[wall[0], wall[1]] = dungeon.tile_types[wall[2]]
            else:
                continue

    wall_update_thread = mt.Thread(
        target=updateWalls,
        args=(wall_layout, dungeon)
    )

    room_thread.start()
    tunnel_thread.start()
    # wall_thread.start()
    # wall_thread.join()

    # wall_update_thread.start()

    # room_spawn_enemies.join()
    # room_spawn_items.join()
    # tunnel_spawn_enemies.join()
    # tunnel_spawn_items.join()
    room_thread.join()
    tunnel_thread.join()
    # wall_update_thread.join()

    return dungeon
