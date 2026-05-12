from typing import ClassVar, List

import socket

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.client import AsyncClient


class ReverseIPLookup(BaseService):

    name: ClassVar[str] = "ReverseIP"
    description: ClassVar[str] = "Other domains on the same IP"
    category: ClassVar[Category] = Category.NETWORK
    input_type: ClassVar[InputType] = InputType.DOMAIN
    input_label: ClassVar[str] = "enter domain"

    async def execute(self, target: str) -> ServiceResult:
        domains = await self.lookup(target)
        if domains:
            return ServiceResult.ok(
                domains, result_type=ResultType.LIST,
                save_filename="result_reverseip.txt",
            )
        return ServiceResult.fail("No domains found")

    # -- legacy static API --

    @staticmethod
    async def lookup(domain: str) -> List[str]:
        try:
            ip = socket.gethostbyname(domain)
            async with AsyncClient() as client:
                status, data = await client.get(
                    f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
                )
                if status == 200:
                    return [
                        d for d in data.strip().split('\n')
                        if d and 'error' not in d.lower()
                    ]
        except Exception:
            pass
        return []