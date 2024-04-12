from src import save, player


print(__name__)
def mainMenu():
  global play, menu_open, rules, clear
  clear()
  print("1: New Game")
  print("2: Load Game")
  print("3: Rules")
  print("4: Quit/Exit")

  if rules:
    print("I'm the creator and here are my rules MUAHAHAHA")
    rules = False
    choice = ""
    input('> ')
  else:
    choice = input("#> ")

  match choice:
    case "1":
      player.player["name"] = input("Enter your hero's name: ")
      clear()
      menu_open = False
      play = True
    case "2":
      save.load()
      print("Hero " + player.player["name"] + " was successfully loaded with HP: "+player.player["HP"]+" and ATK: "+player.player["ATK"]+". They had "+player.player["potions"]+" potion(s), "+ player.player["elixers"]+" elixir(s) and "+player.player["money"]+" coin(s) on them.")
      input('> ')
      clear()
      menu_open = False
      play = True
    case "3":
      rules = True
    case "4":
      clear()
      quit()
