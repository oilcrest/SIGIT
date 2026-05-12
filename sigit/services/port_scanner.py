import socket
from typing import ClassVar, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult


class PortScanner(BaseService):

    name: ClassVar[str] = "PortScanner"
    description: ClassVar[str] = "Scan 17 common network ports"
    category: ClassVar[Category] = Category.NETWORK
    input_type: ClassVar[InputType] = InputType.TARGET
    input_label: ClassVar[str] = "enter DOMAIN or IP Address"

    COMMON_PORTS: ClassVar[Dict[int, str]] = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
        3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
        8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB"
    }

    async def execute(self, target: str) -> ServiceResult:
        results = await self.scan(target)
        if results:
            return ServiceResult.ok(
                results, result_type=ResultType.TABLE,
                save_filename="result_portscan.txt",
            )
        return ServiceResult.fail("No open ports found")

    # -- legacy static API --

    @staticmethod
    async def scan(target: str, ports: Optional[List[int]] = None) -> List[Dict]:
        if ports is None:
            ports = list(PortScanner.COMMON_PORTS.keys())

        results: List[Dict] = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(PortScanner._check, target, p): p for p in ports}
            for future in as_completed(futures):
                res = future.result()
                if res:
                    results.append(res)
        return results

    @staticmethod
    def _check(target: str, port: int) -> Optional[Dict]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(1)
            if sock.connect_ex((target, port)) == 0:
                return {"port": port, "status": "open"}
        except Exception:
            pass
        finally:
            sock.close()
        return None