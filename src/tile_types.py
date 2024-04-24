from typing import Tuple
import numpy as np # type: ignore
import src.utils.constants as constants

graphic_dt = np.dtype(
  dtype=[
    ("ch", np.int32),
    ("fg", "3B"),
    ("bg", "3B"),
  ]
)

tile_dt = np.dtype(
  dtype=[
    ("walkable", np.bool_),
    ("transparent", np.bool_),
    ("dark", graphic_dt),
    ("light", graphic_dt),
  ]
)

def new_tile(
  *,
  walkable: int,
  transparent: int,
  dark: Tuple[int, Tuple[int,int,int], Tuple[int,int,int]],
  light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
  """Helper Function for defining individual tile types."""
  return np.array(object=(walkable, transparent, dark, light), dtype=tile_dt)

tile_types = {
  'shroud': np.array(object=(ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt),
  'floor': new_tile(
    walkable=True, 
    transparent=True, 
    dark=(ord(constants.floor_char), (100, 100, 100), (10, 10, 10)), 
    light=(ord(constants.floor_char), (255, 255, 255), (0, 0, 0))
  ),
  'wall': new_tile(
    walkable=False, 
    transparent=False, 
    dark=(ord("#"), (100, 100, 100), (10, 10, 10)),
    light=(ord("#"), (255, 255, 255), (0, 0, 0))
  ),
  'stairs_down': new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(constants.stairs_down), (0, 0, 100), (50, 50, 150)),
    light=(ord(constants.stairs_down), (255, 255, 255), (200, 180, 50)),
  ),
  "mapfill": new_tile(
    walkable=False, 
    transparent=True, 
    dark=(ord(" "), (255, 255, 255), (0, 0, 1)), 
    light=(ord(" "), (255, 255, 255), (0, 0, 1))
  ),
}