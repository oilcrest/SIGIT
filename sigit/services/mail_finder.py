from concurrent.futures import ThreadPoolExecutor
from typing import ClassVar, List

import requests

from ..core.base import BaseService, Category, InputType, ResultType, ServiceResult
from ..core.config import config


class MailFinder(BaseService):

    name: ClassVar[str] = "MailFinder"
    description: ClassVar[str] = "Generate & validate emails from full name"
    category: ClassVar[Category] = Category.EMAIL
    input_type: ClassVar[InputType] = InputType.NAME
    input_label: ClassVar[str] = "enter full name"

    DOMAINS: ClassVar[List[str]] = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
        "protonmail.com", "icloud.com", "aol.com", "mail.com",
        "zoho.com", "gmx.com", "yandex.com", "tutanota.com"
    ]
    API_KEY: ClassVar[str] = "0c6ad1fd-f753-4628-8c0a-7968e722c6c7"

    async def execute(self, target: str) -> ServiceResult:
        emails = await self.find_emails(target.lower())
        if emails:
            return ServiceResult.ok(
                emails, result_type=ResultType.LIST,
                save_filename="result_mailfinder.txt",
            )
        return ServiceResult.fail("No valid emails found")

    # -- legacy static API --

    @staticmethod
    def generate_candidates(fullname: str) -> List[str]:
        names = fullname.lower().split()
        patterns = [
            fullname.replace(" ", ""),
            fullname.replace(" ", "."),
            fullname.replace(" ", "_"),
            f"{names[0]}.{names[-1]}" if len(names) > 1 else names[0],
            f"{names[0]}{names[-1]}" if len(names) > 1 else names[0],
        ]
        return list(set(patterns))

    @staticmethod
    async def find_emails(fullname: str) -> List[str]:
        candidates = MailFinder.generate_candidates(fullname)
        valid_emails: List[str] = []

        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            futures = []
            for cand in candidates:
                for domain in MailFinder.DOMAINS:
                    email = f"{cand}@{domain}"
                    futures.append((executor.submit(MailFinder._validate, email), email))

            for future, email in futures:
                try:
                    if future.result(timeout=config.TIMEOUT):
                        valid_emails.append(email)
                except Exception:
                    pass
        return valid_emails

    @staticmethod
    def _validate(email: str) -> bool:
        try:
            resp = requests.get(
                "https://isitarealemail.com/api/email/validate",
                params={'email': email},
                headers={'Authorization': f"Bearer {MailFinder.API_KEY}"},
                timeout=config.TIMEOUT
            )
            return resp.json().get('status') == 'valid'
        except Exception:
            return False