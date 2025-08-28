# EcoleHub - Context Claude Code

## Projet
EcoleHub - Plateforme scolaire collaborative belge avec croissance progressive par stages.

## Contexte Éducatif Belge
- EcoleHub à Bruxelles
- Système scolaire: M1-M3 (maternelle), P1-P6 (primaire)
- CEB (Certificat d'Études de Base) en fin de P6
- Communautés linguistiques: FR (principal), NL, EN (optionnel)
- RGPD strict dès le début

## Philosophie de Développement
1. **Simplicité avant tout** - Si c'est compliqué, on simplifie
2. **Progressif par stages** - Chaque stage doit être fonctionnel
3. **Production-ready dès Stage 0** - Utilisable par vraies familles
4. **Pas de dette technique** - Code propre mais sans sur-ingénierie
5. **Open source** - Réutilisable par d'autres écoles

## Contraintes Techniques
- Budget: VPS 10€/mois maximum
- Hébergement: Préférence OVH Belgique
- Paiements: Mollie (compatible Bancontact)
- Sécurité: RGPD compliant dès Stage 0

## Stages de Développement

### Stage 0 (ACTUEL - PRIORITÉ) 
- **Objectif**: 5-10 familles
- **Tech**: FastAPI minimal + SQLite + Vue CDN
- **Fonctions**: Auth + Profils + Enfants
- **Durée**: 30 minutes de setup

### Stage 1 (FUTUR)
- **Objectif**: 30 familles 
- **Tech**: +PostgreSQL + SEL
- **Nouvelles fonctions**: Système d'échange local

### Stages 2-4 (PLANIFIÉS)
- Stage 2: +Messagerie/Événements
- Stage 3: +Boutique/Éducation  
- Stage 4: +Multilingual/Analytics

## Règles SEL (Stage 1+)
- Balance initiale: 120 unités (2h)
- Limites: -300 à +600 unités
- 1 heure = 60 unités standard

## Parent Développeur
- Prend en charge technique pour 10 ans
- Approche "sans stress"
- Grandit selon énergie disponible