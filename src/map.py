from __future__ import annotations

from typing import Iterable, Optional, TYPE_CHECKING, Tuple

import numpy as np
import tcod, random

import src.tile_types as tile_types
from src.game import Game
from src.save import Save
from src.entity import Actor, Item
import src.factory.actor_factory as actor_factory
import src.factory.item_factory as item_factory

if TYPE_CHECKING:
    from src.entity import Entity
    from src.engine import Engine
    from src.procgen import RecRoom

class Map:
  def __init__(self, ) -> None:
    self.map = [
      ["P","P","P","P","F","M","C"],
      ["F","F","F", "F", "F", "H", "M"],
      ["F","Fl","B", "P", "H", "F", "H"],
      ["P","Fl","T", "Fl", "P", "H", "M"],
      ["P","Fl","Fl", "P", "H", "M", "M"]
    ]
    self.biomes = {
      "P": {
        "t": "PLAINS",
        "e": True},
      "F": {
        "t": "WOODS",
        "e": True},
      "Fl": {
        "t": "FIELDS",
        "e": False},
      "B": {
        "t": "BRIDGE",
        "e": True},
      "T": {
        "t": "TOWN",
        "e": False},
      "S": {
        "t": "SHOP",
        "e": False},
      "Ma": {
        "t": "MAYOR",
        "e": False},
      "C": {
        "t": "CAVE",
        "e": False},
      "M": {
        "t": "MOUNTAIN",
        "e": True},
      "H": {
        "t": "HILLS",
        "e": True,
      }
    }
    self.x_len = len(self.map[0])-1
    self.y_len = len(self.map)-1
    self.boss = False

  def __str__(self) -> str:
    return f"{self.__dict__}"
  
  def __setitem__(self, key, value) -> None:
    setattr(self, key, value)

  def __getitem__(self, key):# -> Any:
    return getattr(self, key)
  
  def overworld(self, player, tile) -> bool:
    Game().draw()
    print("Current location: " + tile['t'])
    Game().draw()

    print("STATS")
    print("  Name - " + player["name"])
    print("  HP - " + str(object=player["HP"]) + "/" + str(object=player["MAX_HP"]))
    print("  ATK - " + str(object=player["ATK"]))
    print("  Potion(s) - " + str(object=player["potions"]))
    print("  Elixir(s) - " + str(object=player["elixirs"]))
    print("  Coin(s) - " + str(object=player["money"]))
    Game().draw()
    print("Available actions:")
    if player["y"] > 0:
      print("  1 - Move North")
    if player["x"] < self.x_len:
      print("  2 - Move East")
    if player["y"] < self.y_len:
      print("  3 - Move South")
    if player["x"] > 0:
      print("  4 - Move West")
    if player["potions"] > 0:
      print("  5 - Use Potion")
    if tile["t"] == "TOWN":
      print('  6 - Enter Town')
    if tile["t"] == "CAVE":
      print('  6 - Enter Cave')
    print('  quit - Exit Game')
    Game().draw()

    choice = input(prompt="#> ")

    match choice:
      case 'quit':
        Save().save(player=player)
        return False
      case "1":
        if player["y"] > 0:
          player["y"] -= 1
          player.safe = False
        else :
          print("You can't go that way")
      case "2":
        if player["x"] < self.x_len:
          player["x"] += 1
          player.safe = False
        else:
          print("You can't go that way")
      case "3":
        if player["y"] < self.y_len:
          player["y"] += 1
          player.safe = False
        else:
          print("You can't go that way")
      case "4":
        if player["x"] > 0:
          player["x"] -= 1
          player.safe = False
        else:
          print("You can't go that way")
      case "5":
        player.safe = True
        player.heal(player)
      case "6":
        if tile["t"] == "TOWN":
          player.location = "TOWN"
        if tile['t'] == "CAVE":
          player.location = "CAVE"
      case _:
        player.safe = True
    return True

  def town(self, player) -> None:
    print("Town")
    while player.location == "TOWN":
      Game().clear()
      Game().draw()
      print("Welcome to the Town!")
      Game().draw()
      print("STATS")
      print("  Name - " + player["name"])
      print("  HP - " + str(object=player["HP"]) + "/" + str(object=player["MAX_HP"]))
      print("  ATK - " + str(object=player["ATK"]))
      print("  Potion(s) - " + str(object=player["potions"]))
      print("  Elixir(s) - " + str(object=player["elixirs"]))
      print("  Coin(s) - " + str(object=player["money"]))
      Game().draw()
      print("Available actions:")
      print('  1 - Go Shopping')
      print('  2 - Talk to Mayor')
      print('  3 - Leave Town')
      Game().draw()
      choice = input(prompt="#> ")

      match choice:
        case "1":
          player.location = "SHOP"
          print("You enter the local Store")
        case "2":
          player.location = "MAYOR"
          print('You go to the mayor')
        case "3":
          player.location = "OVERWORLD"
          print("You leave town to go exploring")
        case _:
          pass
      input(prompt="> ")

  def shop(self, player):
    print("Shop")
    while player.location == "SHOP":
      Game().clear()
      Game().draw()
      print("Welcome to the shop!")
      Game().draw()
      print("INVENTORY:")
      print("  Potions: " + str(object=player.potions))
      print("  Elixirs: " + str(object=player.elixirs))
      print("  ATK: " + str(object=player.ATK))
      print("  Gold: " + str(object=player.money))
      Game().draw()
      print("Available actions:")
      print("  1 - Buy Potion (+30 HP) - 5 Gold")
      print("  2 - Buy Elixir (+1 ATK) - 8 Gold")
      print("  3 - Upgrade Weapon (+2 ATK) - 10 Gold")
      print("  4 - Exit Shop")
      Game().draw()
      choice = input(prompt="#> ")

      match choice:
        case "1":
          if player.money >= 5:
            player.money -= 5
            player.potions += 1
            print("You bought a potion!")
          else:
            print("You don't have enough gold!")
        case "2":
          if player.money >= 8:
            player.money -= 8
            player.elixirs += 1
            print("You bought an elixir!")
          else:
            print("You don't have enough gold!")
        case "3":
          if player.money >= 10:
            player.ATK += 2
            player.money -= 10
            print("You improved your weapon!")
          else:
            print("You don't have enough gold!")
        case "4":
          player.location = "TOWN"
        case _:
          pass
      input(prompt="> ")


  def mayor(self, player):
    print("Mayor")
    while player.location == "MAYOR":
        Game().clear()
        Game().draw()
        print("Hello there, " + player.name + "!")
        if player.ATK < 10:
          print("You don't look strong enough to face the dragon! Come back once you've grown stronger!")
        else:
          print("You look like you might stand a chance against the dragon! Take this key and go to the cave far north east from here. But be on your guard that beast is dangerous!")
          player.key = True
        Game().draw()
        print("Available actions:")
        print("  1 - Return to the Town")
        Game().draw()

        choice = input("# ")

        if choice == "1":
          player.location = "TOWN"

  def cave(self, player):
    print("Cave")
    while  player.location == 'CAVE':
      Game().clear()
      Game().draw()
      print("Here be Dragons! Unseal the beast to claim its life?")
      Game().draw()
      print("Available actions:")
      if player.key:
        print("  1 - Use key to unseal the Dragon")
        print('  2 - Leave the Cave')
      else:
        print('  1 - Leave the Cave')
      Game().draw()
      choice = input("#> ")

      match choice:
        case "1":
          if player.key:
            print("You unseal the Dragon! Prepare for a FIGHT...")
            player.combat = True
            player.location = "BOSS"
          else:
            player.location = "OVERWORLD"
            print("You decide to leave the Dragon to its sealed slumber!")
        case "2":
          player.location = "OVERWORLD"
          print("You decide to leave the Dragon to its sealed slumber!")
        case _:
          pass
      input("> ")
