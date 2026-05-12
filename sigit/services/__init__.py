"""SIGIT Services — auto-discovered via ServiceRegistry.

Usage (recommended)::

    from sigit.core.registry import ServiceRegistry

    for svc_cls in ServiceRegistry.ordered():
        print(svc_cls.name, svc_cls.description)

Individual imports still work for backward compatibility::

    from sigit.services.user_recon import UserRecon
"""

from sigit.core.registry import ServiceRegistry

# Trigger discovery on import
ServiceRegistry.discover()

# Backward-compatible explicit exports
from .user_recon import UserRecon
from .ip_location import IPLocation
from .phone_info import PhoneInfo
from .mail_finder import MailFinder
from .subdomain_scanner import SubdomainScanner
from .port_scanner import PortScanner
from .dns_recon import DNSRecon
from .whois import WHOISLookup
from .ssl_checker import SSLChecker
from .header_analyzer import HeaderAnalyzer
from .github_recon import GitHubRecon
from .breach_checker import DataBreachChecker
from .tech_detector import TechStackDetector
from .reverse_ip import ReverseIPLookup

__all__ = [
    "ServiceRegistry",
    "UserRecon", "IPLocation", "PhoneInfo", "MailFinder",
    "SubdomainScanner", "PortScanner", "DNSRecon", "WHOISLookup",
    "SSLChecker", "HeaderAnalyzer", "GitHubRecon",
    "DataBreachChecker", "TechStackDetector", "ReverseIPLookup",
]