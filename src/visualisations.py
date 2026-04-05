import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ── Palette de couleurs du projet ──────────────────────
COULEURS = ['#1D9E75','#378ADD','#BA7517',
            '#D4537E','#7F77DD','#5DCAA5','#E24B4A']
VERT     = '#1D9E75'   # couleur principale
BLEU     = '#378ADD'
FOND     = '#F8F9FA'   # couleur de fond
TEXTE    = '#1A1A2E'   # couleur du texte

# ── Style global appliqué à TOUS les graphiques ────────
sns.set_theme(style='whitegrid', palette=COULEURS)
plt.rcParams.update({
    'figure.facecolor'  : FOND,
    'axes.facecolor'    : FOND,
    'axes.spines.top'   : False,
    'axes.spines.right' : False,
    'font.size'         : 11,
    'axes.titlesize'    : 13,
    'axes.titleweight'  : 'bold',
    'axes.titlecolor'   : TEXTE,
    'grid.color'        : '#EEEEEE',
    'grid.linewidth'    : 0.8,
})

# ── Créer le dossier de sortie ─────────────────────────
os.makedirs('outputs/figures', exist_ok=True)

'''=================================================================    '''

# Charger les données nettoyées
df = pd.read_csv('data/processed/ecommerce_valide.csv',
                 parse_dates=['date'])

# Charger les KPIs déjà calculés
mensuel      = pd.read_csv('data/processed/kpi_mensuel.csv')
par_categorie= pd.read_csv('data/processed/kpi_categorie.csv')
par_region   = pd.read_csv('data/processed/kpi_region.csv')
top_produits = pd.read_csv('data/processed/kpi_top_produits.csv')

# Dictionnaire mois numéro → abréviation
MOIS = {1:'Jan',2:'Fév',3:'Mar',4:'Avr',5:'Mai',6:'Jun',
        7:'Jul',8:'Aoû',9:'Sep',10:'Oct',11:'Nov',12:'Déc'}
mensuel['label'] = mensuel['mois_num'].map(MOIS)

print("✅ Bloc 2 OK — données chargées")
print(f"   {len(df)} commandes | "
      f"{len(mensuel)} mois | "
      f"{len(par_categorie)} catégories")


'''=================================================================    '''

print("\n  Graphique 1 — Évolution mensuelle du CA...")

# Créer la figure avec 2 zones de dessin côte à côte
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Évolution mensuelle — 2023",
             fontsize=15, fontweight='bold', y=1.02)

# ── Zone gauche : barres CA ──────────────────────────
ax = axes[0]

# Colorer différemment le meilleur mois
couleur_barres = [
    VERT if v == mensuel['ca'].max() else '#B0D9CC'
    for v in mensuel['ca']
]

barres = ax.bar(mensuel['label'], mensuel['ca'] / 1000,
                color=couleur_barres,
                edgecolor='white', linewidth=0.5)

ax.set_title("Chiffre d'affaires mensuel (k€)")
ax.set_ylabel("CA (k€)")

# Ajouter les valeurs au dessus de chaque barre
for barre, val in zip(barres, mensuel['ca']):
    ax.text(
        barre.get_x() + barre.get_width() / 2,  # position x = centre de la barre
        barre.get_height() + 0.2,                # position y = sommet + petit espace
        f"{val/1000:.1f}k",                      # texte affiché
        ha='center', va='bottom',                # alignement
        fontsize=9, fontweight='bold', color=TEXTE
    )

# ── Zone droite : courbe commandes ───────────────────
ax2 = axes[1]

ax2.plot(mensuel['label'], mensuel['commandes'],
         color=BLEU, linewidth=2.5,
         marker='o', markersize=7)

# Zone colorée sous la courbe
ax2.fill_between(mensuel['label'], mensuel['commandes'],
                 alpha=0.12, color=BLEU)

ax2.set_title("Nombre de commandes par mois")
ax2.set_ylabel("Commandes")

# Étiquettes au dessus de chaque point
for x, y in zip(mensuel['label'], mensuel['commandes']):
    ax2.annotate(str(y), (x, y),
                 textcoords='offset points', xytext=(0, 8),
                 ha='center', fontsize=9, color=BLEU)

plt.tight_layout()
plt.savefig('outputs/figures/01_evolution_mensuelle.png',
            dpi=150, bbox_inches='tight', facecolor=FOND)
plt.close()
print("  ✅ outputs/figures/01_evolution_mensuelle.png")

'''=================================================================    '''

print("  Graphique 2 — Analyse par catégorie...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Performance par catégorie",
             fontsize=15, fontweight='bold', y=1.02)

# ── Zone gauche : barres horizontales ────────────────
ax = axes[0]
couleurs_cat = COULEURS[:len(par_categorie)]

barres = ax.barh(
    par_categorie['categorie'],
    par_categorie['ca'] / 1000,
    color=couleurs_cat,
    edgecolor='white', height=0.6
)

ax.set_title("CA par catégorie (k€)")
ax.set_xlabel("CA (k€)")
ax.invert_yaxis()  # meilleur en haut

