# Spécification fonctionnelle

Le jeu se présente sous la forme d'un jeu de plateau dans lequel deux utilisateurs peuvent interagir avec les différents pions présents sur le plateau 

Ce document décrit les fonctions principales du jeu ainsi que ses règles spécifiques : 


## **Mouvement Basique** 


Dans le jeu EsCATe  les déplacements constituent l’action fondamentale qui rythme chaque tour. Ils définissent la manière dont les pions (chats et gardiens/robots) évoluent sur le plateau et interagissent entre eux.

<br>
<br>

**Initiative du déplacement :**

À chaque tour, c’est l’utilisateur (joueur) qui choisit quel pion déplacer et dans quelle direction.
L’application exécute ensuite le mouvement choisi et affiche le nouvel état du plateau.

<br>

**Règles générales :**

Les pions se déplacent d’une case à la fois, dans une direction autorisée (haut, bas, gauche, droite).
Les déplacements en diagonale ne sont pas permis.
Un pion ne peut pas traverser une case occupée par un obstacle ou un autre pion adverse.
Les cases libres sont accessibles et permettent la progression vers les sorties.

<br>

**Chats :**

Les chats cherchent à atteindre une sortie pour échapper aux gardiens.
Ils se déplacent librement sur les cases disponibles, en respectant les règles de mouvement. •  Lorsqu’un chat atteint une sortie, il est considéré comme "sauvé" et retiré du plateau





## **Les Fonctions Speciales** 

<br>

### **Le Piege Furtif**

<br>

Lorsqu’un gardien se déplace, il peut choisir de poser un *"piège furtif"* sur une case libre du plateau. Ce piège reste invisible pour le joueur des chats jusqu’à ce qu’un chat y entre.

*Effet du piège :*
Si un chat marche sur la case piégée, il est immobilisé pendant un tour complet.
Pendant ce temps, il ne peut pas se déplacer et devient une cible facile pour les gardiens.
Après activation, le piège disparaît et la case redevient normale.

*Conditions d’utilisation :*
Chaque gardien ne peut poser qu’un seul piège à la fois.
Poser un piège consomme le tour du gardien (il ne peut pas se déplacer et piéger en même temps).
Les chats ne peuvent pas détecter les pièges à l’avance, sauf s’ils utilisent un pouvoir spécial (ex. invisibilité ou protection).

*Impact sur la dynamique du jeu :*
Cela ajoute une dimension de bluff et de stratégie : les gardiens doivent anticiper les déplacements des chats.
Les chats doivent prendre des risques et rester vigilants, car une mauvaise décision peut les immobiliser.
Le jeu gagne en tension et en imprévisibilité, rendant chaque tour plus excitant.

<br>
<br>


### **Pouvoir spécial : Chat invisible**

<br>

Lorsqu’un joueur parvient à faire sortir un chat par une sortie au tour précédent, il obtient un avantage stratégique pour le tour suivant. Ce pouvoir spécial consiste à rendre un chat de son choix **invisible** pendant un tour **complet**.

*Effet du pouvoir :*
Le chat choisi est placé en mode "invisible".
Pendant ce tour, il ne peut pas être capturé par les gardiens ou les robots.
Il se déplace normalement sur le plateau, mais reste hors de portée des actions adverses.

*Conditions d’activation :*
Le pouvoir est déclenché uniquement lorsqu’un chat sort par une sortie au tour précédent.
Le joueur doit désigner quel chat bénéficie de l’invisibilité au début de son nouveau tour.

*Durée :*
L’invisibilité dure exactement un tour.
À la fin du tour, le chat redevient visible et peut de nouveau être ciblé par les gardiens.
Impact sur la dynamique du jeu :
Ce pouvoir renforce la stratégie du joueur en récompensant la réussite d’une sortie.
Il permet de protéger temporairement un pion clé et d’augmenter les chances de progression vers une nouvelle sortie.
Il introduit une dimension tactique supplémentaire, obligeant l’adversaire à anticiper les déplacements d’un pion qu’il ne peut pas neutraliser
