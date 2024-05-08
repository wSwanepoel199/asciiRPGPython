from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from src.map import GameMap


class Tunnel:
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], middle: int, width: int = 2, height: int = 2, horizontal: bool = True) -> None:
        self.x1, self.y1 = start
        self.z = middle
        x, y = end
        self.x2, self.y2 = x, y
        self.width = width
        self.height = height
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
        # gamemap.tiles[self.x1, self.y1] = gamemap.tile_types["l-wall-d-r"]
        # gamemap.tiles[self.x3, self.y1] = gamemap.tile_types["l-wall-d-l"]
        # gamemap.tiles[self.x1, self.y3] = gamemap.tile_types["l-wall-t-r"]
        # gamemap.tiles[self.x3, self.y3] = gamemap.tile_types["l-wall-t-l"]
        # gamemap.tiles[
        #     self.x1+1:self.x3,
        #     self.y1
        # ] = gamemap.tile_types["h-wall"]
        # gamemap.tiles[
        #     self.x1+1:self.x3,
        #     self.y3
        # ] = gamemap.tile_types["h-wall"]
        # gamemap.tiles[
        #     self.x1,
        #     self.y1+1:self.y3
        # ] = gamemap.tile_types["v-wall"]
        # gamemap.tiles[
        #     self.x3,
        #     self.y1+1:self.y3
        # ] = gamemap.tile_types["v-wall"]
        # gamemap.tiles[self.x1, self.y1] = gamemap.tile_types["wall"]
        # gamemap.tiles[self.x2, self.y1] = gamemap.tile_types["wall"]
        # gamemap.tiles[self.x1, self.y2] = gamemap.tile_types["wall"]
        # gamemap.tiles[self.x2, self.y2] = gamemap.tile_types["wall"]
        # attempting to get tunnel to generate own walls, shits complicated man
        if self.horizontal:
            if self.x1 < self.x2:
                gamemap.tiles[
                    self.x1,
                    self.y1+1
                ] = gamemap.tile_types["wall"]
                gamemap.tiles[
                    self.x1 + self.width,
                    self.y1+1
                ] = gamemap.tile_types["wall"]
                gamemap.tiles[
                    self.x2,
                    self.y2
                ] = gamemap.tile_types["wall"]
                gamemap.tiles[
                    self.x2 + self.width,
                    self.y2
                ] = gamemap.tile_types["wall"]

            # gamemap.tiles[
            #     self.x1,
            #     self.z + self.height
            # ] = gamemap.tile_types["l-wall-t-r"]
            # gamemap.tiles[
            #     self.x1 + self.width,
            #     self.z
            # ] = gamemap.tile_types["l-wall-t-r"]
            # gamemap.tiles[
            #     self.x2+self.width,
            #     self.z
            # ] = gamemap.tile_types["l-wall-d-l"]
            # gamemap.tiles[
            #     self.x2 + self.width,
            #     self.z + self.height
            # ] = gamemap.tile_types["l-wall-d-l"]
        else:
            pass

    def genFloors(self, gamemap: GameMap) -> None:

        if self.horizontal:
            if self.y1 < self.z:
                gamemap.tiles[
                    self.x1+1:self.x1+self.width,
                    self.y1:self.z
                ] = gamemap.tile_types["floor"]
            else:
                gamemap.tiles[
                    self.x1+1:self.x1+self.width,
                    self.z:self.y1
                ] = gamemap.tile_types["floor"]

            if self.y2 >= self.z:
                gamemap.tiles[
                    self.x2+1:self.x2+self.width,
                    self.z:self.y2
                ] = gamemap.tile_types["floor"]
            else:
                gamemap.tiles[
                    self.x2+1:self.x2+self.width,
                    self.y2:self.z
                ] = gamemap.tile_types["floor"]
            pass
        else:
            pass