# Valeurs à droite de chaque barre
for barre, val in zip(barres, par_categorie['ca']):
    ax.text(barre.get_width() + 0.3,
            barre.get_y() + barre.get_height() / 2,
            f"{val/1000:.1f}k",
            va='center', fontsize=10,
            fontweight='bold', color=TEXTE)

# ── Zone droite : donut ───────────────────────────────
ax2 = axes[1]

coins, textes, autotextes = ax2.pie(
    par_categorie['ca'],
    labels=None,
    colors=couleurs_cat,
    autopct='%1.1f%%',       # afficher les pourcentages
    startangle=140,          # angle de départ
    pctdistance=0.78,        # distance des % au centre
    wedgeprops=dict(
        width=0.5,           # épaisseur = donut (pas camembert plein)
        edgecolor='white',
        linewidth=2
    )
)

# Style des pourcentages
for at in autotextes:
    at.set_fontsize(9)
    at.set_color(TEXTE)

# Légende en dessous
ax2.legend(par_categorie['categorie'],
           loc='lower center',
           bbox_to_anchor=(0.5, -0.15),
           ncol=2, fontsize=9, frameon=False)

ax2.set_title("Part du CA par catégorie")

plt.tight_layout()
plt.savefig('outputs/figures/02_categories.png',
            dpi=150, bbox_inches='tight', facecolor=FOND)
plt.close()
print("  ✅ outputs/figures/02_categories.png")

'''=================================================================    '''

print("  Graphique 3 — Top produits...")

fig, ax = plt.subplots(figsize=(12, 6))

# Associer une couleur à chaque catégorie
cat_couleur = {
    cat: COULEURS[i % len(COULEURS)]
    for i, cat in enumerate(df['categorie'].unique())
}
couleurs_prod = [cat_couleur[c] for c in top_produits['categorie']]

# Labels avec nom du produit ET catégorie sur 2 lignes
labels = [f"{p}\n({c})"
          for p, c in zip(top_produits['produit'],
                          top_produits['categorie'])]

barres = ax.bar(range(len(top_produits)),
                top_produits['ca'] / 1000,
                color=couleurs_prod,
                edgecolor='white', linewidth=0.5)

ax.set_xticks(range(len(top_produits)))
ax.set_xticklabels(labels, fontsize=9, rotation=20, ha='right')
ax.set_title("Top produits par chiffre d'affaires",
             fontsize=14, fontweight='bold')
ax.set_ylabel("CA (k€)")

# Valeurs au dessus des barres
for barre, val in zip(barres, top_produits['ca']):
    ax.text(barre.get_x() + barre.get_width() / 2,
            barre.get_height() + 0.1,
            f"{val/1000:.1f}k",
            ha='center', fontsize=9,
            fontweight='bold', color=TEXTE)

# Légende des catégories
from matplotlib.patches import Patch
legende = [Patch(facecolor=cat_couleur[c], label=c)
           for c in df['categorie'].unique()]
ax.legend(handles=legende, loc='upper right',
          fontsize=9, frameon=False)

plt.tight_layout()
plt.savefig('outputs/figures/03_top_produits.png',
            dpi=150, bbox_inches='tight', facecolor=FOND)
plt.close()
print("  ✅ outputs/figures/03_top_produits.png")

'''=================================================================    '''

print("  Graphique 4 — Géographie...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Performance géographique",
             fontsize=15, fontweight='bold', y=1.02)

# ── CA par région ─────────────────────────────────────
ax = axes[0]
palette_verte = sns.color_palette('YlGn', len(par_region))[::-1]

sns.barplot(data=par_region, y='region', x='ca',
            palette=palette_verte, ax=ax,
            edgecolor='white')

ax.set_title("CA par région (€)")
ax.set_xlabel("Chiffre d'affaires (€)")
ax.set_ylabel("")
ax.xaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k")
)

# ── Panier moyen par région ───────────────────────────
ax2 = axes[1]
sns.barplot(data=par_region, y='region', x='panier_moy',
            palette='Blues_r', ax=ax2, edgecolor='white')

ax2.set_title("Panier moyen par région (€)")
ax2.set_xlabel("Panier moyen (€)")
ax2.set_ylabel("")
ax2.xaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x:.0f}€")
)

plt.tight_layout()
plt.savefig('outputs/figures/04_geographie.png',
            dpi=150, bbox_inches='tight', facecolor=FOND)
plt.close()
print("  ✅ outputs/figures/04_geographie.png")


'''=================================================================    '''

print("  Graphique 5 — Heatmap...")

# Créer un tableau croisé : catégorie en ligne, trimestre en colonne
pivot = (df.groupby(['categorie', 'trimestre'])['revenu']
           .sum()
           .unstack('trimestre')
           .fillna(0) / 1000)

fig, ax = plt.subplots(figsize=(10, 5))

sns.heatmap(
    pivot,
    annot=True,          # afficher les valeurs dans chaque cellule
    fmt='.1f',           # format : 1 décimale
    cmap='YlGn',         # palette de couleurs (jaune → vert)
    linewidths=0.5,      # lignes entre les cellules
    linecolor='white',
    cbar_kws={'label': 'CA (k€)'},
    ax=ax
)

