from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from src.components.base_component import BaseComponent
import src.factory.actor_factory as actor_factory


if TYPE_CHECKING:
    from src.entity import Actor


class BaseEnemyType(BaseComponent):
    parent: Actor

    def action(self, entity: Actor) -> None:
        raise NotImplementedError()


class Goblin(BaseEnemyType):
    """
    Goblins are small and weak, they rely on their numbers to attack.
    When a goblin gets a target, they will alert nearby enemies, causing them to get a target as well.
    """

    def action(self, entity: Actor) -> None:
        player = self.engine.player
        if not entity.distance(player.x, player.y) <= 5:
            return
        for actor in set(self.engine.game_map.actors) - {entity} - {player}:
            dist = entity.distance(actor.x, actor.y)
            if dist <= 5 and actor.ai:
                actor.ai.memory = entity.ai.memory
                actor.ai.last_seen = entity.ai.last_seen


class Slime(BaseEnemyType):
    """
    Slimes are not strong but they can quickly overwhelm. 
    If killed they will spawn smaller slimes. Once split they will not split again
    """

    def action(self, entity: Actor) -> None:
        if entity.fighter.HP <= 0:
            x = entity.x
            y = entity.y
            game_map = entity.gamemap
            for _ in range(2):
                if game_map.tiles["walkable"][x+1, y] and not any(entity.x == x+1 and entity.y == y for entity in game_map.actors):
                    actor_factory.mini_slime.spawn(
                        gamemap=game_map,
                        x=x+1,
                        y=y,
                    )
                    continue
                if game_map.tiles["walkable"][x, y+1] and not any(entity.x == x and entity.y == y+1 for entity in game_map.actors):
                    actor_factory.mini_slime.spawn(
                        gamemap=game_map,
                        x=x,
                        y=y+1,
                    )
                    continue
                if game_map.tiles["walkable"][x-1, y] and not any(entity.x == x-1 and entity.y == y for entity in game_map.actors):
                    actor_factory.mini_slime.spawn(
                        gamemap=game_map,
                        x=x-1,
                        y=y,
                    )
                    continue
                if game_map.tiles["walkable"][x, y-1] and not any(entity.x == x and entity.y == y-1 for entity in game_map.actors):
                    actor_factory.mini_slime.spawn(
                        gamemap=game_map,
                        x=x,
                        y=y-1,
                    )
                    continue
