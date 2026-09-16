from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.text.run import Run
from docx.oxml.ns import qn
from pathlib import Path
import mistletoe
import re
import unicodedata
import html as module_html


# --------------------------------------------------
# Conversion du gras, italique et images
# --------------------------------------------------

def convertir_run(run_element, paragraphe, dossier_images):
    run = Run(run_element, paragraphe)
    texte = run.text

    # Gras + italique
    if run.bold and run.italic:
        texte = f"***{texte}***"

    # Gras
    elif run.bold:
        texte = f"**{texte}**"

    # Italique
    elif run.italic:
        texte = f"*{texte}*"

    resultat = texte

    # Recherche d'images dans le run
    for element in run_element.iter():
        if element.tag == qn("a:blip"):

            relation_id = element.get(qn("r:embed"))

            if relation_id:
                relation = paragraphe.part.rels[relation_id]
                image = relation.target_part

                nom_image = Path(image.partname).name
                chemin_image = dossier_images / nom_image

                # Sauvegarde de l'image
                with open(chemin_image, "wb") as fichier:
                    fichier.write(image.blob)

                # Syntaxe Markdown pour une image
                resultat += f"\n\n![{nom_image}](images/{nom_image})\n\n"

    return resultat


# --------------------------------------------------
# Conversion d'un paragraphe
# --------------------------------------------------

def convertir_paragraphe(paragraphe, dossier_images):
    texte_markdown = ""

    # On parcourt les éléments XML pour détecter
    # les textes normaux ET les hyperliens
    for element in paragraphe._p:

        # Texte normal
        if element.tag == qn("w:r"):
            texte_markdown += convertir_run(
                element,
                paragraphe,
                dossier_images
            )

        # Hyperlien
        elif element.tag == qn("w:hyperlink"):
            relation_id = element.get(qn("r:id"))
            texte_lien = ""

            # Récupérer le texte du lien
            for run_element in element.findall(qn("w:r")):
                texte_lien += convertir_run(
                    run_element,
                    paragraphe,
                    dossier_images
                )

            # Récupérer l'adresse URL
            if relation_id:
                relation = paragraphe.part.rels[relation_id]
                url = relation.target_ref

                # Conversion en Markdown
                texte_markdown += f"[{texte_lien}]({url})"

            else:
                texte_markdown += texte_lien

    return texte_markdown


# --------------------------------------------------
# Conversion d'un tableau Word en Markdown
# --------------------------------------------------

def convertir_tableau(tableau, dossier_images):
    markdown = "\n\n"

    for numero_ligne, ligne in enumerate(tableau.rows):
        cellules = []

        for cellule in ligne.cells:
            contenu = ""

            for paragraphe in cellule.paragraphs:
                texte = convertir_paragraphe(
                    paragraphe,
                    dossier_images
                ).strip()

                if texte:
                    contenu += texte + " "

            contenu = contenu.strip()
            contenu = contenu.replace("|", "\\|")
            contenu = contenu.replace("\n", "<br>")

            cellules.append(contenu)

        markdown += "| " + " | ".join(cellules) + " |\n"

        # Séparateur Markdown après la première ligne
        if numero_ligne == 0:
            markdown += "|"

            for _ in cellules:
                markdown += " --- |"

            markdown += "\n"

    markdown += "\n"

    return markdown


# --------------------------------------------------
# Conversion Word vers Markdown
# --------------------------------------------------

def convertir_en_markdown(chemin, dossier_images):
    document = Document(chemin)
    markdown = ""

    # Garder l'ordre des paragraphes et tableaux
    for element in document.element.body.iterchildren():

        # ------------------------------------------
        # PARAGRAPHE
        # ------------------------------------------

        if element.tag == qn("w:p"):
            paragraphe = Paragraph(element, document)

            texte = convertir_paragraphe(
                paragraphe,
                dossier_images
            ).strip()

            if texte == "":
                continue

            style = paragraphe.style.name

            # Titres
            if style == "Heading 1":
                markdown += "# " + texte + "\n\n"

            elif style == "Heading 2":
                markdown += "## " + texte + "\n\n"

            elif style == "Heading 3":
                markdown += "### " + texte + "\n\n"

            # Liste à puces
            elif style == "List Bullet":
                markdown += "- " + texte + "\n"

            # Liste numérotée
            elif style == "List Number":
                markdown += "1. " + texte + "\n"

            # Paragraphe normal
            else:
                markdown += texte + "\n\n"

        # ------------------------------------------
        # TABLEAU
        # ------------------------------------------

        elif element.tag == qn("w:tbl"):
            tableau = Table(element, document)

            markdown += convertir_tableau(
                tableau,
                dossier_images
            )

    return markdown


# --------------------------------------------------
# Création d'un identifiant pour les titres
# --------------------------------------------------

def creer_identifiant(titre):

    # Retirer les accents
    titre = unicodedata.normalize("NFKD", titre)

    titre = "".join(
        caractere for caractere in titre
        if not unicodedata.combining(caractere)
    )

    # Convertir en minuscules
    titre = titre.lower()

    # Remplacer les espaces par des tirets
    titre = re.sub(r"\s+", "-", titre)

    # Retirer les caractères spéciaux
    titre = re.sub(r"[^\w-]", "", titre)

    return titre or "section"


