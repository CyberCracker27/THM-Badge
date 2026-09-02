# THM Live Badge Generator

This repository generates a live, public badge for your TryHackMe stats, updated every 30 minutes via a browser extension.

## Quick Setup

1. **Fork** this repository.
2. **Enable GitHub Pages**:  
   Go to Settings → Pages → set source to `main` branch, `/docs` folder.
3. **Install the browser extension** (code provided in the `extension/` folder of this repo).
4. **Create a GitHub Personal Access Token** with `public_repo` scope.
5. **In the extension popup**, fill in:
   - Repo Owner (your GitHub username)
   - Repo Name (the name of this forked repo)
   - Your TryHackMe username
   - Your GitHub token
6. Click **Save Settings** then **Update Now**.

The badge will be available at:  
`https://<your-github-username>.github.io/<repo-name>/tryhackme_badge.png`

Embed it in your README:

\`\`\`markdown
<img src="https://<your-github-username>.github.io/<repo-name>/tryhackme_badge.png" alt="TryHackMe Badge">
\`\`\`

## How it works

- The extension fetches your stats from TryHackMe and commits `data.json`.
- A GitHub Action runs on each commit, generating the badge image.
- The image is served via GitHub Pages.

No servers needed – everything runs on GitHub and your browser.

## Troubleshooting

- If the badge doesn't update, check the Actions tab for errors.
- Ensure your token has the correct `public_repo` scope.
- Make sure GitHub Pages is enabled.

## Credits

Inspired by LeetCode trackers.
