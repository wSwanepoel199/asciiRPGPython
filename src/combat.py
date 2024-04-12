import random
from src import enemy, player

mobs = enemy.mobs

def battle(enemy, tile):
  global play, menu, clear, draw
  print(mobs[enemy])
  hp = mobs[enemy]["hp"]
  max_hp = mobs[enemy]["hp"]
  atk = mobs[enemy]["atk"]
  gold = mobs[enemy]["gold"]
  defend = False
  usedElixir = False

  while player.player["combat"]:
    clear()
  
    draw()
    print("A wild " + enemy + " has appeared from the " + tile["t"] + "!")
    draw()
    print(enemy+"'s STATS")
    print(enemy + "'s HP: " + str(hp) + "/" + str(max_hp))
    print(enemy + "'s ATK: " + str(atk))
    draw()
    print(player.player["name"] + "'s STATS")
    print(player.player["name"] + "'s HP: " + str(player.player["HP"]) + "/" + str(player.player["MAX_HP"]))
    print(player.player["name"] + "'s ATK: " + str(player.player["ATK"]))
    print('Available Potions: ' + str(player.player["potions"]))
    print('Available Elixirs: ' + str(player.player["elixirs"]))
    draw()
    print("Available actions:")
    print("  1 - Attack")
    print("  2 - Defend")
    if player["potions"] > 0:
      print("  3 - Use Potion (+5 HP)")
    if player["elixirs"] > 0:
      print("  4 - Use Elixir (+1 ATK)")
    print('  5 - Run Away')

    action = input('#> ')
    match action:
      case '1':
        hp -= player.player["ATK"]
        print(str(player.player['name']) + ' attacked the ' + enemy + ' for ' + str(player.player["ATK"]) + ' damage!')
        if usedElixir:
            usedElixir = False
            player.player["ATK"] -= 1
            print("The Elixer wears off, returning your strength to " + str(player.player["ATK"]))
      case '2':
        defend = True
        atk -= player.player["ATK"]
        print(str(player.player['name']) + ' is defending against the ' + enemy + "'s attacks!")
      case '3':
        if player.player["potions"] > 0:
          player.player["potions"] -= 1
          player.player["HP"] += 5
          print(str(player.player['name']) + ' used a potion and restored 5 HP!')
      case '4':
        if player.player["elixirs"] > 0:
          usedElixir = True
          player.player["elixirs"] -= 1
          player.player["ATK"] += 1
          print(str(player.player['name']) + ' used an elixir and gained 1 ATK!')
      case '5':
        player.player["combat"] = False
    input('> ')
    if hp >= 1:
      # if defending
      #   check if able to damage
      if atk >=1:
        player.player["HP"] -= atk
      if defend:
        if atk <= 0:
          print("The " + enemy + " tried to attack but recoiled against your defences!")
        else:
          print('The '+ enemy + ' attacked you but onlt dealt ' + str(atk) + ' damage because you were defending!')
        atk = mobs[enemy]["atk"]
        defend = False
      else:
        print('The '+ enemy + ' attacked you for ' + str(atk) + ' damage!')
    else:
      clear()
      print('You have defeated the ' + enemy + '!')
      player.player["money"] += gold
      player.player["combat"] = False
      if random.randint(0,100) <= 10:
        print('You found a potion after the battle!')
        player.player["potions"] += 1
      if random.randint(0,100) <= 5:
        print('You found an elixer after the battle!')
        player.player["elixirs"] += 1
    if player.player["HP"] <= 0:
      clear()
      player.player["combat"] = False
      play = False
      menu = True
      draw()
      print("GAME OVER.\nYou have been defeated by the " + enemy + "!")
      if usedElixir:
        usedElixir = False
        player.player["ATK"] -= 1
      if defend:
        defend = False
      draw()
    input('> ')
    clear()