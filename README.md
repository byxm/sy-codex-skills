# sy-codex-skills

Reusable Codex skills maintained as a monorepo.

This repository is structured so each skill can be installed independently from a stable path inside the repo. The first published skill is `git-sync-delivery`.

## Repository Layout

```text
skills/.curated/<skill-name>/
```

Current skills:

- `git-sync-delivery`

Install path:

- `skills/.curated/git-sync-delivery`

## Install

Using the Codex skill installer with repo + path:

```bash
scripts/install-skill-from-github.py --repo byxm/sy-codex-skills --path skills/.curated/git-sync-delivery
```

Using a GitHub URL:

```bash
scripts/install-skill-from-github.py --url https://github.com/byxm/sy-codex-skills/tree/main/skills/.curated/git-sync-delivery
```

After installation, restart Codex to pick up the new skill.

## Add New Skills

Add each new skill under:

```text
skills/.curated/<new-skill-name>/
```

Each skill should remain self-contained and include at least:

- `SKILL.md`
- `agents/openai.yaml` when UI metadata is needed

Optional directories can be added per skill when necessary:

- `scripts/`
- `references/`
- `assets/`
