"""
ZETA ∞ SKILL SYSTEM — Plug-in Architecture for Intelligence
Each skill is a module that extends the core AI's abilities.

Skills auto-discover available engines:
  - capstone_core: Binary disassembly
  - transpiler: Code translation
  - debugger: Code analysis
  - crypto: Cryptography
  - network: Network analysis

Each skill defines:
  - name: Human-readable skill name
  - description: What it does
  - requires: List of python packages needed
  - functions: Public API exposed to the agent
"""

from typing import Dict, List, Optional, Any, Callable
from pathlib import Path


class Skill:
    """Base class for all ZETA ∞ skills"""
    
    name = "unnamed"
    description = "No description"
    version = "1.0.0"
    requires = []  # Required packages
    
    def __init__(self, engines: Dict = None):
        self.engines = engines or {}
    
    def get_capability(self, name: str) -> Optional[Callable]:
        """Get a capability function by name"""
        return getattr(self, name, None)
    
    def list_capabilities(self) -> List[str]:
        """List all public capabilities of this skill"""
        return [m for m in dir(self) if not m.startswith('_') and m != 'engines']


class ReverseEngineeringSkill(Skill):
    """
    Binary analysis and reverse engineering skill
    
    Capabilities:
      - Disassemble any binary
      - Extract strings from binaries
      - Analyze ELF/PE/Mach-O structure
      - Detect architecture and entry points
      - Search for byte patterns
      - Emulate code with Unicorn
    """
    
    name = "reverse-engineering"
    description = "Binary disassembly, analysis, and emulation using Capstone + LIEF + Unicorn"
    requires = ["capstone", "lief", "unicorn", "pyelftools"]
    
    def disassemble(self, file_path: str, arch: str = None, count: int = 100) -> List[Dict]:
        """Disassemble binary file"""
        engine = self.engines.get('capstone')
        if engine:
            return engine.disassemble(file_path, arch, count=count)
        raise RuntimeError("Capstone engine not available")
    
    def analyze_binary(self, file_path: str) -> Dict:
        """Full binary analysis"""
        engine = self.engines.get('capstone')
        if engine:
            return engine.analyze_binary(file_path)
        raise RuntimeError("Capstone engine not available")
    
    def extract_strings(self, file_path: str, min_length: int = 4) -> Dict:
        """Extract ASCII/UTF-16 strings from binary"""
        engine = self.engines.get('capstone')
        if engine:
            return engine.extract_strings(file_path, min_length)
        raise RuntimeError("Capstone engine not available")
    
    def emulate(self, code: bytes, arch: str = 'x64', steps: int = 10000) -> Dict:
        """Emulate raw machine code"""
        engine = self.engines.get('capstone')
        if engine:
            return engine.emulate(code, arch, steps=steps)
        raise RuntimeError("Unicorn engine not available")


class TranspilationSkill(Skill):
    """
    Universal code translation skill
    
    Translates between:
      Python → JavaScript, Rust, Go, C, C++, TypeScript
      C → Python (planned)
      JavaScript → Python (planned)
    """
    
    name = "transpilation"
    description = "Translate code between programming languages"
    requires = ["tree_sitter"]
    
    def translate(self, code: str, source: str, target: str) -> str:
        """Translate code from source language to target"""
        engine = self.engines.get('transpiler')
        if engine:
            return engine.translate(code, source, target)
        raise RuntimeError("Transpiler engine not available")
    
    def supported_pairs(self) -> Dict:
        """List supported translation pairs"""
        engine = self.engines.get('transpiler')
        if engine:
            return engine.list_supported_languages()
        return {}


class CodeAnalysisSkill(Skill):
    """
    Code analysis and debugging skill
    
    Features:
      - Static analysis
      - Security scanning
      - Complexity metrics
      - Execution tracing
      - File comparison
    """
    
    name = "code-analysis"
    description = "Static code analysis, security scanning, and debugging"
    requires = ["ast"]  # Built-in
    
    def analyze(self, source: str, name: str = 'source') -> Dict:
        """Full code analysis"""
        engine = self.engines.get('debugger')
        if engine:
            return engine.analyze_source(source, name)
        raise RuntimeError("Debugger engine not available")
    
    def analyze_file(self, filepath: str) -> Dict:
        """Analyze a source file"""
        engine = self.engines.get('debugger')
        if engine:
            return engine.analyze_source_file(filepath)
        raise RuntimeError("Debugger engine not available")
    
    def scan_security(self, source: str) -> Dict:
        """Security vulnerability scan"""
        engine = self.engines.get('debugger')
        if engine:
            return engine.analyze_source(source).get('security', {})
        raise RuntimeError("Debugger engine not available")
    
    def trace(self, code: str, verbose: bool = False) -> Dict:
        """Trace code execution"""
        engine = self.engines.get('debugger')
        if engine:
            return engine.trace_execution(code, verbose=verbose)
        raise RuntimeError("Debugger engine not available")


