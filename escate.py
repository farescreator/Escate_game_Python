import random
import json
from typing import Tuple, List, Optional, Set

# ==================== CLASSES DE BASE ====================

Coord = Tuple[int, int]


class Chat:
    def __init__(self, position: Coord, capturé=False, evadé=False):
        self.position = position
        self.r, self.c = position
        self.capturé = capturé
        self.evadé = evadé
        self.pos = position

    def __repr__(self):
        return f"Chat(pos={self.position}, capturé={self.capturé}, evadé={self.evadé})"


class Gardien:
    def __init__(self, position: Coord):
        self.position = position
        self.r, self.c = position
        self.pos = position

    def __repr__(self):
        return f"Gardien(pos={self.position})"


class Robot:
    def __init__(self, position: Coord):
        self.position = position
        self.r, self.c = position
        self.pos = position

    def __repr__(self):
        return f"Robot(pos={self.position})"


# ==================== FONCTIONNALITÉ 1 : SHADOW ====================
# Permet de rendre un chat invisible aux gardiens pendant 1 tour
# Se débloque quand un chat s'évade
# Restriction : le chat choisi doit être à plus de 2 cases d'une sortie

class Shadow:
    def __init__(self):
        self.dispo = False          # True si le joueur peut activer le shadow
        self.chat_actif = None      # Index du chat en shadow (None = aucun)
        self.tours_restants = 0     # Compteur de tours (1 tour max)

    def debloquer(self):
        # Appelé quand un chat s'évade -> rend le shadow utilisable
        self.dispo = True

    def distance(self, p1, p2):
        # Distance de Chebyshev = nb de coups pour aller de p1 à p2 (diagonale comptée)
        # Exemple : (0,0) à (2,3) -> max(2,3) = 3
        return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

    def trop_proche_sortie(self, pos_chat, sorties):
        # Vérifie si le chat est à 2 cases ou moins d'une sortie
        # Si oui -> on refuse le shadow (sinon trop facile de s'évader juste après)
        for s in sorties:
            if self.distance(pos_chat, s) <= 2:
                return True
        return False

    def activer(self, idx, chats, sorties):
        # Tente d'activer le shadow sur le chat d'index idx
        # Retourne (succès, message)

        # Vérif 1 : shadow disponible ?
        if not self.dispo:
            return False, "Pas de shadow disponible, il faut d'abord évader un chat"

        # Vérif 2 : index valide ?
        if idx < 0 or idx >= len(chats):
            return False, f"Chat {idx} n'existe pas"

        # Vérif 3 : pas déjà un chat en shadow ?
        if self.chat_actif is not None:
            return False, f"Chat {self.chat_actif} est déjà en mode shadow"

        # Vérif 4 : chat pas trop proche d'une sortie ?
        if self.trop_proche_sortie(chats[idx].position, sorties):
            return False, f"Chat {idx} est trop proche d'une sortie (max 2 cases)"

        # Tout OK -> activation
        self.chat_actif = idx
        self.tours_restants = 1
        self.dispo = False  # Consomme la dispo
        return True, f"Chat {idx} passe en mode shadow pour 1 tour (incapturable)"

    def fin_tour(self):
        # Appelé à la fin de chaque tour
        # Décrémente le compteur et désactive si expiré
        msg = []
        if self.chat_actif is not None:
            self.tours_restants -= 1
            if self.tours_restants <= 0:
                msg.append(f"Shadow terminé pour le chat {self.chat_actif}")
                self.chat_actif = None
        return msg

    def est_shadow(self, idx):
        # Retourne True si le chat à cet index est en shadow
        # Utilisé pour bloquer la capture par les gardiens
        return self.chat_actif == idx

    def update_apres_suppression(self, idx_supprime):
        # Quand un chat est retiré (évadé/capturé), les index changent
        # Cette fonction recale l'index du chat shadow
        if self.chat_actif is None:
            return
        if self.chat_actif == idx_supprime:
            # Le chat shadow lui-même est parti -> reset
            self.chat_actif = None
            self.tours_restants = 0
        elif self.chat_actif > idx_supprime:
            # Un chat avant lui est parti -> décale l'index
            self.chat_actif -= 1



