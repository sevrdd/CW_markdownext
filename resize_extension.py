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
                    "expected closing @@@."
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
                    "missing 'src'."
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
    with open(md_path, "r", encoding="utf-8") as fin:
        markdown_text = fin.read()

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

if __name__ == "__main__":
    render_markdown_file("foo.md", "foo.html")
    print("Wrote foo.html")