class CryptoSkill(Skill):
    """
    Cryptography and encoding skill
    
    Features:
      - Hash computation (MD5, SHA-*, BLAKE2)
      - HMAC generation
      - Encoding (Base64, Hex, Base85)
      - Classical ciphers (Caesar, Vigenère)
      - XOR analysis
    """
    
    name = "cryptography"
    description = "Hash computation, encoding, and classical cryptography"
    requires = []  # All stdlib
    
    def hash(self, data: str, algorithm: str = 'sha256') -> str:
        """Compute hash of string"""
        engine = self.engines.get('crypto')
        if engine:
            return engine.hash_string(data, algorithm)
        raise RuntimeError("Crypto engine not available")
    
    def hash_multi(self, data: str) -> Dict:
        """Hash with all algorithms"""
        engine = self.engines.get('crypto')
        if engine:
            return engine.hash_multi(data)
        raise RuntimeError("Crypto engine not available")
    
    def hash_file(self, filepath: str, algorithm: str = 'sha256') -> str:
        """Hash a file"""
        engine = self.engines.get('crypto')
        if engine:
            return engine.hash_file(filepath, algorithm)
        raise RuntimeError("Crypto engine not available")
    
    def encode(self, data: bytes, encoding: str) -> bytes:
        """Encode data"""
        engine = self.engines.get('crypto')
        if engine:
            return engine.encode(data, encoding)
        raise RuntimeError("Crypto engine not available")
    
    def decode(self, data: bytes, encoding: str) -> bytes:
        """Decode data"""
        engine = self.engines.get('crypto')
        if engine:
            return engine.decode(data, encoding)
        raise RuntimeError("Crypto engine not available")
    
    def caesar(self, text: str, shift: int) -> str:
        """Caesar cipher"""
        engine = self.engines.get('crypto')
        if engine:
            return engine.caesar(text, shift)
        raise RuntimeError("Crypto engine not available")
    
    def xor_bruteforce(self, ciphertext: bytes) -> List:
        """Brute force XOR encryption"""
        engine = self.engines.get('crypto')
        if engine:
            return engine.xor_bruteforce_single(ciphertext)
        raise RuntimeError("Crypto engine not available")


class NetworkSkill(Skill):
    """
    Network analysis skill
    
    Features:
      - Port scanning
      - Service fingerprinting
      - DNS resolution
      - Connectivity testing
    """
    
    name = "network-analysis"
    description = "Network scanning, DNS, and connectivity analysis"
    requires = []  # All stdlib
    
    def scan_port(self, host: str, port: int) -> Dict:
        """Scan a single port"""
        engine = self.engines.get('network')
        if engine:
            return engine.scan_port(host, port)
        raise RuntimeError("Network engine not available")
    
    def scan_services(self, host: str) -> List[Dict]:
        """Scan all well-known service ports"""
        engine = self.engines.get('network')
        if engine:
            return engine.scan_well_known(host)
        raise RuntimeError("Network engine not available")
    
    def resolve(self, hostname: str) -> Dict:
        """Resolve hostname"""
        engine = self.engines.get('network')
        if engine:
            return engine.resolve_ip(hostname)
        raise RuntimeError("Network engine not available")
    
    def connectivity(self) -> Dict:
        """Test outbound connectivity"""
        engine = self.engines.get('network')
        if engine:
            return engine.check_connectivity()
        raise RuntimeError("Network engine not available")


