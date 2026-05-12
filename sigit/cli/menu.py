"""Registry-driven interactive CLI menu for SIGIT.

The menu is built dynamically from the :class:`ServiceRegistry`.
Adding a new service to ``sigit/services/`` is enough — no edits needed here.
"""

import sys
from typing import List, Type

from ..core.base import BaseService
from ..core.registry import ServiceRegistry
from ..core.colors import Colors
from ..core.config import config
from .display import (
    clear, LOGO, separator, print_header, input_prompt,
    render_result, ask_save_results,
)

c = Colors()


class Menu:

    @staticmethod
    def _services() -> List[Type[BaseService]]:
        """Return ordered list of registered services."""
        return ServiceRegistry.ordered()

    @staticmethod
    def show() -> None:
        clear()
        print(LOGO)
        services = Menu._services()
        
        from itertools import groupby
        sorted_svcs = sorted(services, key=lambda x: x.category.value)
        
        print()        
        idx = 1
        for cat, group in groupby(sorted_svcs, key=lambda x: x.category.value):
            # Print category header
            print(f"{config.SPACE}{c.BLUE}● {c.RESET}{c.BOLD}{cat.upper()}{c.RESET}")
            
            for svc in group:
                # Print service with nice numbering and description
                print(f"{config.SPACE}  {c.BLUE}{idx:02d}.{c.RESET} {svc.name:<18} {c.DIM}{svc.description}{c.RESET}")
                idx += 1
            print() # Spacer between categories
        
        # Exit option
        print(f"{config.SPACE}  {c.BLUE}{idx:02d}.{c.RESET} {'Exit Tool':<20} {c.DIM}{'Close application':<30}{c.RESET}")
        print()

    @staticmethod
    async def run() -> None:
        while True:
            try:
                services = Menu._services()
                exit_num = len(services) + 1
                
                cmd = input(f"{config.SPACE}{c.BLUE}┌──({c.RESET}sigit{c.BLUE})─[{c.RESET}menu{c.BLUE}]\n{config.SPACE}└─➤ {c.RESET}").strip().lower()

                if cmd in ("exit", "quit", str(exit_num)):
                    print(f"\n{config.SPACE}{c.BLUE}* {c.RESET}Goodbye!")
                    break

                try:
                    choice = int(cmd)
                except ValueError:
                    if cmd: print(f"{config.SPACE}{c.RED}* Invalid option{c.RESET}")
                    continue

                if 1 <= choice <= len(services):
                    # Find service by index (they were sorted by category in show())
                    sorted_svcs = sorted(services, key=lambda x: x.category.value)
                    await Menu._run_service(sorted_svcs[choice-1])
                elif choice == exit_num:
                    break
                else:
                    print(f"{config.SPACE}{c.RED}* Choice out of range{c.RESET}")

            except (KeyboardInterrupt, EOFError):
                print(f"\n\n{config.SPACE}{c.BLUE}* {c.RESET}Exiting SIGIT... Goodbye!")
                sys.exit(0)

    @staticmethod
    async def _run_service(svc_cls: Type[BaseService]) -> None:
        """Generic handler with progress bar and interrupt support."""
        try:
            target = input_prompt(svc_cls.input_label)
            if not target:
                return

            print_header(svc_cls.name.upper())

            from .display import show_progress
            import asyncio

            # Create the progress bar
            pbar = show_progress(f"Running {svc_cls.name}")
            
            # Execute tool in background
            svc = svc_cls()
            task = asyncio.create_task(svc.execute(target))
            
            # Update bar while waiting
            try:
                while not task.done():
                    pbar.update(5)
                    if pbar.n >= 95: pbar.n = 95 # stay at 95 until done
                    pbar.refresh()
                    await asyncio.sleep(0.2)
                
                pbar.n = 100
                pbar.refresh()
                pbar.close()
                
                result = await task
                render_result(result)
            except asyncio.CancelledError:
                task.cancel()
                pbar.close()
                print(f"\n{config.SPACE}{c.RED}* Task cancelled{c.RESET}")
                return

            separator()
            default_file = f"result_{svc_cls.name.lower()}.txt"
            ask_save_results(result, default_file)
            input(f"\n{config.SPACE}{c.DIM}Press Enter to return to menu...{c.RESET}")
            Menu.show()

        except KeyboardInterrupt:
            print(f"\n\n{config.SPACE}{c.YELLOW}! {c.RESET}Operation aborted by user")
            Menu.show()