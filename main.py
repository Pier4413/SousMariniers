import sys
import math
import random

##############################################################################
#######################    Classe CMap   #####################################
### Tous est defini en statique our cette classe. Pas besoin d'instance    ###
##############################################################################
class CMap:
    k_MapSize = 15
    k_MapSector = 3
    k_GridSector = k_MapSize//k_MapSector

    # Info sur chaque case : clé = (x,y), donnée : {"Island", "Sector", "BoatNeighbourCellsList", "TorpedoNeighbourCellsList", "EnemyCellProbabiity" }
    CoordonatesInfo = {}

    # Liste des coordonnées (x,y) par secteur 
    SectorInfo = { 1 : [ ],  2 : [ ],  3 : [ ],  4 : [ ],
                        5 : [ ],  6 : [ ],  7 : [ ],  8 : [ ],  9 : [ ]
                        }
    for i in range(0,k_MapSize):
        for j in range(0, k_MapSize):
            sector = (i//k_GridSector)+(k_MapSector*(j//k_GridSector))+1;
            SectorInfo[sector].append((i,j))
    
    # Liste des coordonnées (x,y) seulement eau (pas ile) par secteur 
    SectorInfoOnlyWater = { 1 : [ ],  2 : [ ],  3 : [ ],  4 : [ ],
                        5 : [ ],  6 : [ ],  7 : [ ],  8 : [ ],  9 : [ ]
                        }

    # Dictionnaire prevu pour le calcul recursif
    # Clé : coordonnées (x,y) : Donnée : profondeur de recursivité
    CellDepthList = {}

    # Initialisation des dictionnaires
    for x in range(k_MapSize):
        for y in range(k_MapSize):

            CellDepthList[x,y] = 0

            for sectorIndex, coordonatesList  in SectorInfo.items():
                if (x,y) in coordonatesList:
                    CoordonatesInfo[x, y] = { "Island" : False, 
                                              "Sector" : sectorIndex, 
                                              "BoatNeighbourCellsList" : [], 
                                              "TorpedoNeighbourCellsList" : [], 
                                              "EnemyCellProbabiity" : 0.5}
                    break

      

##############################################################################
#######################    Classe CMyBoat   ##################################
############################################################################## 
class CMyBoat:
    def __init__(self):
        # Coordonnees des cases déjà visité
        self.CoordonatesList = []

    def getInitialPosition(self):
      l_randomSectorIndex = random.randrange(1,9)
      print("l_randomSectorIndex = "  + str(l_randomSectorIndex), file=sys.stderr, flush=True)
      print("len(CMap.SectorInfoOnlyWater[l_randomSectorIndex] = "  + str(len(CMap.SectorInfoOnlyWater[l_randomSectorIndex])), file=sys.stderr, flush=True)
      l_randomCoordonatesIndex = random.randrange(0, len(CMap.SectorInfoOnlyWater[l_randomSectorIndex]) - 1)
      return CMap.SectorInfoOnlyWater[l_randomSectorIndex][l_randomCoordonatesIndex]

    def getFreeAreaListInternal(self, x,y, i_AreaList, i_CellDepth):
      l_CurrentCellDepth = i_CellDepth + 1

      # Cellule pas deja passé
      if not (x,y) in self.CoordonatesList:
        # Cellule pas deja calculé
        if CMap.CellDepthList[x, y] == 0:
            CMap.CellDepthList[x, y] = l_CurrentCellDepth
            # Ajout de la cellule courante
            i_AreaList.append((x,y))
            # Parcours des cellules voisines
            for currentNeighbourCoordonates in CMap.CoordonatesInfo[x,y]["BoatNeighbourCellsList"] :
              i_AreaList = self.getFreeAreaListInternal(currentNeighbourCoordonates[0], 
                                                        currentNeighbourCoordonates[1], 
                                                        i_AreaList, l_CurrentCellDepth)
      return i_AreaList

    def getFreeAreaList(self, x,y):
      l_TorpedoAreaList = []
      l_TorpedoAreaList = self.getFreeAreaListInternal(x,y,l_TorpedoAreaList,0)
      
      # Reset all values
      for CurrentCellCoordonates in CMap.CellDepthList.keys():
        CMap.CellDepthList[CurrentCellCoordonates] = 0

      return l_TorpedoAreaList

    def getBestMoveOnBiggerFreeArea(self):
      # Coordonnées courante de mon bateau
      x = self.CoordonatesList[-1][0]
      y = self.CoordonatesList[-1][1]

      l_NextCoordonates = (15,15)
      l_AreaSize = 0
      for currentNeighbourCoordonates in CMap.CoordonatesInfo[x,y]["BoatNeighbourCellsList"]:    
        l_CurrentAreaSize = len(self.getFreeAreaList(currentNeighbourCoordonates[0], currentNeighbourCoordonates[1]))
        if l_CurrentAreaSize > l_AreaSize:
          l_AreaSize = l_CurrentAreaSize
          l_NextCoordonates = currentNeighbourCoordonates

      l_nextMoveString = ""
      if l_NextCoordonates == (15,15):
        l_nextMoveString = "SURFACE"
        self.CoordonatesList.clear()
      
      if l_nextMoveString == "":
        if x > 0:
          if l_NextCoordonates == (x - 1, y):
            l_nextMoveString = "MOVE W"
      if l_nextMoveString == "":
        if x < 14:
          if l_NextCoordonates == (x + 1, y):
            l_nextMoveString = "MOVE E"
      if l_nextMoveString == "":
        if y > 0:
          if l_NextCoordonates == (x, y - 1):
            l_nextMoveString = "MOVE N"
      if l_nextMoveString == "":
        if y < 14:
          if l_NextCoordonates == (x, y + 1):
            l_nextMoveString = "MOVE S"

      return l_nextMoveString

##############################################
############## MAIN ##########################
##############################################
if __name__ == '__main__':

    width, height, my_id = [int(i) for i in input().split()]
    for y in range(height):
        line = input()
        #print("line = "  + line, file=sys.stderr, flush=True)
        x = 0
        for XString in line :
            l_IsIsland = False
            if XString == "x":
                l_IsIsland = True
            else:
                CMap.SectorInfoOnlyWater[CMap.CoordonatesInfo[x, y]["Sector"]].append((x, y))
            CMap.CoordonatesInfo[x, y]["Island"] = l_IsIsland
            x = x + 1

    # Initialisation des listes de cellules proches
    for x in range(CMap.k_MapSize):
        for y in range(CMap.k_MapSize):
          # Cellules adjacentes horizontales et verticales
          l_BoatNeighbourCellsList = []
          # Cellules adjacentes horizontales, verticales et diagonales
          l_TorpedoNeighbourCellsList = []

          # Celllules horizontales et verticales
          if (x != 0) :
            if CMap.CoordonatesInfo[x - 1, y]["Island"] == False :
              l_BoatNeighbourCellsList.append((x - 1, y))
              l_TorpedoNeighbourCellsList.append((x - 1, y))
          if (y != 0) :
            if CMap.CoordonatesInfo[x, y - 1]["Island"] == False :
              l_BoatNeighbourCellsList.append((x, y - 1))
              l_TorpedoNeighbourCellsList.append((x, y - 1))
          if (x != 14) :
            if CMap.CoordonatesInfo[x + 1, y]["Island"] == False :
              l_BoatNeighbourCellsList.append((x + 1, y))
              l_TorpedoNeighbourCellsList.append((x + 1, y))
          if (y != 14) :
            if CMap.CoordonatesInfo[x, y + 1]["Island"] == False :
              l_BoatNeighbourCellsList.append((x, y + 1))
              l_TorpedoNeighbourCellsList.append((x, y + 1))
          # Cellules diagonales
          if (x != 0) and (y != 0) :
            if CMap.CoordonatesInfo[x - 1, y - 1]["Island"] == False :
              l_TorpedoNeighbourCellsList.append((x - 1, y - 1))
          if (x != 14) and (y != 0) :
            if CMap.CoordonatesInfo[x + 1, y - 1]["Island"] == False :
              l_TorpedoNeighbourCellsList.append((x + 1, y - 1))
          if (x != 14) and (y != 14) :
            if CMap.CoordonatesInfo[x + 1, y + 1]["Island"] == False :
              l_TorpedoNeighbourCellsList.append((x + 1, y + 1))
          if (x != 0) and (y != 14) :
            if CMap.CoordonatesInfo[x - 1, y + 1]["Island"] == False :
              l_TorpedoNeighbourCellsList.append((x - 1, y + 1))

          # Ajout des listes
          CMap.CoordonatesInfo[x, y]["BoatNeighbourCellsList"] = l_BoatNeighbourCellsList
          CMap.CoordonatesInfo[x, y]["TorpedoNeighbourCellsList"] = l_TorpedoNeighbourCellsList



    l_myBoat = CMyBoat()
    l_initialPosition = l_myBoat.getInitialPosition()
    print(str(l_initialPosition[0]) + " " + str(l_initialPosition[1]))

    # game loop
    while True:
        print(f"{CMap.SectorInfo}", file=sys.stderr, flush=True)
        x, y, my_life, opp_life, torpedo_cooldown, sonar_cooldown, silence_cooldown, mine_cooldown = [int(i) for i in input().split()]
        sonar_result = input()
        opponent_orders = input()
        print("LOOP : torpedo_cooldown = "  + str(torpedo_cooldown), file=sys.stderr, flush=True)
        print("LOOP : sonar_result = "  + str(sonar_result), file=sys.stderr, flush=True)
        print("LOOP : opponent_orders = "  + str(opponent_orders), file=sys.stderr, flush=True)

        l_myBoat.CoordonatesList.append((x,y))

        print(l_myBoat.getBestMoveOnBiggerFreeArea() + " TORPEDO")
