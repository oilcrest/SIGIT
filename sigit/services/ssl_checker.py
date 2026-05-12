import ssl
import socket
import certifi

from typing import ClassVar, Dict
from datetime import datetime

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult


class SSLChecker(BaseService):

    name: ClassVar[str] = "SSLChecker"
    description: ClassVar[str] = "SSL/TLS certificate analysis (expiry, issuer)"
    category: ClassVar[Category] = Category.SECURITY
    input_type: ClassVar[InputType] = InputType.DOMAIN
    input_label: ClassVar[str] = "enter domain"

    async def execute(self, target: str) -> ServiceResult:
        # strip protocol if user pastes a URL
        domain = target.split('/')[0].replace('http://', '').replace('https://', '')
        data = await self.check(domain)
        if data:
            return ServiceResult.ok(data, result_type=ResultType.KEY_VALUE)
        return ServiceResult.fail("Failed to retrieve certificate")

    # -- legacy static API --

    @staticmethod
    async def check(domain: str) -> Dict:
        try:
            context = ssl.create_default_context(cafile=certifi.where())
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    subject = dict(x[0] for x in cert.get('subject', []))  # type: ignore
                    issuer = dict(x[0] for x in cert.get('issuer', []))  # type: ignore
                    return {
                        'subject': subject,
                        'issuer': issuer,
                        'not_before': cert.get('notBefore'),  # type: ignore
                        'not_after': cert.get('notAfter'),  # type: ignore
                        'expired': datetime.strptime(
                            cert.get('notAfter'), '%b %d %H:%M:%S %Y %Z'  # type: ignore
                        ) < datetime.now()
                    }
        except Exception:
            return {}