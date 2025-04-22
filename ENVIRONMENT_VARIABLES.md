# Variables d'Environnement Requises

## Configuration de Base
```env
PROJECT_ID="votre-id-projet-gcp"  # Obligatoire - ID du projet Google Cloud
LOCATION="us-central1"            # Obligatoire - Région des services Vertex AI
```

## Authentification Google Cloud
```env
GOOGLE_APPLICATION_CREDENTIALS="chemin/vers/cles-service.json"  # Requis pour les déploiements locaux
```

## Configuration Avancée
```env
# Pour les intégrations externes (optionnel)
IEEE_API_KEY="votre-cle-ieee"
ACM_API_KEY="votre-cle-acm"
ZOTERO_API_KEY="votre-cle-zotero"

# Sécurité de l'API (recommandé)
API_SECRET_KEY="votre-secret-complexe"  # Pour la signature JWT
CORS_ALLOWED_ORIGINS="https://votre-domaine.com"  # Restreindre les origines CORS
```

## Exemple de Configuration
```python
# Dans cloud_run/research_service/app.py
vertexai.init(
    project=os.environ["PROJECT_ID"], 
    location=os.environ["LOCATION"]
)
```

## Vérification
```bash
# Commande pour tester la configuration
echo "PROJECT_ID=$PROJECT_ID, LOCATION=$LOCATION"