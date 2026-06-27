#!/bin/bash
# SEO SWARM - One-line installer
# Usage: curl -fsSL https://raw.githubusercontent.com/uthumany/seo-swarm/main/scripts/install.sh | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}"
echo "   ╔══════════════════════════════════════════════════════════════╗"
echo "   ║        ███████╗███████╗ ██████╗     ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗   ║"
echo "   ║        ██╔════╝██╔════╝██╔═══██╗    ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║   ║"
echo "   ║        ███████╗█████╗  ██║   ██║    ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║   ║"
echo "   ║        ╚════██║██╔══╝  ██║   ██║    ╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║   ║"
echo "   ║        ███████║███████╗╚██████╔╝    ███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║   ║"
echo "   ║        ╚══════╝╚══════╝ ╚═════╝     ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝   ║"
echo "   ╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "${YELLOW}🐝 SEO SWARM Installer${NC}"
echo ""

# Detect package manager
if command -v npm &>/dev/null; then
    echo -e "${GREEN}✓${NC} Installing via npm..."
    npm install -g seo-swarm
elif command -v yarn &>/dev/null; then
    echo -e "${GREEN}✓${NC} Installing via yarn..."
    yarn global add seo-swarm
elif command -v pnpm &>/dev/null; then
    echo -e "${GREEN}✓${NC} Installing via pnpm..."
    pnpm add -g seo-swarm
elif command -v bun &>/dev/null; then
    echo -e "${GREEN}✓${NC} Installing via bun..."
    bun install -g seo-swarm
elif command -v pip3 &>/dev/null; then
    echo -e "${GREEN}✓${NC} Installing via pip..."
    pip3 install seo-swarm
elif command -v pip &>/dev/null; then
    echo -e "${GREEN}✓${NC} Installing via pip..."
    pip install seo-swarm
else
    echo -e "${RED}✗${NC} No supported package manager found."
    echo "  Install one of: npm, yarn, pnpm, bun, pip"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ SEO SWARM installed successfully!${NC}"
echo -e "  Run: ${CYAN}seo-swarm --help${NC}"
echo -e "  Quick audit: ${CYAN}seo-swarm audit https://example.com${NC}"
