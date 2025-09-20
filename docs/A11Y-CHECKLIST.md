# Accessibilité – Checklist (WCAG 2.1 AA)

Cette checklist aide à auditer l’accessibilité de la plateforme.

Clavier & Focus
- Navigation au clavier complète (Tab/Shift+Tab) sans piège.
- Ordre logique de tabulation; focus visible (contraste suffisant).
- Gestion focus lors des modales/menus (piégeage + retour focus). 
- Lien « Aller au contenu » en haut de page.

Structure & Sémantique
- Landmarks: `header`, `nav`, `main`, `aside`, `footer` (ou rôles ARIA).
- Hiérarchie des titres (`h1` unique, progression logique des `h2+`).
- Listes, tableaux, boutons/links sémantiques (pas de `div` cliquables non labellisés).

Couleurs & Contraste
- Contraste ≥ 4.5:1 (texte normal), ≥ 3:1 (gros texte/icônes informatives).
- État focus/hover actif et visible; ne pas baser l’info sur la couleur seule.

Formulaires
- `label` associé à chaque champ; `aria-describedby` pour aides/erreurs.
- Erreurs claires (texte + icône); focus vers message d’erreur.
- Groupes de champs (`fieldset/legend`) pour ensembles logiques.

Images & Médias
- `alt` descriptifs (ou vides si purement décoratif via CSS/background).
- Sous-titres/transcriptions pour vidéos/audio si présents.

Mouvements & Préférences
- Respect `prefers-reduced-motion`; éviter animations agressives.
- Zoom ≥ 200% sans perte de contenu ni scroll horizontal inutile.

Tables & Graphiques
- En-têtes (`th`, `scope`) corrects; résumé si complexe.
- Alternatives textuelles aux graphiques/charts.

Notifications & Live Regions
- Annoncer les toasts/erreurs/success (`role="status"|"alert"`).

ARIA & Internationalisation
- ARIA utile seulement si nécessaire; pas de sur‑ARIA.
- `lang` HTML correct; contenu multilingue correctement balisé.

Tests recommandés
- Pa11y/axe, Lighthouse, lecteurs d’écran (NVDA/VoiceOver), navigation clavier.