ax.set_title("CA (k€) par catégorie et trimestre",
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel("Catégorie")
ax.set_xlabel("Trimestre")

plt.tight_layout()
plt.savefig('outputs/figures/05_heatmap.png',
            dpi=150, bbox_inches='tight', facecolor=FOND)
plt.close()
print("  ✅ outputs/figures/05_heatmap.png")


'''=================================================================    '''

print("  Graphique 6 — Paiements...")

par_paiement = df.groupby('paiement').agg(
    commandes = ('order_id', 'count'),
    ca        = ('revenu', 'sum')
).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Analyse des modes de paiement",
             fontsize=15, fontweight='bold', y=1.02)

# ── Donut paiements ───────────────────────────────────
ax = axes[0]
coins, textes, autotextes = ax.pie(
    par_paiement['commandes'],
    labels=par_paiement['paiement'],
    colors=COULEURS[:len(par_paiement)],
    autopct='%1.1f%%',
    startangle=90,
    wedgeprops=dict(edgecolor='white', linewidth=2),
    pctdistance=0.75
)
for at in autotextes:
    at.set_fontsize(10)
    at.set_color('white')
    at.set_fontweight('bold')
ax.set_title("Répartition par mode de paiement")

# ── CA par mode de paiement ───────────────────────────
ax2 = axes[1]
ax2.bar(par_paiement['paiement'],
        par_paiement['ca'] / 1000,
        color=COULEURS[:len(par_paiement)],
        edgecolor='white')
ax2.set_title("CA généré par mode de paiement")
ax2.set_ylabel("CA (k€)")
ax2.tick_params(axis='x', rotation=15)
ax2.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x:.0f}k")
)

plt.tight_layout()
plt.savefig('outputs/figures/06_paiements.png',
            dpi=150, bbox_inches='tight', facecolor=FOND)
plt.close()
print("  ✅ outputs/figures/06_paiements.png")

'''=================================================================    '''

print("  Graphique 7 — Segmentation RFM...")

# Calculer le RFM
rfm = df.groupby('client_id').agg(
    frequence  = ('order_id', 'count'),
    montant    = ('revenu', 'sum'),
    derniere   = ('date', 'max')
).reset_index()

rfm['recence_jours'] = (df['date'].max() - rfm['derniere']).dt.days

# Segmenter
def segmenter(row):
    if (row['montant'] > rfm['montant'].quantile(0.75)
            and row['frequence'] >= 3):
        return 'VIP'
    elif row['montant'] > rfm['montant'].quantile(0.50):
        return 'Fidèle'
    elif row['recence_jours'] > 180:
        return 'Inactif'
    return 'Occasionnel'

rfm['segment'] = rfm.apply(segmenter, axis=1)

# Couleurs par segment
seg_couleurs = {
    'VIP'        : VERT,
    'Fidèle'     : BLEU,
    'Occasionnel': '#BA7517',
    'Inactif'    : '#E24B4A'
}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Segmentation clients (méthode RFM)",
             fontsize=15, fontweight='bold', y=1.02)

# ── Scatter fréquence × montant ───────────────────────
ax = axes[0]
for segment, groupe in rfm.groupby('segment'):
    ax.scatter(
        groupe['frequence'],
        groupe['montant'],
        label=segment,
        color=seg_couleurs[segment],
        alpha=0.6, s=40,
        edgecolors='white', linewidth=0.3
    )

ax.set_title("Fréquence vs CA par client")
ax.set_xlabel("Nombre d'achats")
ax.set_ylabel("CA total client (€)")
ax.legend(frameon=False, fontsize=10)

# ── Barres nombre de clients par segment ──────────────
ax2 = axes[1]
seg_counts = rfm['segment'].value_counts()

barres = ax2.bar(
    seg_counts.index,
    seg_counts.values,
    color=[seg_couleurs[s] for s in seg_counts.index],
    edgecolor='white', width=0.6
)

ax2.set_title("Nombre de clients par segment")
ax2.set_ylabel("Clients")

for barre, val in zip(barres, seg_counts.values):
    ax2.text(
        barre.get_x() + barre.get_width() / 2,
        barre.get_height() + 2,
        str(val),
        ha='center', fontsize=11,
        fontweight='bold', color=TEXTE
    )

plt.tight_layout()
plt.savefig('outputs/figures/07_segmentation_rfm.png',
            dpi=150, bbox_inches='tight', facecolor=FOND)
plt.close()
print("  ✅ outputs/figures/07_segmentation_rfm.png")


''' =================================================================    '''

print("\n" + "="*50)
print("  RÉSUMÉ — GRAPHIQUES GÉNÉRÉS")
print("="*50)

figures = sorted(os.listdir('outputs/figures'))
for f in figures:
    taille = os.path.getsize(f'outputs/figures/{f}')
    print(f"  ✅ {f:<45} ({taille/1024:.0f} Ko)")

print(f"\n  Total : {len(figures)} graphiques")
print("\n" + "="*50)
print("  ÉTAPE 5 TERMINÉE AVEC SUCCÈS ✅")
print("="*50)