from __future__ import annotations

from typing import Iterable, Iterator, Optional, Tuple, TYPE_CHECKING

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
      x: int,
      y: int,
      width:int,
      height: int,
      # columns: int, 
      # rows: int, 
      map_type: str = "openworld", 
      entities: Iterable[Entity] = ()
    ) -> None:
    self.x = x
    self.y = y
    self.engine = engine
    self.width = width-min((width // 4), 55)
    self.height = height
    # self.columns = self.width
    # self.rows = rows
    self.offset = (width - self.columns)//2
    self.map_type = map_type
    self.tile_types = tile_types.tile_types
    self.seeing = np.full(
      shape=(self.columns, self.rows), 
      fill_value=False, 
      order="F"
    )
    self.seen = np.full(
      shape=(self.columns, self.rows), 
      fill_value=False, 
      order="F"
    )
    self.entities = set(entities)
    self.tiles = np.full(shape=(self.columns, self.rows), fill_value=self.tile_types["mapfill"], order="F")
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
  @property
  def columns(self) -> int:
    return min(self.width, self.height-2)
  @property
  def rows(self) -> int:
    return min(self.width, self.height-2)
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
    return 0 <= x < self.columns and 0 <= y < self.rows
  
  def render(self, console:tcod.console.Console) -> None:
    """
    Renders the map.

    If a tile is in the "visible" array, then draw it with the "light" colors.
    If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
    Otherwise, the default is "SHROUD".

    ╔ ╗ ╚ ╝ ╠ ╣ ║ ╩ ╬ ╦ ═
    """
    if not self.console:
      self.console = self.engine.context.new_console(
        min_columns=self.columns,
        min_rows=self.rows,
        order="F",
        magnification=1
      )
    # tcod.console.Console(
    #   width=self.columns,
    #   height=self.rows,
    #   order="F"
    # )

    self.console.rgb[0:self.columns, 0:self.rows] = np.select(
      condlist=[self.seeing, self.seen],
      choicelist=[self.tiles["light"], self.tiles["dark"]],
      default=self.tile_types['shroud'],
    )

    player = list(filter(lambda entity: entity['entity_type'] == 'PLAYER', self.entities))
    actors = list(filter(lambda entity: entity['entity_type'] == 'ACTOR', self.entities))
    objects = list(filter(lambda entity: entity['entity_type'] == 'OBJECT', self.entities))
    items = list(filter(lambda entity: entity['entity_type'] == 'ITEM', self.entities))

    for entity in objects + items + actors + player:
       if self.seeing[entity.x, entity.y]:
        self.console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.colour)
    # for entity in self.entities:
    #   if self.seeing[entity.x, entity.y]:
    #     console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.colour)
    
    self.console.blit(
      dest=console,
      dest_x=0+self.offset,
      dest_y=0+1,
      # src_x=self.x,
      # src_y=self.y,
      width=self.columns,
      height=self.rows
    )
    console.draw_frame(
      x=0,
      y=0,
      width=self.width,
      height=self.height,
      clear= False,
      fg=self.engine.colours['white'],
      decoration="╔═╗║ ║╚═╝"
    )

  
  def place_entities(
    self, 
    room: RecRoom, 
    # dungeon: GameMap, 
    maximum_monsters: int,
    maximum_items: int
  ) -> None:
    number_of_monsters = random.randint(a=0, b=maximum_monsters)
    number_of_items = random.randint(a=0, b=maximum_items)

    available_enemies = {
      "Goblin" : actor_factory.goblin,
      "Orc" : actor_factory.orc,
      "Slime" : actor_factory.slime,
      "Dragon" : actor_factory.dragon,
    }

    available_items = {
      "Healing Potion" : item_factory.healing_potion,
      "Cure Wounds Scroll": item_factory.cure_wounds_scroll,
      "Lightning Bolt Scroll" : item_factory.lightning_bolt_scroll,
      "Confusion Scroll": item_factory.confusion_scroll,
      "Teleport Scroll": item_factory.teleport_scroll,
      "Fireball Scroll": item_factory.fireball_scroll
    }

    for i in range(number_of_monsters):
      x = random.randint(a=room.point1[0] + 1, b=room.point2[0] - 1)
      y = random.randint(a=room.point1[1] + 1, b=room.point2[1] - 1)
      # entity = random.choice(list(available_enemies.values()))
      if not any(entity.x == x and entity.y == y for entity in self.actors):
        spawn_chance = random.random()
        # print("Enemy: ", spawn_chance)
        # if random.random() < 0.8 and not entity.name == "Dragon":
        if spawn_chance == 0:
          continue
        # elif spawn_chance < 0.2:
        #   available_enemies["Dragon"].spawn(gamemap=self, x=x, y=y)
        elif spawn_chance < 0.4:
          available_enemies["Orc"].spawn(gamemap=self, x=x, y=y)
        elif spawn_chance < 0.5:
          available_enemies["Slime"].spawn(gamemap=self, x=x, y=y)
        elif spawn_chance < 0.7:
          # entity.spawn(gamemap=self, x=x, y=y)
          available_enemies["Goblin"].spawn(gamemap=self, x=x, y=y)
    for i in range(number_of_items):
      x = random.randint(a=room.point1[0] + 1, b=room.point2[0] - 1)
      y = random.randint(a=room.point1[1] + 1, b=room.point2[1] - 1)
      # entity = random.choice(list(available_items.values()))
      if not any(entity.x == x and entity.y == y for entity in self.entities):
        spawn_chance = random.random()
        # print("Item: ", spawn_chance)
        if spawn_chance == 0:
          continue
        elif spawn_chance < 0.5:
          # random.choice([
          #   available_items["Cure Wounds Scroll"].spawn(gamemap=self, x=x, y=y),
          #   available_items["Confusion Scroll"].spawn(gamemap=self, x=x, y=y),
          #   available_items["Lightning Bolt Scroll"].spawn(gamemap=self, x=x, y=y),
          #   available_items["Teleport Scroll"].spawn(gamemap=self, x=x, y=y)
          # ])
          random.choice([
            available_items["Cure Wounds Scroll"],
            available_items["Confusion Scroll"],
            available_items["Lightning Bolt Scroll"],
            available_items["Teleport Scroll"],
            available_items["Fireball Scroll"]
          ]).spawn(gamemap=self, x=x, y=y)
        elif spawn_chance < 0.8:
          available_items["Healing Potion"].spawn(gamemap=self, x=x, y=y)

  def placeWall(self, x:int, y:int, dungeon: GameMap) -> None:
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