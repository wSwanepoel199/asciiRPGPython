
from src.components.consumable import HealingPotion

from src.entity import Item

healing_potion = Item(
  entity_type='ITEM',
  char="!",
  colour=(127, 0, 255),
  name="Healing Potion",
  consumable=HealingPotion(amount=4)
)