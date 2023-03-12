import sys

class Box(object):

  def __init__(self, x : int, y : int, sector : int, is_island : bool, is_start : bool):
    """
      Constructeur

      :param x: La position en X de la case
      :type x: int
      :param y: La position en Y de la case
      :type y: int
      :param sector: Le secteur de la case
      :type sector: int
      :param is_island: Ile ou non ?
      :type is_island: bool
      :param is_start: Permet de savoir si on peut partir de ce point pour faire un mouvement ou non ?
      :type is_start: bool
    """
    self.x = x
    self.y = y
    self.sector = sector
    self.is_island = is_island
    self.is_start = is_start
    self.last_turn = 0
  
  def determine_mouvement(self, end_box : "Box"):
    if end_box.is_island is False:
      end_box.is_start = self.is_start

  def __str__(self) -> str:
    ret = f""
    """
    if self.is_island:
      ret = f"{ret}x"
    else:
      ret = f"{ret}."
    """
    ret = f"{ret}{1 if self.is_start is True else 0}"
    return ret

class Row(list[Box]):
  def __str__(self) -> str:
    ret = f""
    for b in self:
      ret = f"{ret} {str(b)}"
    return ret

class Grid(list[Row]):
  def copy(self, other : "Grid"):
    self.clear()
    for row in other:
      temp_row = Row()
      for box in row:
        temp_row.append(Box(box.x, box.y, box.sector, box.is_island, box.is_start))
      self.append(temp_row)

    return self

  def __str__(self) -> str:
    ret = f"Grid : \n"

    for r in self:
      ret = f"{ret}{str(r)}\n"

    return ret
  
class Player(object):

  def __init__(self, id : int, grid : Grid) -> None:
    """
      Constructeur

      :param id: Identifiant du joueur
      :type id: int
      :param grid: La grille du jeu attaché au joueur
      :type grid: Grid
    """
    self.id = id
    self.x = 0
    self.y = 0
    self.grid_start = grid
    self.grid_end = Grid().copy(grid)
    self.life = 6
    self.torpedo = 0
    self.sonar = 0
    self.silence = 0
    self.mine = 0
  
  def calculate_is_possible(self, mouvement : str):
    for row in self.grid_start:
      for box in row:
        if mouvement == "N":
          if box.y - 1 >= 0:
            box.determine_mouvement(self.grid_end[box.y-1][box.x])
        elif mouvement == "S":
          if box.y + 1 < k_MapSize:
            box.determine_mouvement(self.grid_end[box.y+1][box.x])
        elif mouvement == "E":
          if box.x + 1 < k_MapSize:
            box.determine_mouvement(self.grid_end[box.y][box.x+1])
        elif mouvement == "S":
          if box.x - 1 >= 0:
            box.determine_mouvement(self.grid_end[box.y][box.x-1])

k_MapSize = 15
k_MapSector = 3
k_GridSector = k_MapSize//k_MapSector
current_turn = -1

if __name__ == "__main__":

  file = None
  if len(sys.argv) > 1 and sys.argv[1] == "Testing":
    file = open("tester.txt", "r")

  if file is None:
    width, height, my_id = [int(i) for i in input().split()]
  else:
    width, height, my_id = [int(i) for i in file.readline().split()]
  my_grid = Grid()
  opp_grid = Grid()

  k_MapSize = height
  k_GridSector = k_MapSize//k_MapSector
  for y in range(height):
    my_row = Row()
    opp_row = Row()

    if file is None:
      data = input()
    else:
      data = file.readline()

    for index, x in enumerate(data):
      my_row.append(Box(index, y, (index//k_GridSector)+(k_MapSector*(y//k_GridSector))+1, x == "x", x != "x"))
      opp_row.append(Box(index, y, (index//k_GridSector)+(k_MapSector*(y//k_GridSector))+1, x == "x", x != "x"))
    my_grid.append(my_row)
    opp_grid.append(opp_row)

  my_player = Player(my_id, my_grid)
  opp_player = Player(1-my_id, opp_grid)

  print("0 0")
  while True:
    if file is None:
      x, y, my_life, opp_life, torpedo_cooldown, sonar_cooldown, silence_cooldown, mine_cooldown = [int(i) for i in input().split()]
      my_player.x = x
      my_player.y = y
      my_player.life = my_life
      my_player.torpedo = torpedo_cooldown
      my_player.sonar = sonar_cooldown
      my_player.silence = silence_cooldown
      my_player.mine = mine_cooldown
      sonar_result = input().split()
      opponent_orders = input().split("|")
    else:
      line = file.readline() # Utiliser pour verifier s'il reste des lignes avec len(line) == 0 et couper pour eviter une exception
      if len(line) == 0:
        break
      x, y, my_life, opp_life = [int(i) for i in line.split()]
      sonar_result = file.readline().split()
      opponent_orders = file.readline().split("|")
    my_player.life = my_life
    opp_player.life = opp_life
    
    for o in opponent_orders:
      if "MOVE" in o:
        mouvement = o.split()[1]
        opp_player.calculate_is_possible(mouvement=mouvement)

    opp_player.grid_start.copy(opp_player.grid_end)
    print("MOVE S")
    print(str(opp_player.grid_end), file=sys.stderr, flush=True)