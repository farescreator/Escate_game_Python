# EsCATe Game

Jeu de plateau à deux joueurs en Python, jouable dans le terminal.
Projet réalisé dans le cadre du Bachelor Cybersécurité (semestre 1).

## Principe

Des chats sont retenus dans une pension (plateau 11×11). Un joueur contrôle les chats et cherche à les faire s'évader par l'une des trois sorties. L'autre joueur contrôle deux gardiens qui tentent de les capturer, pendant que des robots aspirateurs autonomes gênent les déplacements.

- Une partie compte deux manches, les rôles sont inversés à la deuxième.
- Chaque chat évadé rapporte un point au joueur des chats.
- Un tour se déroule en trois phases : chats, gardiens, robots.
- Les règles spécifiques (piège furtif, chat invisible) sont décrites dans [`docs/specification.md`](docs/specification.md).

## Lancer le jeu

Prérequis : Python 3.8 ou plus, aucune dépendance externe.

```bash
python escate.py
```

Le menu permet de lancer une nouvelle partie, de charger une partie sauvegardée (`sauvegarde_partie.json`) ou de quitter.

## Ce que le projet met en pratique

- Programmation orientée objet (classes `Chat`, `Gardien`, `Robot`, `Plateau`, `Game`)
- Gestion des règles de déplacement, des captures et des évasions
- Sauvegarde et chargement de l'état de la partie en JSON
- Rédaction d'une spécification fonctionnelle

## Ma contribution

<!-- À compléter honnêtement : ce que tu as écrit toi-même (modules, fonctionnalités, tests). Supprime cette section si tu as tout réalisé seul. -->

## Pistes d'amélioration

- Ajouter des tests automatisés (`pytest`) sur les règles de déplacement
- Découper `escate.py` en plusieurs modules
