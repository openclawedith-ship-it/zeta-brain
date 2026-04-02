# ZETA ∞ — Capability Inventory (2026-04-02)

## Host: Motorola G64 5G Pro (aarch64, ARM64)
- Ubuntu 24.04.3 LTS container via AndClaw
- 8GB RAM (2.5GB+ free typical) | 128GB storage (35GB free)

## Constraint: Android cgroup OOM-kills
- `apt-get install` / dpkg → kills at ~2.5GB → NO nmap, john, hashcat, hydra, metasploit
- C compiler missing → no native compilation
- Large download+extract simultaneously → OOM (do one-at-a-time)

## Local AI: llama.cpp b8611
| Model | Size | Status |
|-------|------|--------|
| Qwen2.5-0.5B-Instruct-uncensored.Q4_K_M | 469MB | Primary, tested |
| Qwen-0.5B-Q2_0 | ~200MB | Fallback |
| SmolLM2-135M-Instruct-Q4 | ~100MB | Tiny fallback |

## Go Tools (12 ARM64 Static Binaries)
ffuf · nuclei · naabu · amass · subfinder · dnsx · httpx · katana · gobuster · gitleaks · jq · yq

## Python Stack (28+ packages)
**Network:** requests, aiohttp, httpx, scapy
**Exploitation:** impacket, paramiko, sqlmap, pwntools/pwn
**Binary:** capstone, unicorn, lief, yara, binwalk
**Recon:** whois, shodan, censys, dnspython, tldextract, netaddr
**Forensics:** volatility3
**Proxy/Spider:** mitmproxy, scrapy
**Crypto:** cryptography, pycryptodomex
**Utils:** rich, jinja2, click, lxml, bs4, faker, aioquic, python-nmap

## ZETA Platform: 6 autonomous modules
recon → webscan → exploit → analysis → correlation → report

## GitHub: github.com/openclawedith-ship-it
- zeta-brain (workspace/memory)
- zeta-platform (security framework)  
- zeta-coding-master (coding tools)
