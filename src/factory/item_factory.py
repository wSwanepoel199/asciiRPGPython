
import src.components.consumable as consumable 

from src.entity import Item

healing_potion = Item(
  entity_type='ITEM',
  char="!",
  colour=(156, 0, 0),
  name="Healing Potion",
  consumable=consumable.HealingConsumable(amount=4, on_use="You drink the Healing Potion! Healing <amount> of HP!"),
)

cure_wounds_scroll = Item(
  entity_type='ITEM',
  char='~',
  colour=(38, 255, 0),
  name="Scroll of Cure Wounds",
  consumable=consumable.HealingConsumable(amount=10,  on_use="You cast Cure Wounds! Healing <amount> of HP!"),
)

lightning_bolt_scroll = Item(
  entity_type='ITEM',
  char='~',
  colour=(0, 221, 255),
  name="Scroll of Lightning Bolt",
  consumable=consumable.LineDamageCosumable(damage=20, range=5, on_hit_message="A lightning bolt strikes out at the <target> dealing <damage> damage!")
)