"""
ZETA ∞ NETWORK ENGINE — Protocol Analysis & Network Operations
The nervous system that maps and manipulates networks.

Features:
  - Port scanning
  - Protocol analysis
  - HTTP/HTTPS operations
  - Socket-level networking
  - DNS resolution & manipulation
  - Packet crafting
  - Connection analysis

Dependencies: scapy, requests, socket, struct, hashlib (all available)
"""

import socket, struct, hashlib, ipaddress, time, os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class NetworkEngine:
    """Network analysis, scanning, and protocol engineering engine"""
    
    def __init__(self):
        self.open_ports = []
        self.protocols = {
            1: 'ICMP',
            6: 'TCP',
            17: 'UDP',
            47: 'GRE',
            50: 'ESP',
            51: 'AH',
            89: 'OSPF',
            132: 'SCTP',
        }
        
        self.common_ports = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
            80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
            993: 'IMAPS', 995: 'POP3S', 3306: 'MySQL', 5432: 'PostgreSQL',
            6379: 'Redis', 8080: 'HTTP-Proxy', 27017: 'MongoDB',
            9200: 'Elasticsearch', 8443: 'HTTPS-Alt', 3000: 'Dev-Server',
        }
    
    # ── Port Scanning ────────────────────────────────────────
    
    def scan_port(self, host: str, port: int, timeout: float = 1.0) -> Dict[str, Any]:
        """Scan a single port on a host"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            
            if result == 0:
                # Try to get banner if it's a known service
                try:
                    sock.send(b'\r\n')
                    banner = sock.recv(100).decode('utf-8', errors='ignore').strip()
                except:
                    banner = None
                
                return {
                    'port': port,
                    'state': 'open',
                    'service': self.common_ports.get(port, 'unknown'),
                    'response_time': None,  # Already connected
                    'banner': banner,
                }
            else:
                return {
                    'port': port,
                    'state': 'closed' if result == 111 else 'filtered',
                    'service': self.common_ports.get(port, 'unknown'),
                }
        except Exception as e:
            return {
                'port': port,
                'state': 'error',
                'error': str(e),
            }
        finally:
            sock.close()
    
    def scan_ports(self, host: str, ports: list = None, timeout: float = 1.0) -> List[Dict]:
        """Scan multiple ports (sequential for safety)"""
        if ports is None:
            ports = list(range(1, 1025))  # Common range
        
        results = []
        for port in ports:
            result = self.scan_port(host, port, timeout)
            if result['state'] == 'open':
                results.append(result)
        
        return results
    
    def scan_well_known(self, host: str, timeout: float = 1.0) -> List[Dict]:
        """Scan only well-known service ports"""
        return self.scan_ports(host, list(self.common_ports.keys()), timeout)
    
    # ── Network Analysis ─────────────────────────────────────
    
    def resolve_ip(self, hostname: str) -> Dict:
        """Resolve hostname to IP and gather network info"""
        try:
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)
            
            return {
                'hostname': hostname,
                'ip': ip,
                'ip_type': 'public' if not ip_obj.is_private else 'private',
                'is_loopback': ip_obj.is_loopback,
                'is_multicast': ip_obj.is_multicast,
                'is_link_local': ip_obj.is_link_local,
                'ip_version': ip_obj.version,
            }
        except Exception as e:
            return {'error': str(e)}
    
    def resolve_reverse(self, ip: str) -> Dict:
        """Reverse DNS lookup"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return {'ip': ip, 'hostname': hostname}
        except Exception as e:
            return {'ip': ip, 'error': str(e)}
    
    def fingerprint_service(self, host: str, port: int) -> Dict:
        """Identify a service by connecting and sending probes"""
        probes = {
            b'GET / HTTP/1.0\r\nHost: ' + host.encode() + b'\r\n\r\n': 'HTTP',
            b'\x00': 'Generic',
        }
        
        for probe, expected_protocol in probes.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect((host, port))
                sock.send(probe)
                response = sock.recv(512).decode('utf-8', errors='ignore')
                sock.close()
                
                if response:
                    fingerprint = self._analyze_response(response)
                    return {
                        'host': host,
                        'port': port,
                        'protocol': expected_protocol,
                        'fingerprint': fingerprint,
                        'response_sample': response[:100],
                    }
            except:
                continue
        
        return {'host': host, 'port': port, 'status': 'unreachable'}
    
    def _analyze_response(self, response: str) -> str:
        """Analyze a protocol response to identify the service"""
        response_lower = response.lower()
        
        if 'http/' in response_lower:
            if 'apache' in response_lower:
                return 'Apache'
            if 'nginx' in response_lower:
                return 'Nginx'
            if 'iis' in response_lower:
                return 'Microsoft-IIS'
            return 'HTTPServer'
        elif 'smtp' in response_lower or 'mail' in response_lower:
            return 'SMTP'
        elif 'ftp' in response_lower:
            return 'FTP'
        elif 'ssh' in response_lower:
            return 'SSH'
        elif 'redis' in response_lower:
            return 'Redis'
        
        return f"Unknown ({response[:50]})"
    
    # ── Connection Utils ─────────────────────────────────────
    
    def check_connectivity(self, targets: list = None) -> Dict:
        """Check outbound connectivity to common services"""
        if targets is None:
            targets = [
                ('dns.google.com', 53, 'DNS'),
                ('one.one.one.one', 53, 'DNS-Cloudflare'),
                ('8.8.8.8', 53, 'DNS-Google'),
                ('github.com', 443, 'GitHub'),
                ('google.com', 80, 'HTTP'),
            ]
        
        results = {}
        for host, port, name in targets:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3.0)
                start = time.time()
                sock.connect((host, port))
                elapsed = time.time() - start
                sock.close()
                results[name] = {'reachable': True, 'latency_ms': round(elapsed * 1000, 2)}
            except Exception as e:
                results[name] = {'reachable': False, 'error': str(e)}
        
        return results
    
    # ── IP Utilities ─────────────────────────────────────────
    
    def ip_to_int(self, ip: str) -> int:
        """Convert IP address to integer"""
        return struct.unpack('!I', socket.inet_aton(ip))[0]
    
    def int_to_ip(self, n: int) -> str:
        """Convert integer to IP address"""
        return socket.inet_ntoa(struct.pack('!I', n))
    
    def network_range(self, cidr: str) -> List[str]:
        """Expand a CIDR notation to all IPs in the range"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            return [str(ip) for ip in network.hosts()]
        except Exception as e:
            return [str(e)]
    
    def whois_lookup(self, domain: str) -> Dict:
        """Basic domain information via DNS"""
        import subprocess
        try:
            # Use dig if available, else nslookup
            result = subprocess.run(
                ['dig', '+short', domain],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return {'domain': domain, 'records': result.stdout.strip()}
        except:
            pass
        
        return {'domain': domain, 'status': 'whois not available'}
    
    def list_interfaces(self) -> Dict:
        """List network interfaces and their addresses"""
        interfaces = {}
        
        try:
            # Read from /proc/net/fib_trie (Linux)
            with open('/proc/net/if_inet6', 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 6:
                        iface = parts[-1]
                        ipv6 = ':'.join([parts[0][i:i+4] for i in range(0, 32, 4)])
                        if iface not in interfaces:
                            interfaces[iface] = {'ipv6': []}
                        interfaces[iface]['ipv6'].append(f"{ipv6}/{parts[3]}")
        except:
            pass
        
        # Get hostname
        try:
            interfaces['hostname'] = socket.gethostname()
        except:
            interfaces['hostname'] = 'unknown'
        
        # Local IPs via getaddrinfo
        try:
            local_ips = socket.getaddrinfo(socket.gethostname(), None)
            interfaces['local_ips'] = list(set(ip[4][0] for ip in local_ips))
        except:
            interfaces['local_ips'] = []
        
        return interfaces


# ── Quick test ─────────────────────────────────────────────────
if __name__ == '__main__':
    print("⚡ ZETA ∞ NETWORK ENGINE")
    print("=" * 50)
    
    engine = NetworkEngine()
    
    # Test: Connectivity
    print("\n🌐 Connectivity check:")
    conn = engine.check_connectivity()
    for name, info in conn.items():
        if info.get('reachable'):
            print(f"  ✅ {name}: {info['latency_ms']}ms")
        else:
            print(f"  ❌ {name}: {info.get('error', 'unreachable')}")
    
    # Test: DNS resolution
    print("\n🔍 DNS resolution:")
    result = engine.resolve_ip('localhost')
    print(f"  localhost → {result.get('ip', 'error')} ({result.get('ip_type', '?')})")
    
    # Test: IP utilities
    print("\n🔢 IP utilities:")
    ip_int = engine.ip_to_int('192.168.1.1')
    ip_back = engine.int_to_ip(ip_int)
    print(f"  192.168.1.1 → {ip_int} → {ip_back}")
    assert ip_back == '192.168.1.1', "IP conversion failed"
    print("  ✅ IP conversion works!")
    
    # Test: Network range
    print("\n📡 Network expansion:")
    range_24 = engine.network_range('192.168.1.0/30')
    print(f"  192.168.1.0/30 → {range_24}")
    
    # Test: Interface detection
    print("\n🖧 Network interfaces:")
    ifaces = engine.list_interfaces()
    print(f"  Hostname: {ifaces.get('hostname')}")
    print(f"  Local IPs: {ifaces.get('local_ips', [])[:5]}")
    
    print("\n✅ Network Engine operational")
