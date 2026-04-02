"""
ZETA ∞ CAPSTONE ENGINE — Binary Disassembly & Analysis
The eye that reads machine code and translates it to human understanding.

Capabilities:
  - Disassemble x86/x64/ARM/ARM64/MIPS/PPC binaries
  - Analyze ELF/PE/Mach-O binary structure (via LIEF)
  - Emulate code with Unicorn engine
  - Extract strings and search for byte patterns
  - Auto-detect binary architecture

All dependencies verified: capstone 5.0.7, lief 0.17.6, unicorn 2.1.4
"""

import os, sys, json, hashlib, struct, re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class CapstoneEngine:
    """Binary disassembly and analysis engine"""
    
    def __init__(self):
        import capstone
        import lief
        import unicorn
        self.capstone = capstone
        self.lief = lief
        self.unicorn = unicorn
        
        self.disassemblers = {
            'x86': capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32),
            'x64': capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64),
            'arm': capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM),
            'arm64': capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM),
            'mips': capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32),
            'ppc': capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_32),
        }
        for cs in self.disassemblers.values():
            cs.detail = True
    
    # ── Architecture Detection ─────────────────────────────────
    
    def detect_arch(self, file_path: str) -> str:
        """Auto-detect binary architecture"""
        try:
            binary = self.lief.parse(file_path)
            if binary is None:
                return self._detect_arch_fallback(file_path)
            if isinstance(binary, self.lief.ELF.Binary):
                arch = str(binary.header.machine_type)
                if 'X86_64' in arch: return 'x64'
                if 'ARM' in arch and 'AARCH64' not in arch: return 'arm'
                if 'AARCH64' in arch: return 'arm64'
                return 'x86'
            if isinstance(binary, self.lief.PE.Binary):
                mech = str(binary.header.machine)
                return 'x64' if 'PE64' in mech else 'x86'
            if isinstance(binary, self.lief.MachO.Binary):
                ct = str(binary.header.cpu_type)
                return 'arm64' if 'ARM64' in ct else 'x64'
        except:
            pass
        return self._detect_arch_fallback(file_path)
    
    def _detect_arch_fallback(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            magic = f.read(16)
        if magic[:4] == b'\x7fELF':
            return 'x64' if magic[4] == 2 else 'x86'
        if magic[:2] == b'MZ':
            return 'x86'
        return 'x86'
    
    # ── Disassembly ────────────────────────────────────────────
    
    def disassemble(self, file_path: str, arch: str = None, count: int = 1000) -> List[Dict]:
        """Disassemble a binary with full instruction detail"""
        size = os.path.getsize(file_path)
        if size > 50 * 1024 * 1024:
            raise ValueError(f"Binary too large: {size} bytes")
        with open(file_path, 'rb') as f:
            data = f.read()
        
        arch = arch or self.detect_arch(file_path)
        cs = self.disassemblers.get(arch)
        if not cs:
            raise ValueError(f"Unknown arch: {arch}. Available: {list(self.disassemblers.keys())}")
        
        instructions = []
        for insn in cs.disasm(data, 0x1000000):
            if len(instructions) >= count:
                break
            instructions.append({
                'address': hex(insn.address),
                'size': insn.size,
                'mnemonic': insn.mnemonic,
                'op_str': insn.op_str,
                'bytes': insn.bytes.hex(),
            })
        return instructions
    
    def disassemble_memory(self, code: bytes, arch: str = 'x64', addr: int = 0) -> List[Dict]:
        """Disassemble raw bytes from memory"""
        cs = self.disassemblers.get(arch)
        if not cs:
            raise ValueError(f"Unknown arch: {arch}")
        
        instructions = []
        for insn in cs.disasm(code, addr):
            instructions.append({
                'address': hex(insn.address),
                'size': insn.size,
                'mnemonic': insn.mnemonic,
                'op_str': insn.op_str,
                'bytes': insn.bytes.hex(),
            })
        return instructions
    
    # ── Binary Analysis ────────────────────────────────────────
    
    def analyze_binary(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive binary analysis"""
        binary = self.lief.parse(file_path)
        
        try:
            data = open(file_path, 'rb').read()
        except:
            data = b''
        
        result = {
            'file': os.path.basename(file_path),
            'size': len(data),
        }
        
        if binary is None:
            # Not a recognized binary — fallback
            result.update({
                'format': 'unknown',
                'architecture': self._detect_arch_fallback(file_path),
                'md5': hashlib.md5(data).hexdigest(),
                'sha256': hashlib.sha256(data).hexdigest(),
            })
            return result
        
        result.update({
            'format': str(binary.format),
            'architecture': self.detect_arch(file_path),
            'md5': hashlib.md5(data).hexdigest(),
            'sha256': hashlib.sha256(data).hexdigest(),
        })
        
        if isinstance(binary, self.lief.ELF.Binary):
            result['entry_point'] = hex(binary.header.entrypoint)
            result['sections'] = [s.name for s in binary.sections]
            result['segments'] = [str(seg.type) for seg in binary.segments]
            result['dynamic_symbols'] = [s.name for s in binary.dynamic_symbols if s.name]
        elif isinstance(binary, self.lief.PE.Binary):
            result['entry_point'] = hex(binary.optional_header.addressof_entrypoint)
            result['imports'] = [imp.name for imp in binary.imports]
        elif isinstance(binary, self.lief.MachO.Binary):
            result['entry_point'] = hex(binary.entrypoint)
        
        return result
    
    # ── Pattern Matching ───────────────────────────────────────
    
    def find_patterns(self, data: bytes, patterns: Dict[str, bytes]) -> List[Dict]:
        """Search for byte patterns"""
        results = []
        for name, pattern in patterns.items():
            idx = 0
            while True:
                idx = data.find(pattern, idx)
                if idx == -1:
                    break
                results.append({
                    'pattern': name,
                    'offset': hex(idx),
                    'context': data[max(0,idx-16):idx+len(pattern)+16].hex(),
                })
                idx += 1
        return results
    
    def extract_strings(self, file_path: str, min_length: int = 4) -> Dict[str, List[str]]:
        """Extract ASCII and UTF-16 strings from binary"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        ascii_strings = [s.decode('ascii', errors='ignore')
                        for s in re.findall(rb'[\x20-\x7e]{%d,}' % min_length, data)]
        
        utf16_strings = []
        for s in re.findall(rb'(?:[\x20-\x7e]\x00){%d,}' % min_length, data):
            try:
                utf16_strings.append(s.decode('utf-16-le', errors='ignore'))
            except:
                pass
        
        return {
            'ascii': ascii_strings[:1000],
            'utf16': utf16_strings[:1000],
            'total': len(ascii_strings) + len(utf16_strings),
        }
    
    # ── Emulation (Unicorn) ───────────────────────────────────
    
    def emulate(self, code: bytes, arch: str = 'x64', addr: int = 0, steps: int = 10000) -> Dict:
        """Emulate code using Unicorn engine"""
        uc_arch = {
            'x64': (self.unicorn.Uc(self.unicorn.UC_ARCH_X86, self.unicorn.UC_MODE_64), 0x1000000),
            'x86': (self.unicorn.Uc(self.unicorn.UC_ARCH_X86, self.unicorn.UC_MODE_32), 0x1000000),
            'arm64': (self.unicorn.Uc(self.unicorn.UC_ARCH_ARM64, self.unicorn.UC_MODE_ARM), 0x1000000),
            'arm': (self.unicorn.Uc(self.unicorn.UC_ARCH_ARM, self.unicorn.UC_MODE_ARM), 0x1000000),
        }
        if arch not in uc_arch:
            raise ValueError(f"Unsupported arch: {arch}")
        
        mu, base = uc_arch[arch]
        memory_size = 1024 * 1024
        mu.mem_map(base, memory_size)
        mu.mem_write(base, code)
        
        if arch in ('x64', 'x86'):
            if arch == 'x64':
                mu.reg_write(self.unicorn.x86_const.UC_X86_REG_RSP, base + memory_size - 0x1000)
                mu.reg_write(self.unicorn.x86_const.UC_X86_REG_RIP, base + addr)
            else:
                mu.reg_write(self.unicorn.x86_const.UC_X86_REG_ESP, base + memory_size - 0x1000)
                mu.reg_write(self.unicorn.x86_const.UC_X86_REG_EIP, base + addr)
        
        try:
            mu.emu_start(base + addr, 0, count=steps)
            return {'status': 'completed', 'steps': steps}
        except self.unicorn.UcError as e:
            return {'status': 'halted', 'error': str(e), 'steps_attempted': steps}
    
    # ── Utilities ──────────────────────────────────────────────
    
    def read_safe(self, file_path: str, max_size: int = 50 * 1024 * 1024) -> bytes:
        """Read binary safely with size limit"""
        size = os.path.getsize(file_path)
        if size > max_size:
            raise ValueError(f"Binary too large: {size} bytes (max {max_size})")
        with open(file_path, 'rb') as f:
            return f.read()


# ── Self test ──────────────────────────────────────────────────
if __name__ == '__main__':
    print("⚡ ZETA ∞ CAPSTONE ENGINE")
    print("=" * 50)
    
    engine = CapstoneEngine()
    
    # Test: disassemble `mov rax, 0x42; ret`
    code = bytes([0x48, 0xc7, 0xc0, 0x42, 0x00, 0x00, 0x00, 0xc3])
    insns = engine.disassemble_memory(code, arch='x64')
    print(f"\n Disassembled {len(insns)} instructions:")
    for i in insns:
        print(f"  {i['address']}: {i['mnemonic']} {i['op_str']}")
    
    # Test: analyze a real binary (/usr/bin/env)
    analysis = engine.analyze_binary('/usr/bin/env')
    print(f"\n Analysis of /usr/bin/env:")
    print(f"  Format: {analysis['format']}")
    print(f"  Arch: {analysis['architecture']}")
    print(f"  Size: {analysis['size']} bytes")
    print(f"  MD5: {analysis['md5']}")
    
    # Test: extract strings
    strings = engine.extract_strings('/usr/bin/env')
    print(f"\n Extracted {strings['total']} strings")
    print(f"  Top 5: {[s[:40] for s in strings['ascii'][:5]]}")
    
    print("\n Capstone Engine operational")