# ==================== CONSTANTES ====================

CHAT = 'C'
ROBOT = 'R'
GARDIEN = 'W'
BASSIN = 'O'
SORTIE = 'S'
VIDE = 0
CHAT_SHADOW = 'Ç'  # Nouveau symbole pour chat en mode shadow

BASSIN_COORDS: Set[Coord] = {
    (2, 4), (2, 5), (2, 6),
    (3, 4), (3, 5), (3, 6)
}

SORTIES_COORDS: Set[Coord] = {
    (0, 5), (4, 0), (4, 10)
}

ZONE_DEPART_CHATS: Set[Coord] = {
    (7, 5),
    (8, 4), (8, 5), (8, 6),
    (9, 3), (9, 4), (9, 5), (9, 6), (9, 7),
    (10, 3), (10, 4), (10, 5), (10, 6), (10, 7)
}


# ==================== FONCTIONS UTILITAIRES ====================

def in_bounds(pos: Coord) -> bool:
    r, c = pos
    return 0 <= r < 11 and 0 <= c < 11


def coord_to_alpha(pos: Coord) -> str:
    ligne, col = pos
    lettre = chr(ord('A') + col)
    return f"{ligne + 1}{lettre}"


def alpha_to_coord(alpha: str) -> Coord:
    alpha = alpha.upper().strip()
    lettre = alpha[-1]
    numero = int(alpha[:-1])
    ligne = numero - 1
    col = ord(lettre) - ord('A')
    return (ligne, col)


# ==================== PLATEAU ====================

class Plateau:
    def __init__(self):
        self.grille = [[VIDE for _ in range(11)] for _ in range(11)]
        self.initialiser()

    def initialiser(self):
        for pos in BASSIN_COORDS:
            r, c = pos
            self.grille[r][c] = BASSIN

        for pos in SORTIES_COORDS:
            r, c = pos
            self.grille[r][c] = SORTIE

    def case_est_interdite_pour_gardien_robot(self, r: int, c: int) -> bool:
        pos = (r, c)
        if pos in BASSIN_COORDS:
            return True
        if pos in SORTIES_COORDS:
            return True
        if pos in ZONE_DEPART_CHATS:
            return True
        return False

    def afficher(self, chats: List[Chat], gardiens: List[Gardien], robots: List[Robot], shadow: Shadow):
        grille_affichage = [row[:] for row in self.grille]

        for i, chat in enumerate(chats):
            if not chat.capturé and not chat.evadé:
                r, c = chat.position
                if shadow.est_shadow(i):
                    grille_affichage[r][c] = CHAT_SHADOW
                else:
                    grille_affichage[r][c] = CHAT

        for gardien in gardiens:
            r, c = gardien.position
            grille_affichage[r][c] = GARDIEN

        for robot in robots:
            r, c = robot.position
            grille_affichage[r][c] = ROBOT

        print("\n   ", end="")
        for lettre in "ABCDEFGHIJK":
            print(f" {lettre} ", end="")
        print()

        for i in range(11):
            print(f"{i + 1:2} ", end="")
            for j in range(11):
                element = grille_affichage[i][j]
                if element == VIDE:
                    print(" . ", end="")
                else:
                    print(f" {element} ", end="")
            print()


# ==================== JEU PRINCIPAL ====================

