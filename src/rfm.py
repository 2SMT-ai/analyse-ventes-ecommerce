import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# Style
COULEURS = ['#1D9E75','#378ADD','#BA7517','#D4537E']
FOND     = '#F8F9FA'
TEXTE    = '#1A1A2E'

sns.set_theme(style='whitegrid', palette=COULEURS)
plt.rcParams.update({
    'figure.facecolor' : FOND,
    'axes.facecolor'   : FOND,
    'axes.spines.top'  : False,
    'axes.spines.right': False,
    'font.size'        : 11,
    'axes.titleweight' : 'bold',
})

os.makedirs('outputs/figures', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

# Charger les données
df = pd.read_csv('data/processed/ecommerce_valide.csv',
                 parse_dates=['date'])

# Date de référence = dernier jour du dataset
# (comme si on était "aujourd'hui" à cette date)
DATE_REF = df['date'].max()

print(f"   {len(df)} commandes")
print(f"   Date de référence : {DATE_REF.date()}")

'''=================================================================='''

print("\n" + "="*55)
print("  CALCUL DES MÉTRIQUES RFM")
print("="*55)

rfm = df.groupby('client_id').agg(
    # R : nombre de jours depuis le dernier achat
    derniere_commande = ('date', 'max'),

    # F : nombre total de commandes
    frequence         = ('order_id', 'count'),

    # M : montant total dépensé
    montant_total     = ('revenu', 'sum'),

    # Infos supplémentaires utiles
    premiere_commande = ('date', 'min'),
    panier_moyen      = ('revenu', 'mean'),
    nb_categories     = ('categorie', 'nunique'),
).reset_index()

# Calculer la récence en jours
rfm['recence_jours'] = (
    DATE_REF - rfm['derniere_commande']
).dt.days

# Calculer la durée de vie du client (jours entre 1er et dernier achat)
rfm['duree_vie_jours'] = (
    rfm['derniere_commande'] - rfm['premiere_commande']
).dt.days

print(f"\n   {len(rfm)} clients analysés")
print(f"\n   Métriques calculées :")
print(f"   R — Récence moyenne    : {rfm['recence_jours'].mean():.0f} jours")
print(f"   F — Fréquence moyenne  : {rfm['frequence'].mean():.1f} achats")
print(f"   M — Montant moyen      : {rfm['montant_total'].mean():.0f} €")
print(f"\n   Aperçu :")
print(rfm[['client_id','recence_jours','frequence',
           'montant_total']].head(5).to_string(index=False))

'''=================================================================='''

print("\n" + "="*55)
print("  SCORING RFM (1 à 4)")
print("="*55)

# ── Fonction robuste de scoring ──────────────────────
# pd.qcut échoue quand trop de valeurs identiques
# On utilise rank() + pd.cut() à la place — plus solide

def scorer_colonne(serie, inverse=False):
    """
    Divise une série en 4 groupes égaux via le rang.
    inverse=True → moins = meilleur (pour la récence)
    """
    # rank() transforme les valeurs en rangs (1 = plus petit)
    # method='first' : en cas d'égalité, premier arrivé = rang le plus bas
    rangs = serie.rank(method='first', ascending=not inverse)

    # Diviser les rangs en 4 groupes égaux
    score = pd.cut(
        rangs,
        bins=4,
        labels=[1, 2, 3, 4]
    ).astype(int)

    return score

# Score R : inverse=True (moins de jours = meilleur)
rfm['score_R'] = scorer_colonne(rfm['recence_jours'], inverse=True)

# Score F : normal (plus de commandes = meilleur)
rfm['score_F'] = scorer_colonne(rfm['frequence'], inverse=False)

# Score M : normal (plus de montant = meilleur)
rfm['score_M'] = scorer_colonne(rfm['montant_total'], inverse=False)

# Score global = somme des 3 scores (entre 3 et 12)
rfm['score_rfm'] = rfm['score_R'] + rfm['score_F'] + rfm['score_M']

print(f"\n   Distribution des scores :")
print(f"   Score R : min={rfm['score_R'].min()} "
      f"max={rfm['score_R'].max()} "
      f"moy={rfm['score_R'].mean():.1f}")
print(f"   Score F : min={rfm['score_F'].min()} "
      f"max={rfm['score_F'].max()} "
      f"moy={rfm['score_F'].mean():.1f}")
print(f"   Score M : min={rfm['score_M'].min()} "
      f"max={rfm['score_M'].max()} "
      f"moy={rfm['score_M'].mean():.1f}")
print(f"   Score global : min={rfm['score_rfm'].min()} "
      f"max={rfm['score_rfm'].max()} "
      f"moy={rfm['score_rfm'].mean():.1f}")

'''=================================================================='''

print("\n" + "="*55)
print("  SEGMENTATION")
print("="*55)

def assigner_segment(row):
    r = row['score_R']
    f = row['score_F']
    m = row['score_M']
    score = row['score_rfm']

    # VIP : meilleurs scores partout
    if score >= 10:
        return 'VIP'

    # Champions : achètent souvent et beaucoup
    elif f >= 3 and m >= 3:
        return 'Fidèle'

    # Nouveaux clients : achat récent mais peu de fois
    elif r >= 3 and f <= 2:
        return 'Nouveau'

    # À risque : bons historiques mais n'achètent plus
    elif r <= 2 and f >= 3:
        return 'À risque'

    # Inactifs : n'achètent plus et peu de montant
    elif r == 1 and score <= 5:
        return 'Inactif'

    # Tous les autres
    else:
        return 'Occasionnel'

rfm['segment'] = rfm.apply(assigner_segment, axis=1)

# Résumé par segment
resume_seg = rfm.groupby('segment').agg(
    nb_clients    = ('client_id', 'count'),
    montant_moy   = ('montant_total', 'mean'),
    frequence_moy = ('frequence', 'mean'),
    recence_moy   = ('recence_jours', 'mean'),
    ca_total      = ('montant_total', 'sum'),
).round(1).reset_index()

resume_seg['part_clients_pct'] = (
    resume_seg['nb_clients'] / resume_seg['nb_clients'].sum() * 100
).round(1)

resume_seg['part_ca_pct'] = (
    resume_seg['ca_total'] / resume_seg['ca_total'].sum() * 100
).round(1)

resume_seg = resume_seg.sort_values('ca_total', ascending=False)

print(f"\n  {'Segment':<12} {'Clients':>8} {'Part':>7} "
      f"{'CA total':>10} {'Part CA':>8} {'Panier moy':>11}")
print("  " + "─"*58)
for _, r in resume_seg.iterrows():
    print(f"  {r['segment']:<12} {r['nb_clients']:>8} "
          f"{r['part_clients_pct']:>6.1f}% "
          f"{r['ca_total']:>10,.0f} "
          f"{r['part_ca_pct']:>7.1f}% "
          f"{r['montant_moy']:>10.0f}€")
    

    '''=================================================================='''

print("\n" + "="*55)
print("  RECOMMANDATIONS MARKETING")
print("="*55)

recommandations = {
    'VIP': {
        'icone'  : '👑',
        'action' : 'Programme fidélité exclusif + accès anticipé aux nouveautés',
        'objectif': 'Maintenir et récompenser',
    },
    'Fidèle': {
        'icone'  : '⭐',
        'action' : 'Offres de montée en gamme + recommandations personnalisées',
        'objectif': 'Augmenter le panier moyen',
    },
    'Nouveau': {
        'icone'  : '🌱',
        'action' : 'Email de bienvenue + bon de réduction 2ème commande',
        'objectif': 'Convertir en client régulier',
    },
    'À risque': {
        'icone'  : '⚠️',
        'action' : 'Campagne réactivation urgente + offre personnalisée -15%',
        'objectif': 'Éviter la perte du client',
    },
    'Occasionnel': {
        'icone'  : '🔄',
        'action' : 'Newsletter promotionnelle + rappels saisonniers',
        'objectif': 'Augmenter la fréquence',
    },
    'Inactif': {
        'icone'  : '😴',
        'action' : 'Email "Vous nous manquez" + remise -20% limitée',
        'objectif': 'Réactiver ou accepter la perte',
    },
}

for seg, infos in recommandations.items():
    nb = resume_seg.loc[
        resume_seg['segment']==seg, 'nb_clients'
    ].values
    nb_str = str(nb[0]) if len(nb) > 0 else '0'
    print(f"\n  {infos['icone']} {seg} ({nb_str} clients)")
    print(f"     Action   : {infos['action']}")
    print(f"     Objectif : {infos['objectif']}")


'''=================================================================='''


print("\n  Création des graphiques RFM...")

SEG_COULEURS = {
    'VIP'        : '#1D9E75',
    'Fidèle'     : '#378ADD',
    'Nouveau'    : '#5DCAA5',
    'À risque'   : '#BA7517',
    'Occasionnel': '#7F77DD',
    'Inactif'    : '#E24B4A',
}

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Analyse RFM — Segmentation clients",
             fontsize=16, fontweight='bold', y=1.01)

