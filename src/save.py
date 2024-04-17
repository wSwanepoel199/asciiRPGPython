
import json, os

class Save:
  def save(self, player) -> None:
    list = {}
    for key, value in player.items():
      list[key] = value
    json_object = json.dumps(obj=list, indent=2)

    path = os.path.join('./', 'saves')

    try:
      os.makedirs(name=path)
      print("Directory '% s' created" % 'saves')
    except OSError:
      pass

    with open(file="./saves/save.json", mode="w") as outfile:
      outfile.write(json_object)

  def load(self, player) -> None:
    try:
      with open(file='./saves/save.json', mode='r') as openFile:
        json_object = json.load(fp=openFile)
        for key, value in json_object.items():
          player[key] = value
    except OSError:
      print("No save file found. Returning to main menu.")
