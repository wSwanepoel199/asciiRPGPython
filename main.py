print(__name__)
import random, tcod
from src.engine import Engine
from src.map import Map, GameMap
from src.event_handler import EventHandler
# from src.player import Player
from src.entity import Entity, enemy_stats
from src.combat import Combat
from src.menu import Menu
from src.save import Save
from src.game import Game
from src.procgen import genDungeon

initialLoad = True

def runGame() -> None:
  global initialLoad
  game = Game()
  player = Entity()
  menu = Menu()
  map = Map()

  while game.run:
    while menu.mainmenu:
      game.clear()
      player = menu.mainMenu(player=player, game=game)

    while game.play:
      Save().save(player=player)
      game.clear()
      tile = map.biomes[map.map[player["y"]][player["x"]]]
      if not player.safe or not initialLoad:
        if tile["e"]:
          selectEnemy = enemy_stats.items()[random.randint(a=0, b=len(enemy_stats)-1)]
          encounterCheck = random.randint(a=0, b=100)
          if encounterCheck < enemy_stats[selectEnemy]["spawn"]:
            player["combat"] = True
            combat = Combat(target=selectEnemy)
            game.play = combat.battle(player=player)
            menu.mainmenu = not game.play
            Save().save(player=player)
            game.clear()
      initialLoad = False
      if game.play:
        match player.location:
          case "TOWN":
            map.town(player=player)
          case "SHOP":
            map.shop(player=player)
          case "MAYOR":
            map.mayor(player=player)
          case "CAVE":
            map.cave(player=player)
          case "BOSS":
            combat = Combat(target="Dragon")
            game.play = combat.battle(player=player)
            menu.mainmenu = not game.play
            if game.play:
              player.location = "CAVE"
            Save().save(player=player)
            game.clear()
          case _:
            game.play = map.overworld(player=player, tile=tile)
            menu.mainmenu = not game.play

if __name__ == "__main__":
  # runGame()
  game = Game()
  game.addEntity(entity={
    'entityType': 'PLAYER',
    'char': '@',
    'colour': (255,255,255),
    'name': 'Test',
    'HP': 50,
    'ATK': 3,
    'inventory':{
      'potions': 1,
      'elixirs': 0,
    },
    'money': 0,
    'x': 0,
    'y': 0,
    'location': 'overworld',
    'safe': True,
    'key': False,
    'combat': False
  })

  game.addEntity(entity={
    'entityType': 'NPC',
    'char': '@',
    'colour': (255,255,0),
    'name': 'npc1',
    'HP': 50,
    'ATK': 3,
    'inventory':{
      'potions': 0,
      'elixirs': 0,
    },
    'money': 0,
    'x': 0,
    'y': 0,
    'location': 'overworld'
  })

  screen_width = 80
  screen_height = 45

  map_width = 80
  map_height = 45

  game.setPlayer(player = list(filter(lambda player: player['entityType'] == 'PLAYER', game.entities))[0])
  game.player.x = int(screen_width/2)
  game.player.y = int(screen_height/2)

  npc=game.entities[1]
  npc.x = int(screen_width/2)-5
  npc.y = int(screen_height/2)

  event_handler = EventHandler()

  # game_map = GameMap(width=80, height=45)

  game_map = genDungeon(w=map_width, h=map_height)

  engine = Engine(entities=game.entities, event_handler=event_handler, player=game.player, game_map=game_map)
  
  engine.createConsole(width=screen_width, height=screen_height, tileset_image="./src/assets/dejavu10x10_gs_tc.png", tileset_width=32, tileset_height=8)
  

  while True:
    engine.render()

    engine.handle_event(events=tcod.event.wait())
  # engine.screen(game=game)