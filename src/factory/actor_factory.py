import src.utils.constants as constants
from src.components.ai import HostileAi
from src.components.fighter import Fighter
from src.components.inventory import Inventory
from src.components.level import Level
from src.entity import Actor

player = Actor(
  entity_type="PLAYER",
  char=constants.player_char,
  colour=(255, 255, 255),
  name="Player",
  ai_cls=HostileAi,
  fighter=Fighter(HP=30, ATK=[2,5], DEF=1),
  inventory=Inventory(capacity=16),
  level=Level(level_up_base=50)
)

goblin = Actor(
  entity_type="ACTOR",
  char="G",
  colour=(0, 200, 0),
  name="Goblin",
  money=8,
  ai_cls=HostileAi,
  fighter=Fighter(HP=15, ATK=[1,3], DEF=0),
  level=Level(xp_given=10)
)
slime = Actor(
  entity_type="ACTOR",
  char="S",
  colour=(0, 133, 235),
  name="Slime",
  money=10,
  ai_cls=HostileAi,
  fighter=Fighter(HP=30, ATK=[2,3], DEF=2),
  level=Level(xp_given=25)
)

orc = Actor(
  entity_type="ACTOR",
  char="0",
  colour=(200, 200, 200),
  name="Orc",
  ai_cls=HostileAi,
  money=18,
  fighter=Fighter(HP=35, ATK=[2,6], DEF=1),
  level=Level(xp_given=50)
)


dragon = Actor(
  entity_type="ACTOR",
  char="D",
  colour=(210,0,0),
  name="Dragon",
  money=100,
  ai_cls=HostileAi,
  fighter=Fighter(HP=100, ATK=[5,10], DEF=5),
  level=Level(xp_given=200)
)