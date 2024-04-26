import json
import src.assets.load_asset as load_asset

def loadColours() -> dict:
  with open(file=load_asset.colours, mode='r') as openFile:
    return json.load(fp=openFile)