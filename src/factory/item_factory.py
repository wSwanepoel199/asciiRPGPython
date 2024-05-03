import src.utils.constants as constants

from src.components import consumable, equippable
from src.entity import Item

healing_potion = Item(
  char=constants.potion_char,
  colour=(156, 0, 0),
  name="Healing Potion",
  consumable=consumable.HealingConsumable(amount=[4,10], on_use="You drink the Healing Potion! Healing <amount> of HP!"),
)

cure_wounds_scroll = Item(
  char=constants.scroll_char,
  colour=(38, 255, 0),
  name="Scroll of Cure Wounds",
  consumable=consumable.HealingConsumable(amount=[7,21],  on_use="You cast Cure Wounds! Healing <amount> of HP!"),
)

lightning_bolt_scroll = Item(
  char=constants.scroll_char,
  colour=(0, 221, 255),
  name="Scroll of Lightning Bolt",
  consumable=consumable.LightningBoltConsumable(damage=[10,20], range=7, on_hit_message="A lightning bolt strikes out at the <target> dealing <damage> damage!")
)

confusion_scroll = Item(
  char=constants.scroll_char,
  colour=(207, 63, 255),
  name="Scroll of Confusion",
  consumable=consumable.ConfusionConsumable(turns=[5,10], range=4)
)

teleport_scroll = Item(
  char=constants.scroll_char,
  colour=(224, 63, 224),
  name="Scroll of Teleportation",
  consumable=consumable.TeleportConsumable(range=10)
)

fireball_scroll = Item(
  char=constants.scroll_char,
  colour=(255, 0, 0),
  name="Scroll of Fireball",
  consumable=consumable.FireballDamageConsumable(damage=[8,48], radius=3)
)

dagger = Item(
  char="/", 
  colour=(0, 191, 255), 
  name="Dagger", 
  equippable=equippable.Dagger()
)

sword = Item(
  char="/", 
  colour=(0, 191, 255), 
  name="Sword", 
  equippable=equippable.Sword()
)

leather_armour = Item(
  char=constants.armour,
  colour=(102, 63, 24),
  name="Leather Armour",
  equippable=equippable.LeatherArmour(),
)

chain_mail = Item(
  char=constants.armour, 
  colour=(145, 142, 140), 
  name="Chain Mail", 
  equippable=equippable.ChainMail()
)