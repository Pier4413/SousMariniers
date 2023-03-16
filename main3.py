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
  
  def determine_mouvement(self, end_box : "Box"):
    """
      Determine si une case est disponible pour etre un bon point d'arrivee ou pas
    """
    if end_box.is_island is False:
      end_box.is_start = self.is_start

  def __eq__(self, __o: object) -> bool:
    if type(__o) != "Box":
      return False
    
    return __o.x == self.x and __o.y == self.y
  
  def __str__(self) -> str:
    return f"{1 if self.is_start is True else 0}"

class Row(list[Box]):
  
  def __init__(self):
    """
      Constructeur

      Initialise une liste vide pour les cases d'eau uniquement
    """
    self.list_of_water = list[Box]()

  def append(self, __object: "Box") -> None:
    """
      Ajoute un element de type box dans la grille
      Si la case est de l'eau on l'ajoute aussi a la liste des cases d'eau

      :param __object: La boite a ajouter
      :type __object: Box
    """
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
    """
      Constructeur

      Initialise une liste vide pour les cases d'eau uniquement
    """
    self.list_of_water = list[list[Box]]()

  def append(self, __object: "Row") -> None:
    """
      Ajoute un element de type row dans la grille

      :param __object: La ligne a ajouter
      :type __object: Row
    """
    super().append(__object)
    self.list_of_water.append(__object.list_of_water)

  def copy(self, other : "Grid"):
    """
      Copieur de grille par valeur

      :param other: La grille que l'on veut copier
      :type other: Grid
    """
    self.clear()
    for row in other:
      temp_row = Row()
      for box in row:
        temp_row.append(Box(box.x, box.y, box.sector, box.is_island, box.is_start))
      self.append(temp_row)

    return self

  def __str__(self) -> str:
    """
      Affichage de la grille
    """
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
    self.id = id # Identifiant du joueur
    self.x = 0 # Position courante en X
    self.y = 0 # Position courant en Y
    self.grid_start = grid # Grille de depart
    self.grid_end = Grid().copy(grid) # Grille de fin
    self.life = 6 # Nombre de points de vie au depart
    self.torpedo = 0 # Nombre de tours avant chargement d'une torpille
    self.sonar = 0 # Nombre de tours avant chargement du sonar
    self.silence = 0 # Nombre de tours avant chargement du silence
    self.mine = 0 # Nombre de tours avant le chargement des mines
    self.coordinate_list = list[Box]() # Liste des coordonnes des cases deja visites (reinit sur SURFACE)
  
  def calculate_is_possible(self, mouvement : str):
    """
      A partir d'un mouvement donne. On calcule toutes les cases de depart possible pour ce
      mouvement. Le but est de determiner avec une bonne certitude ou peut etre l'ennemi

      A noter si le mouvement est W alors on peut partir du principe que l'ennemi n'est pas dans la premiere colonne
      De meme pour E et la derniere colonne, pour N et la premiere ligne et pour S et la derniere ligne

      :param mouvement: Le mouvement a analyser
      :type mouvement: str
    """
    for row in self.grid_start:
      for box in row:
        if mouvement == "N":
          if box.y - 1 > 0:
            box.determine_mouvement(self.grid_end[box.y-1][box.x])
          if box.y == 0:
            self.grid_end[box.y][box.x].is_start = False
        elif mouvement == "S":
          if box.y + 1 < k_MapSize:
            box.determine_mouvement(self.grid_end[box.y+1][box.x])
          if box.y == k_MapSize - 1:
            self.grid_end[box.y][box.x].is_start = False
        elif mouvement == "E":
          if box.x + 1 < k_MapSize:
            box.determine_mouvement(self.grid_end[box.y][box.x+1])
          if box.x == k_MapSize - 1:
            self.grid_end[box.y][box.x].is_start = False
        elif mouvement == "S":
          if box.x - 1 > 0:
            box.determine_mouvement(self.grid_end[box.y][box.x-1])
          if box.x == 0:
            self.grid_end[box.y][box.x].is_start = False

  def get_initial_position(self) -> str:
    """
      On choisit la position de départ

      Le choix est random dans une case d'eau
    """
    l_random_row_index = random.randrange(0,len(self.grid_start) - 1)
    l_random_row = self.grid_start.list_of_water[l_random_row_index]
    l_box_index = random.randrange(0, len(l_random_row) - 1)
    l_box = l_random_row[l_box_index]
    self.coordinate_list.append(l_box)
    return f"{l_box.x} {l_box.y}"
  
  def get_best_move(self, opp_end_grid : dict) -> str:
    """
      Choix du déplacement

      On choisit la case vers laquelle se déplacer. Le but est de se rapprocher de la position probable de
      l'adversaire
    """
    # TODO : Trouver un moyen de se rapprocher de l'adversaire en fonction de la grille des zones de fin (grid_end)
    # On cree la liste des boites voisines
    
    # Seuil a partir du quel on vise le secteur dans lequel se trouve l'ennemi, sinon on fait le serpent de mer
    threshold = 15
    max_sector = opp_end_grid["maximum"]
    
    list_neighbourgs = {
      "N": None,
      "S": None,
      "E": None,
      "W": None
    }

    if self.x - 1 >= 0: 
      list_neighbourgs["E"] = self.grid_start[self.y][self.x-1]

    if self.x + 1 < k_MapSize:
      list_neighbourgs["W"] = self.grid_start[self.y][self.x+1]
    
    if self.y - 1 >= 0:
      list_neighbourgs["N"] = self.grid_start[self.y-1][self.x]
    
    if self.y + 1 < k_MapSize:
      list_neighbourgs["S"] = self.grid_start[self.y+1][self.x]

    # On regarde les voisins en commencant par se demander si on peut
    # on peut se deplacer a l'ouest
    # puis a l'est
    # puis au nord
    # puis au sud
    if max_sector[1] < threshold:
      if self.grid_start[self.y][self.x].sector // 3 > max_sector[0] //3:
        return self.make_a_move("N", list_neighbourgs["N"], list_neighbourgs)
      elif self.grid_start[self.y][self.x].sector // 3 < max_sector[0] //3:
        return self.make_a_move("S", list_neighbourgs["S"], list_neighbourgs)
      else:
        if self.grid_start[self.y][self.x].sector % 3 > max_sector[0] % 3:
          return self.make_a_move("E", list_neighbourgs["E"], list_neighbourgs)
        elif self.grid_start[self.y][self.x].sector % 3 < max_sector[0] % 3:
          return self.make_a_move("W", list_neighbourgs["W"], list_neighbourgs)
        else:
          return self.make_a_move(None, None, list_neighbourgs)
    else:
      return self.make_a_move(None, None, list_neighbourgs)
  
  def make_a_move(self, move : str, neighbourg : Box, list_neighbourgs : dict) -> str:
    ret = None
    if move is not None and neighbourg is not None and neighbourg not in self.coordinate_list and neighbourg.is_island is False:
      self.coordinate_list.append(neighbourg)
      ret = f"MOVE {move}"
    else:
      for neighbourg in list_neighbourgs.values():
        if ret is None and neighbourg is not None:
          ret = self.random_move(neighbourg)
    
    if ret is None:
      self.coordinate_list.clear()
      self.coordinate_list.append(self.grid_start[self.y][self.x])
      return f"SURFACE"
    else:
      return ret
    
  def get_best_item_to_charge(self) -> str:
    """
      Choix du meilleur outil a charger

      Le choix est le suivant :

      - Toujours avoir du SILENCE
      - Ensuite toujours avoir des MINES
      - Puis toujours avoir une TORPILLE
      - Puis enfin avoir du SONAR si possible
    """
    if self.silence > 0:
      return "SILENCE"
    elif self.mine > 0:
      return "MINE"
    elif self.torpedo > 0:
      return "TORPEDO"
    elif self.sonar > 0:
      return "SONAR"
    return ""
  
  def calculate_torpedo_impact(self, torpedo_coordinates : tuple[int, int]) -> None:
    """
      Ameliore la grille de fin a partir des coups de torpille adverses

      Fonctionne sur un carre de 4 de cote et non pas sur la zone reelle.
      On peut avoir des petits ecarts (en plus) sur la position
    """
    l_box_impact = self.grid_start[torpedo_coordinates[1]][torpedo_coordinates[0]]
    for row in self.grid_start:
      for box in row:
        if box.x < l_box_impact.x - 4 or box.x > l_box_impact.x + 4 or box.y < l_box_impact.y - 4 or box.y > l_box_impact.y + 4:
          box.is_start = False

  def calculate_number_of_ones_by_sector(self, sector : int) -> int:
    """
      Calcule le nombre de 1 pour un secteur donne

      :param sector: Le secteur que l'on vise
      :type sector: int
      :return: Le nombre de 1 dans le secteur
      :rtype: int
    """
    result = 0
    for row in self.grid_end:
      for box in row:
        if box.sector == sector and box.is_start:
          result += 1
    return result

  def calculate_ones_by_sectors_and_max(self) -> dict:
    """
      Calcule les uns par secteur et trouve le couple maximum (secteur et valeur)
    """
    ret = {
      "maximum": (0, 0),
      "values" : list[tuple[int, int]]()
    }

    for i in range(1,10):
      value = self.calculate_number_of_ones_by_sector(i)
      ret["values"].append((i, value))

      if value > ret["maximum"][1]:
        ret["maximum"] = (i, value)

    return ret
  
  def should_use_sonar(self, max_values : dict) -> int:
    """
      Determine s'il faut utiliser le sonar et si ou dans quel secteur
    """
    if self.sonar == 0 and max_values["maximum"][0] > 0:
      return max_values["maximum"][0]
  
  def activate_sonar_sector(self, sector : int) -> None:
    """
      Supprime toutes les cases hors d'un secteur de l'algo de placement

      :param sector: Le secteur vise
      :type sector: int
    """
    for row in self.grid_start:
      for box in row:
        if box.sector != sector:
          box.is_start = False
  
  def clear_sonar_sector(self, sector : int) -> None:
    """
      Supprime toutes les cases dans un secteur vise de l'algo de placement

      :param sector: Le secteur vise
      :type sector: int
    """
    for row in self.grid_start:
      for box in row:
        if box.sector == sector:
          box.is_start = False
  
  def calculate_silence(self) -> None:
    """
      Mets à jour la grille en fonction des silences pour permettre de prendre en compte le fait que
      l'adversaire peut s'etre deplace de plusieurs cases avec le silence dans n'importe quelle direction
    """
    for row in self.grid_start:
      for box in row:
        if box.is_start is True:
          # Permet de gerer si on rencontre une ile sur le chemin (impossible de traverser)
          has_island_on_x = False
          has_island_on_y = False
          # -4 à -1 : sens W et N
          # 0 : position courante possible
          # 1 à 4 : sens E et S
          for i in range(-4,5):
            # On reinitialise les presences d'iles sur les deux sens pour ne pas compter une ile qui n'existe pas (i.e elle existe vers le W mais pas le E par exemple)
            if i == 0:
              has_island_on_y = False
              has_island_on_x = False

            # On gere les silences possibles horizontalement
            if (box.x + i) >= 0 and (box.x + i) < k_MapSize:
              box_x = self.grid_end[box.y][box.x+i]
              if box_x.is_island is False and has_island_on_x is False:
                box_x.is_start = True 
              else:
                has_island_on_x = True

            # On gere les silences possibles verticalement
            if (box.y + i) >= 0 and (box.y + i) < k_MapSize:
              box_y = self.grid_end[box.y+i][box.x]
              if box_y.is_island is False and has_island_on_y is False:
                box_y.is_start = True
              else:
                has_island_on_y = True 

  def random_move(self, neighbourg : Box) -> str:
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
      
  def __str__(self) -> str:
    """
      Affiche des informations sur le joueur pour le debug
    """
    return f"X : {self.x} | Y : {self.y} | Life : {self.life} | Torpedo : {self.torpedo} | Sonar : {self.sonar} | Silence : {self.silence} | Mine : {self.mine}"
  
