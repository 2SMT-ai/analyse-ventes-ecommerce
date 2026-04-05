import pandas as pd
import numpy as np
import os

# Charger les données nettoyées (valides uniquement)
df = pd.read_csv('data/processed/ecommerce_valide.csv',
                 parse_dates=['date'])

print("✅ Bloc 1 OK - données chargées")
print(f"   {len(df)} commandes valides prêtes pour l'analyse")



print("\n" + "="*55)
print("  KPIs GLOBAUX")
print("="*55)

# Calculer chaque KPI
ca_total        = df['revenu'].sum()
nb_commandes    = len(df)
panier_moyen    = df['revenu'].mean()
clients_uniques = df['client_id'].nunique()
unites_vendues  = df['quantite'].sum()

# Charger aussi le dataset complet pour le taux de retour
df_complet   = pd.read_csv('data/processed/ecommerce_complet.csv')
taux_retour  = df_complet['est_retourne'].mean() * 100

# Afficher les résultats
print(f"""
  💰 CA Total          : {ca_total:>12,.2f} €
  📦 Commandes         : {nb_commandes:>12,}
  🛒 Panier moyen      : {panier_moyen:>12.2f} €
  👤 Clients uniques   : {clients_uniques:>12,}
  📦 Unités vendues    : {unites_vendues:>12,}
  🔄 Taux de retour    : {taux_retour:>11.1f} %
""")



print("\n" + "="*55)
print("  ANALYSE MENSUELLE")
print("="*55)

# Grouper par mois et calculer CA + nombre de commandes
mensuel = df.groupby('mois_num').agg(
    ca          = ('revenu', 'sum'),
    commandes   = ('order_id', 'count'),
    panier_moy  = ('revenu', 'mean')
).reset_index()

# Ajouter le nom du mois
mois_noms = {
    1:'Janvier', 2:'Février', 3:'Mars',    4:'Avril',
    5:'Mai',     6:'Juin',    7:'Juillet', 8:'Août',
    9:'Septembre',10:'Octobre',11:'Novembre',12:'Décembre'
}
mensuel['mois_nom'] = mensuel['mois_num'].map(mois_noms)

# Trouver le meilleur mois
meilleur_mois = mensuel.loc[mensuel['ca'].idxmax()]

print(f"\n  Meilleur mois  : {meilleur_mois['mois_nom']}")
print(f"  CA             : {meilleur_mois['ca']:,.2f} €")
print(f"  Commandes      : {meilleur_mois['commandes']:.0f}")

print(f"\n  Tableau mensuel :")
print(mensuel[['mois_nom','ca','commandes','panier_moy']]
      .to_string(index=False, float_format='{:.2f}'.format))



print("\n" + "="*55)
print("  ANALYSE PAR CATÉGORIE")
print("="*55)

# Grouper par catégorie
par_categorie = df.groupby('categorie').agg(
    ca          = ('revenu', 'sum'),
    commandes   = ('order_id', 'count'),
    panier_moy  = ('revenu', 'mean'),
    unites      = ('quantite', 'sum')
).sort_values('ca', ascending=False).reset_index()

# Ajouter la part du CA total
par_categorie['part_ca_pct'] = (
    par_categorie['ca'] / par_categorie['ca'].sum() * 100
).round(1)

print("\n  Classement des catégories par CA :")
print(f"\n  {'Catégorie':<20} {'CA (€)':>10} {'Part':>7} {'Cmdes':>7} {'Panier':>8}")
print("  " + "-"*54)
for _, row in par_categorie.iterrows():
    print(f"  {row['categorie']:<20} {row['ca']:>10,.0f} "
          f"{row['part_ca_pct']:>6.1f}% {row['commandes']:>7.0f} "
          f"{row['panier_moy']:>7.0f}€")
    


print("\n" + "="*55)
print("  TOP 5 PRODUITS")
print("="*55)

top_produits = df.groupby(['produit', 'categorie']).agg(
    ca        = ('revenu', 'sum'),
    commandes = ('order_id', 'count'),
    prix_moy  = ('prix_vente', 'mean')
).sort_values('ca', ascending=False).head(5).reset_index()

print(f"\n  {'Produit':<25} {'Catégorie':<15} {'CA (€)':>10}")
print("  " + "-"*52)
for _, row in top_produits.iterrows():
    print(f"  {row['produit']:<25} {row['categorie']:<15} "
          f"{row['ca']:>10,.0f}")
    


print("\n" + "="*55)
print("  ANALYSE PAR RÉGION")
print("="*55)

par_region = df.groupby('region').agg(
    ca          = ('revenu', 'sum'),
    commandes   = ('order_id', 'count'),
    panier_moy  = ('revenu', 'mean')
).sort_values('ca', ascending=False).reset_index()

print(f"\n  {'Région':<15} {'CA (€)':>10} {'Cmdes':>7} {'Panier':>8}")
print("  " + "-"*42)
for _, row in par_region.iterrows():
    print(f"  {row['region']:<15} {row['ca']:>10,.0f} "
          f"{row['commandes']:>7.0f} {row['panier_moy']:>7.0f}€")
    


print("\n" + "="*55)
print("  ANALYSE DES PAIEMENTS")
print("="*55)

par_paiement = df.groupby('paiement').agg(
    commandes = ('order_id', 'count'),
    ca        = ('revenu', 'sum')
).reset_index()

par_paiement['part_pct'] = (
    par_paiement['commandes'] / par_paiement['commandes'].sum() * 100
).round(1)

par_paiement = par_paiement.sort_values('commandes', ascending=False)

print(f"\n  {'Paiement':<20} {'Cmdes':>7} {'Part':>7} {'CA (€)':>10}")
print("  " + "-"*46)
for _, row in par_paiement.iterrows():
    print(f"  {row['paiement']:<20} {row['commandes']:>7.0f} "
          f"{row['part_pct']:>6.1f}% {row['ca']:>10,.0f}")



print("\n" + "="*55)
print("  ANALYSE PAR TRIMESTRE")
print("="*55)

par_trimestre = df.groupby('trimestre').agg(
    ca        = ('revenu', 'sum'),
    commandes = ('order_id', 'count')
).reset_index()

# Calculer la croissance entre trimestres
par_trimestre['croissance_pct'] = (
    par_trimestre['ca'].pct_change() * 100
).round(1)

print(f"\n  {'Trimestre':<12} {'CA (€)':>12} {'Cmdes':>8} {'Croissance':>12}")
print("  " + "-"*46)
for _, row in par_trimestre.iterrows():
    croiss = f"{row['croissance_pct']:+.1f}%" if pd.notna(row['croissance_pct']) else "   —"
    print(f"  {row['trimestre']:<12} {row['ca']:>12,.0f} "
          f"{row['commandes']:>8.0f} {croiss:>12}")   



print("\n" + "="*55)
print("  SAUVEGARDE DES RÉSULTATS")
print("="*55)

os.makedirs('data/processed', exist_ok=True)

# Sauvegarder chaque tableau
mensuel.to_csv('data/processed/kpi_mensuel.csv', index=False)
par_categorie.to_csv('data/processed/kpi_categorie.csv', index=False)
par_region.to_csv('data/processed/kpi_region.csv', index=False)
top_produits.to_csv('data/processed/kpi_top_produits.csv', index=False)

print("""
  ✅ data/processed/kpi_mensuel.csv
  ✅ data/processed/kpi_categorie.csv
  ✅ data/processed/kpi_region.csv
  ✅ data/processed/kpi_top_produits.csv
""")

print("="*55)
print("="*55)         
