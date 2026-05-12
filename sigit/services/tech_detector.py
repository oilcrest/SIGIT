from typing import ClassVar, Dict, List

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.client import AsyncClient


class TechStackDetector(BaseService):

    name: ClassVar[str] = "TechDetector"
    description: ClassVar[str] = "Detect CMS, Framework, CDN, Analytics"
    category: ClassVar[Category] = Category.RECON
    input_type: ClassVar[InputType] = InputType.URL
    input_label: ClassVar[str] = "enter URL"

    PATTERNS: ClassVar[Dict[str, List[str]]] = {
        'WordPress': ['wp-content', 'wp-includes'],
        'Joomla': ['joomla'], 'Drupal': ['drupal'],
        'React': ['react', '_reactRoot'], 'Vue.js': ['vue', '__vue__'],
        'Angular': ['ng-version', 'angular'], 'Bootstrap': ['bootstrap'],
        'jQuery': ['jquery']
    }

    async def execute(self, target: str) -> ServiceResult:
        url = target if target.startswith(('http://', 'https://')) else f'https://{target}'
        data = await self.detect(url)
        return ServiceResult.ok(data, result_type=ResultType.KEY_VALUE)

    # -- legacy static API --

    @staticmethod
    async def detect(url: str) -> Dict:
        tech: Dict[str, List[str]] = {
            'servers': [], 'frameworks': [], 'analytics': [], 'cdn': [],
        }
        async with AsyncClient() as client:
            status, html = await client.get(url)
            if status != 200:
                return tech
            async with client.session.get(url) as resp:  # type: ignore
                headers = resp.headers
                if 'Server' in headers:
                    tech['servers'].append(headers['Server'])
                html_lower = html.lower()
                for name, kws in TechStackDetector.PATTERNS.items():
                    if any(kw in html_lower for kw in kws):
                        tech['frameworks'].append(name)
                if 'google-analytics' in html_lower or 'gtag' in html_lower:
                    tech['analytics'].append('Google Analytics')
                cdn_map = {'cf-ray': 'Cloudflare', 'x-amz-cf-id': 'AWS CloudFront'}
                for h, name in cdn_map.items():
                    if h in headers:
                        tech['cdn'].append(name)
        return tech