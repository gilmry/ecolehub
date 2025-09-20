# EcoleHub - Context Claude Code

## Projet
EcoleHub - Plateforme scolaire collaborative open-source avec croissance progressive par stages.

## Contexte Éducatif
- Plateforme générique pour écoles primaires
- Compatible système belge: M1-M3 (maternelle), P1-P6 (primaire)
- CEB (Certificat d'Études de Base) en fin de P6
- Support multilingue: FR, NL, EN
- RGPD compliant par défaut

## Philosophie de Développement
1. **Simplicité avant tout** - Si c'est compliqué, on simplifie
2. **Progressif par stages** - Chaque stage doit être fonctionnel
3. **Production-ready dès Stage 0** - Utilisable par vraies familles
4. **Pas de dette technique** - Code propre mais sans sur-ingénierie
5. **Open source** - Réutilisable par d'autres écoles

## Contraintes Techniques
- Budget: Optimisé pour VPS économiques
- Hébergement: Compatible tout fournisseur
- Paiements: Mollie (compatible Bancontact belge)
- Sécurité: RGPD compliant par défaut

## Architecture Actuelle

### Implémentation Complète (Stage 4)
- **Capacité**: 200+ familles
- **Tech**: FastAPI + PostgreSQL + Redis + Vue.js + Traefik
- **Fonctions**: Complet (Auth + SEL + Messages + Shop + Education + Analytics)
- **Déploiement**: 5 minutes avec docker-compose.traefik.yml

### Architecture Progressive
- **Stage 0-1**: Auth + Profils + SEL (30 familles)
- **Stage 2**: +Messagerie/Événements (60 familles)
- **Stage 3**: +Boutique/Éducation (100 familles)
- **Stage 4**: +Multilingual/Analytics (200+ familles)

## Règles SEL
- Balance initiale: 120 unités (2h)
- Limites: -300 à +600 unités
- 1 heure = 60 unités standard

## Open Source
- Libre d'usage pour toute école
- Documentation complète
- Configuration générique
- Support communautaire