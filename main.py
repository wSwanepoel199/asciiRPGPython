print(__name__)
import random, tcod, copy
import src.factory.entity_factory as entity_factory
from src.engine import Engine
from src.map import Map, GameMap
# from src.player import Player
from src.entity import Entity
from src.combat import Combat
from src.menu import Menu
from src.save import Save
from src.game import Game
from src.procgen import genDungeon

initialLoad = True

# def runGame() -> None:
#   global initialLoad
#   game = Game()
#   player = Entity()
#   menu = Menu()
#   map = Map()

#   while game.run:
#     while menu.mainmenu:
#       game.clear()
#       player = menu.mainMenu(player=player, game=game)

#     while game.play:
#       Save().save(player=player)
#       game.clear()
#       tile = map.biomes[map.map[player["y"]][player["x"]]]
#       if not player.safe or not initialLoad:
#         if tile["e"]:
#           selectEnemy = enemy_stats.items()[random.randint(a=0, b=len(enemy_stats)-1)]
#           encounterCheck = random.randint(a=0, b=100)
#           if encounterCheck < enemy_stats[selectEnemy]["spawn"]:
#             player["combat"] = True
#             combat = Combat(target=selectEnemy)
#             game.play = combat.battle(player=player)
#             menu.mainmenu = not game.play
#             Save().save(player=player)
#             game.clear()
#       initialLoad = False
#       if game.play:
#         match player.location:
#           case "TOWN":
#             map.town(player=player)
#           case "SHOP":
#             map.shop(player=player)
#           case "MAYOR":
#             map.mayor(player=player)
#           case "CAVE":
#             map.cave(player=player)
#           case "BOSS":
#             combat = Combat(target="Dragon")
#             game.play = combat.battle(player=player)
#             menu.mainmenu = not game.play
#             if game.play:
#               player.location = "CAVE"
#             Save().save(player=player)
#             game.clear()
#           case _:
#             game.play = map.overworld(player=player, tile=tile)
#             menu.mainmenu = not game.play

if __name__ == "__main__":
  # runGame()
  screen_width = 80
  screen_height = 45

  map_width = 80
  map_height = 45

  room_size_min = 6
  room_size_max = 10
  max_rooms = 30

  room_max_enemy = 2

  game = Game()

  # player = copy.deepcopy(Entity(
  #   entityType='PLAYER',
  #   char="@",
  #   name="Player",
  #   HP=50,
  #   ATK=3,
  #   inventory={
  #     'potion':1,
  #     'elixir':0
  #   },
  #   money=0,
  #   blocks_movement=True
  # ))

  player = copy.deepcopy(entity_factory.player)
  
  # game.addEntity(entity={
  #   'entityType': 'PLAYER',
  #   'char': '@',
  #   'colour': (255,255,255),
  #   'name': 'Test',
  #   'HP': 50,
  #   'ATK': 3,
  #   'inventory':{
  #     'potions': 1,
  #     'elixirs': 0,
  #   },
  #   'money': 0,
  #   'x': 0,
  #   'y': 0,
  #   'location': 'overworld',
  #   'safe': True,
  #   'key': False,
  #   'combat': False,
  #   'blocks_movement':True
  # })

  # for enemy in enemy_stats.values():
  #   game.addEntity(entity={
  #     'entityType': 'ENEMY',
  #     'char': enemy['char'],
  #     'colour': enemy['colour'],
  #     'name': enemy,
  #     'HP': enemy["HP"],
  #     'ATK': enemy["ATK"],
  #     'inventory':{
  #       'potions': 0,
  #       'elixirs': 0,
  #     },
  #     'money': 0,
  #     'x': 0,
  #     'y': 0,
  #     'location': 'overworld'
  #   })

  # game.addEntity(entity={
  #   'entityType': 'NPC',
  #   'char': '@',
  #   'colour': (255,255,0),
  #   'name': 'npc1',
  #   'HP': 50,
  #   'ATK': 3,
  #   'inventory':{
  #     'potions': 0,
  #     'elixirs': 0,
  #   },
  #   'money': 0,
  #   'x': int(screen_width/2)-5,
  #   'y': int(screen_height/2),
  #   'location': 'overworld'
  # })

  # game.setPlayer(player = list(filter(lambda player: player['entityType'] == 'PLAYER', game.entities))[0])

  engine = Engine(player=player)

  # game_map = GameMap(width=80, height=45)

  engine.game_map = genDungeon(
    w=map_width, 
    h=map_height, 
    min=room_size_min, 
    max=room_size_max, 
    room_limit=max_rooms, 
    max_enemy_per_room=room_max_enemy,
    engine=engine,
  )
  engine.update_fov()
  
  engine.createConsole(width=screen_width, height=screen_height, tileset_image="./src/assets/dejavu10x10_gs_tc.png", tileset_width=32, tileset_height=8)
  

  while True:
    engine.render()

    engine.event_handler.handle_events()