# ── Graphique 1 : Scatter F × M coloré par segment ───
ax = axes[0, 0]
for seg, groupe in rfm.groupby('segment'):
    ax.scatter(
        groupe['frequence'],
        groupe['montant_total'],
        label=seg,
        color=SEG_COULEURS.get(seg, '#888888'),
        alpha=0.55, s=35,
        edgecolors='white', linewidth=0.3
    )
ax.set_title("Fréquence vs Montant total par client")
ax.set_xlabel("Nombre d'achats")
ax.set_ylabel("CA total (€)")
ax.legend(frameon=False, fontsize=9)

# ── Graphique 2 : Barres clients par segment ─────────
ax2 = axes[0, 1]
seg_order = resume_seg.sort_values('nb_clients', ascending=False)
barres = ax2.bar(
    seg_order['segment'],
    seg_order['nb_clients'],
    color=[SEG_COULEURS.get(s, '#888') for s in seg_order['segment']],
    edgecolor='white', width=0.6
)
ax2.set_title("Nombre de clients par segment")
ax2.set_ylabel("Clients")
ax2.tick_params(axis='x', rotation=20)
for b, v in zip(barres, seg_order['nb_clients']):
    ax2.text(b.get_x() + b.get_width()/2,
             b.get_height() + 1, str(v),
             ha='center', fontsize=10,
             fontweight='bold', color=TEXTE)

