from mistletoe import markdown

# Creation d'un gabarit HTML pour le rendu final
PAGE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<style>
</style>
</head>
<body>
{body}
</body>
</html>
"""

# Liste des propriétés CSS valides reconnues
# Pour faire un check des propriétés CSS, on peut utiliser cette liste pour valider les entrées de l'utilisateur
VALID_CSS_PROPERTIES = {
    "align-content", "align-items", "align-self", "all", "animation",
    "animation-delay", "animation-direction", "animation-duration",
    "animation-fill-mode", "animation-iteration-count", "animation-name",
    "animation-play-state", "animation-timing-function", "backdrop-filter",
    "background", "background-attachment", "background-blend-mode",
    "background-clip", "background-color", "background-image",
    "background-origin", "background-position", "background-repeat",
    "background-size", "border", "border-bottom", "border-bottom-color",
    "border-bottom-left-radius", "border-bottom-right-radius",
    "border-bottom-style", "border-bottom-width", "border-collapse",
    "border-color", "border-image", "border-left", "border-left-color",
    "border-left-style", "border-left-width", "border-radius",
    "border-right", "border-right-color", "border-right-style",
    "border-right-width", "border-spacing", "border-style", "border-top",
    "border-top-color", "border-top-left-radius", "border-top-right-radius",
    "border-top-style", "border-top-width", "border-width", "bottom",
    "box-shadow", "box-sizing", "caption-side", "caret-color", "clear",
    "clip", "clip-path", "color", "column-count", "column-gap",
    "column-rule", "column-width", "columns", "content", "cursor",
    "direction", "display", "filter", "flex", "flex-basis",
    "flex-direction", "flex-flow", "flex-grow", "flex-shrink", "flex-wrap",
    "float", "font", "font-family", "font-size", "font-style",
    "font-variant", "font-weight", "gap", "grid", "grid-area",
    "grid-column", "grid-column-end", "grid-column-start", "grid-gap",
    "grid-row", "grid-row-end", "grid-row-start", "grid-template",
    "grid-template-areas", "grid-template-columns", "grid-template-rows",
    "height", "inset", "justify-content", "justify-items", "justify-self",
    "left", "letter-spacing", "line-height", "list-style",
    "list-style-image", "list-style-position", "list-style-type", "margin",
    "margin-bottom", "margin-left", "margin-right", "margin-top",
    "max-height", "max-width", "min-height", "min-width", "object-fit",
    "object-position", "opacity", "order", "outline", "outline-color",
    "outline-offset", "outline-style", "outline-width", "overflow",
    "overflow-x", "overflow-y", "padding", "padding-bottom",
    "padding-left", "padding-right", "padding-top", "perspective",
    "pointer-events", "position", "resize", "right", "rotate", "scale",
    "table-layout", "text-align", "text-decoration", "text-indent",
    "text-overflow", "text-shadow", "text-transform", "top", "transform",
    "transform-origin", "transition", "transition-delay",
    "transition-duration", "transition-property",
    "transition-timing-function", "translate", "user-select",
    "vertical-align", "visibility", "white-space", "width", "word-break",
    "word-spacing", "word-wrap", "z-index", "src", "alt", "title"
}

def preprocess(text):
    """
    Trouve les blocs d'image @@@ et les remplace par du HTML.

    Syntaxe:

        @@@
        src: ocean.jpg
        width: 300
        height: 300
        margin-left: 50px
        margin-top: 20px
        border-radius: 10px
        @@@

    Chaque ligne est une propriété sous la forme:

        propriété: valeur
    """

    # Analyse le texte ligne par ligne
    lines = text.splitlines()
    output = []

    i = 0

    while i < len(lines):

        # Cherche le début d'un bloc @@@
        # Une fois trouvé, on cherche le prochain @@@ pour marquer la fin du bloc 
        if lines[i].strip() == "@@@":

            # Recherche le prochain @@@ qui marque la fin du bloc
            j = i + 1

            while j < len(lines) and lines[j].strip() != "@@@":
                j += 1

            # Aucun @@@ de fermeture trouvé
            if j >= len(lines):
                raise ValueError(
                    f"@@@ Invalide a la ligne {i + 1}: "
                    "@@@ de fermeture attendue."
                )

            # Dictionnaire contenant les propriétés de l'image
            properties = {}

            # Analyse chaque ligne du bloc
            for line in lines[i + 1:j]:

                # Ignore les lignes vides
                line = line.strip()

                if not line:
                    continue

                # Vérifie que la ligne contient ":"
                if ":" not in line:
                    raise ValueError(
                        f"Propriétés invalide dans le bloc @@@: {line}"
                    )

                # Sépare la propriété et sa valeur
                # On détermine la clé et la valeur en utilisant le premier ":" trouvé comme séparateur
                key, value = line.split(":", 1)

                # Nettoie les espaces
                key = key.strip()
                value = value.strip()

                if key == "alt":
                    alt_description = value
                    print("alt detected")
                    continue

                if key == "title":
                    title_description = value
                    print("title detected")
                    continue

                # Vérifie que la clé est une propriété CSS valide
                if key not in VALID_CSS_PROPERTIES:
                    raise ValueError(
                        f"Propriété CSS inconnu dans le bloc @@@ "
                        f"a la ligne {i + 1}: '{key}'"
                    )

                # Ajoute la propriété au dictionnaire
                """
                Cela ressemble a:
                {
                    "width": "300px"
                }
                """
                properties[key] = value

            # L'attribut src est obligatoire (ofc lol)
            if "src" not in properties:
                raise ValueError(
                    f"@@@ Invalide a la ligne {i + 1}: "
                    "'src' manquant."
                )

            # Récupère le chemin de l'image
            src = properties.pop("src")

            # Construction des attributs CSS
            css_properties = []

            # Transforme les propriétés en attributs CSS
            for key, value in properties.items():
                css_properties.append(f"{key}: {value}")

            # Transforme les propriétés CSS en une seule chaîne
            style = "; ".join(css_properties)

            # Génère le HTML de l'image
            html = f'<img src="{src}"'

            if style:
                html += f' style="{style};"'

            if alt_description:
                html += f' alt="{alt_description}"'

            if alt_description:
                html += f' title="{title_description}"'

            alt_description = ""  # Reset pour pas leak
            title_description = ""  # Reset pour pas leak

            # Pour fermer la balise img, on ajoute le ">" à la fin
            html += '>'

            # Ajoute le HTML à la sortie
            output.append(html)

            # Saute tout le bloc, y compris les deux @@@
            i = j + 1

        else:
            # Ligne normale de Markdown
            output.append(lines[i])
            i += 1

    # Reconstitue le texte final
    return "\n".join(output)

def render_markdown_file(md_path, html_path):
    """
    Lit un fichier Markdown, traite les blocs d'image @@@, et écrit le fichier HTML résultant.
    """

    # Lecture fichier Markdown
    try:
        with open(md_path, "r", encoding="utf-8") as fin:
            markdown_text = fin.read()
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{md_path}' n'a pas été trouvé.")
        return

    # Appele de la fonction pre-process pour traiter les blocs d'image @@@
    markdown_text = preprocess(markdown_text)
    # print(markdown_text) # debug stuff

    # Conversion du Markdown en HTML
    body = markdown(markdown_text)

    # Finalisation du code HTML avec le gabarit (post-processing) (ajout du contenue principal dans le body)
    html = PAGE_TEMPLATE.format(body=body)

    # Ecriture du fichier HTML
    with open(html_path, "w", encoding="utf-8") as fout:
        fout.write(html)
        print("Fichier HTML généré avec succès: ", html_path)

if __name__ == "__main__":
    render_markdown_file("foo.md", "foo.html")