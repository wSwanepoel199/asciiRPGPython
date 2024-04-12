
import json
from src import player

def save():
  list = {}
  for key, value in player.player.items():
    list[key] = value
  json_object = json.dumps(list, indent=2)
  with open("save.json", "w") as outfile:
    outfile.write(json_object)

def load():
  try:
    with open('save.json', 'r') as openfile:
      json_object = json.load(openfile)
      for key, value in json_object.items():
        player.player[key] = value
  except OSError:
    print("No save file found. Returning to main menu.")
