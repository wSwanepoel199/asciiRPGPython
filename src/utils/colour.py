import json

def loadColours() -> dict:
  with open(file='./src/utils/colour.json', mode='r') as openFile:
    return json.load(fp=openFile)