# Moved map sizing to use columns and rows and map render sizing to use width and height, need to switch map generation to feed both
class GameMap:
  def __init__(
      self, 
      engine: Engine,
      width:int,
      height: int,
      map_type: str = "openworld", 
      entities: Iterable[Entity] = (),
    ) -> None:
    # self.x = x
    # self.y = y
    
    self.engine = engine
    self.width = width
    self.height = height
    # self.columns = width
    # self.rows = height
    self.map_type = map_type
    self.entities = set(entities)
    self.tile_types = tile_types.tile_types
    self.tiles = np.full(shape=(self.width, self.height), fill_value=self.tile_types["mapfill"], order="F")
    self.visible = np.full(shape=(self.width, self.height), fill_value=False, order="F")
    self.explored = np.full(shape=(self.width, self.height), fill_value=False, order="F")
    self.stairsdown = (0,0)
    self.console = None
    # match map_type:
    #   # case "dungeon":
    #   #   self.tiles = np.full(shape=(width, height), fill_value=self.tile_types["wall"], order="F")
    #   case _:
    #     self.tiles = np.full(shape=(width, height), fill_value=self.tile_types["mapfill"], order="F")
  
  @property
  def gamemap(self) -> GameMap:
    return self
  @property
  def actors(self) -> Iterable[Actor]:
    yield from (
      entity
      for entity in self.entities
      if isinstance(entity, Actor) and entity.alive
    )
  @property
  def items(self) -> Iterable[Item]:
    yield from (
      entity
      for entity in self.entities
      if isinstance(entity, Item)
    )
  @property
  def player(self) -> Actor:
    return self.engine.player
  def get_blocking_entity(self, x:int, y:int) -> Optional[Entity]:
    for entity in self.entities:
      if (
        entity.blocks_movement 
        and entity.x == x 
        and entity.y == y
      ):
        return entity
    return None
  def get_actor_at_location(self, x:int, y:int) -> Optional[Actor]:
    for actor in self.actors:
      if actor.x == x and actor.y == y:
        return actor
    return None
  def in_bounds(self, x: int, y: int) -> bool:
    """Return True if x and y are inside the bounds of the map."""
    return 0 <= x < self.width and 0 <= y < self.height
  
  def get_viewport(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    x = self.player.x
    y = self.player.y
    width = self.engine.game_world.viewport_width
    height = self.engine.game_world.viewport_height
    half_width = width // 2
    half_height = height // 2
    start_x = x - half_width if x - half_width >= 0 else 0
    start_y = y - half_height if y - half_height >= 0 else 0
    
    end_x = start_x + width
    end_y = start_y + height

    
    if end_x > self.width:
      x_diff = end_x - self.width
      start_x -= x_diff
      end_x -= x_diff
      # end_x = self.width

    if end_y > self.height:
      y_diff = end_y - self.height
      start_y -= y_diff
      end_y -= y_diff
      # end_y = self.height

    return ((start_x, start_y), (end_x-1, end_y-1))


  def render(self, console:tcod.console.Console) -> None:
    """
    Renders the map.

    If a tile is in the "visible" array, then draw it with the "light" colors.
    If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
    Otherwise, the default is "SHROUD".

    ╔ ╗ ╚ ╝ ╠ ╣ ║ ╩ ╬ ╦ ═
    """
    self.console = console
    (x1,y1),(x2,y2) = self.get_viewport()

    viewport_width = self.engine.game_world.viewport_width
    viewport_height = self.engine.game_world.viewport_height

    offset_x = slice(x1, x2+1)
    offset_y = slice(y1, y2+1)
    viewport_tiles = self.tiles[offset_x, offset_y]
    viewport_visible = self.visible[offset_x, offset_y]
    viewport_explored = self.explored[offset_x, offset_y]

    # if not self.console:
    # self.console = self.engine.context.new_console(
    #   min_columns=self.columns,
    #   min_rows=self.rows,
    #   order="F"
    # )
    # self.console = tcod.console.Console(
    #   width=self.columns,
    #   height=self.rows,
    #   order="F"
    # )
    # self.xoffset = (console.width - self.engine.side_console - self.console.width)//2
    # self.yoffset = (console.height - self.console.height)//2
    # self.xoffset = 0
    # self.yoffset = 0
    
    # self.console.rgb[0:self.columns, 0:self.rows] = np.select(
    #   condlist=[self.visible, self.explored],
    #   choicelist=[self.tiles["light"], self.tiles["dark"]],
    #   default=self.tile_types['shroud'],
    # )

    self.console.rgb[0:viewport_width, 0:viewport_height] = np.select(
      condlist=[viewport_visible, viewport_explored],
      choicelist=[viewport_tiles["light"], viewport_tiles["dark"]],
      default=self.tile_types['shroud'],
    )

    player = list(filter(lambda entity: entity['entity_type'] == 'PLAYER', self.entities))
    actors = list(filter(lambda entity: entity['entity_type'] == 'ACTOR', self.entities))
    objects = list(filter(lambda entity: entity['entity_type'] == 'OBJECT', self.entities))
    items = list(filter(lambda entity: entity['entity_type'] == 'ITEM', self.entities))

    for entity in objects + items + actors + player:
       if self.visible[entity.x, entity.y]:
        self.console.print(
          x=entity.x-x1,
          y=entity.y-y1,
          string=entity.char, 
          fg=entity.colour
        )
    
    # self.console.blit(
    #   dest=console,
    #   dest_x=0+self.xoffset,
    #   dest_y=0+self.yoffset,
    #   src_x=0,
    #   src_y=0,
    #   width=self.console.width,
    #   height=self.console.height
    # )
    console.draw_frame(
      x=0,
      y=0,
      width=console.width-self.engine.side_console,
      height=console.height,
      clear= False,
      fg=self.engine.colours['white'],
      decoration="╔═╗║ ║╚═╝"
    )

  def placeWall(self, x:int, y:int, dungeon: GameMap) -> None:
    if dungeon.tiles[x+1,y] == dungeon.tile_types["mapfill"]:
      dungeon.tiles[x+1,y] = dungeon.tile_types["wall"]
    if dungeon.tiles[x+1,y-1] == dungeon.tile_types["mapfill"]:
      dungeon.tiles[x+1,y-1] = dungeon.tile_types["wall"]
    if dungeon.tiles[x,y-1] == dungeon.tile_types["mapfill"]:
      dungeon.tiles[x,y-1] = dungeon.tile_types["wall"]
    if dungeon.tiles[x-1,y-1] == dungeon.tile_types["mapfill"]:
      dungeon.tiles[x-1,y-1] = dungeon.tile_types["wall"]
    if dungeon.tiles[x-1,y] == dungeon.tile_types["mapfill"]:
      dungeon.tiles[x-1,y] = dungeon.tile_types["wall"]
    if dungeon.tiles[x-1,y+1] == dungeon.tile_types["mapfill"]:
      dungeon.tiles[x-1,y+1] = dungeon.tile_types["wall"]
    if dungeon.tiles[x,y+1] == dungeon.tile_types["mapfill"]:
      dungeon.tiles[x,y+1] = dungeon.tile_types["wall"]
    if dungeon.tiles[x+1,y+1] == dungeon.tile_types["mapfill"]:
      dungeon.tiles[x+1,y+1] = dungeon.tile_types["wall"]

class GameWorld:
  """
  Holds the settings for the GameMap, and generates new maps when moving down the stairs.
  """

  def __init__(
    self,
    *,
    engine: Engine,
    viewport_width: int,
    viewport_height: int,
    room_limit: int,
    min_room_size: int,
    max_room_size: int,
    current_floor: int = 0
    ):
    self.engine = engine

    self.viewport_width = viewport_width
    self.viewport_height = viewport_height
    self.min_map_width = viewport_width
    self.min_map_height = viewport_height
    print(viewport_width, viewport_height)
    self.room_limit = room_limit

    self.min_room_size = min_room_size
    self.max_room_size = max_room_size

    # self.enemy_limit = enemy_limit
    # self.item_limit = item_limit

    self.current_floor = current_floor
  
  def gen_floor(self) -> None:
    from src.procgen import genDungeon

    self.current_floor += 1

    self.engine.game_map = genDungeon(
      map_width=70 + self.current_floor * 10,
      map_height=70 + self.current_floor * 10,
      min_room_size=self.min_room_size,
      max_room_size=self.min_room_size,
      room_limit=self.room_limit,
      # enemy_limit=self.enemy_limit,
      # item_limit=self.item_limit,
      engine=self.engine
    )