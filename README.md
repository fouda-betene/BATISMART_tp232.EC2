# BATISMART — Application de Collecte & Analyse des Données
## Établissement de Vente de Matériaux de Construction
### INF232 EC2 | Université de Yaoundé

---

## Description
BATISMART est une application web complète de collecte et d'analyse descriptive
des données pour un établissement de vente de matériaux de construction.

## Fonctionnalités
- **Collecte des ventes** : saisie complète (produit, client, quantité, prix, remise, mode de paiement)
- **Gestion des clients** : enregistrement, types, historique d'achats
- **Gestion du stock** : alertes de seuil critique, entrées, corrections d'inventaire
- **Suivi des dépenses** : catégorisation, bénéficiaires, synthèse mensuelle
- **Analyse descriptive** : moyenne, médiane, écart-type, variance, quartiles, distribution
- **Tableaux de bord** : KPIs, graphiques dynamiques, revenus vs dépenses
- **Export CSV** : export de l'historique complet des ventes

## Technologies
- **Backend** : Python 3.10+, Flask
- **Frontend** : HTML5, CSS3, JavaScript (Chart.js)
- **Déploiement** : Render.com (gratuit)

---

## Déploiement sur Render.com (GRATUIT)

### Étape 1 : Créer un compte GitHub
Allez sur https://github.com et créez un compte gratuit.

### Étape 2 : Créer un nouveau dépôt
1. Cliquez "New repository"
2. Nommez-le `batismart`
3. Choisissez "Public"
4. Cliquez "Create repository"

### Étape 3 : Uploader les fichiers
Uploadez les 3 fichiers : `app.py`, `requirements.txt`, `Procfile`

### Étape 4 : Déployer sur Render
1. Allez sur https://render.com
2. Créez un compte gratuit (avec votre email ou GitHub)
3. Cliquez "New +" → "Web Service"
4. Connectez votre dépôt GitHub `batismart`
5. Configurez :
   - **Name** : batismart
   - **Runtime** : Python 3
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app --bind 0.0.0.0:$PORT`
6. Cliquez "Create Web Service"
7. Attendez ~2 minutes → votre URL sera du type : `https://batismart.onrender.com`

---

## Lancement en local
```bash
pip install flask gunicorn
python app.py
# Ouvrez http://localhost:5000
```

---

## Structure du projet
```
batismart/
├── app.py           # Application complète (backend + frontend)
├── requirements.txt # Dépendances Python
├── Procfile         # Configuration serveur Render/Heroku
└── README.md        # Ce fichier
```

---

*INF232 EC2 — Application développée avec Python Flask*

