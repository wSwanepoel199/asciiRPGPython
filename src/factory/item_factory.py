import src.utils.constants as constants
import src.components.consumable as consumable 

from src.entity import Item

healing_potion = Item(
  entity_type='ITEM',
  char=constants.potion_char,
  colour=(156, 0, 0),
  name="Healing Potion",
  consumable=consumable.HealingConsumable(amount=[4,10], on_use="You drink the Healing Potion! Healing <amount> of HP!"),
)

cure_wounds_scroll = Item(
  entity_type='ITEM',
  char=constants.scroll_char,
  colour=(38, 255, 0),
  name="Scroll of Cure Wounds",
  consumable=consumable.HealingConsumable(amount=[7,21],  on_use="You cast Cure Wounds! Healing <amount> of HP!"),
)

lightning_bolt_scroll = Item(
  entity_type='ITEM',
  char=constants.scroll_char,
  colour=(0, 221, 255),
  name="Scroll of Lightning Bolt",
  consumable=consumable.LineDamageConsumable(damage=[10,20], range=5, on_hit_message="A lightning bolt strikes out at the <target> dealing <damage> damage!")
)

confusion_scroll = Item(
  entity_type='ITEM',
  char=constants.scroll_char,
  colour=(207, 63, 255),
  name="Scroll of Confusion",
  consumable=consumable.ConfusionConsumable(turns=[5,10], range=4)
)

teleport_scroll = Item(
  entity_type='ITEM',
  char=constants.scroll_char,
  colour=(224, 63, 224),
  name="Scroll of Teleportation",
  consumable=consumable.TeleportConsumable(range=10)
)

fireball_scroll = Item(
  entity_type='ITEM',
  char=constants.scroll_char,
  colour=(255, 0, 0),
  name="Scroll of Fireball",
  consumable=consumable.FireballDamageConsumable(damage=[8,48], radius=3)
)