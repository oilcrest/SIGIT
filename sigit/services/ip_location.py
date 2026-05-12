from typing import ClassVar, Dict, Any

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.client import AsyncClient


class IPLocation(BaseService):

    name: ClassVar[str] = "IPLocation"
    description: ClassVar[str] = "IP → Location, ISP, GPS Coordinates"
    category: ClassVar[Category] = Category.NETWORK
    input_type: ClassVar[InputType] = InputType.IP
    input_label: ClassVar[str] = "enter IP Address"

    # Only show these fields from the API response
    _DISPLAY_FIELDS: ClassVar[Dict[str, str]] = {
        'ip': 'IP Address',
        'hostname': 'Hostname',
        'city': 'City',
        'region': 'Region',
        'country': 'Country',
        'loc': 'Coordinates',
        'org': 'Organization',
        'postal': 'Postal Code',
        'timezone': 'Timezone',
    }

    async def execute(self, target: str) -> ServiceResult:
        raw = await self.lookup(target)
        if not raw or 'bogon' in raw:
            return ServiceResult.fail("Could not retrieve IP info (bogon or invalid)")

        # Build clean output with readable labels
        clean: Dict[str, Any] = {}
        for key, label in self._DISPLAY_FIELDS.items():
            if key in raw and raw[key]:
                clean[label] = raw[key]

        if clean:
            return ServiceResult.ok(clean, result_type=ResultType.KEY_VALUE)
        return ServiceResult.fail("No location data available for this IP")

    # -- legacy static API --

    @staticmethod
    async def lookup(ip: str) -> Dict[str, str]:
        async with AsyncClient() as client:
            _, data = await client.get_json(f"https://ipinfo.io/{ip}/json")
            return data if isinstance(data, dict) else {}