# --------------------------------------------------
# Création de la table des matières
# --------------------------------------------------

def creer_table_matiere(markdown):

    # Rechercher le marqueur contenu:
    marqueur = None

    for ligne in re.finditer(r"(?m)^[^\r\n]*", markdown):

        texte = ligne.group(0)

        # Supprimer les astérisques Markdown
        texte = texte.replace("*", "")

        # Supprimer les espaces
        texte = re.sub(r"\s+", "", texte)

        # Vérifier si le marqueur correspond
        if texte.lower() == "contenu:":

            marqueur = ligne
            break

    # Si le marqueur n'existe pas
    if marqueur is None:

        print("Aucun **contenu:** détecté.")

        return markdown

    print("**contenu:** détecté.")

    # Début de la table des matières
    table = "**Table des matières**\n\n"

    # Rechercher les titres Markdown
    modele = r"(?m)^(#{1,6})[ \t]+(.+?)[ \t]*$"

    identifiants = {}

    for correspondance in re.finditer(modele, markdown):

        # Déterminer le niveau du titre
        niveau = len(correspondance.group(1))

        # Récupérer le titre
        titre = correspondance.group(2).strip()

        # Retirer les marqueurs simples de gras et d'italique
        titre_simple = titre.replace("*", "")

        # Créer l'identifiant
        identifiant = creer_identifiant(titre_simple)

        # Éviter les identifiants identiques
        nombre = identifiants.get(identifiant, 0)

        identifiants[identifiant] = nombre + 1

        if nombre > 0:
            identifiant += f"-{nombre}"

        # Ajouter les titres de niveau 2 à 6
        if niveau >= 2:

            indentation = "  " * (niveau - 2)

            table += (
                f"{indentation}- "
                f"[{titre_simple}](#{identifiant})\n"
            )

    # Insérer la table après le marqueur
    position = marqueur.end()

    markdown = (
        markdown[:position]
        + "\n\n"
        + table
        + "\n"
        + markdown[position:]
    )

    print("Table des matières créée.")

    return markdown


# --------------------------------------------------
# Ajouter les identifiants aux titres HTML
# --------------------------------------------------

def ajouter_identifiants_html(contenu_html):

    identifiants = {}

    # Rechercher les titres HTML h1 à h6
    modele = r"<h([1-6])>(.*?)</h\1>"

    def modifier_titre(correspondance):

        niveau = correspondance.group(1)

        contenu = correspondance.group(2)

        # Récupérer uniquement le texte du titre
        titre = re.sub(r"<[^>]+>", "", contenu)

        titre = module_html.unescape(titre)

        # Créer l'identifiant
        identifiant = creer_identifiant(titre)

        # Éviter les identifiants identiques
        nombre = identifiants.get(identifiant, 0)

        identifiants[identifiant] = nombre + 1

        if nombre > 0:
            identifiant += f"-{nombre}"

        # Ajouter l'identifiant au titre HTML
        return (
            f'<h{niveau} id="{identifiant}">'
            f'{contenu}'
            f'</h{niveau}>'
        )

    # Modifier tous les titres HTML
    contenu_html = re.sub(
        modele,
        modifier_titre,
        contenu_html,
        flags=re.DOTALL
    )

    return contenu_html


# --------------------------------------------------
# CHEMINS
# --------------------------------------------------

dossier_script = Path(__file__).parent

fichier_word = dossier_script / "test.docx"
fichier_markdown = dossier_script / "output.md"
fichier_html = dossier_script / "output.html"
dossier_images = dossier_script / "images"

# Créer le dossier images s'il n'existe pas
dossier_images.mkdir(exist_ok=True)


# --------------------------------------------------
# WORD VERS MARKDOWN
# --------------------------------------------------

markdown = convertir_en_markdown(
    fichier_word,
    dossier_images
)


# --------------------------------------------------
# CRÉATION DE LA TABLE DES MATIÈRES
# --------------------------------------------------

markdown = creer_table_matiere(markdown)


# --------------------------------------------------
# SAUVEGARDER LE MARKDOWN
# --------------------------------------------------

with open(
    fichier_markdown,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(markdown)


# --------------------------------------------------
# MARKDOWN VERS HTML AVEC MISTLETOE
# --------------------------------------------------

contenu_html = mistletoe.markdown(markdown)


# --------------------------------------------------
# AJOUT DES IDENTIFIANTS AUX TITRES HTML
# --------------------------------------------------

contenu_html = ajouter_identifiants_html(contenu_html)


# --------------------------------------------------
# CRÉATION DE LA PAGE HTML
# --------------------------------------------------

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Document converti</title>

    <style>
        table {{
            border-collapse: collapse;
            margin-top: 20px;
            margin-bottom: 20px;
        }}

        th, td {{
            border: 1px solid black;
            padding: 10px;
            text-align: left;
        }}

        img {{
            max-width: 500px;
            height: auto;
        }}
    </style>
</head>
<body>
{contenu_html}
</body>
</html>
"""


# --------------------------------------------------
# SAUVEGARDE DU FICHIER HTML
# --------------------------------------------------

with open(
    fichier_html,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(html)


print("Conversion terminée.")
print("Markdown :", fichier_markdown)
print("HTML :", fichier_html)
print("Images :", dossier_images)