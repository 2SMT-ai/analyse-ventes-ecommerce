import pandas as pd      # pour créer le tableau de données
import numpy as np       # pour les calculs et le hasard
from faker import Faker  # pour générer des faux noms réalistes
import random            # pour faire des choix aléatoires
import os                # pour créer des dossiers

# Initialiser Faker en français
fake = Faker('fr_FR')

# Fixer les "graines" du hasard
# → sans ça, les données changent à chaque exécution
# → avec ça, on obtient toujours les mêmes données
np.random.seed(42)
random.seed(42)

# Nombre de commandes à générer
N_COMMANDES = 2000

print(f"   On va générer {N_COMMANDES} commandes")


# Dictionnaire : catégorie → liste de (produit, prix_de_base)
PRODUITS = {
    'Électronique': [
        ('Smartphone Samsung', 450),
        ('Écouteurs Bluetooth', 45),
        ('Laptop Lenovo', 620),
        ('Tablette iPad', 380),
        ('Montre connectée', 130),
    ],
    'Vêtements': [
        ('T-shirt premium', 25),
        ('Jean slim', 55),
        ('Robe d été', 40),
        ('Veste cuir', 120),
        ('Sneakers Nike', 85),
    ],
    'Alimentation': [
        ('Café arabica 1kg', 18),
        ('Thé vert BIO', 12),
        ('Huile olive premium', 22),
        ('Chocolat noir', 8),
        ('Miel naturel', 15),
    ],
    'Sport': [
        ('Tapis yoga', 30),
        ('Haltères 5kg', 25),
        ('Vélo elliptique', 280),
        ('Gourde sport', 18),
        ('Resistance bands', 15),
    ],
    'Beauté': [
        ('Crème hydratante', 25),
        ('Parfum femme', 65),
        ('Sérum vitamine C', 40),
        ('Mascara', 15),
        ('Rouge à lèvres', 18),
    ],
}

# Les catégories avec leurs probabilités d'apparition
# → Électronique apparaît 30% du temps, Vêtements 25%, etc.
CATEGORIES     = list(PRODUITS.keys())
CAT_POIDS      = [0.30, 0.25, 0.20, 0.15, 0.10]

# Les régions avec leurs probabilités
REGIONS        = ['Dakar', 'Thiès', 'Abidjan', 'Bamako', 'Paris', 'Lyon', 'Douala']
REGION_POIDS   = [0.30, 0.10, 0.20, 0.15, 0.12, 0.08, 0.05]

# Les modes de paiement
PAIEMENTS      = ['Mobile Money', 'Carte bancaire', 'Virement', 'Cash on delivery']
PAIE_POIDS     = [0.40, 0.35, 0.10, 0.15]

print(f"   {len(CATEGORIES)} catégories, {sum(len(v) for v in PRODUITS.values())} produits")


# Générer N_COMMANDES dates réparties sur toute l'année 2023
dates = pd.date_range(
    start='2023-01-01',
    end='2023-12-31',
    periods=N_COMMANDES   # répartir équitablement
)

# Trier les dates (du plus ancien au plus récent)
dates = sorted(dates)

print(f"   De {dates[0].date()} à {dates[-1].date()}")


# Liste qui va stocker toutes les commandes
commandes = []

for i, date in enumerate(dates):

    # 1. Choisir une catégorie (selon les poids définis)
    categorie = random.choices(CATEGORIES, weights=CAT_POIDS)[0]

    # 2. Choisir un produit dans cette catégorie
    produit, prix_base = random.choice(PRODUITS[categorie])

    # 3. Choisir une quantité (1 article la plupart du temps)
    quantite = random.choices(
        [1, 2, 3, 4, 5],
        weights=[0.55, 0.25, 0.12, 0.05, 0.03]
    )[0]

    # 4. Choisir une remise (souvent pas de remise)
    remise = random.choices(
        [0, 5, 10, 15, 20],
        weights=[0.50, 0.20, 0.15, 0.10, 0.05]
    )[0]

    # 5. Calculer le prix de vente après remise
    prix_vente = round(prix_base * (1 - remise / 100), 2)

    # 6. Calculer le revenu total
    revenu = round(prix_vente * quantite, 2)

    # 7. Créer la ligne de données (un dictionnaire)
    commande = {
        'order_id'       : f'ORD-{10000 + i}',
        'date'           : date.date(),
        'mois'           : date.month,
        'trimestre'      : f'Q{(date.month - 1) // 3 + 1}',
        'client_id'      : f'CLIENT-{random.randint(1000, 3500)}',
        'client_nom'     : fake.name(),
        'region'         : random.choices(REGIONS, weights=REGION_POIDS)[0],
        'categorie'      : categorie,
        'produit'        : produit,
        'quantite'       : quantite,
        'prix_unitaire'  : prix_base,
        'remise_pct'     : remise,
        'prix_vente'     : prix_vente,
        'revenu'         : revenu,
        'paiement'       : random.choices(PAIEMENTS, weights=PAIE_POIDS)[0],
        'est_retourne'   : random.choices([0, 1], weights=[0.93, 0.07])[0],
    }

    # 8. Ajouter la commande à la liste
    commandes.append(commande)

print(f"✅{len(commandes)} commandes générées")


# Transformer la liste de dictionnaires en DataFrame Pandas
df = pd.DataFrame(commandes)

# Créer le dossier si il n'existe pas
os.makedirs('data/raw', exist_ok=True)

# Sauvegarder en CSV
df.to_csv('data/raw/ecommerce_sales.csv', index=False)

# Afficher un résumé
print("\n" + "="*50)
print("  RÉSUMÉ DU DATASET GÉNÉRÉ")
print("="*50)
print(f"  Lignes      : {len(df)}")
print(f"  Colonnes    : {len(df.columns)}")
print(f"  Fichier     : data/raw/ecommerce_sales.csv")
print("="*50)

# Afficher les 3 premières lignes
print("\nAperçu des premières lignes :")
print(df.head(3).to_string())

# Afficher les colonnes créées
print(f"\nColonnes créées :")
for col in df.columns:
    print(f"  • {col} ({df[col].dtype})")