class Game:
    def __init__(self):
        self.plateau = Plateau()
        self.chats: List[Chat] = []
        self.gardiens: List[Gardien] = []
        self.robots: List[Robot] = []
        self.score_chats_total = 0
        self.manche = 1
        self.joueur_chats_nom = ""
        self.joueur_gardiens_nom = ""
        self.shadow = Shadow()
        self.robot_bonus_1_spawn = False
        self.robot_bonus_2_spawn = False
        self.nb_chats_total = 14

    def _initialiser_acteurs(self):
        self.chats = [Chat(pos) for pos in ZONE_DEPART_CHATS]
        self.gardiens = [Gardien((1, 2)), Gardien((1, 8))]

        # Placement aléatoire des 9 robots
        positions_robots = self._generer_positions_robots(9)
        self.robots = [Robot(pos) for pos in positions_robots]
        self.shadow = Shadow()

    def _generer_positions_robots(self, nombre: int) -> List[Coord]:
        """Génère des positions aléatoires valides pour les robots"""
        positions = []
        tentatives_max = 1000
        tentatives = 0

        # Liste de toutes les positions déjà occupées
        positions_occupees = set()
        for chat in self.chats:
            if not chat.capturé and not chat.evadé:
                positions_occupees.add(chat.position)
        for gardien in self.gardiens:
            positions_occupees.add(gardien.position)
        for robot in self.robots:
            positions_occupees.add(robot.position)

        while len(positions) < nombre and tentatives < tentatives_max:
            r = random.randint(0, 10)
            c = random.randint(0, 10)
            pos = (r, c)

            # Vérifier que la position est valide
            if self.plateau.case_est_interdite_pour_gardien_robot(r, c):
                tentatives += 1
                continue

            # Vérifier que la position n'est pas déjà prise
            if pos in positions or pos in positions_occupees:
                tentatives += 1
                continue

            positions.append(pos)
            tentatives = 0  # Reset des tentatives quand on trouve une position

        if len(positions) < nombre:
            print(f"AVERTISSEMENT: Seulement {len(positions)} robots placés au lieu de {nombre}")

        return positions

    def initialiser_partie(self):
        print(f"\n{'=' * 50}")
        print(f"DEBUT DE LA MANCHE {self.manche}")
        print(f"{'=' * 50}")
        self.plateau = Plateau()
        self._initialiser_acteurs()
        self.robot_bonus_1_spawn = False
        self.robot_bonus_2_spawn = False
        self.nb_chats_total = len(self.chats)

    def boucle_principale(self):
        tour = 1

        while True:
            print(f"\n{'=' * 60}")
            print(f"TOUR {tour} - MANCHE {self.manche}")
            print(f"{'=' * 60}")

            self.plateau.afficher(self.chats, self.gardiens, self.robots, self.shadow)

            chats_actifs = sum(1 for c in self.chats if not c.capturé and not c.evadé)
            chats_captures = sum(1 for c in self.chats if c.capturé)
            chats_evades = sum(1 for c in self.chats if c.evadé)

            print(f"\nChats actifs: {chats_actifs} | Captures: {chats_captures} | Evades: {chats_evades}")

            if self.shadow.chat_actif is not None:
                print(f"⚡ SHADOW ACTIF: Chat {self.shadow.chat_actif} est incapturable (Ç)")

            if chats_actifs == 0:
                self.gerer_fin_manche()
                break

            print(f"\nPHASE DES CHATS ({self.joueur_chats_nom})")
            self._tour_chats()

            chats_actifs = sum(1 for c in self.chats if not c.capturé and not c.evadé)
            if chats_actifs == 0:
                self.gerer_fin_manche()
                break

            print(f"\nPHASE DES GARDIENS ({self.joueur_gardiens_nom})")
            self._tour_gardiens()

            print(f"\nPHASE DES ROBOTS (automatique)")
            self._tour_robots()

            # Gestion fin de tour shadow
            msgs = self.shadow.fin_tour()
            for msg in msgs:
                print(f"⚡ {msg}")

            tour += 1

    def _tour_chats(self):
        moves_restants = 7
        chats_deplaces_ce_tour = []

        while moves_restants > 0:
            chats_disponibles = [(i, c) for i, c in enumerate(self.chats)
                                 if not c.capturé and not c.evadé and c not in chats_deplaces_ce_tour]

            if not chats_disponibles:
                print("Aucun chat disponible")
                break

            print(f"\nDeplacement {8 - moves_restants}/7")
            print("Chats disponibles:")
            for i, chat in chats_disponibles:
                shadow_marker = " ⚡SHADOW" if self.shadow.est_shadow(i) else ""
                print(f"  [{i}] Chat en {coord_to_alpha(chat.position)}{shadow_marker}")

            choix = input("\nIndex du chat a deplacer (ou 'f' pour finir): ").strip()

            if choix.lower() == 'f':
                break

            try:
                index = int(choix)
                if index not in [i for i, _ in chats_disponibles]:
                    print("ERREUR: Index invalide ou chat deja deplace")
                    continue

                chat_selectionne = self.chats[index]
                dest_input = input(f"Destination (ex: 6F): ").strip()
                coord_dest = alpha_to_coord(dest_input)

                dr = abs(chat_selectionne.r - coord_dest[0])
                dc = abs(chat_selectionne.c - coord_dest[1])
                if max(dr, dc) != 1:
                    print("ERREUR: Deplacement invalide, doit etre d'une case adjacente (diagonale autorisee).")
                    continue

                if not in_bounds(coord_dest):
                    print("ERREUR: Hors des limites du plateau")
                    continue

                if coord_dest in BASSIN_COORDS:
                    print("ERREUR: Le chat ne peut pas aller dans l'eau.")
                    continue

                case_occupee = False
                for p in self.gardiens + self.robots:
                    if p.pos == coord_dest:
                        case_occupee = True
                        break

                for c in self.chats:
                    if not c.evadé and not c.capturé and c != chat_selectionne and c.pos == coord_dest:
                        case_occupee = True
                        break

                if case_occupee and coord_dest not in SORTIES_COORDS:
                    print("ERREUR: Case deja occupee.")
                    continue

                chat_selectionne.position = coord_dest
                chat_selectionne.r, chat_selectionne.c = coord_dest
                chat_selectionne.pos = coord_dest
                chats_deplaces_ce_tour.append(chat_selectionne)
                moves_restants -= 1

                if coord_dest in SORTIES_COORDS:
                    print(f"✨ SUCCES: Le chat s'est evade en {coord_to_alpha(coord_dest)} !")
                    chat_selectionne.evadé = True
                    self.shadow.update_apres_suppression(index)
                    self.shadow.debloquer()

                    # Vérifier si on doit spawner un robot bonus
                    self._verifier_spawn_robot_bonus()

                    # Proposition d'activer shadow
                    if self.shadow.dispo:
                        print("\n⚡ SHADOW DISPONIBLE ! Voulez-vous activer le mode shadow sur un chat ?")
                        choix_shadow = input("Index du chat (ou 'n' pour refuser): ").strip()
                        if choix_shadow.lower() != 'n':
                            try:
                                idx_shadow = int(choix_shadow)
                                ok, msg = self.shadow.activer(idx_shadow, self.chats, SORTIES_COORDS)
                                print(f"⚡ {msg}")
                            except ValueError:
                                print("Index invalide")
                else:
                    print(f"SUCCES: Chat deplace vers {coord_to_alpha(coord_dest)}")

            except (ValueError, IndexError) as e:
                print(f"ERREUR: Entree invalide: {e}")

    def _verifier_spawn_robot_bonus(self):
        """Vérifie et spawn des robots bonus selon le nombre de chats évadés"""
        nb_evades = sum(1 for c in self.chats if c.evadé)
        seuil_1 = self.nb_chats_total // 2  # Moitié des chats (7)
        seuil_2 = seuil_1 + (seuil_1 // 2)  # Moitié + moitié de moitié (10-11)

        # Premier robot bonus à 7 chats évadés
        if not self.robot_bonus_1_spawn and nb_evades >= seuil_1:
            pos_robot = self._generer_positions_robots(1)
            if pos_robot:
                self.robots.append(Robot(pos_robot[0]))
                self.robot_bonus_1_spawn = True
                print(f"\n🤖 ROBOT BONUS APPARU ! ({nb_evades} chats évadés, seuil: {seuil_1})")
                print(f"   Nouveau robot en {coord_to_alpha(pos_robot[0])}")

        # Deuxième robot bonus à 10-11 chats évadés
        elif self.robot_bonus_1_spawn and not self.robot_bonus_2_spawn and nb_evades >= seuil_2:
            pos_robot = self._generer_positions_robots(1)
            if pos_robot:
                self.robots.append(Robot(pos_robot[0]))
                self.robot_bonus_2_spawn = True
                print(f"\n🤖 DEUXIEME ROBOT BONUS APPARU ! ({nb_evades} chats évadés, seuil: {seuil_2})")
                print(f"   Nouveau robot en {coord_to_alpha(pos_robot[0])}")

    def _tour_gardiens(self):
        for idx_gardien, gardien in enumerate(self.gardiens):
            print(f"\nGardien {idx_gardien + 1}/2 en {coord_to_alpha(gardien.position)}")
            dest_input = input("Destination (ou 'p' pour passer): ").strip()

            if dest_input.lower() == 'p':
                print("Gardien passe son tour")
                continue

            try:
                coord_dest = alpha_to_coord(dest_input)
                coord_dep = gardien.pos

                dx = coord_dest[0] - coord_dep[0]
                dy = coord_dest[1] - coord_dep[1]
                dist = max(abs(dx), abs(dy))

                valid_move = False
                saut_effectue = False

                if dist == 1:
                    valid_move = True

                elif dist == 2 and (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
                    mid_r = coord_dep[0] + (dx // 2 if dx != 0 else 0)
                    mid_c = coord_dep[1] + (dy // 2 if dy != 0 else 0)

                    robot_au_milieu = any(r.r == mid_r and r.c == mid_c for r in self.robots)
                    if robot_au_milieu:
                        valid_move = True
                        saut_effectue = True
                    else:
                        print("ERREUR: Saut impossible, pas de robot a sauter.")
                        continue

                if not valid_move:
                    print("ERREUR: Deplacement invalide (max 1 case ou saut par-dessus robot).")
                    continue

                if not in_bounds(coord_dest):
                    print("ERREUR: Hors des limites du plateau")
                    continue

                if self.plateau.case_est_interdite_pour_gardien_robot(coord_dest[0], coord_dest[1]):
                    print("ERREUR: Terrain interdit aux gardiens.")
                    continue

                case_occupee_par_autre = False
                for p in self.gardiens + self.robots:
                    if p != gardien and p.pos == coord_dest:
                        case_occupee_par_autre = True
                        break

                if case_occupee_par_autre:
                    print("ERREUR: Case occupee par un gardien ou robot.")
                    continue

                gardien.position = coord_dest
                gardien.r, gardien.c = coord_dest
                gardien.pos = coord_dest

                if saut_effectue:
                    print(f"SUCCES: Gardien saute vers {coord_to_alpha(coord_dest)}")
                else:
                    print(f"SUCCES: Gardien deplace vers {coord_to_alpha(coord_dest)}")

                for i, chat in enumerate(self.chats):
                    if not chat.evadé and not chat.capturé and chat.pos == coord_dest:
                        if self.shadow.est_shadow(i):
                            print(f"⚡ Chat en mode SHADOW ! Il ne peut pas être capturé !")
                        else:
                            print(f"CAPTURE: Chat capture en {coord_to_alpha(coord_dest)} !")
                            chat.capturé = True
                            self.shadow.update_apres_suppression(i)

            except (ValueError, IndexError) as e:
                print(f"ERREUR: Entree invalide: {e}")

    def _tour_robots(self):
        for idx, robot in enumerate(self.robots):
            if random.randint(1, 3) == 1:

                voisins_possibles = [
                    (robot.r + 1, robot.c), (robot.r - 1, robot.c),
                    (robot.r, robot.c + 1), (robot.r, robot.c - 1)
                ]

                candidats = []
                for nr, nc in voisins_possibles:
                    if not in_bounds((nr, nc)):
                        continue

                    if self.plateau.case_est_interdite_pour_gardien_robot(nr, nc):
                        continue

                    occupe = False
                    for ent in self.chats + self.gardiens + self.robots:
                        if ent.pos == (nr, nc) and ent != robot:
                            occupe = True
                            break

                    if not occupe:
                        candidats.append((nr, nc))

                if candidats:
                    nouvelle_pos = random.choice(candidats)
                    robot.position = nouvelle_pos
                    robot.r, robot.c = nouvelle_pos
                    robot.pos = nouvelle_pos
                    print(f"Robot {idx}: deplace vers {coord_to_alpha(nouvelle_pos)}")
                else:
                    print(f"Robot {idx}: bloque, reste en place")
            else:
                print(f"Robot {idx}: reste immobile")

    def gerer_fin_manche(self):
        chats_evades = sum(1 for c in self.chats if c.evadé)
        self.score_chats_total += chats_evades

        print(f"\n{'=' * 60}")
        print(f"FIN DE LA MANCHE {self.manche}")
        print(f"{'=' * 60}")
        print(f"Chats evades cette manche: {chats_evades}")
        print(f"Score total: {self.score_chats_total}")

        if self.manche == 1:
            print("\nInversion des roles pour la manche 2!")
            self.joueur_chats_nom, self.joueur_gardiens_nom = \
                self.joueur_gardiens_nom, self.joueur_chats_nom
            self.manche = 2
            self.initialiser_partie()
            self.boucle_principale()
        else:
            print(f"\n{'=' * 60}")
            print("FIN DE LA PARTIE")
            print(f"{'=' * 60}")
            print(f"Score final: {self.score_chats_total} chats evades")

    def sauvegarder(self):
        try:
            donnees = {
                "manche": self.manche,
                "score_total": self.score_chats_total,
                "joueur_chats": self.joueur_chats_nom,
                "joueur_gardiens": self.joueur_gardiens_nom,
                "chats": [{"pos": c.position, "capt": c.capturé, "evad": c.evadé}
                          for c in self.chats],
                "gardiens": [g.position for g in self.gardiens],
                "robots": [r.position for r in self.robots],
            }

            with open("sauvegarde_partie.json", "w") as f:
                json.dump(donnees, f, indent=4)
            print("Sauvegarde reussie")

        except Exception as e:
            print(f"Erreur: {e}")

    @classmethod
    def charger(cls):
        try:
            with open("sauvegarde_partie.json", "r") as f:
                donnees = json.load(f)

            game = cls()
            game.manche = donnees["manche"]
            game.score_chats_total = donnees["score_total"]
            game.joueur_chats_nom = donnees["joueur_chats"]
            game.joueur_gardiens_nom = donnees["joueur_gardiens"]

            game.chats = [Chat(tuple(c["pos"]), c["capt"], c["evad"])
                          for c in donnees["chats"]]
            game.gardiens = [Gardien(tuple(g)) for g in donnees["gardiens"]]
            game.robots = [Robot(tuple(r)) for r in donnees["robots"]]

            print(f"Partie chargee (Manche {game.manche})")
            return game

        except FileNotFoundError:
            print("Fichier de sauvegarde introuvable")
            return None
        except Exception as e:
            print(f"Erreur: {e}")
            return None


# ==================== MENU PRINCIPAL ====================

def afficher_menu():
    print("\n" + "=" * 40)
    print("CHAT & GARDES")
    print("=" * 40)
    print("1. Nouvelle Partie")
    print("2. Charger Partie")
    print("3. Quitter")
    return input("Votre choix: ").strip()


def main():
    while True:
        choix = afficher_menu()

        if choix == '1':
            partie = Game()
            partie.joueur_chats_nom = input("Nom du joueur Chats (Manche 1): ").strip()
            partie.joueur_gardiens_nom = input("Nom du joueur Gardiens (Manche 1): ").strip()
            partie.initialiser_partie()
            partie.boucle_principale()

        elif choix == '2':
            partie = Game.charger()
            if partie:
                partie.boucle_principale()

        elif choix == '3':
            print("\nMerci d'avoir joue!")
            break

        else:
            print("Choix invalide")


if __name__ == "__main__":
    main()
