SUP One UI — GitHub + Cloudflare Pages automatic Eventernote sync

1. Extract this ZIP and upload index.html, event_snapshot.json, server.py,
   update_events.py, requirements.txt, and the .github/workflows/update-events.yml
   path to a GitHub repository. Keep index.html in the repository root.
2. In GitHub Settings > Actions > General, ensure workflow permissions allow
   Read and write permissions if your repository defaults to read-only.
3. GitHub Actions > Update Eventernote events > Run workflow.
   Verify that the job succeeds and event_snapshot.json changes.
4. In Cloudflare Workers & Pages, create a NEW Pages project using Connect to Git.
   Select the repository, Framework preset: None, Build command: blank,
   Build output directory: / (repository root), production branch: main.
5. Cloudflare deploys each change committed by the workflow.

IMPORTANT: A pre-existing Direct Upload Pages project cannot be converted to
Git integration. Create a new Pages project, or use Wrangler with API credentials.

Eventernote parsing uses the existing experimental server.py scraper and may
fail if Eventernote's HTML changes or blocks automated requests. When it fails,
GitHub Actions will show an error and will preserve the previous snapshot.
GitHub scheduled workflows can be delayed or disabled after inactivity.
