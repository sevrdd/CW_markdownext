# Markdown extension

## Scrum Master: Said Tarzalt
## Développeur: William Champagne (sevrdd)

Extension permettant de gérer plusieurs paramètres pour différents types d’images. Cette extension permet d'utiliser les multiples paramètres pour image de CSS (Pragmatiquement; un CSS wrapper).

---

## Guide d'utilisateur
---
Vue d'ensemble

Ce script convertit un fichier Markdown en HTML, avec une syntaxe spéciale (@@@) permettant d'insérer des images stylées (taille, marges, coins arrondis, etc.) sans écrire de HTML directement.

Utilisation de base

from mistletoe_imgext import render_markdown_file

render_markdown_file("foo.md", "foo.html")

Pour insérer une image avec des styles personnalisés, utilisez la syntaxe d'exemple suivante:

```
@@@
src: ocean.jpg
width: 300px
height: 300px
margin-left: 50px
margin-top: 20px
border-radius: 10px
@@@
```


Puisque cette extension est un wrapper CSS, les propriétés possibles, ainsi que la syntaxe associée sont identique.

Voici une liste des propriétées possibles/acceptées:

https://www.w3schools.com/css/css3_images.asp
