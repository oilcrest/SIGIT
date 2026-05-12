import os

from pathlib import Path
from typing import Any, Dict, List

from ..core.colors import Colors
from ..core.config import config
from ..core.base import ResultType, ServiceResult

from tqdm import tqdm
import time
import asyncio

c = Colors()

# Logo
LOGO = f"""{c.BLUE}
                    _cyqyc_
                :>3qKKKKKKKq3>:
            ';CpKKKKKKKKKKKKKKKKKpC;'
        -"iPKKKKKKKKKKKKKKKKKKKKKKKPi"-
    `~v]KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK]v~`
,rwKKKKKKKKKKKKKPv;,:'-':,;vPKKKKKKKKKKKKKwr,
!KKKKKKKKKKKKKKK/             !KKKKKKKKKKKKKKK!
!KKKKKKKKKKKKKKf               CKKKKKKKKKKKKKK!
!KKKKKKKKKKKKKp-               -qKKKKKKKKKKKKK!
!KKKKKKKKKKKKK>"               "\\KKKKKKKKKKKKK!
!KKKKKKKw;,_'-                   .-:,"wKKKKKKK!
!KKKKKKKKhi*;"                   ";*ihKKKKKKKK!
!KKKKKKKKKKKKK;                 ;KKKKKKKKKKKKK!
!KKKKKKKKKKKKK2>'             '>2KKKKKKKKKKKKK!
!KKKKKKKKKKKKKKKZ             ZKKKKKKKKKKKKKKK!
!KKKKKKKKKKKKKKK5             eKKKKKKKKKKKKKKK!
!KKKKKKKKKKKqC;-               -;CqKKKKKKKKKKK!
<KKKKKKKKkr,                       ,rSKKKKKKKK<
-"v]qj;-                             -;jq]v"-
                {c.RESET}[ S.I.G.I.T ]{c.BLUE}
    {c.DIM}Simple Information Gathering Toolkit{c.RESET}
        {c.DIM}Author by {c.RESET}{c.RED}@termuxhackers.id{c.RESET}"""


def clear() -> None:
    os.system('clear' if os.name == 'posix' else 'cls')


def separator() -> None:
    print(f"{c.RESET}{config.SPACE}" + "-" * 44)


def print_user_result(result: dict) -> None:
    """Cleaner user reconnaissance result."""
    status_color = result.get('color', c.RESET)
    status_text = result.get('status', '???')
    print(f"{config.SPACE}{c.BLUE}  ▸ {c.RESET}{result['url']:<40} {c.BLUE}[{status_color}{status_text}{c.BLUE}]{c.RESET}")


def save_results(data: list | dict | str, filename: str) -> None:
    """Write data to file."""
    if isinstance(data, list):
        text = "\n".join(map(str, data))
    elif isinstance(data, dict):
        lines = []
        for k, v in data.items():
            if isinstance(v, list):
                for item in v:
                    lines.append(f"{k}: {item}")
            else:
                lines.append(f"{k}: {v}")
        text = "\n".join(lines)
    else:
        text = str(data)
    Path(filename).write_text(text)
    print(f"{config.SPACE}{c.BLUE}> {c.RESET}Results saved to: {c.YELLOW}{filename}{c.RESET}")


