# Déploiement RGPD — EcoleHub

Cette note décrit les paramètres et vérifications nécessaires pour un déploiement conforme au RGPD.

## Variables d'environnement clés
- `PRIVACY_POLICY_VERSION` — version de votre politique (ex: `1.2.0`)
- `GDPR_PRIVACY_CONTACT_EMAIL` — contact DPO/Privacy (ex: `dpo@votre-ecole.be`)
- `GDPR_DATA_RETENTION_DAYS` — durée de conservation (ex: `365`)

## Endpoints disponibles
- `GET /api/privacy` — version, contact, rétention, locales
- `GET /api/privacy/doc` — contenu markdown de la politique (docs/PRIVACY.md)
- `POST /api/consent` — enregistrement consentement (version/locale/date)
- `POST /api/consent/withdraw` — retrait du consentement (désactive le compte)
- `GET/POST /api/consent/preferences` — préférences granulaires (analytics/newsletter/…)
- `GET /api/me/data_export` — export portabilité (option `?include_events=true`)
- `GET /api/me/privacy_events` — historique des événements de confidentialité
- `PATCH /api/me` — rectification (prénom/nom)
- `DELETE /api/me` — effacement (anonymisation + soft‑delete)
- `POST /api/admin/privacy/purge` — purge administrateur (événements anciens, anonymisation finale)

## Journaux/minimisation
- Les événements de confidentialité `PrivacyEvent` journalisent les actions requises.
- Éviter les PII dans `details`.

## Purge (cron-friendly)
- Script local: `make gdpr-purge` (utilise `backend/scripts/gdpr_purge.py`)
- Planifier via cron ou job Kubernetes selon votre infra.

## Frontend (consentement)
- Bannière de consentement accessible (dialog, focus trap); accès depuis l’en‑tête et le pied de page
- Préférences synchronisées avec le backend pour les utilisateurs authentifiés

## Documentation
- Remplir `docs/PRIVACY.md` (version, contact, rétention, sous-traitants, droits, sécurité, cookies)
- Maintenir un registre des traitements (ROPA) et des DPA avec vos sous-traitants

---

Ces contrôles techniques ne remplacent pas un audit légal/organisationnel. La conformité finale dépend de vos processus, contrats et pratiques.
### Exemples curl

Export des données (JSON):

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://<host>/api/me/data_export \
  -o ecolehub-export.json
```

Export des données incluant l'historique des événements:

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  "http://<host>/api/me/data_export?include_events=true" \
  -o ecolehub-export-with-events.json
```

Lecture des préférences de consentement:

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://<host>/api/consent/preferences
```

Mise à jour des préférences (ex: activer analytics et newsletter):

```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"consent_analytics_platform": true, "consent_comms_newsletter": true}' \
  http://<host>/api/consent/preferences
```

Retrait du consentement:

```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  http://<host>/api/consent/withdraw
```

Purge admin (événements + anonymisation finale):

```bash
curl -X POST -H "Authorization: Bearer <ADMIN_TOKEN>" \
  http://<host>/api/admin/privacy/purge
```
