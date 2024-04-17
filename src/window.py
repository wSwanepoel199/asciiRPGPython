from typing import NoReturn
import tcod
from src import entity
from action import Action, MovementAction, EscapeAction

def screen() -> NoReturn: 
  screen_width = 80
  screen_height = 60

  player = entity.Entity(args={
    'entityType': 'PLAYER',
    'icon': '@',
    'colour': 'white',
    'name': '',
    'HP': 50,
    'ATK': 3,
    'inventory':{
      'potions': 1,
      'elixirs': 0,
    },
    'money': 0,
    'x': int(screen_width/2),
    'y': int(screen_height/2),
    'location': 'overworld',
    'safe': True,
    'key': False,
    'combat': False
  })
  
  tileset = tcod.tileset.load_tilesheet(
    "./src/assets/dejavu10x10_gs_tc.png", columns=32, rows=8, charmap=tcod.tileset.CHARMAP_TCOD
  )

  with tcod.context.new_terminal(
    columns=screen_width,
    rows=screen_height,
    tileset=tileset,
    title="Rogue but worse",
    vsync=True,
  ) as context:
    root_console = tcod.console.Console(width=screen_width, height=screen_height, order="F")
    while True:
      root_console.print(x=0, y=0, string="Hello, world!", fg=(255, 255, 255))
      root_console.print(x=player.x, y=player.y, string="@", fg=(255, 255, 255))
      context.present(console=root_console)

      for event in tcod.event.wait():
        if event.type == "QUIT":
          raise SystemExit()
        
class EventHandler(tcod.event.EventDispatch[Action]):
  def ev_quit(self, event: tcod.event.Quit) -> NoReturn:
    raise SystemExit()

  def ev_keydown(self, event: tcod.event.KeyDown):# -> MovementAction | Any | None:
        action = None

        key = event.sym

        if key == tcod.event.K_UP:
            action = MovementAction(dx=0, dy=-1)
        elif key == tcod.event.K_DOWN:
            action = MovementAction(dx=0, dy=1)
        elif key == tcod.event.K_LEFT:
            action = MovementAction(dx=-1, dy=0)
        elif key == tcod.event.K_RIGHT:
            action = MovementAction(dx=1, dy=0)

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction()

        # No valid key was pressed
        return action