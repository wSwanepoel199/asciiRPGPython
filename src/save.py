
import json, os

class Save:
  def save(self, player):
    list = {}
    for key, value in player.items():
      list[key] = value
    json_object = json.dumps(list, indent=2)

    path = os.path.join('./', 'saves')

    try:
      os.makedirs(path)
      print("Directory '% s' created" % 'saves')
    except OSError:
      print("Directory '% s' already exists" % 'saves')

    with open("./saves/save.json", "w") as outfile:
      outfile.write(json_object)

  def load(self, player):
    try:
      with open('./saves/save.json', 'r') as openfile:
        json_object = json.load(openfile)
        for key, value in json_object.items():
          player[key] = value
    except OSError:
      print("No save file found. Returning to main menu.")
