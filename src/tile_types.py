from typing import Tuple
import numpy as np # type: ignore

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
  ]
)

def new_tile(
  *,
  walkable: int,
  transparent: int,
  dark: Tuple[int, Tuple[int,int,int], Tuple[int,int,int]]
) -> np.ndarray:
  """Helper Function for defining individual tile types."""
  return np.array(object=(walkable, transparent, dark), dtype=tile_dt)

tile_types = {
  'floor': new_tile(walkable=True, transparent=True, dark=(ord("."), (255, 255, 255), (0, 0, 0))),
  'wall': new_tile(walkable=False, transparent=False, dark=(ord("#"), (255, 255, 255), (0, 0, 0))),
  "mapfill": new_tile(walkable=True, transparent=True, dark=(ord(" "), (255, 255, 255), (0, 0, 1))),
}