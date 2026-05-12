from typing import ClassVar, List, Optional

import socket
import asyncio

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.client import AsyncClient


class SubdomainScanner(BaseService):

    name: ClassVar[str] = "SubdomainScan"
    description: ClassVar[str] = "Enumerate common subdomains"
    category: ClassVar[Category] = Category.DOMAIN
    input_type: ClassVar[InputType] = InputType.DOMAIN
    input_label: ClassVar[str] = "enter domain"

    COMMON_SUBS: ClassVar[List[str]] = [
        "www", "mail", "ftp", "admin", "blog", "dev", "test", "api",
        "staging", "portal", "m", "mobile", "app", "vpn", "beta",
        "dashboard", "secure", "support", "help", "shop", "store"
    ]

    async def execute(self, target: str) -> ServiceResult:
        subs = await self.scan(target)
        if subs:
            return ServiceResult.ok(
                subs, result_type=ResultType.LIST,
                save_filename="result_subdomains.txt",
            )
        return ServiceResult.fail("No subdomains found")

    # -- legacy static API --

    @staticmethod
    async def scan(domain: str) -> List[str]:
        found: set[str] = set()
        async with AsyncClient() as client:
            tasks = [
                SubdomainScanner._check(client, f"{sub}.{domain}")
                for sub in SubdomainScanner.COMMON_SUBS
            ]
            for coro in asyncio.as_completed(tasks):
                result = await coro
                if result:
                    found.add(result)
        return list(found)

    @staticmethod
    async def _check(client: AsyncClient, sub: str) -> Optional[str]:
        try:
            status, _ = await client.get(f"http://{sub}", allow_redirects=False)
            if status > 0 and status != 404:
                return sub
        except Exception:
            pass
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, socket.gethostbyname, sub,
            )
            return sub
        except Exception:
            return None