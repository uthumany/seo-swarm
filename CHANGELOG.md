# Changelog

All notable changes to SEO SWARM will be documented in this file.

## [1.1.0] - 2025-06-27

### Added — Pixel Art Agent Portraits 🎨
- Complete pixel art engine (`pixel_art.py`) with 16×16 agent portraits
- 10 unique pixel art portraits designed for terminal rendering
- 3-level shading system (empty, light, solid) using Unicode block characters
- 8 color palettes matching each agent's theme (cyan, green, magenta, yellow, blue, red, white, gray)
- Pixel art gallery grid view (`seo-swarm agents --pixel-gallery`)
- Detailed pixel art agent cards with metadata (`seo-swarm agents --pixel-cards`)
- Compact agent row view with pixel portraits (`seo-swarm agents --row`)
- Single agent pixel portrait command (`seo-swarm portrait <agent-id>`)
- Dedicated `seo-swarm pixel-gallery` command
- Compact portrait mode (`--compact` flag)
- Retro GameBoy-era styling with one-line art

### Changed
- Agent card display now defaults to pixel art (replaces ASCII line art)
- Banner updated to v1.1.0 with pixel art indicators
- Help text updated with all new pixel art commands

### Technical
- `PixelRenderer` class with deterministic 16×16 → terminal rendering
- Hex-encoded pixel data format for compact agent portrait storage
- Row/cell normalization for robust pixel art parsing
- Fixed-width 2-character-per-cell rendering for clean grid alignment

## [1.0.0] - 2025-06-27

### Added — Initial Release 🚀
- 10 specialized SEO agents with profile cards
- Parallel swarm execution engine (ThreadPoolExecutor)
- Self-improving memory system (SQLite)
- Terminal UI dashboard with ANSI colors
- ASCII art agent profile cards
- 30+ preloaded SEO skills
- 10 browser automation skills
- 11 package manager installation methods
- Full documentation suite

[1.1.0]: https://github.com/uthumany/seo-swarm/releases/tag/v1.1.0
[1.0.0]: https://github.com/uthumany/seo-swarm/releases/tag/v1.0.0
