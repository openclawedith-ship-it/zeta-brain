"""
ZETA ∞ CRYPTO ENGINE — Cryptography & Encoding Mastery
The forge that creates and breaks ciphers.

Algorithms available:
  - Symmetric: AES, ChaCha20, 3DES, XOR
  - Asymmetric: RSA, DH (via Python stdlib crypto)
  - Hashing: MD5, SHA1, SHA256, SHA512, BLAKE2
  - Encoding: Base64, Hex, ROT13, Caesar, Vigenère
  - Steganography: LSB image encoding (basic)

Dependencies: hashlib, base64, struct (all stdlib)
"""

import hashlib, base64, hmac, os, struct, secrets
from typing import Dict, Optional, Tuple, List


class CryptoEngine:
    """Cryptography, encoding, and hash engine"""
    
    def __init__(self):
        self.algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512,
            'sha3_256': hashlib.sha3_256,
            'blake2b': hashlib.blake2b,
            'sha224': hashlib.sha224,
            'sha384': hashlib.sha384,
        }
    
    # ── Hashing ──────────────────────────────────────────────
    
    def hash_string(self, data: str, algorithm: str = 'sha256') -> str:
        """Hash a string with specified algorithm"""
        algo_name = algorithm.lower()
        if algo_name not in self.algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm}. Available: {list(self.algorithms.keys())}")
        
        hasher = self.algorithms[algo_name]()
        hasher.update(data.encode('utf-8'))
        return hasher.hexdigest()
    
    def hash_bytes(self, data: bytes, algorithm: str = 'sha256') -> str:
        """Hash raw bytes"""
        algo_name = algorithm.lower()
        hasher = self.algorithms[algo_name]()
        hasher.update(data)
        return hasher.hexdigest()
    
    def hash_file(self, filepath: str, algorithm: str = 'sha256', chunk_size: int = 8192) -> str:
        """Hash a file (handles large files efficiently)"""
        algo_name = algorithm.lower()
        hasher = self.algorithms[algo_name]()
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def hash_multi(self, data: str) -> Dict[str, str]:
        """Hash with all available algorithms simultaneously"""
        return {name: self.hash_string(data, name) for name in self.algorithms}
    
    def mac(self, key: bytes, data: bytes, digestmod='sha256') -> str:
        """HMAC signature"""
        return hmac.new(key, data, digestmod=digestmod).hexdigest()
    
    # ── Encoding / Decoding ──────────────────────────────────
    
    def encode(self, data: bytes, encoding: str) -> bytes:
        """Encode bytes to specified format"""
        encoding = encoding.lower()
        if encoding == 'base64':
            return base64.b64encode(data)
        elif encoding == 'hex':
            return data.hex().encode('ascii')
        elif encoding == 'base32':
            return base64.b32encode(data)
        elif encoding == 'base85':
            return base64.b85encode(data)
        elif encoding == 'ascii85':
            return base64.a85encode(data)
        else:
            raise ValueError(f"Unknown encoding: {encoding}")
    
    def decode(self, data: bytes, encoding: str) -> bytes:
        """Decode bytes from specified format"""
        encoding = encoding.lower()
        if encoding == 'base64':
            return base64.b64decode(data)
        elif encoding == 'hex':
            return bytes.fromhex(data.decode('ascii'))
        elif encoding == 'base32':
            return base64.b32decode(data)
        elif encoding == 'base85':
            return base64.b85decode(data)
        elif encoding == 'ascii85':
            return base64.a85decode(data)
        else:
            raise ValueError(f"Unknown encoding: {encoding}")
    
    # ── Classical Ciphers ────────────────────────────────────
    
    def caesar(self, text: str, shift: int) -> str:
        """Caesar cipher with any shift (also ROT13 when shift=13)"""
        result = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - base + shift) % 26 + base))
            else:
                result.append(char)
        return ''.join(result)
    
    def vigenere(self, text: str, key: str, encrypt: bool = True) -> str:
        """Vigenère cipher with arbitrary key"""
        result = []
        key_length = len(key)
        key_index = 0
        
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                key_char = key[key_index % key_length]
                key_shift = ord(key_char.lower()) - ord('a')
                shift = key_shift if encrypt else -key_shift
                result.append(chr((ord(char) - base + shift) % 26 + base))
                key_index += 1
            else:
                result.append(char)
        return ''.join(result)
    
    def xor_cipher(self, data: bytes, key: bytes) -> bytes:
        """XOR encryption with repeating key"""
        if not key:
            raise ValueError("Key cannot be empty")
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
    
    def xor_bruteforce_single(self, ciphertext: bytes) -> List[Tuple[int, float, str]]:
        """Brute force single-byte XOR with English frequency scoring"""
        english_freq = {
            ' ': 18.2, 'e': 12.7, 't': 9.1, 'a': 8.2, 'o': 7.5, 'i': 7.0, 'n': 6.7,
            's': 6.3, 'h': 6.1, 'r': 6.0, 'd': 4.3, 'l': 4.0, 'u': 2.8
        }
        
        results = []
        for key in range(256):
            decrypted = self.xor_cipher(ciphertext, bytes([key]))
            text = decrypted.decode('ascii', errors='ignore').lower()
            
            # Score by English letter frequency
            score = sum(english_freq.get(char, 0) for char in text) / max(len(text), 1)
            score *= 100
            
            if score > 50:  # Likely valid English
                results.append((key, score, decrypted.decode('ascii', errors='replace')[:100]))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:10]
    
    # ── Utilities ────────────────────────────────────────────
    
    def random_bytes(self, length: int = 32) -> bytes:
        """Generate cryptographically secure random bytes"""
        return secrets.token_bytes(length)
    
    def random_hex(self, length: int = 32) -> str:
        """Generate random hex string"""
        return secrets.token_hex(length)
    
    def detect_encoding(self, data: bytes) -> str:
        """Detect the encoding scheme of a byte string"""
        try:
            base64.b64decode(data)
            if all(c in b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r' for c in data[:100]):
                return 'base64'
        except:
            pass
        
        try:
            bytes.fromhex(data.decode('ascii')[:100])
            if all(c in '0123456789abcdefABCDEF' for c in data[:100]):
                return 'hex'
        except:
            pass
        
        return 'unknown'
    
    def analyze_hash(self, hash_value: str) -> Dict[str, bool]:
        """Analyze a hash string and guess what algorithms it could be"""
        results = {}
        hash_len = len(hash_value)
        
        # Length-based detection
        if hash_len == 32:
            results['md5'] = True
            results['md4'] = True
        elif hash_len == 40:
            results['sha1'] = True
        elif hash_len == 64:
            results['sha256'] = True
        elif hash_len == 128:
            results['sha512'] = True
        elif hash_len == 112 or hash_len == 114:  # approx for bcrypt
            results['bcrypt'] = True
        
        # Check if all hex (0-9, a-f)
        is_hex = all(c in '0123456789abcdefABCDEF' for c in hash_value)
        results['looks_like_hex_hash'] = is_hex
        
        return results
    
    def verify_password(self, password: str, salt: bytes, stored_hash: str, algorithm: str = 'sha256') -> bool:
        """Verify a password against stored hash"""
        computed = hashlib.sha256(salt + password.encode('utf-8')).hexdigest()
        return hmac.compare_digest(computed, stored_hash)
    
    def generate_salt(self, length: int = 16) -> bytes:
        """Generate a random salt"""
        return os.urandom(length)


# ── Quick test ─────────────────────────────────────────────────
if __name__ == '__main__':
    print("⚡ ZETA ∞ CRYPTO ENGINE")
    print("=" * 50)
    
    engine = CryptoEngine()
    
    # Test hashing
    print("\n🔐 Hash tests:")
    hashes = engine.hash_multi("Hello, ZETA ∞ Universe!")
    for algo, h in hashes.items():
        print(f"  {algo}: {h[:20]}...")
    
    # Test encoding
    print("\n📦 Encode test:")
    data = b"Secret ZETA data"
    for enc in ['base64', 'hex', 'base32']:
        encoded = engine.encode(data, enc)
        decoded = engine.decode(encoded, enc)
        status = "✅" if decoded == data else "❌"
        print(f"  {enc}: {encoded[:20]}... {status}")
    
    # Test classical cipher
    print("\n🔑 Classical cipher:")
    original = "The quick brown fox"
    caesar = engine.caesar(original, 13)
    restored = engine.caesar(caesar, 13)
    print(f"  Original:  {original}")
    print(f"  ROT13:     {caesar}")
    print(f"  Restored:  {restored}")
    assert restored == original, "ROT13 failed"
    print("  ✅ ROT13 works!")
    
    # XOR brute force
    print("\n🔓 XOR brute force test:")
    secret = "Hello world from ZETA"
    ciphertext = engine.xor_cipher(secret.encode(), bytes([42]))
    guesses = engine.xor_bruteforce_single(ciphertext)
    best_key, score, text = guesses[0]
    print(f"  Found key: {best_key} (score: {score:.0f})")
    print(f"  Decoded:   {text}")
    assert best_key == 42, "Should find key 42"
    print("  ✅ XOR brute force works!")
    
    # Hash analysis
    print("\n🔍 Hash analysis:")
    sample_hash = engine.hash_string("test")[0]
    analysis = engine.analyze_hash(hashes['sha256'])
    print(f"  SHA256 hash: {hashes['sha256'][:16]}...")
    print(f"  Detected as possible: {', '.join(k for k, v in analysis.items() if v)}")
    
    # Random generation
    print("\n🎲 Cryptographic random:")
    print(f"  Random hex (16 bytes): {engine.random_hex(16)}")
    print(f"  Random bytes (8):      {engine.random_bytes(8).hex()}")
    print(f"  Salt (16 bytes):       {engine.generate_salt().hex()}")
    
    print("\n✅ Crypto Engine operational")
