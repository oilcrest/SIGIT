from typing import ClassVar, Dict, List

import socket
import asyncio

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.client import AsyncClient


class DNSRecon(BaseService):

    name: ClassVar[str] = "DNSRecon"
    description: ClassVar[str] = "A, MX, NS, TXT records via Google DNS"
    category: ClassVar[Category] = Category.DOMAIN
    input_type: ClassVar[InputType] = InputType.DOMAIN
    input_label: ClassVar[str] = "enter domain"

    async def execute(self, target: str) -> ServiceResult:
        data = await self.lookup(target)
        if data:
            return ServiceResult.ok(data, result_type=ResultType.KEY_VALUE)
        return ServiceResult.fail("No DNS records found")

    # -- legacy static API --

    @staticmethod
    async def lookup(domain: str) -> Dict[str, str | List[str]]:
        results: Dict[str, str | List[str]] = {}
        try:
            ip = await asyncio.get_event_loop().run_in_executor(
                None, socket.gethostbyname, domain,
            )
            results['A'] = ip
        except Exception:
            pass

        try:
            async with AsyncClient() as client:
                _, data = await client.get_json(
                    f"https://dns.google/resolve?name={domain}&type=ANY"
                )
                if 'Answer' in data:
                    for rec in data['Answer']:
                        t = rec.get('type')
                        d = rec.get('data', '')
                        if t == 15:
                            results.setdefault('MX', []).append(d)  # type: ignore[union-attr]
                        elif t == 2:
                            results.setdefault('NS', []).append(d)  # type: ignore[union-attr]
                        elif t == 16:
                            results.setdefault('TXT', []).append(d)  # type: ignore[union-attr]
        except Exception:
            pass
        return results