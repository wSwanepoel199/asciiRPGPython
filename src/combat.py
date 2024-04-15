import random
from src import enemy

class Combat:
  def __init__(self, target):
    self.enemyStats = enemy.enemy_stats[target]
    self.enemy = target
    self.defend = False
    self.usedElixir = False
  
  def __str__(self):
    return f"{self.__dict__}"

  def __setitem__(self, key, value):
        setattr(self, key, value)

  def __getitem__(self, key):
    return getattr(self, key)

  def battle(self, player, tile, game):

    hp = self.enemyStats["hp"]
    max_hp = self.enemyStats["hp"]
    atk = self.enemyStats["atk"]
    gold = self.enemyStats["gold"]

    while player["combat"]:
      game.clear()
      game.draw()
      print("A wild " + self.enemy + " has appeared from the " + tile["t"] + "!")
      game.draw()
      print(self.enemy+"'s STATS")
      print(self.enemy + "'s HP: " + str(hp) + "/" + str(max_hp))
      print(self.enemy + "'s ATK: " + str(atk))
      game.draw()
      print(player["name"] + "'s STATS")
      print(player["name"] + "'s HP: " + str(player["HP"]) + "/" + str(player["MAX_HP"]))
      print(player["name"] + "'s ATK: " + str(player["ATK"]))
      print('Available Potions: ' + str(player["potions"]))
      print('Available Elixirs: ' + str(player["elixirs"]))
      game.draw()
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
          hp -= player["ATK"]
          print(str(player['name']) + ' attacked the ' + self.enemy + ' for ' + str(player["ATK"]) + ' damage!')
          if self.usedElixir:
            self.usedElixir = False
            player["ATK"] -= 1
            print("The Elixir wears off, returning your strength to " + str(player["ATK"]))
        case '2':
          self.defend = True
          atk -= player["ATK"]
          print(str(player['name']) + ' is defending against the ' + self.enemy + "'s attacks!")
        case '3':
          if player["potions"] > 0:
            player.heal()
        case '4':
          if player["elixirs"] > 0:
            self.usedElixir = True
            player["elixirs"] -= 1
            player["ATK"] += 1
            print(str(player['name']) + ' used an elixir and gained 1 ATK!')
        case '5':
          player["combat"] = False
      input('> ')
      if hp >= 1:
        # if defending
        #   check if able to damage
        if atk >=1:
          player["HP"] -= atk
        if self.defend:
          if atk <= 0:
            print("The " + self.enemy + " attacked but could not piece through your defenses!")
          else:
            print('The '+ self.enemy + ' attacked you but onlt dealt ' + str(atk) + ' damage because you were defending!')
          atk = self.enemyStats["atk"]
          self.defend = False
        else:
          print('The '+ self.enemy + ' attacked you for ' + str(atk) + ' damage!')
      else:
        print('You have defeated the ' + self.enemy + '!')
        player["money"] += gold
        player["combat"] = False
        if random.randint(0,100) <= 10:
          print('You found a potion after the battle!')
          player["potions"] += 1
        if random.randint(0,100) <= 5:
          print('You found an elixir after the battle!')
          player["elixirs"] += 1
        input('> ')
        return True
      if player["HP"] <= 0:
        player["combat"] = False
        game.draw()
        print("GAME OVER.\nYou have been defeated by the " + self.enemy + "!")
        if self.usedElixir:
          self.usedElixir = False
          player["ATK"] -= 1
        if self.defend:
          self.defend = False
        game.draw()
        input('> ')
        return False
      input('> ')