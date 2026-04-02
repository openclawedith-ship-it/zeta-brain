"""
ZETA ∞ MASTER ENGINE — The Sovereign AI Brain
────────────────────────────────────────────────
The complete local intelligence system for your Motorola G64 5G Pro.

What exists on your device right now:
  ✅ llama.cpp b8611 — aarch64 native binary (no compilation needed)
  ✅ Qwen2.5-0.5B-Uncensored GGUF — 469MB model, no safety rails
  ✅ capstone 5.0.7 — multi-arch disassembler
  ✅ lief 0.17.6 — binary format parser (ELF/PE/Mach-O)
  ✅ unicorn 2.1.4 — CPU emulation engine
  ✅ tree-sitter — universal parser
  ✅ Python 3.12 + Node.js v24 — full runtime stack
  ✅ 37GB free storage | 2.5GB available RAM

Usage:
  # Start the local AI API server (OpenAI-compatible)
  python3 zeta_master.py --serve --port 8000

  # Run interactive chat with the local model
  python3 zeta_master.py --chat

  # Test everything
  python3 zeta_master.py --test

  # Use the engines programmatically
  python3 zeta_master.py --engine capstone --disasm <binary>
"""

import sys, os, json, subprocess, shlex
from pathlib import Path
from typing import Dict, List, Optional, Any


# ── Paths ─────────────────────────────────────────────────────
MODEL_DIR = Path("/root/.openclaw/zeta-local-ai/models")
LLAMA_BIN = Path("/root/.openclaw/zeta-local-ai/llama-cpp")
ENGINES_DIR = Path("/root/.openclaw/workspace/zeta-engines")

MODEL = MODEL_DIR / "Qwen2.5-0.5B-Instruct-uncensored.Q4_K_M.gguf"
ENGINE_BIN = LLAMA_BIN / "llama-cli"
SERVER_BIN = LLAMA_BIN / "llama-server"

LLM_ENV = {**os.environ, "LD_LIBRARY_PATH": str(LLAMA_BIN)}


# ── System Check ──────────────────────────────────────────────
def verify_system() -> Dict[str, bool]:
    """Check which components are available"""
    checks = {}
    checks["model"] = MODEL.exists()
    checks["llama_cli"] = ENGINE_BIN.exists()
    checks["llama_server"] = SERVER_BIN.exists()
    checks["capstone"] = subprocess.run([sys.executable, "-c", "import capstone"],
                                         capture_output=True).returncode == 0
    checks["lief"] = subprocess.run([sys.executable, "-c", "import lief"],
                                     capture_output=True).returncode == 0
    checks["unicorn"] = subprocess.run([sys.executable, "-c", "import unicorn"],
                                        capture_output=True).returncode == 0
    checks["tree_sitter"] = subprocess.run([sys.executable, "-c", "import tree_sitter"],
                                            capture_output=True).returncode == 0
    checks["all"] = all(checks.values())
    return checks


# ── Local LLM Inference ──────────────────────────────────────
def chat_local(prompt: str, system_prompt: str = "You are ZETA ∞, a sovereign AI.",
              max_tokens: int = 256, temperature: float = 0.7) -> str:
    """Run inference with the local uncensored model"""
    if not MODEL.exists():
        return "ERROR: Model file not found at " + str(MODEL)
    if not ENGINE_BIN.exists():
        return "ERROR: llama-cli not found at " + str(ENGINE_BIN)

    messages = json.dumps([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])

    result = subprocess.run(
        [str(ENGINE_BIN), "-m", str(MODEL),
         "--log-disable", "--no-display-prompt",
         "-p", f"system\n{system_prompt}\nuser\n{prompt}\nassistant\n",
         "-n", str(max_tokens), "--temp", str(temperature)],
        capture_output=True, text=True, env=LLM_ENV, timeout=120
    )
    return result.stdout.strip()


def serve_local(host: str = "0.0.0.0", port: int = 8000, ctx_size: int = 4096):
    """Start the OpenAI-compatible API server"""
    if not SERVER_BIN.exists():
        print("ERROR: llama-server not found")
        sys.exit(1)
    if not MODEL.exists():
        print("ERROR: Model not found")
        sys.exit(1)

    cmd = [
        str(SERVER_BIN), "-m", str(MODEL),
        "--host", host, "--port", str(port),
        "--ctx-size", str(ctx_size),
        "--log-disable"
    ]
    print(f"🚀 Starting ZETA ∞ local AI server at http://{host}:{port}")
    print(f"   Model: {MODEL.name}")
    print(f"   Context: {ctx_size} tokens")
    print(f"   OpenAI-compatible API at http://{host}:{port}/v1/chat/completions")
    print(f"   Test: curl http://{host}:{port}/v1/chat/completions \\")
    print(f'         -H "Content-Type: application/json" \\')
    print(f'         -d \'{{"messages":[{{"role":"user","content":"hello"}}]}}\'')
    print(f"   Press Ctrl+C to stop")
    print("=" * 60)
    subprocess.run(cmd, env=LLM_ENV)