def ask_save_results(result: 'ServiceResult', default_name: str) -> None:
    """Ask the user whether to save results to a file."""
    if not result.success or result.data is None:
        return
    try:
        ans = input(
            f"{config.SPACE}{c.BLUE}> {c.RESET}Save results? "
            f"{c.DIM}(y/n){c.RESET} "
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return
    if ans in ('y', 'yes'):
        filename = result.save_filename or default_name
        save_results(result.data, filename)


def print_header(title: str) -> None:
    """Print a minimalist professional header."""
    print(f"\n{config.SPACE}{c.BLUE}─── {c.RESET}{c.BOLD}{title.upper()}{c.BLUE} ───{c.RESET}")


def print_found(count: int, item: str = "results") -> None:
    """Professional summary line."""
    print(f"\n{config.SPACE}{c.BLUE}➤ {c.RESET}Total: {c.YELLOW}{count}{c.RESET} {item}")


def show_progress(text: str = "Processing"):
    """Simple indeterminate progress bar for tools."""
    return tqdm(
        total=100,
        desc=f"{config.SPACE}{c.BLUE}{text}{c.RESET}",
        bar_format="{desc}: {percentage:3.0f}%|{bar}|",
        ncols=60,
        leave=False
    )


def input_prompt(prompt: str) -> str:
    """Professional input prompt."""
    try:
        return input(f"{config.SPACE}{c.BLUE}┌──({c.RESET}sigit{c.BLUE})─[{c.RESET}{prompt}{c.BLUE}]\n{config.SPACE}└─➤ {c.RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return ""


# ---------------------------------------------------------------------------
# Generic result renderer (registry-driven)
# ---------------------------------------------------------------------------

def render_result(result: ServiceResult) -> None:
    """Render a :class:`ServiceResult` to the terminal based on its type."""
    if not result.success:
        print(f"{config.SPACE}{c.RED}* {result.error}{c.RESET}")
        return

    data = result.data

    if result.result_type == ResultType.KEY_VALUE:
        _render_key_value(data)
    elif result.result_type == ResultType.TABLE:
        _render_table(data)
    elif result.result_type == ResultType.LIST:
        _render_list(data)
    elif result.result_type == ResultType.TEXT:
        _render_text(data)
    elif result.result_type == ResultType.SCORED:
        _render_scored(data)

    # Saving is now handled by ask_save_results() in the menu


def _render_key_value(data: Dict[str, Any]) -> None:
    for key, value in data.items():
        if isinstance(value, list):
            label = key.replace('_', ' ').title()
            print(f"{config.SPACE}{c.BLUE}  ▸ {c.RESET}{label:15}:")
            for item in value:
                print(f"{config.SPACE}    {c.BLUE}◦ {c.RESET}{item}")
        elif isinstance(value, dict):
            print(f"{config.SPACE}{c.BLUE}{key}:{c.RESET}")
            for k2, v2 in value.items():
                print(f"{config.SPACE}  {c.DIM}{k2}:{c.RESET} {v2}")
        else:
            label = key.replace('_', ' ').title()
            print(f"{config.SPACE}{c.BLUE}  ▸ {c.RESET}{label:15}: {c.YELLOW}{value}{c.RESET}")


def _render_table(data: List[Dict[str, Any]]) -> None:
    for row in data:
        if 'color' in row and 'status' in row and 'url' in row:
            # UserRecon-style result
            print_user_result(row)
        elif 'port' in row:
            # PortScanner-style result
            print(f"{config.SPACE}{c.BG_GREEN} OPEN {c.RESET} "
                  f"Port {c.YELLOW}{row['port']}{c.RESET} - {row.get('service', '')}")
        else:
            parts = " | ".join(f"{k}: {v}" for k, v in row.items())
            print(f"{config.SPACE}{c.BLUE}-{c.RESET} {parts}")
    print_found(len(data))


def _render_list(data: List[str]) -> None:
    for item in data:
        print(f"{config.SPACE}{c.BLUE}  ▸ {c.RESET}{item}")
    print_found(len(data))


def _render_text(data: str) -> None:
    for line in data.split('\n')[:30]:
        if line.strip():
            print(f"{config.SPACE}{c.DIM}{line}{c.RESET}")


def _render_scored(data: Dict[str, Any]) -> None:
    score = data.get('score', 0)
    total = data.get('total', 0)
    pct = data.get('percentage', 0)
    print(f"{config.SPACE}{c.BLUE}Security Score:{c.RESET} {score}/{total} ({pct:.0f}%)")
    if pct >= 80:
        print(f"{config.SPACE}{c.GREEN}Excellent security posture!{c.RESET}")
    elif pct >= 50:
        print(f"{config.SPACE}{c.YELLOW}Moderate security{c.RESET}")
    else:
        print(f"{config.SPACE}{c.RED}Poor security - needs improvement{c.RESET}")