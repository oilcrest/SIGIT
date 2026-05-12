import asyncio
from typing import ClassVar, Dict, Any

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult


class WHOISLookup(BaseService):

    name: ClassVar[str] = "WHOISLookup"
    description: ClassVar[str] = "Full domain registration info"
    category: ClassVar[Category] = Category.DOMAIN
    input_type: ClassVar[InputType] = InputType.DOMAIN
    input_label: ClassVar[str] = "enter DOMAIN or IP Address"

    async def execute(self, target: str) -> ServiceResult:
        data = await self.lookup(target)
        if data:
            return ServiceResult.ok(data, result_type=ResultType.TEXT)
        return ServiceResult.fail("Could not retrieve WHOIS data or 'whois' command not found")

    @staticmethod
    async def lookup(domain: str) -> str:
        """Use system 'whois' command via subprocess (Free & Reliable)."""
        try:
            process = await asyncio.create_subprocess_exec(
                'whois', domain,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                output = stdout.decode().strip()
                if output:
                    return output
            return ""
        except Exception:
            return ""