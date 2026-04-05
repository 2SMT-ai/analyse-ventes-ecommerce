import pandas as pd
import numpy as np
import os


# Charger le fichier CSV
df = pd.read_csv('data/raw/ecommerce_sales.csv')

print(f"\n   Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes")


print("\n" + "="*50)
print("  INSPECTION INITIALE")
print("="*50)

# 1. Afficher les 5 premières lignes
print("\n--- Les 5 premières lignes ---")
print(df.head())

# 2. Afficher les 5 dernières lignes
print("\n--- Les 5 dernières lignes ---")
print(df.tail())

# 3. Afficher les types de chaque colonne
print("\n--- Types des colonnes ---")
print(df.dtypes)

# 4. Statistiques descriptives rapides
print("\n--- Statistiques descriptives ---")
print(df.describe())


print("\n" + "="*50)
print("  DÉTECTION DES PROBLÈMES")
print("="*50)

# 1. Valeurs manquantes par colonne
print("\n--- Valeurs manquantes ---")
valeurs_nulles = df.isnull().sum()
print(valeurs_nulles)

# Afficher le pourcentage
print("\n--- Pourcentage de valeurs manquantes ---")
pct_nulles = (df.isnull().sum() / len(df) * 100).round(2)
print(pct_nulles[pct_nulles > 0])  # afficher seulement celles > 0%

# 2. Doublons
print(f"\n--- Doublons ---")
n_doublons = df.duplicated().sum()
print(f"   Nombre de lignes dupliquées : {n_doublons}")

# 3. Valeurs uniques par colonne catégorielle
print("\n--- Valeurs uniques ---")
cols_cat = ['categorie', 'region', 'paiement']
for col in cols_cat:
    print(f"   {col} : {df[col].unique()}")


print("\n" + "="*50)
print("  CORRECTION DES TYPES")
print("="*50)

# Avant conversion
print(f"\n   Type de 'date' AVANT : {df['date'].dtype}")
print(f"   Exemple             : {df['date'].iloc[0]}")

# Convertir la colonne date en vrai format date
df['date'] = pd.to_datetime(df['date'])

# Après conversion
print(f"\n   Type de 'date' APRÈS : {df['date'].dtype}")
print(f"   Exemple              : {df['date'].iloc[0]}")

# Maintenant on peut extraire des informations de la date
df['annee']      = df['date'].dt.year
df['mois_num']   = df['date'].dt.month
df['jour_semaine'] = df['date'].dt.day_name()  # lundi, mardi...
df['mois_nom']   = df['date'].dt.strftime('%b') # Jan, Feb, Mar...

print("\n   Nouvelles colonnes créées depuis la date :")
print(f"   • annee        : {df['annee'].unique()}")
print(f"   • mois_num     : {sorted(df['mois_num'].unique())}")
print(f"   • jour_semaine : {df['jour_semaine'].unique()[:3]}...")
print(f"   • mois_nom     : {df['mois_nom'].unique()}")


print("\n" + "="*50)
print("  SÉPARATION DES DONNÉES")
print("="*50)

# Compter les retours
n_total    = len(df)
n_retours  = df['est_retourne'].sum()
n_valides  = n_total - n_retours
pct_retour = round(n_retours / n_total * 100, 1)

print(f"\n   Total commandes  : {n_total}")
print(f"   Retournées       : {n_retours} ({pct_retour}%)")
print(f"   Valides          : {n_valides} ({100 - pct_retour}%)")

# Créer un DataFrame avec seulement les commandes valides
# → c'est sur ce DataFrame qu'on fera toutes les analyses
df_valide = df[df['est_retourne'] == 0].copy()

print(f"\n   df_valide créé : {len(df_valide)} lignes")


print("\n" + "="*50)
print("  VALEURS ABERRANTES")
print("="*50)

# Vérifier les prix
print("\n--- Prix unitaires ---")
print(f"   Min  : {df_valide['prix_unitaire'].min()} €")
print(f"   Max  : {df_valide['prix_unitaire'].max()} €")
print(f"   Moy  : {df_valide['prix_unitaire'].mean():.2f} €")

# Vérifier les quantités
print("\n--- Quantités ---")
print(f"   Min  : {df_valide['quantite'].min()}")
print(f"   Max  : {df_valide['quantite'].max()}")
print(df_valide['quantite'].value_counts().sort_index())

# Vérifier les revenus
print("\n--- Revenus par commande ---")
print(f"   Min  : {df_valide['revenu'].min()} €")
print(f"   Max  : {df_valide['revenu'].max()} €")
print(f"   Moy  : {df_valide['revenu'].mean():.2f} €")

# Détecter les revenus négatifs (ne devrait pas exister)
revenus_negatifs = df_valide[df_valide['revenu'] < 0]
print(f"\n   Revenus négatifs : {len(revenus_negatifs)} (doit être 0)")


print("\n" + "="*50)
print("  SAUVEGARDE")
print("="*50)

# Créer le dossier si nécessaire
os.makedirs('data/processed', exist_ok=True)

# Sauvegarder le dataset complet nettoyé (avec les retours)
df.to_csv('data/processed/ecommerce_complet.csv', index=False)

# Sauvegarder seulement les commandes valides
df_valide.to_csv('data/processed/ecommerce_valide.csv', index=False)

print(f"\n   ✅ data/processed/ecommerce_complet.csv")
print(f"      → {len(df)} lignes, {len(df.columns)} colonnes")

print(f"\n   ✅ data/processed/ecommerce_valide.csv")
print(f"      → {len(df_valide)} lignes, {len(df_valide.columns)} colonnes")

print("\n" + "="*50)
print("="*50)