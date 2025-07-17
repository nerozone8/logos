import os
from PIL import Image, ImageDraw, ImageFont
import itertools
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm  # Per la barra di avanzamento

# ✅ Dizionario delle squadre suddiviso per lega
leghe = {
    "Serie A": {
        "Atalanta": [(0, 0, 0), (0, 0, 255)],
        "Bologna": [(153, 0, 0), (0, 0, 153)],
        "Cagliari": [(178, 34, 34), (0, 0, 139)],
        "Como": [(30, 144, 255)],
        "Empoli": [(0, 191, 255)],
        "Fiorentina": [(138, 43, 226)],
        "Genoa": [(220, 20, 60), (0, 0, 139)],
        "Verona": [(255, 255, 0), (0, 0, 139)],
        "Inter": [(0, 51, 153), (0, 0, 0)],
        "Juventus": [(255, 255, 255), (0, 0, 0)],
        "Lazio": [(135, 206, 235), (255, 255, 255)],
        "Lecce": [(255, 215, 0), (255, 0, 0)],
        "Milan": [(255, 0, 0), (0, 0, 0)],
        "Monza": [(255, 0, 0)],
        "Napoli": [(0, 102, 204)],
        "Roma": [(212, 175, 55), (128, 0, 0)],
        "Torino": [(128, 0, 32)],
        "Udinese": [(192, 192, 192), (0, 0, 0)],
        "Venezia": [(0, 128, 0), (255, 165, 0), (0, 0, 0)],
        "Parma": [(255, 221, 51), (0, 51, 153)]
    },
    "Serie B": {
       "Sassuolo": [(0, 100, 0), (0, 0, 0)],
    "Pisa": [(0, 0, 0), (0, 0, 255)],
    "Spezia": [(255, 255, 255), (0, 0, 0)],
    "Cremonese": [(178, 34, 34), (128, 128, 128)],
    "Juve Stabia": [(255, 255, 0), (0, 0, 0)],
    "Palermo": [(255, 182, 193), (0, 0, 0)],
    "Catanzaro": [(255, 255, 0), (255, 0, 0)],
    "Bari": [(204, 0, 0), (255, 255, 255)],
    "Modena": [(255, 255, 0), (0, 0, 139)],
    "Cesena": [(255, 255, 255), (0, 0, 0)],
    "Carrarese": [(255, 255, 0), (0, 0, 255)],
    "Frosinone": [(255, 221, 0), (0, 67, 147)],
    "Südtirol": [(255, 0, 0), (255, 255, 255)],
    "Mantova": [(255, 0, 0), (255, 255, 255)],
    "Salernitana": [(102, 0, 0), (255, 255, 255)],
    "Brescia": [(0, 0, 255), (255, 255, 255)],
    "Sampdoria": [(0, 0, 255), (255, 255, 255)],
    "Reggiana": [(128, 0, 32), (255, 255, 255)],
    "Cittadella": [(128, 0, 0), (255, 255, 255)],
    "Cosenza": [(0, 51, 102), (204, 0, 0)]
    },
    "Serie C": {
 
    "Padova": [(0, 0, 0), (255, 255, 255)],  # nero e bianco
    "Vicenza": [(0, 51, 153), (255, 255, 255)],  # blu scuro e bianco
    "FeralpiSalo": [(0, 102, 0), (255, 255, 255)],  # verde scuro e bianco
    "AlbinoLeffe": [(0, 0, 128), (255, 255, 255)],  # blu navy e bianco
    "Renate": [(255, 0, 0), (255, 255, 255)],  # rosso e bianco
    "Giana Erminio": [(0, 128, 0), (255, 255, 255)],  # verde e bianco
    "Trento": [(0, 51, 102), (255, 255, 255)],  # blu scuro e bianco
    "Atalanta U-23": [(0, 0, 0), (0, 255, 0)],  # nero e verde
    "Virtus Verona": [(255, 255, 255), (255, 0, 0)],  # bianco e rosso
    "Arzignano Valchiampo": [(255, 255, 0), (0, 128, 128)],  # giallo e celeste
    "Novara": [(255, 255, 255), (0, 0, 255)],  # bianco e blu
    "Alcione": [(255, 165, 0), (0, 0, 255)],  # arancione e blu
    "Lecco": [(0, 0, 128), (255, 255, 255)],  # blu navy e bianco
    "Pergolettese": [(255, 0, 0), (255, 255, 255)],  # rosso e bianco
    "Lumezzane": [(0, 128, 0), (255, 255, 255)],  # verde e bianco
    "Triestina": [(255, 255, 255), (0, 0, 255)],  # bianco e blu
    "Pro Vercelli": [(255, 255, 255), (0, 0, 255)],  # bianco e blu
    "Pro Patria": [(0, 128, 0), (255, 255, 255)],  # verde e bianco
    "Caldiero Terme": [(255, 0, 0), (255, 255, 255)]  # rosso e bianco
    
    }
}