k_MapSize = 15
k_MapSector = 3
k_GridSector = k_MapSize//k_MapSector
current_turn = -1

if __name__ == "__main__":

  # On cree le fichier et on l'ouvre si on est en mode Testing
  file = None
  if len(sys.argv) > 1 and sys.argv[1] == "Testing":
    file = open("tester.txt", "r")

  # On lit les dimensions de la carte
  if file is None:
    width, height, my_id = [int(i) for i in input().split()]
  else:
    width, height, my_id = [int(i) for i in file.readline().split()]
  
  # On cree nos deux grilles (la notre et celle de l'adversaire)
  # On a besoin de deux grilles differentes car elles ont vont evoluees differemment en fonction des ordres
  my_grid = Grid()
  opp_grid = Grid()

  # On recupere la taille de la carte et le nombre de cases dans une ligne/colonne de secteur
  k_MapSize = height
  k_GridSector = k_MapSize//k_MapSector

  # On parse la carte ce qui nous permet de remplir nos deux grilles de departs
  for y in range(height):

    # Une ligne de la grille (de meme deux lignes une pour le joueur et une pour l'adversaire)
    my_row = Row()
    opp_row = Row()

    # Suivant si on est dans le fichier ou pas pour le mode testing
    if file is None:
      data = input().strip()
    else:
      data = file.readline().strip()

    # On parse la ligne en cours
    for index, x in enumerate(data):
      # Le numero du secteur en fonction des coordonnees
      sector = (index//k_GridSector)+(k_MapSector*(y//k_GridSector)) + 1
      my_row.append(Box(index, y, sector, x == "x", x != "x"))
      opp_row.append(Box(index, y, sector, x == "x", x != "x"))
    my_grid.append(my_row)
    opp_grid.append(opp_row)

  # On cree les deux joueurs avec leurs id
  my_player = Player(my_id, my_grid)
  opp_player = Player(1-my_id, opp_grid)

  # On choisit la position de depart
  print(my_player.get_initial_position())
  
  sector_of_sonar = None

  while True:

    # On recupere la liste des inputs (soit depuis le jeu, soit depuis le fichier pour les tests)
    if file is None:
      my_player.x, my_player.y, my_player.life, opp_player.life, my_player.torpedo, my_player.sonar, my_player.silence, my_player.mine = [int(i) for i in input().split()]
      sonar_result = input()
      
      # On prend en compte le restultat du sonar pour mettre a jour la grille
      if sonar_result == "Y":
        opp_player.activate_sonar_sector(sector_of_sonar)
      elif sonar_result == "N":
        opp_player.clear_sonar_sector(sector_of_sonar)

      opponent_orders = input().split("|")
    else:
      line = file.readline() # Utiliser pour verifier s'il reste des lignes avec len(line) == 0 et couper pour eviter une exception
      if len(line) == 0:
        break
      my_player.x, my_player.y, my_player.life, opp_player.life = [int(i) for i in line.split()]
      sonar_result = file.readline().split()
      opponent_orders = file.readline().split("|")
    
    # On parse les ordres adverses pour detecter la position la plus probable de celui-ci
    for o in opponent_orders:
      if "MOVE" in o:
        mouvement = o.split()[1]
        opp_player.calculate_is_possible(mouvement=mouvement)
      elif "TORPEDO" in o:
        case_coordinate = (int(o.split()[1]), int(o.split()[2]))
        opp_player.calculate_torpedo_impact(torpedo_coordinates=case_coordinate)
      elif "SILENCE" in o:
        opp_player.calculate_silence()

    # On copie la grille de fin dans la grille de depart pour le prochain tour
    opp_player.grid_start.copy(opp_player.grid_end)
    
    # Calcule des uns par secteur (on le fait dans une méthode séparé pour le faire qu'une seule dans toute la boucle)
    new_pos = opp_player.calculate_ones_by_sectors_and_max()

    # On calcule nos ordres en fonction de la position probable de l'adversaire
    order = f"{my_player.get_best_move(new_pos)} {my_player.get_best_item_to_charge()}"

    should_use_torpedo = None # TODO : Implementer l'algo de gestion des tirs de torpille
    sector_of_sonar = opp_player.should_use_sonar(new_pos)
    if should_use_torpedo is not None:
      pass
    elif sector_of_sonar is not None:
      order = f"{order} | SONAR {sector_of_sonar}"
      sector_of_sonar = None
        
    # On affiche la grille des positions possibles de l'adversaire et on envoie l'ordre final
    print(opp_player.grid_end, file=sys.stderr, flush=True)
    print(order)