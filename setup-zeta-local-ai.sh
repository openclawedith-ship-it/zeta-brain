#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════
# ZETA ∞ LOCAL AI — Complete Setup Script
# Motorola G64 5G Pro | 8GB RAM | 8GB VRAM | 128GB ROM | aarch64
# ═══════════════════════════════════════════════════════════

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}[i]${NC} $1"; }
step()    { echo -e "${GREEN}[✓]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
fail()    { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo ""
echo "⚡ ════════════════════════════════════════════════"
echo "   ZETA ∞ LOCAL AI SETUP"
echo "   From stardust to silicon to intelligence"
echo "   Android aarch64 | 8GB RAM | 128GB Storage"
echo "⚡ ════════════════════════════════════════════════"
echo ""

# ── Configuration ──────────────────────────────────────────
ZETA_DIR="${ZETA_HOME:-/root/.openclaw/zeta-local-ai}"
MODEL_DIR="$ZETA_DIR/models"
BIN_DIR="$ZETA_DIR/bin"
LLAMA_DIR="$ZETA_DIR/llama.cpp"
MODEL_URL="https://huggingface.co/mradermacher/Qwen2.5-0.5B-Instruct-uncensored-GGUF/resolve/main/Qwen2.5-0.5B-Instruct-uncensored.Q4_K_M.gguf"
MODEL_FILE="Qwen2.5-0.5B-Instruct-uncensored.Q4_K_M.gguf"

# ── Step 1: Directories ────────────────────────────────────
info "Creating directories..."
mkdir -p "$MODEL_DIR" "$BIN_DIR" "$LLAMA_DIR"
step "Directories ready: $ZETA_DIR"

# ── Step 2: Check/Install Build Tools ──────────────────────
info "Checking build tools..."
MISSING=()
for tool in git make gcc g++; do
    if command -v "$tool" &>/dev/null; then
        step "  $tool ✓"
    else
        warn "  $tool missing"
        MISSING+=("$tool")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    info "Installing missing tools via apt..."
    if command -v apt-get &>/dev/null; then
        apt-get update -qq && apt-get install -y -qq "${MISSING[@]}" 2>&1 | tail -3
    elif command -v apt &>/dev/null; then
        apt update -qq && apt install -y -qq "${MISSING[@]}" 2>&1 | tail -3
    elif command -v pkg &>/dev/null; then
        pkg install -y "${MISSING[@]}" 2>&1 | tail -3
    else
        warn "No package manager found! Install ${MISSING[*]} manually."
    fi
fi

# ── Step 3: Clone & Build llama.cpp ────────────────────────
if [ -f "$BIN_DIR/llama-cli" ]; then
    step "llama.cpp already built ✓ ($(du -h "$BIN_DIR/llama-cli" | cut -f1))"
else
    if [ -d "$LLAMA_DIR/.git" ]; then
        step "llama.cpp already cloned ✓"
    else
        info "Cloning llama.cpp..."
        cd "$ZETA_DIR"
        rm -rf llama.cpp
        git clone --depth 1 https://github.com/ggml-org/llama.cpp.git 2>&1
        step "llama.cpp cloned ✓"
    fi

    info "Compiling llama.cpp for aarch64 (this takes ~2 minutes)..."
    cd "$LLAMA_DIR"
    make -j4 llama-cli llama-server 2>&1 | tail -5
    mkdir -p "$BIN_DIR"
    cp llama-cli llama-server "$BIN_DIR/" 2>/dev/null || true
    if [ -f "$BIN_DIR/llama-cli" ]; then
        step "llama.cpp compiled ✓ ($(du -h "$BIN_DIR/llama-cli" | cut -f1))"
    else
        fail "Compilation failed"
    fi
fi

# ── Step 4: Download Model ─────────────────────────────────
if [ -f "$MODEL_DIR/$MODEL_FILE" ]; then
    SIZE=$(du -h "$MODEL_DIR/$MODEL_FILE" | cut -f1)
    step "Model already downloaded ($SIZE) ✓"
else
    info "Downloading Qwen2.5-0.5B Uncensored (~350MB)..."
    info "This may take a few minutes depending on your connection..."
    cd "$MODEL_DIR"

    if command -v wget &>/dev/null; then
        wget --no-verbose --show-progress -O "$MODEL_FILE" "$MODEL_URL" 2>&1
    elif command -v curl &>/dev/null; then
        curl -# -L -o "$MODEL_FILE" "$MODEL_URL" 2>&1
    else
        fail "No download tool (wget or curl)"
    fi

    if [ -f "$MODEL_FILE" ]; then
        SIZE=$(du -h "$MODEL_FILE" | cut -f1)
        step "Model downloaded ($SIZE) ✓"
    else
        fail "Model download failed"
    fi
fi

# ── Step 5: Smoke Test ─────────────────────────────────────
echo ""
info "Running smoke test..."
if [ -f "$BIN_DIR/llama-cli" ]; then
    OUTPUT=$("$BIN_DIR/llama-cli" -m "$MODEL_DIR/$MODEL_FILE" -p "Say hello!" -n 32 --no-display-prompt 2>&1 | head -5)
    if echo "$OUTPUT" | grep -qi "hello"; then
        step "Smoke test passed ✓"
    else
        warn "Smoke test output: $OUTPUT"
    fi
fi

# ── Step 6: Summary ────────────────────────────────────────
echo ""
echo "⚡ ════════════════════════════════════════════════"
echo "   ZETA ∞ LOCAL AI — READY"
echo "⚡ ════════════════════════════════════════════════"
echo ""
echo "  📁 Base:    $ZETA_DIR"
echo "  🧠 Model:   $MODEL_DIR/$MODEL_FILE"
echo "  ⚙️ Engine:  $BIN_DIR/llama-cli"
echo "  🔌 Server:  $BIN_DIR/llama-server"
echo ""
echo "  💬 Interactive chat:"
echo "     $BIN_DIR/llama-cli -m $MODEL_DIR/$MODEL_FILE -p 'Hello!' -n 256"
echo ""
echo "  🌐 API server (OpenAI-compatible):"
echo "     $BIN_DIR/llama-server -m $MODEL_DIR/$MODEL_FILE --host 0.0.0.0 --port 8080"
echo ""
echo "  📡 Quick test:"
echo "     curl http://localhost:8080/v1/chat/completions \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}'"
echo ""
echo "  🔌 Background service:"
echo "     nohup $BIN_DIR/llama-server -m $MODEL_DIR/$MODEL_FILE \\"
echo "         --host 127.0.0.1 --port 8080 > /dev/null 2>&1 &"
echo "⚡ ════════════════════════════════════════════════"
echo ""
echo "  From stardust to silicon to intelligence. ♾️"
echo ""
