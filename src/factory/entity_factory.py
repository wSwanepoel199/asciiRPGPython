from src.ai import HostileAi
from src.entity import Actor

player = Actor(
  char="@",
  colour=(255, 255, 255),
  name="Player",
  ai_cls=HostileAi,
  HP=30,
  ATK=5,
  DEF=2,
)

goblin = Actor(
  char="G",
  colour=(0, 200, 0),
  name="Goblin",
  ai_cls=HostileAi,
  HP=15,
  ATK=3,
  DEF=0,
  money=8
)

orc = Actor(
  char="0",
  colour=(200, 200, 200),
  name="Orc",
  ai_cls=HostileAi,
  HP=35,
  ATK=5,
  DEF=0,
  money=18
)

slime = Actor(
  char="S",
  colour=(0, 133, 235),
  name="Slime",
  ai_cls=HostileAi,
  HP=30,
  ATK=2,
  DEF=0,
  money=10
)

dragon = Actor(
  char="D",
  colour=(210,0,0),
  name="Dragon",
  ai_cls=HostileAi,
  HP=100,
  ATK=8,
  DEF=0,
  money=100
)