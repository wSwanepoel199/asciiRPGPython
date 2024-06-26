import src.utils.constants as constants
from src.components.ai import HostileAi
from src.components.fighter import Fighter
from src.components.inventory import Inventory, Equipment
from src.components.level import Level
from src.components.enemy_type import Goblin, Slime
from src.entity import Actor

player = Actor(
    entity_type="PLAYER",
    char=constants.player_char,
    colour=(255, 255, 255),
    name="Player",
    ai_cls=HostileAi,
    fighter=Fighter(
        Base_HP=30,
        Base_ATK=[2, 3],
        Base_DEF=10,
        Base_ACC=2
    ),
    equipment=Equipment(),
    inventory=Inventory(capacity=16),
    # level=Level(level_up_base=50)
)

goblin = Actor(
    entity_type="ACTOR",
    char="G",
    colour=(0, 200, 0),
    name="Goblin",
    money=8,
    ai_cls=HostileAi,
    fighter=Fighter(
        Base_HP=15,
        Base_ATK=[2, 3],
        Base_DEF=10,
        Base_ACC=2),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    enemy_type=Goblin(),
    # level=Level(xp_given=10)
)
slime = Actor(
    entity_type="ACTOR",
    char="S",
    colour=(0, 133, 235),
    name="Slime",
    money=10,
    ai_cls=HostileAi,
    fighter=Fighter(
        Base_HP=30,
        Base_ATK=[1, 3],
        Base_DEF=12,
        Base_ACC=1),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    enemy_type=Slime()
    # level=Level(xp_given=25)
)

mini_slime = Actor(
    entity_type="ACTOR",
    char="s",
    colour=(0, 133, 235),
    name="Mini Slime",
    money=10,
    ai_cls=HostileAi,
    fighter=Fighter(
        Base_HP=15,
        Base_ATK=[1, 2],
        Base_DEF=10,
        Base_ACC=1),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    # level=Level(xp_given=25)
)

orc = Actor(
    entity_type="ACTOR",
    char="0",
    colour=(200, 200, 200),
    name="Orc",
    ai_cls=HostileAi,
    money=18,
    fighter=Fighter(
        Base_HP=35,
        Base_ATK=[3, 6],
        Base_DEF=13,
        Base_ACC=4),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    # level=Level(xp_given=50)
)


dragon = Actor(
    entity_type="ACTOR",
    char="D",
    colour=(210, 0, 0),
    name="Dragon",
    money=100,
    ai_cls=HostileAi,
    fighter=Fighter(
        Base_HP=100,
        Base_ATK=[5, 10],
        Base_DEF=15,
        Base_ACC=5),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    # level=Level(xp_given=200)
)
