# Publication automation

This directory contains the controlled publication pipeline for Bahá’í Lighthouse.

## Safety model

- The workflow is manual-only (`workflow_dispatch`). A normal push does not publish the website.
- Validation runs before deployment and uses the repository's existing `build/build-deploy.sh` security and required-file checks.
- Deployment is a separate job and only runs when the workflow input is explicitly set to `deploy`.
- GitHub repository contents are read-only inside the workflow.
- Cloudflare credentials must be stored as GitHub Actions secrets. Never commit tokens, account IDs, `.env` files, or credentials.
- The deploy job uses the GitHub `production` environment so repository-level deployment protections can be added without changing the workflow.

## Required GitHub Actions secrets

Before production deployment can run, configure:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

The Cloudflare token should be narrowly scoped to the Bahá’í Lighthouse Worker/account permissions needed for deployment.

## Intended flow

1. Finish and verify website changes.
2. Commit the approved changes.
3. Run **Publication Pipeline** with `validate`.
4. Review the successful validation.
5. Run it again with `deploy` when publication is intended.

This foundation deliberately does not post to social networks yet. Distribution channels will be added separately so each service can receive only the minimum permission it needs.