# ── Graphique 3 : CA par segment ──────────────────────
ax3 = axes[1, 0]
seg_ca = resume_seg.sort_values('ca_total', ascending=False)
barres3 = ax3.barh(
    seg_ca['segment'],
    seg_ca['ca_total'] / 1000,
    color=[SEG_COULEURS.get(s, '#888') for s in seg_ca['segment']],
    edgecolor='white'
)
ax3.set_title("CA total par segment (k€)")
ax3.set_xlabel("CA (k€)")
ax3.invert_yaxis()
for b, v in zip(barres3, seg_ca['ca_total']):
    ax3.text(b.get_width() + 0.2,
             b.get_y() + b.get_height()/2,
             f"{v/1000:.1f}k",
             va='center', fontsize=10,
             fontweight='bold', color=TEXTE)

# ── Graphique 4 : Distribution score RFM global ───────
ax4 = axes[1, 1]
ax4.hist(rfm['score_rfm'], bins=10,
         color='#378ADD', edgecolor='white',
         linewidth=0.5)
ax4.set_title("Distribution du score RFM global")
ax4.set_xlabel("Score RFM (3 = mauvais → 12 = excellent)")
ax4.set_ylabel("Nombre de clients")
ax4.axvline(rfm['score_rfm'].mean(), color='#E24B4A',
            linestyle='--', linewidth=1.5,
            label=f"Moy : {rfm['score_rfm'].mean():.1f}")
ax4.legend(frameon=False)

plt.tight_layout()
plt.savefig('outputs/figures/08_rfm_complet.png',
            dpi=150, bbox_inches='tight', facecolor=FOND)
plt.close()
print("  ✅ outputs/figures/08_rfm_complet.png")


'''=================================================================='''

print("\n" + "="*55)
print("  SAUVEGARDE")
print("="*55)

# Sauvegarder le tableau RFM complet
rfm.to_csv('data/processed/rfm_clients.csv', index=False)

# Sauvegarder le résumé par segment
resume_seg.to_csv('data/processed/rfm_segments.csv', index=False)

print("""
  ✅ data/processed/rfm_clients.csv
     → un score RFM par client

  ✅ data/processed/rfm_segments.csv
     → résumé par segment

  ✅ outputs/figures/08_rfm_complet.png
     → 4 graphiques RFM
""")

print("="*55)
print("  ÉTAPE 6 TERMINÉE AVEC SUCCÈS ✅")
print("="*55)