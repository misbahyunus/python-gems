Title: security: remove committed Fixer API key, add config template

This PR removes the committed Fixer API key from the working tree and replaces it with a safe template (Exchange Rate Info/config.ini). It also adds Exchange Rate Info/config.ini to .gitignore so local configs are not tracked.

IMPORTANT: The key was committed to repository history and must be rotated at the provider (fixer.io). Removing the file from the tip does not scrub it from history — use BFG or git-filter-repo to remove the secret from past commits and force-push.

Changes in this PR:
- Exchange Rate Info/config.ini (replaced with template)
- .gitignore (updated to ignore Exchange Rate Info/config.ini)

Action items for repo owner:
1. Rotate the leaked Fixer API key at fixer.io immediately.
2. Use BFG or git-filter-repo to remove the secret from repo history and force-push.
3. After history rewrite, inform collaborators to reclone or reset their local clones.