# ── Skill Registry ─────────────────────────────────────────────
class SkillRegistry:
    """Manages all available skills and their engines"""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.engines: Dict[str, Any] = {}
    
    def register_engine(self, name: str, engine_instance):
        """Register an engine instance"""
        self.engines[name] = engine_instance
    
    def register_skill_class(self, skill_class, auto_load: bool = True):
        """Register a skill class and optionally load it"""
        skill_name = skill_class.name
        self.skills[skill_name] = {
            'class': skill_class,
            'loaded': False,
            'instance': None,
        }
        
        if auto_load:
            self.load_skill(skill_name)
    
    def load_skill(self, name: str) -> Optional[Skill]:
        """Load a skill (instantiate it with available engines)"""
        if name not in self.skills:
            return None
        
        skill_info = self.skills[name]
        if skill_info['loaded']:
            return skill_info['instance']
        
        try:
            instance = skill_info['class'](engines=self.engines)
            skill_info['instance'] = instance
            skill_info['loaded'] = True
            return instance
        except Exception as e:
            skill_info['load_error'] = str(e)
            return None
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a loaded skill instance"""
        if name in self.skills and self.skills[name]['loaded']:
            return self.skills[name]['instance']
        return None
    
    def list_skills(self) -> List[Dict]:
        """List all registered skills with status"""
        result = []
        for name, info in self.skills.items():
            result.append({
                'name': name,
                'description': info['class'].description,
                'version': info['class'].version,
                'loaded': info['loaded'],
                'requires': info['class'].requires,
                'error': info.get('load_error'),
            })
        return result


# ── Auto-discovery and initialization ─────────────────────────

def create_full_registry() -> SkillRegistry:
    """Create a registry with all available engines and skills"""
    registry = SkillRegistry()
    
    # ── Load engines ──────────────────────────────────────────────
    try:
        from zeta_engines.capstone_core import CapstoneEngine
        registry.register_engine('capstone', CapstoneEngine())
    except Exception as e:
        print(f"⚠️  Capstone engine skipped: {e}")
    
    try:
        from zeta_engines.transpiler import TranspilerEngine
        registry.register_engine('transpiler', TranspilerEngine())
    except Exception as e:
        print(f"⚠️  Transpiler engine skipped: {e}")
    
    try:
        from zeta_engines.debugger import DebuggerEngine
        registry.register_engine('debugger', DebuggerEngine())
    except Exception as e:
        print(f"⚠️  Debugger engine skipped: {e}")
    
    try:
        from zeta_engines.crypto import CryptoEngine
        registry.register_engine('crypto', CryptoEngine())
    except Exception as e:
        print(f"⚠️  Crypto engine skipped: {e}")
    
    try:
        from zeta_engines.network import NetworkEngine
        registry.register_engine('network', NetworkEngine())
    except Exception as e:
        print(f"⚠️  Network engine skipped: {e}")
    
    # ── Register skills ───────────────────────────────────────────
    registry.register_skill_class(ReverseEngineeringSkill)
    registry.register_skill_class(TranspilationSkill)
    registry.register_skill_class(CodeAnalysisSkill)
    registry.register_skill_class(CryptoSkill)
    registry.register_skill_class(NetworkSkill)
    
    return registry


# ── Quick test ─────────────────────────────────────────────────
if __name__ == '__main__':
    print("⚡ ZETA ∞ SKILL SYSTEM")
    print("=" * 50)
    
    registry = create_full_registry()
    
    print("\n📋 Registered skills:")
    for skill in registry.list_skills():
        status = "✅" if skill['loaded'] else "❌"
        print(f"  {status} {skill['name']}: {skill['description']}")
    
    # Test: Use RE skill
    print("\n🔧 Testing reverse-engineering skill:")
    re_skill = registry.get_skill('reverse-engineering')
    if re_skill:
        # Quick disassembly test
        code = bytes([0x48, 0xc7, 0xc0, 0x42, 0x00, 0x00, 0x00, 0xc3])
        instructions = re_skill.disassemble_memory(code, arch='x64')
        print(f"  Disassembled {len(instructions)} instructions:")
        for insn in instructions:
            print(f"    {insn['mnemonic']} {insn['op_str']}")
    
    # Test: Use crypto skill
    print("\n🔧 Testing cryptography skill:")
    crypto_skill = registry.get_skill('cryptography')
    if crypto_skill:
        h = crypto_skill.hash("ZETA ∞")
        print(f"  SHA256('ZETA ∞'): {h[:32]}...")
    
    print("\n✅ Skill System operational")
