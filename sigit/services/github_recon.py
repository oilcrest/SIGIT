from typing import ClassVar, Dict, List, Any

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.client import AsyncClient


class GitHubRecon(BaseService):

    name: ClassVar[str] = "GitHubRecon"
    description: ClassVar[str] = "GitHub user info + 5 latest repos"
    category: ClassVar[Category] = Category.SOCIAL
    input_type: ClassVar[InputType] = InputType.USERNAME
    input_label: ClassVar[str] = "enter github username"

    # Fields to extract from user profile
    _USER_FIELDS: ClassVar[List[str]] = [
        'name', 'bio', 'location', 'email', 'company',
        'followers', 'following', 'public_repos',
    ]

    async def execute(self, target: str) -> ServiceResult:
        raw = await self.recon(target)
        if not raw:
            return ServiceResult.fail("User not found or error")

        # Build clean output — no raw JSON
        clean: Dict[str, Any] = {}
        for field in self._USER_FIELDS:
            value = raw.get(field)
            clean[field] = value if value is not None else "N/A"

        # Format repos as readable strings instead of raw dicts
        repos: List[Dict[str, Any]] = raw.get('recent_repos', [])
        if repos:
            formatted_repos: List[str] = []
            for repo in repos:
                name = repo.get('name', '?')
                desc = repo.get('description') or 'No description'
                stars = repo.get('stargazers_count', 0)
                lang = repo.get('language') or '-'
                formatted_repos.append(
                    f"★{stars}  {name} [{lang}] — {desc[:60]}"
                )
            clean['recent_repos'] = formatted_repos

        return ServiceResult.ok(clean, result_type=ResultType.KEY_VALUE)

    # -- legacy static API --

    @staticmethod
    async def recon(username: str) -> Dict:
        async with AsyncClient() as client:
            _, user = await client.get_json(
                f"https://api.github.com/users/{username}"
            )
            if 'message' in user:
                return {}
            _, repos = await client.get_json(
                f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
            )
            user['recent_repos'] = repos[:5] if isinstance(repos, list) else []
            return user