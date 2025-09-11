"""
EcoleHub - Gestionnaire sécurisé des secrets
Lecture des secrets Docker Swarm avec fallback variables d'environnement
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration
SECRETS_PATH = Path("/run/secrets")
ENV_FALLBACK = True  # Autoriser les variables d'env en développement

class SecretsManager:
    """Gestionnaire centralisé des secrets EcoleHub"""
    
    def __init__(self, secrets_path: str = "/run/secrets"):
        self.secrets_path = Path(secrets_path)
        self._cache = {}  # Cache en mémoire pour éviter les I/O répétées
        
    def read_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Lit un secret avec priorité Docker secrets > variables d'env > défaut
        
        Args:
            secret_name: Nom du secret (ex: 'secret_key', 'db_password')
            default: Valeur par défaut si le secret n'est pas trouvé
            
        Returns:
            Valeur du secret ou None
            
        Raises:
            RuntimeError: Si le secret critique est manquant
        """
        # Vérifier le cache
        if secret_name in self._cache:
            return self._cache[secret_name]
            
        secret_value = None
        
        # 1. Priorité: Docker secrets (/run/secrets/)
        secret_file = self.secrets_path / f"{secret_name}.txt"
        if secret_file.exists():
            try:
                with open(secret_file, 'r', encoding='utf-8') as f:
                    secret_value = f.read().strip()
                logger.debug(f"Secret '{secret_name}' lu depuis Docker secrets")
            except Exception as e:
                logger.error(f"Erreur lecture secret Docker '{secret_name}': {e}")
        
        # 2. Fallback: Variables d'environnement (développement)
        if not secret_value and ENV_FALLBACK:
            env_name = secret_name.upper()
            secret_value = os.getenv(env_name)
            if secret_value:
                logger.debug(f"Secret '{secret_name}' lu depuis variable d'env")
        
        # 3. Valeur par défaut
        if not secret_value:
            secret_value = default
            if secret_value:
                logger.warning(f"Secret '{secret_name}' utilise la valeur par défaut")
        
        # Validation des secrets critiques
        if not secret_value and secret_name in self.get_critical_secrets():
            raise RuntimeError(
                f"Secret critique '{secret_name}' manquant! "
                f"Vérifiez Docker secrets ou variables d'environnement."
            )
        
        # Mise en cache (éviter les lectures répétées)
        if secret_value:
            self._cache[secret_name] = secret_value
            
        return secret_value
    
    def get_critical_secrets(self) -> list[str]:
        """Liste des secrets critiques qui ne peuvent pas être vides"""
        return [
            'secret_key',      # JWT signing - obligatoire
            'db_password',     # PostgreSQL - obligatoire Stage 1+
        ]
    
    def validate_secrets(self, stage: int = 4) -> dict[str, bool]:
        """
        Valide la présence des secrets requis selon le stage
        
        Args:
            stage: Stage EcoleHub (0-4)
            
        Returns:
            Dict avec status de validation par secret
        """
        required_secrets = self.get_required_secrets(stage)
        validation_results = {}
        
        for secret_name in required_secrets:
            try:
                secret_value = self.read_secret(secret_name)
                is_valid = bool(secret_value and len(secret_value.strip()) >= 8)
                validation_results[secret_name] = is_valid
                
                if not is_valid:
                    logger.error(f"Validation échouée pour secret: {secret_name}")
                    
            except Exception as e:
                logger.error(f"Erreur validation secret {secret_name}: {e}")
                validation_results[secret_name] = False
        
        return validation_results
    
    def get_required_secrets(self, stage: int) -> list[str]:
        """Retourne les secrets requis selon le stage"""
        secrets = ['secret_key']  # Stage 0+
        
        if stage >= 1:
            secrets.extend(['db_password'])
            
        if stage >= 2:
            secrets.extend(['redis_password'])
            
        if stage >= 3:
            secrets.extend([
                'minio_access_key',
                'minio_secret_key',
                'mollie_api_key',     # Optionnel en dev
                'printful_api_key',   # Optionnel en dev
            ])
            
        if stage >= 4:
            secrets.extend(['grafana_password'])
            
        return secrets
    
    def get_connection_string(self, db_type: str, **kwargs) -> str:
        """
        Génère une chaîne de connexion sécurisée
        
        Args:
            db_type: Type de base ('postgresql', 'redis')
            **kwargs: Paramètres de connexion
            
        Returns:
            Chaîne de connexion avec mot de passe sécurisé
        """
        if db_type == 'postgresql':
            password = self.read_secret('db_password')
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 5432)
            user = kwargs.get('user', 'ecolehub')
            database = kwargs.get('database', 'ecolehub')
            
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
            
        elif db_type == 'redis':
            password = self.read_secret('redis_password')
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 6379)
            db = kwargs.get('db', 0)
            
            return f"redis://:{password}@{host}:{port}/{db}"
        
        else:
            raise ValueError(f"Type de base de données non supporté: {db_type}")
    
    def clear_cache(self):
        """Vide le cache des secrets (utile pour les tests)"""
        self._cache.clear()
        logger.debug("Cache des secrets vidé")


# Instance globale du gestionnaire
secrets_manager = SecretsManager()

# Fonctions helper pour compatibilité
def read_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """Helper function - lit un secret via le gestionnaire global"""
    return secrets_manager.read_secret(secret_name, default)

def get_jwt_secret() -> str:
    """Retourne la clé de signature JWT"""
    secret_key = read_secret('secret_key')
    if not secret_key:
        raise RuntimeError("JWT secret_key manquant - sécurité compromise!")
    return secret_key

def get_database_url() -> str:
    """Retourne l'URL de base de données avec mot de passe sécurisé"""
    return secrets_manager.get_connection_string(
        'postgresql',
        host=os.getenv('DB_HOST', 'postgres'),
        port=int(os.getenv('DB_PORT', '5432')),
        user=os.getenv('DB_USER', 'ecolehub'),
        database=os.getenv('DB_NAME', 'ecolehub')
    )

def get_redis_url() -> str:
    """Retourne l'URL Redis avec mot de passe sécurisé"""
    return secrets_manager.get_connection_string(
        'redis',
        host=os.getenv('REDIS_HOST', 'redis'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        db=int(os.getenv('REDIS_DB', '0'))
    )

def get_external_api_key(service: str) -> Optional[str]:
    """
    Retourne la clé API pour un service externe
    
    Args:
        service: 'mollie', 'printful', etc.
    """
    secret_name = f"{service}_api_key"
    return read_secret(secret_name)

# Configuration logging
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    # Test du gestionnaire
    manager = SecretsManager()
    
    print("=== Test SecretsManager ===")
    print(f"Secret key: {manager.read_secret('secret_key', 'dev-fallback')[:10]}...")
    print(f"DB password: {manager.read_secret('db_password', 'dev-fallback')[:10]}...")
    
    validation = manager.validate_secrets(stage=4)
    print(f"Validation: {validation}")