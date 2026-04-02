#!/usr/bin/env bash
###############################################################################
# PHASE 1: SYSTEM FOUNDATION — Install all missing build tools & infrastructure
# Target: aarch64 Android container (Motorola G64, 8GB RAM, 39GB free)
###############################################################################
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[i]${NC} $1"; }
step()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
fail()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo ""
echo "⚡ ════════════════════════════════════════════════"
echo "   ZETA ∞ PHASE 1: SYSTEM FOUNDATION"
echo "   Building the sovereign infrastructure"
echo "⚡ ════════════════════════════════════════════════"
echo ""

# ── Step 1: Update package lists ──────────────────────────────
info "Updating package lists..."
apt-get update -qq 2>&1 | tail -3
step "Package lists updated"

# ── Step 2: Install compilers & build tools ───────────────────
info "Installing compilers and build tools..."
apt-get install -y -qq \
    build-essential gcc g++ make cmake autoconf automake pkg-config \
    2>&1 | tail -5
step "Compilers installed: gcc, g++, make, cmake"

# ── Step 3: Install Python packages ───────────────────────────
info "Installing Python packages..."
apt-get install -y -qq \
    python3-pip python3-dev python3-venv python3-setuptools \
    2>&1 | tail -3
pip3 install --break-system-packages \
    capstone keystone-engine unicorn angr lief pyelftools \
    scapy requests flask fastapi uvicorn \
    tree_sitter tree-sitter-c tree-sitter-cpp tree-sitter-python tree-sitter-javascript tree-sitter-rust tree-sitter-go tree-sitter-java tree-sitter-typescript \
    numpy scipy 2>&1 | tail -5
step "Python packages installed"

# ── Step 4: Install system tools ──────────────────────────────
info "Installing system analysis tools..."
apt-get install -y -qq \
    radare2 \
    binutils objdump readelf strings nm \
    file libmagic1 \
    strace ltrace \
    gdb \
    jq \
    sqlite3 \
    tmux vim nano \
    htop iotop \
    net-tools iproute2 \
    strace ltrace \
    2>&1 | tail -5
step "System tools installed"

# ── Step 5: Install Node.js tools ─────────────────────────────
info "Installing Node.js tools..."
npm install -g @anthropic-ai/claude-code 2>/dev/null || true
step "Node ecosystem ready"

# ── Summary ──────────────────────────────────────────────────
echo ""
echo "⚡ ════════════════════════════════════════════════"
echo "   PHASE 1 COMPLETE"
echo "   All foundational tools installed"
echo "⚡ ════════════════════════════════════════════════"
