# THM Badge

A live, auto-updating TryHackMe stats badge for your GitHub profile or README — powered by a Firefox extension, no personal access tokens required.

![THM Badge preview](docs/tryhackme_badge.png)

The companion browser extension reads your TryHackMe profile every 30 minutes and commits the stats to this repo's `data.json`. A GitHub Action then renders them into a badge image, served for free via GitHub Pages.

```
TryHackMe API -> Firefox extension -> GitHub App (OAuth+PKCE) -> data.json -> GitHub Action -> badge.png -> GitHub Pages
```

## Quick Setup

### 1. Fork this repository

### 2. Enable GitHub Pages
**Settings → Pages** → set source to the `main` branch, `/docs` folder.

### 3. Load the extension in Firefox
The extension code lives in the `extension/` folder of this repo.

1. Open `about:debugging#/runtime/this-firefox` in Firefox.
2. Click **Load Temporary Add-on…**.
3. Select `extension/manifest.json`.

This loads it as a **temporary add-on** — it works immediately but is removed when Firefox restarts, so you'll need to reload it each session.

**For a permanent install instead**, either:
- Package and self-distribute a signed `.xpi` via [addons.mozilla.org](https://addons.mozilla.org) (submit as "unlisted" for a private/self-use signed build), or
- Use Firefox Developer Edition or Nightly and set `xpinstall.signatures.required` to `false` in `about:config`, then install the packaged `.xpi` directly.

> The extension's `manifest.json` declares `browser_specific_settings.gecko`, requiring **Firefox 140+** (or Firefox for Android 142+), and requests the `authenticationInfo` and `personallyIdentifyingInfo` data-collection permissions — Firefox will show a data-collection consent prompt for these on install since it talks to GitHub's OAuth flow and reads your GitHub identity.

### 4. Connect and configure
Click the THM Badge icon in the Firefox toolbar to open the popup:
1. Click **Continue with GitHub** — this opens GitHub's authorization page via `identity.launchWebAuthFlow`.
2. Click **Install / manage GitHub App** and install the app on your forked repo.
3. Select that repository from the dropdown and enter your **TryHackMe username**.
4. Click **Save & Generate Badge**.

### 5. Embed the badge
```markdown
<img src="https://<your-github-username>.github.io/<repo-name>/tryhackme_badge.png" alt="TryHackMe Badge">
```

## How it works

- The extension authenticates with GitHub using a **GitHub App + OAuth Authorization Code with PKCE** — no personal access token is ever created or stored.
- Token exchange happens through a separate OAuth backend (a Cloudflare Worker) that holds the GitHub App's client secret, so the secret never ships inside the extension.
- Every 30 minutes (via a `browser.alarms` alarm) or on demand, the extension fetches your public profile from the TryHackMe API and commits it to `data.json` here using the GitHub Contents API.
- Any commit to `data.json` triggers `.github/workflows/update-badge.yml`, which runs `generate_badge.py` to redraw the badge and pushes the new PNG to `docs/`.
- GitHub Pages serves `docs/tryhackme_badge.png` at a stable, public URL.

## Updating

The extension refreshes automatically every 30 minutes while Firefox is running, or click **Update now** in the popup at any time. Since a temporary add-on unloads on restart, the alarm-based auto-update only runs while the add-on is loaded — if you're relying on temporary loading, reload the add-on each session or click **Update now** manually.

## Troubleshooting

- **Extension disappeared after restarting Firefox** — expected for temporary add-ons; reload it via `about:debugging`, or set up a signed permanent install (see step 3).
- **Badge not updating** — check the **Actions** tab on your fork for failed workflow runs.
- **"THM Badge is not installed"** in the popup — the GitHub App hasn't been installed on this repo yet; use **Install / manage GitHub App**.
- **"GitHub session expired"** — the refresh token exchange failed; click **Disconnect**, then **Continue with GitHub** again.
- **Data-collection prompt on install** — this is expected; the extension declares `authenticationInfo` and `personallyIdentifyingInfo` because it authenticates you with GitHub and stores your GitHub username/avatar locally.

## Requirements

- Firefox 140+ (or Firefox for Android 142+)
- Python dependencies for badge generation: `Pillow`, `requests` (see `requirements.txt`) — only needed if you want to run `generate_badge.py` locally; GitHub Actions installs these automatically

## Security notes

- The GitHub App's client secret is never bundled into the extension — it lives only in the OAuth backend's environment.
- Authentication uses OAuth + PKCE with state validation against CSRF; no long-lived personal access token is generated.
- Access and refresh tokens are stored in the extension's local `storage.local`, scoped to the extension.

## Credits

Inspired by LeetCode stat trackers.
