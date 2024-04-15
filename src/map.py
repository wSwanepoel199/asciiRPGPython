
class Map:
  def __init__(self, ):
    self.map = [
      ["P","P","P","P","F","M","C"],
      ["F","F","F", "F", "F", "H", "M"],
      ["F","Fl","B", "P", "H", "F", "H"],
      ["P","S","T", "Ma", "P", "H", "M"],
      ["P","Fl","Fl", "P", "H", "M", "M"]
    ]
    self.biomes = {
      "P": {
        "t": "PLAINS",
        "e": True},
      "F": {
        "t": "WOODS",
        "e": True},
      "Fl": {
        "t": "FIELDS",
        "e": False},
      "B": {
        "t": "BRIGE",
        "e": True},
      "T": {
        "t": "TOWN CENTRE",
        "e": False},
      "S": {
        "t": "SHOP",
        "e": False},
      "Ma": {
        "t": "MAYOR",
        "e": False},
      "C": {
        "t": "CAVE",
        "e": False},
      "M": {
        "t": "MOUNTAIN",
        "e": True},
      "H": {
        "t": "HILLS",
        "e": True,
      }
    }
    self.x_len = len(self.map[0])-1
    self.y_len = len(self.map)-1