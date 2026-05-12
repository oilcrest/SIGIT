from typing import ClassVar, Dict, List, Any

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.client import AsyncClient


class DataBreachChecker(BaseService):

    name: ClassVar[str] = "BreachChecker"
    description: ClassVar[str] = "Check email in data breaches"
    category: ClassVar[Category] = Category.SECURITY
    input_type: ClassVar[InputType] = InputType.EMAIL
    input_label: ClassVar[str] = "enter email"

    async def execute(self, target: str) -> ServiceResult:
        data = await self.check(target)
        
        if not data:
            return ServiceResult.ok(
                {"status": "No breaches found"}, result_type=ResultType.KEY_VALUE,
            )

        # Build clean output
        clean: Dict[str, Any] = {
            "email": target,
            "status": "Success",
        }

        breaches = data.get('breaches', [])
        if breaches:
            # Flatten if nested and ensure strings
            flat_breaches = []
            if isinstance(breaches, list):
                for b in breaches:
                    if isinstance(b, list):
                        flat_breaches.extend([str(i) for i in b])
                    else:
                        flat_breaches.append(str(b))
            
            clean["breaches"] = flat_breaches
            return ServiceResult.ok(clean, result_type=ResultType.KEY_VALUE)

        return ServiceResult.ok(
            {"status": "No breaches found"}, result_type=ResultType.KEY_VALUE,
        )

    # -- legacy static API --

    @staticmethod
    async def check(email: str) -> Dict:
        async with AsyncClient() as client:
            # xposedornot API v1
            status, data = await client.get_json(
                f"https://api.xposedornot.com/v1/check-email/{email}"
            )
            return data if status == 200 and isinstance(data, dict) else {}