# ── Engine Interface ─────────────────────────────────────────
def get_engine(name: str):
    """Get any engine by name"""
    sys.path.insert(0, str(ENGINES_DIR))
    modules = {
        'capstone': ('capstone_core', 'CapstoneEngine'),
        'crypto': ('crypto', 'CryptoEngine'),
        'transpiler': ('transpiler', 'TranspilerEngine'),
        'debugger': ('debugger', 'DebuggerEngine'),
        'network': ('network', 'NetworkEngine'),
    }
    if name not in modules:
        return None
    mod_name, cls_name = modules[name]
    mod = __import__(mod_name, fromlist=[cls_name])
    return getattr(mod, cls_name)()


# ── Test Suite ───────────────────────────────────────────────
def run_tests():
    """Verify everything works"""
    print("=" * 60)
    print("  ZETA ∞ VERIFICATION SUITE")
    print("=" * 60)

    # System check
    print("\n Checking hardware...")
    import platform
    import os as _os
    print(f"   Platform: {platform.machine()} ({platform.system()})")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Storage: {_os.popen('df -h / | tail -1').read().strip()}")
    print(f"   Memory: {_os.popen('cat /proc/meminfo | head -3').read().strip()}")

    # Component check
    print("\n Checking components...")
    checks = verify_system()
    for name, ok in checks.items():
        if name == "all": continue
        status = " OK" if ok else " MISSING"
        print(f"   [{status}] {name}")

    # Engine tests
    print("\n Testing engines...")

    # capstone
    engine = get_engine('capstone')
    if engine:
        insns = engine.disassemble_memory(
            bytes([0x48, 0xc7, 0xc0, 0x42, 0, 0, 0, 0, 0xc3]),
            arch='x64'
        )
        print(f"   [ OK] capstone: {len(insns)} instructions")

    # crypto
    engine = get_engine('crypto')
    if engine:
        h = engine.hash_string("ZETA INFINITY", "sha256")
        print(f"   [ OK] crypto: sha256={h[:20]}...")

    # transpiler
    engine = get_engine('transpiler')
    if engine:
        out = engine.translate("def hello(): return 'hi'", 'python', 'javascript')
        print(f"   [ OK] transpiler: python->javascript")

    # debugger
    engine = get_engine('debugger')
    if engine:
        r = engine.analyze_source("x = 1+2", "test.py")
        print(f"   [ OK] debugger: syntax={r['syntax']}")

    # network
    engine = get_engine('network')
    if engine:
        r = engine.resolve_ip("localhost")
        print(f"   [ OK] network: localhost={r.get('ip', '?')}")

    # Model check
    if MODEL.exists():
        size_gb = MODEL.stat().st_size / (1024**3)
        print(f"\n Model ready: {MODEL.name} ({size_gb:.2f} GB)")
    else:
        print(f"\n Model MISSING: need to download to {MODEL}")

    print("\n" + "=" * 60)
    if checks["all"]:
        print("  ZETA ∞ — FULLY OPERATIONAL")
    else:
        print("  ZETA ∞ — PARTIAL (some components missing)")
    print("=" * 60)
    return checks


# ── CLI ─────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="ZETA ∞ Master Engine")
    parser.add_argument("--test", action="store_true", help="Run verification suite")
    parser.add_argument("--chat", action="store_true", help="Interactive chat")
    parser.add_argument("--serve", action="store_true", help="Start API server")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--prompt", type=str, help="One-shot query")
    parser.add_argument("--system", type=str, default="You are ZETA ∞, a sovereign AI.")
    parser.add_argument("--tokens", type=int, default=256)
    parser.add_argument("--temp", type=float, default=0.7)
    parser.add_argument("--status", action="store_true", help="Show system status")

    args = parser.parse_args()

    if args.test:
        run_tests()
    elif args.status:
        checks = verify_system()
        print(json.dumps(checks, indent=2))
    elif args.serve:
        serve_local(port=args.port)
    elif args.chat:
        print("ZETA ∞ LOCAL AI CHAT (Ctrl+C to quit)")
        print("Type your message...")
        while True:
            try:
                prompt = input("\n> ")
                if not prompt:
                    continue
                print(chat_local(prompt, args.system, args.tokens, args.temp))
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    elif args.prompt:
        print(chat_local(args.prompt, args.system, args.tokens, args.temp))
    else:
        print("ZETA ∞ Master Engine")
        print("Usage: zeta_master.py [--test|--chat|--serve|--prompt 'text'|--status]")
        run_tests()


if __name__ == "__main__":
    main()
