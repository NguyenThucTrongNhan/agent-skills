@'
# Agent Skills

Reusable skills for AI coding agents.

## Available skills

| Skill | Purpose |
|---|---|
| `repo-onboarding-context` | Create a read-only, evidence-based onboarding map for an unfamiliar repository. |
'@ | Set-Content -LiteralPath (Join-Path $repo 'README.md') -Encoding utf8