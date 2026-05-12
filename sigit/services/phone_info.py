from typing import ClassVar, Dict

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.client import AsyncClient


class PhoneInfo(BaseService):

    name: ClassVar[str] = "PhoneInfo"
    description: ClassVar[str] = "Phone number → Country, Carrier, Type"
    category: ClassVar[Category] = Category.RECON
    input_type: ClassVar[InputType] = InputType.PHONE
    input_label: ClassVar[str] = "enter phone number"

    API_KEY: ClassVar[str] = "5F2D6300E445DEA88684053144996C"

    async def execute(self, target: str) -> ServiceResult:
        data = await self.lookup(target)
        if data:
            return ServiceResult.ok(data, result_type=ResultType.KEY_VALUE)
        return ServiceResult.fail("Could not retrieve phone info")

    # -- legacy static API --

    @staticmethod
    async def lookup(phone: str) -> Dict:
        url = f"https://api.veriphone.io/v2/verify?phone={phone}&key={PhoneInfo.API_KEY}"
        async with AsyncClient() as client:
            _, data = await client.get_json(url)
            return data if isinstance(data, dict) else {}