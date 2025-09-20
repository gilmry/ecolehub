# Politique de confidentialité (RGPD)

Dernière mise à jour: {DATE}
Version: {VERSION}
Contact (DPO/Privacy): {CONTACT_EMAIL}

## Responsable du traitement
- EcoleHub (instance locale de l'établissement)
- Contact: {CONTACT_EMAIL}

## Finalités et bases légales
- Authentification et fonctionnement du service: intérêt légitime / exécution du contrat
- Communication opérationnelle: intérêt légitime / exécution du contrat
- Analytics de plateforme: consentement (opt‑in)
- Newsletter / informations boutique: consentement (opt‑in)
- Cookies de préférence: consentement (opt‑in)
- Publication de photos d’activités: consentement (opt‑in)

## Droits des personnes
- Accès et portabilité: via l’interface (« Export de mes données ») /api/me/data_export
- Rectification: via l’interface (« Modifier mon profil ») /api/me (PATCH)
- Effacement: via l’interface (« Supprimer mon compte ») /api/me (DELETE)
- Retrait du consentement: /api/consent/withdraw
- Opposition/limitation: via contact {CONTACT_EMAIL}

## Conservation
- Données conservées {RETENTION_DAYS} jours après inactivité/suppression, puis anonymisation/purge.

## Sécurité
- Mots de passe hachés (bcrypt)
- Clés/Secrets via variables d’environnement / secrets Docker (non versionnés)
- Journalisation minimale, événements de confidentialité (consentement, export, suppression)

## Sous-traitants (exemples)
- Hébergement / Traefik / Redis / MinIO (selon déploiement)
- Pa11y/Playwright en CI (audit technique)
- Toute liste de sous‑traitants doit être maintenue par l’établissement.

## Enfants / Mineurs
- Le parent/titulaire crée et gère le profil « enfant ».
- Pas de traitement de catégories particulières sans consentement explicite.

## Cookies et traceurs
- Cookies essentiels: requis au fonctionnement.
- Cookies de préférences/analytics: uniquement avec consentement (bannière de consentement).

---

Ce document est un modèle. La conformité finale dépend de votre déploiement, de vos contrats (DPA) et de vos processus (registre des traitements, notification des violations, etc.).