# ✅ Crea cartelle se non esistono
os.makedirs("partite", exist_ok=True)

def carica_logo(nome_squadra, dimensione_logo=(60, 60)):
    base_dir = os.path.abspath(os.path.dirname(__file__))  # Usa percorso assoluto per sicurezza
    percorso_logo = os.path.join(base_dir, "loghi", f"{nome_squadra}.png")
    if not os.path.exists(percorso_logo):
        return None  # Logo non trovato
    logo = Image.open(percorso_logo).convert("RGBA")
    logo = logo.resize(dimensione_logo, Image.LANCZOS)
    return logo

def aggiungi_logo_o_iniziali(img, draw, squadra, posizione_x, posizione_y, larghezza, altezza, dimensione_logo=(60, 60)):
    logo = carica_logo(squadra, dimensione_logo)
    if logo:
        posizione_logo = (
            posizione_x + (larghezza - logo.width) // 2,
            posizione_y + (altezza - logo.height) // 2
        )
        img.paste(logo, posizione_logo, logo)
    else:
        iniziali = ''.join([word[0].upper() for word in squadra.split()])
        try:
            # Cambia il font se "arial.ttf" non è disponibile.
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            # Usa un font di default
            font = ImageFont.load_default()

        # Utilizza textbbox per ottenere le dimensioni del testo
        bbox = draw.textbbox((0, 0), iniziali, font=font)
        text_width = bbox[2] - bbox[0]  # Larghezza
        text_height = bbox[3] - bbox[1]  # Altezza

        position = (posizione_x + (larghezza // 2 - text_width // 2), posizione_y + (altezza // 2 - text_height // 2))
        draw.text((position[0] - 1, position[1] - 1), iniziali, font=font, fill=(0, 0, 0))  # Ombra nera
        draw.text(position, iniziali, font=font, fill=(255, 255, 255))  # Testo bianco

def genera_immagine(params):
    casa, trasferta, larghezza, altezza, spessore_linea = params
    img = Image.new("RGB", (larghezza, altezza), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Ottieni i colori delle squadre da tutte le leghe
    colori_casa = None
    colori_trasferta = None

    for lega in leghe.values():
        if casa in lega:
            colori_casa = lega[casa]
        if trasferta in lega:
            colori_trasferta = lega[trasferta]

    if not colori_casa or not colori_trasferta:
        print(f"Colore non trovato per squadre: {casa}, {trasferta}")
        return None

    # Colori squadra casa
    if len(colori_casa) == 1:
        draw.rectangle([(0, 0), (larghezza // 2, altezza)], fill=colori_casa[0])
    else:
        draw.rectangle([(0, 0), (larghezza // 4, altezza)], fill=colori_casa[0])
        draw.rectangle([(larghezza // 4, 0), (larghezza // 2, altezza)], fill=colori_casa[1])

    # Colori squadra trasferta
    if len(colori_trasferta) == 1:
        draw.rectangle([(larghezza // 2, 0), (larghezza, altezza)], fill=colori_trasferta[0])
    else:
        draw.rectangle([(larghezza // 2, 0), (larghezza * 3 // 4, altezza)], fill=colori_trasferta[0])
        draw.rectangle([(larghezza * 3 // 4, 0), (larghezza, altezza)], fill=colori_trasferta[1])

    # Linea bianca centrale
    draw.line([(larghezza // 2, 0), (larghezza // 2, altezza)], fill=(255, 255, 255), width=spessore_linea)

    # Aggiungi logo o iniziali
    aggiungi_logo_o_iniziali(img, draw, casa, 0, 0, larghezza // 2, altezza)
    aggiungi_logo_o_iniziali(img, draw, trasferta, larghezza // 2, 0, larghezza // 2, altezza)

    # Nome file
    nome_file = f"{casa.lower().replace(' ', '_')}_vs_{trasferta.lower().replace(' ', '_')}.png"
    img.save(os.path.join("partite", nome_file))
    return nome_file

def main():
    larghezza = 200
    altezza = 100
    spessore_linea = 2

    combinazioni = []
    for lega in leghe.values():
        combinazioni += list(itertools.permutations(lega.keys(), 2))

    params = [(casa, trasferta, larghezza, altezza, spessore_linea) for casa, trasferta in combinazioni]

    # Barra di avanzamento
    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(genera_immagine, params), total=len(params), desc="Generazione banner"))

if __name__ == "__main__":
    main()