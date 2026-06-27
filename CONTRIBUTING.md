# Contributing to SEO SWARM

First off — thank you for your interest in contributing! 🐝

## Code of Conduct

Be kind, be respectful, be collaborative. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## How to Contribute

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/seo-swarm
cd seo-swarm
npm install
```

### 2. Create a Branch

```bash
git checkout -b feat/my-feature
# or
git checkout -b fix/my-bugfix
```

Branch naming: `feat/description`, `fix/description`, `docs/description`, `refactor/description`

### 3. Make Your Changes

- Follow PEP 8 for Python code
- Keep functions small and focused
- Add docstrings to new functions
- Write tests for new features
- Update README.md if adding new commands

### 4. Test

```bash
# Python tests
python -m pytest tests/ -v

# Lint (coming soon)
python -m ruff check src/
```

### 5. Commit

```bash
git commit -m "feat: add amazing new feature

- Detailed description of changes
- Reference any related issues"
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `test:` — tests
- `refactor:` — code restructuring
- `chore:` — maintenance

### 6. Push & PR

```bash
git push origin feat/my-feature
```

Then open a Pull Request on GitHub.

## Adding a New SEO Agent

1. Add agent definition to `src/seo_swarm/agents/registry.py`
2. Add ASCII art to `src/seo_swarm/ascii/banners.py`
3. Add agent templates to `src/seo_swarm/agents/orchestrator.py`
4. Test with: `seo-swarm agent new-agent --url example.com`

## Adding a New Skill

1. Add skill metadata to `src/seo_swarm/skills/loader.py`
2. Include GitHub repository URL
3. Categorize appropriately (audit, analysis, content, technical, local, etc.)

## Project Structure

```
src/seo_swarm/
├── agents/          # Agent definitions + orchestrator
├── tui/             # Terminal UI dashboard
├── ascii/           # ASCII art banners
├── memory/          # Self-improving memory engine
├── skills/          # Skill loader + registry
└── browser/         # Browser automation engine
```

## Questions?

Open an issue or email: dev@uthuman.com
