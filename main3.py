import sys
import random

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
  
  def __init__(self):
    self.list_of_water = list[Box]()

  def append(self, __object: "Box") -> None:
    super().append(__object)
    if __object.is_island is False:
      self.list_of_water.append(__object)

  def __str__(self) -> str:
    ret = f""
    for b in self:
      ret = f"{ret} {str(b)}"
    return ret

class Grid(list[Row]):
  
  def __init__(self):
    self.list_of_water = list[Row]()

  def append(self, __object: "Row") -> None:
    super().append(__object)
    self.list_of_water.append(__object.list_of_water)

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
    self.coordinate_list = list[Box]()
  
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

  def get_initial_position(self) -> str:
    l_random_row_index = random.randrange(0,len(self.grid_start) - 1)
    l_random_row = self.grid_start.list_of_water[l_random_row_index]
    l_box_index = random.randrange(0, len(l_random_row) - 1)
    l_box = l_random_row[l_box_index]
    self.coordinate_list.append(l_box)
    return f"{l_box.x} {l_box.y}"
  
  def get_best_move(self) -> str:

    # On cree la liste des boites voisines
    list_neighbourgs = list[Box]()

    if self.x - 1 >= 0: 
      list_neighbourgs.append(self.grid_start[self.y][self.x-1])

    if self.x + 1 < k_MapSize:
      list_neighbourgs.append(self.grid_start[self.y][self.x+1])
    
    if self.y - 1 >= 0:
      list_neighbourgs.append(self.grid_start[self.y-1][self.x])
    
    if self.y + 1 < k_MapSize:
      list_neighbourgs.append(self.grid_start[self.y+1][self.x])

    # On regarde les voisins en commencant par se demander si on peut
    # on peut se deplacer a l'ouest
    # puis a l'est
    # puis au nord
    # puis au sud
    for neighbourg in list_neighbourgs:
      # Si on a pas deja visite la case et si la case n'est pas une ile
      if neighbourg not in self.coordinate_list and neighbourg.is_island is False:
        self.coordinate_list.append(neighbourg)
        if neighbourg.x == self.x - 1:
          return "MOVE W"
        elif neighbourg.x == self.x + 1:
          return "MOVE E"
        elif neighbourg.y == self.y - 1:
          return "MOVE N"
        elif neighbourg.y == self.y + 1:
          return "MOVE S"
    
    # Si on a fait surface on nettoie les cases deja visitees et on enregistre la case courante
    # pour ne pas y retourner
    self.coordinate_list.clear()
    self.coordinate_list.append(self.grid_start[self.y][self.x])
    return "SURFACE"
  
  def get_best_item_to_charge(self) -> str:
    if self.silence > 0:
      return "SILENCE"
    elif self.mine > 0:
      return "MINE"
    elif self.torpedo > 0:
      return "TORPEDO"
    elif self.sonar > 0:
      return "SONAR"
    
    return ""
    
  def __str__(self) -> str:
    return f"X : {self.x} | Y : {self.y} | Life : {self.life} | Torpedo : {self.torpedo} | Sonar : {self.sonar} | Silence : {self.silence} | Mine : {self.mine}"
  
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

  print(my_player.get_initial_position())
  while True:
    if file is None:
      my_player.x, my_player.y, my_player.life, opp_player.life, my_player.torpedo, my_player.sonar, my_player.silence, my_player.mine = [int(i) for i in input().split()]
      sonar_result = input().split()
      opponent_orders = input().split("|")
    else:
      line = file.readline() # Utiliser pour verifier s'il reste des lignes avec len(line) == 0 et couper pour eviter une exception
      if len(line) == 0:
        break
      my_player.x, my_player.y, my_player.life, opp_player.life = [int(i) for i in line.split()]
      sonar_result = file.readline().split()
      opponent_orders = file.readline().split("|")
    
    print(f"{str(my_player)}", file=sys.stderr, flush=True)
    for o in opponent_orders:
      if "MOVE" in o:
        mouvement = o.split()[1]
        opp_player.calculate_is_possible(mouvement=mouvement)

    opp_player.grid_start.copy(opp_player.grid_end)
    print(f"{my_player.get_best_move()} {my_player.get_best_item_to_charge()}")