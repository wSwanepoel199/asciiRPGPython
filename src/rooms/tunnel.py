from __future__ import annotations

from typing import TYPE_CHECKING, Tuple
import numpy as np

if TYPE_CHECKING:
    from src.map import GameMap


class Tunnel:
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], middle: int, width: int = 2, height: int = 2, horizontal: bool = True) -> None:
        self.x1, self.y1 = start
        self.z = middle
        self.x2, self.y2 = end
        self.width = width//2
        self.height = height//2
        self.horizontal = horizontal

    @property
    def center(self) -> Tuple[int, int]:
        center_x = (self.x1 + self.z) // 2
        center_y = (self.y1 + self.z) // 2

        return center_x, center_y

    @property
    def inner(self) -> Tuple[int, int]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1, self.x2), slice(self.y1, self.y2), slice(self.x1, self.z)

    @property
    def outer(self) -> Tuple[int, int]:
        """Return the outer area of this room as a 2D array index."""
        return slice(self.x1, self.x2), slice(self.y1, self.y2), slice(self.x1, self.z)

    def genWalls(self, gamemap: GameMap) -> None:
        # attempting to get tunnel to generate own walls, shits complicated man
        if self.horizontal:
            # start
            x1, x2 = self.x1-self.width, self.x1+self.width*2
            y1 = self.y1
            gamemap.tiles[
                x1:x2,
                y1
            ] = gamemap.tile_types["wall"]
            # start to z
            if self.y1 < self.z:
                y1, y2 = self.y1+1, self.z
            else:
                y1, y2 = self.z, self.y1+1
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["v-wall"]
            # end
            x1, x2 = self.x2-self.width, self.x2+self.width*2
            y1 = self.y2
            gamemap.tiles[
                x1:x2,
                y1
            ] = gamemap.tile_types["wall"]
            # end to z
            if self.z < self.y2:
                y1, y2 = self.z, self.y2
            else:
                y1, y2 = self.y2, self.z
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["v-wall"]

            # connect start to end
            if self.x1 < self.x2:
                x1, x2 = self.x1, self.x2+1
            else:
                x1, x2 = self.x2, self.x1+1
            y1, y2 = self.z-self.height, self.z+self.height*2
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["h-wall"]

        else:
            # start
            x1 = self.x1
            y1, y2 = self.y1-self.height, self.y1+self.height*2
            gamemap.tiles[
                x1,
                y1:y2
            ] = gamemap.tile_types["wall"]
            # start to z
            if self.x1 < self.z:
                x1, x2 = self.x1+1, self.z
            else:
                x1, x2 = self.z, self.x1+1
            # gamemap.tiles[
            #     x1:x2,
            #     y1:y2
            # ] = gamemap.tile_types["h-wall"]
            for x in range(
                x1,
                x2
            ):
                for y in range(
                    y1,
                    y2
                ):
                    tile = gamemap.tiles[x, y]
                    print(tile)
                    if tile == gamemap.tile_types["mapfill"]:
                        tile = gamemap.tile_types["h-wall"]
            # end
            x1 = self.x2
            y1, y2 = self.y2-self.height, self.y2+self.height*2
            gamemap.tiles[
                x1,
                y1:y2
            ] = gamemap.tile_types["wall"]
            # end to z
            if self.z < self.x2:
                x1, x2 = self.z, self.x2
            else:
                x1, x2 = self.x2, self.z
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["h-wall"]

            # connect start to end
            x1, x2 = self.z-self.width, self.z+self.width*2
            if self.y1 < self.y2:
                y1, y2 = self.y1, self.y2+1
            else:
                y1, y2 = self.y2, self.y1+1
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["v-wall"]

    def genFloors(self, gamemap: GameMap) -> None:
        if self.horizontal:
            x1, x2 = self.x1, self.x1+self.width
            if self.y1 < self.z:
                y1, y2 = self.y1, self.z
            else:
                y1, y2 = self.z, self.y1
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["floor"]

            x1, x2 = self.x2, self.x2+self.width
            if self.z < self.y2:
                y1, y2 = self.z, self.y2+1
            else:
                y1, y2 = self.y2, self.z
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["floor"]

            if self.x1 < self.x2:
                x1, x2 = self.x1, self.x2+1
            else:
                x1, x2 = self.x2, self.x1+1
            y1, y2 = self.z, self.z+self.height
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["floor"]
        else:
            if self.x1 < self.z:
                x1, x2 = self.x1, self.z
            else:
                x1, x2 = self.z, self.x1
            y1, y2 = self.y1, self.y1+self.height
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["floor"]

            if self.z < self.x2:
                x1, x2 = self.z, self.x2+1
            else:
                x1, x2 = self.x2, self.z
            y1, y2 = self.y2, self.y2+self.height
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["floor"]

            x1, x2 = self.z, self.z+self.width
            if self.y1 < self.y2:
                y1, y2 = self.y1, self.y2+1
            else:
                y1, y2 = self.y2, self.y1+1
            gamemap.tiles[
                x1:x2,
                y1:y2
            ] = gamemap.tile_types["floor"]
