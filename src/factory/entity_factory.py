from src.components.ai import HostileAi
from src.components.fighter import Fighter
from src.entity import Actor

player = Actor(
  entityType="PLAYER",
  char="@",
  colour=(255, 255, 255),
  name="Player",
  ai_cls=HostileAi,
  fighter=Fighter(HP=30, ATK=5, DEF=2)
)

goblin = Actor(
  entityType="ACTOR",
  char="G",
  colour=(0, 200, 0),
  name="Goblin",
  money=8,
  ai_cls=HostileAi,
  fighter=Fighter(HP=15, ATK=3, DEF=0)
)

orc = Actor(
  entityType="ACTOR",
  char="0",
  colour=(200, 200, 200),
  name="Orc",
  ai_cls=HostileAi,
  money=18,
  fighter=Fighter(HP=35, ATK=5, DEF=0)
)

slime = Actor(
  entityType="ACTOR",
  char="S",
  colour=(0, 133, 235),
  name="Slime",
  money=10,
  ai_cls=HostileAi,
  fighter=Fighter(HP=30, ATK=2, DEF=0)
)

dragon = Actor(
  entityType="ACTOR",
  char="D",
  colour=(210,0,0),
  name="Dragon",
  money=100,
  ai_cls=HostileAi,
  fighter=Fighter(HP=100, ATK=8, DEF=0)
)