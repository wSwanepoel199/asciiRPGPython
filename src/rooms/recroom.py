from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from src.map import GameMap


class RecRoom:
    def __init__(self, x: int, y: int, width: int, height) -> None:
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height
        self.node = None

        # self.point1 = (x, y)
        # self.point2 = (x+w, y+h)

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[int, int]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    @property
    def outer(self) -> Tuple[int, int]:
        """Return the outer area of this room as a 2D array index."""
        return slice(self.x1, self.x2+1), slice(self.y1, self.y2+1)

    def intersects(self, other: RecRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (self.x1 <= other.x2 and
                self.x2 >= other.x1 and
                self.y1 <= other.y2 and
                self.y2 >= other.y1)

    def genWalls(self, gamemap: GameMap) -> None:
        gamemap.tiles[self.x1, self.y1] = gamemap.tile_types["l-wall-d-r"]
        gamemap.tiles[self.x2, self.y1] = gamemap.tile_types["l-wall-d-l"]
        gamemap.tiles[self.x1, self.y2] = gamemap.tile_types["l-wall-t-r"]
        gamemap.tiles[self.x2, self.y2] = gamemap.tile_types["l-wall-t-l"]
        gamemap.tiles[
            self.x1+1:self.x2,
            self.y1
        ] = gamemap.tile_types["h-wall"]
        gamemap.tiles[
            self.x1+1:self.x2,
            self.y2
        ] = gamemap.tile_types["h-wall"]
        gamemap.tiles[
            self.x1,
            self.y1+1:self.y2
        ] = gamemap.tile_types["v-wall"]
        gamemap.tiles[
            self.x2,
            self.y1+1:self.y2
        ] = gamemap.tile_types["v-wall"]
