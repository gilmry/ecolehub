# TODO / Roadmap

## Internationalisation (prioritaire)
- Rendre tous les textes interchangeables en FR, NL, DE et EN.
- Centraliser les chaînes (front: `frontend/locales/*.json`, back: messages/erreurs).
- Ajouter `frontend/locales/de-BE.json` et compléter les clés existantes.
- Normaliser les clés i18n (`scope.section.key`, ex: `auth.login.title`).
- Gestion des fallback: `de-BE` → `fr-BE` → `en`.
- Exposer la langue via API (`/api/i18n/locales`, `/api/i18n/translations/{locale}`) avec support `de-BE`.
- Tests: vérifier présence des clés dans les 4 langues et fallback correct.

## Qualité & DX
- Lint i18n: script qui détecte clés manquantes/inutilisées.
- Guide de contribution i18n dans `AGENTS.md` (règles de nommage, process de traduction).
- Exemple de PR: ajout d’une nouvelle clé + 4 traductions + test.

## Tests (prioritaire)
- Résoudre tous les tests et aligner avec Stage 4.
- Mettre à jour les routes de test côté API avec le préfixe `/api`.
- Mock services externes en test: Redis (FakeRedis), MinIO (désactiver réseau en `TESTING=1`).
- Utiliser `UUIDType` pour compatibilité SQLite en tests.
- Couvrir les endpoints Stage 4: analytics, i18n, shop admin.
- CI: ajouter `STRICT=1 make i18n-lint` + `make test` et corriger jusqu’au vert.

## Frontend
- Extraire textes restants en dur de `frontend/index.html` vers JSON.
- Détection de langue navigateur, persistance `localStorage`, sélecteur UI.

## Backend
- Uniformiser messages d’erreur/validation via map de clés i18n.
- Paramètre `Accept-Language` pour formatter certaines réponses.

## Contenu
- Glossaire des termes belges (classes M1–M3, P1–P6, SEL) pour cohérence des traductions.
