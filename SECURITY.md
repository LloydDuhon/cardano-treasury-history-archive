# Security Policy

## Supported Version

Security fixes are handled on the `main` branch. This repository is a live
archive rather than a packaged software release, so `main` is the supported
version unless a tagged archival snapshot explicitly states otherwise.

## Reporting A Vulnerability

Please do not open a public issue for vulnerabilities.

Use GitHub private vulnerability reporting:

https://github.com/LloydDuhon/cardano-treasury-history-archive/security/advisories/new

If private reporting is unavailable, contact the maintainer:

Lloyd Duhon <lloyd.duhon@intersectmbo.org>

Include:

- Affected file, workflow, site page, or data artifact.
- Steps to reproduce.
- Impact and likely exploit path.
- Any proof-of-concept payload, preferably minimized.
- Whether the issue affects the published GitHub Pages site, ETL, raw snapshots,
  generated reports, or repository automation.

## Scope

Security reports are appropriate for:

- Stored or reflected XSS in the static site.
- Unsafe handling of proposer-submitted text or data-derived URLs.
- Poisoned generated artifacts, provenance bypasses, or reproducibility gaps
  that could mislead public users.
- Credential, token, or private-data exposure.
- GitHub Actions, dependency, or supply-chain issues that could alter published
  site output or committed data.
- ETL fetcher behavior that allows untrusted sources to replace trusted source
  snapshots.

Normal data questions, disputed entity matches, incomplete provenance, or
methodology concerns are not security reports unless they create a concrete
integrity or execution risk. Use the data/support issue templates for those.

## Public Keys And Public Tokens

Some upstream systems expose public client-side tokens, such as Supabase anon
keys intended for browser use. These are not treated as secrets by default.
Please report them only if they grant unexpected write access, private data
access, or privilege beyond the public upstream application.

## Response Expectations

The maintainer will acknowledge security reports as soon as practical and will
prioritize issues that affect the published site, repository automation, or
integrity of generated public reports. Fixes may be coordinated through private
advisories until the public patch is ready.
