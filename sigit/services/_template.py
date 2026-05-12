"""
Template for creating a new SIGIT service.

Instructions:
  1. Copy this file to  sigit/services/your_tool_name.py
  2. Rename the class and fill in the metadata
  3. Implement the execute() method
  4. Done! The registry picks it up automatically.
"""

from typing import ClassVar, Dict

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.client import AsyncClient


class MyNewTool(BaseService):
    """One-line description of what this tool does."""

    # ---- metadata (required) ----
    name: ClassVar[str] = "MyNewTool"
    description: ClassVar[str] = "Short description for the menu"
    category: ClassVar[Category] = Category.RECON          # pick from Category enum
    input_type: ClassVar[InputType] = InputType.DOMAIN     # pick from InputType enum
    input_label: ClassVar[str] = "enter domain"           # CLI prompt text

    async def execute(self, target: str) -> ServiceResult:
        """Run the tool against *target* and return a ServiceResult.

        Return types you can use:
          - ServiceResult.ok(dict_data, result_type=ResultType.KEY_VALUE)
          - ServiceResult.ok(list_of_dicts, result_type=ResultType.TABLE)
          - ServiceResult.ok(list_of_strings, result_type=ResultType.LIST)
          - ServiceResult.ok(raw_string, result_type=ResultType.TEXT)
          - ServiceResult.ok(scored_dict, result_type=ResultType.SCORED)
          - ServiceResult.fail("error message")
        """
        async with AsyncClient() as client:
            status, data = await client.get_json(f"https://api.example.com/{target}")

            if status == 200 and isinstance(data, dict):
                return ServiceResult.ok(data, result_type=ResultType.KEY_VALUE)

            return ServiceResult.fail("Could not retrieve data")
