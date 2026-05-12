from typing import ClassVar, Dict, List, Any

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.client import AsyncClient


class HeaderAnalyzer(BaseService):

    name: ClassVar[str] = "HeaderAnalyzer"
    description: ClassVar[str] = "Security headers score (HSTS, CSP, XFO)"
    category: ClassVar[Category] = Category.SECURITY
    input_type: ClassVar[InputType] = InputType.URL
    input_label: ClassVar[str] = "enter URL"

    SECURITY_HEADERS: ClassVar[Dict[str, str]] = {
        'Strict-Transport-Security': 'HSTS — prevents downgrade attacks',
        'Content-Security-Policy': 'CSP — prevents XSS & injection',
        'X-Frame-Options': 'Clickjacking Protection',
        'X-Content-Type-Options': 'MIME Sniffing Protection',
        'X-XSS-Protection': 'XSS Filter (legacy browser)',
        'Referrer-Policy': 'Controls referrer information leakage',
        'Permissions-Policy': 'Restricts browser feature access',
    }

    async def execute(self, target: str) -> ServiceResult:
        url = target if target.startswith(('http://', 'https://')) else f'https://{target}'
        data = await self.analyze(url)

        # Build detailed output with per-header status
        result: Dict[str, Any] = {
            'score': f"{data['score']}/{data['total']} ({data['percentage']:.0f}%)",
        }

        # Grade
        pct = data['percentage']
        if pct >= 80:
            result['grade'] = '🟢 Excellent security posture'
        elif pct >= 50:
            result['grade'] = '🟡 Moderate — some headers missing'
        else:
            result['grade'] = '🔴 Poor — needs improvement'

        # Per-header breakdown
        present: List[str] = []
        missing: List[str] = []
        resp_headers = data.get('headers', {})
        for header, explanation in self.SECURITY_HEADERS.items():
            if header in resp_headers:
                present.append(f"✔ {header} — {explanation}")
            else:
                missing.append(f"✘ {header} — {explanation}")

        if present:
            result['present_headers'] = present
        if missing:
            result['missing_headers'] = missing

        # Show interesting server info
        server = resp_headers.get('Server', '')
        if server:
            result['server'] = server

        return ServiceResult.ok(result, result_type=ResultType.KEY_VALUE)

    # -- legacy static API --

    @staticmethod
    async def analyze(url: str) -> Dict:
        async with AsyncClient() as client:
            async with client.session.get(url) as resp:  # type: ignore
                headers = resp.headers
                score = sum(1 for h in HeaderAnalyzer.SECURITY_HEADERS if h in headers)
                return {
                    'headers': dict(headers),
                    'score': score,
                    'total': len(HeaderAnalyzer.SECURITY_HEADERS),
                    'percentage': (score / len(HeaderAnalyzer.SECURITY_HEADERS)) * 100
                }