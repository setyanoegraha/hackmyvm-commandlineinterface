import typer
import asyncio
import inspect
from rich.console import Console

from hmv.modules import (
    AuthManager, 
    MachineScraper, 
    DownloadManager, 
    FlagManager, 
    WriteupManager,
    __version__,     
    __author__,      
    __github_url__   
)

from hmv.constants import get_banner

console = Console()
auth = AuthManager()

app = typer.Typer(
    help="HMV-CLI - HackMyVM Advanced Versatile Operations CLI Toolkit",
    rich_markup_mode="rich",
    no_args_is_help=False,
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]}
)

@app.callback(invoke_without_command=True)
def main_banner(ctx: typer.Context):
    """
    This callback runs before any subcommand executes.
    We handle the banner printing here.
    """
    if ctx.invoked_subcommand != "config":
        banner_text = get_banner(__version__, __author__, __github_url__)
        console.print(banner_text)

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())

@app.command()
def config():
    """
    [bold blue]Configure[/bold blue] your HackMyVM credentials securely.
    """
    try:
        console.print("[bold blue][*][/bold blue] HackMyVM Account Configuration")
        username = typer.prompt("Username")
        password = typer.prompt("Password", hide_input=True)
        auth.save_credentials(username, password)
    except Exception as e:
        console.print(f"[bold red][!][/bold red] Failed to save configuration: {e}")

@app.command(
    epilog=inspect.cleandoc("""
        [bold yellow]Usage Examples:[/bold yellow]

        1. [bold white]List machines[/bold white] (Default first 20):           [cyan]hmv machine -l[/cyan]

        2. [bold white]List specific page[/bold white]:                         [cyan]hmv machine -l -p <number>[/cyan]

        3. [bold white]Display ALL machines[/bold white] in one single table:   [cyan]hmv machine -a[/cyan]

        4. [bold white]Search for a machine by name[/bold white]:               [cyan]hmv machine -n <name>[/cyan]

        5. [bold white]Filter by difficulty or OS[/bold white]:                 [cyan]hmv machine -s <beginner|intermediate|advanced>[/cyan] | [cyan]hmv machine -s <linux|windows> -a[/cyan]

        6. [bold white]Sort all machines by size[/bold white]:                  [cyan]hmv machine -s size -a[/cyan]

        7. [bold white]Download a machine[/bold white]:                         [cyan]hmv machine -d <name>[/cyan]

        8. [bold white]Get community writeups[/bold white]:                     [cyan]hmv machine -v <name> -w[/cyan]

        9. [bold white]Submit a flag[/bold white]:                              [cyan]hmv machine -v <name> -f <flag>[/cyan]
    """)
)
def machine(
    ctx: typer.Context,
    list_machines: bool = typer.Option(
        False, "--list", "-l", 
        help="List machines with pagination (Local pagination if filtered)."
    ),
    all_machines: bool = typer.Option(
        False, "--all", "-a",
        help="Fetch and display ALL machines in a single table."
    ),
    sort: str = typer.Option(
        None, "--sort", "-s", 
        help="Filter: beginner, intermediate, advanced, windows, linux, size, hacked, all."
    ),
    search: str = typer.Option(
        None, "--name", "-n",
        help="Search for a specific machine by name."
    ),
    page: int = typer.Option(
        1, "--page", "-p", 
        help="Page number (Default: 1)."
    ),
    download: str = typer.Option(
        None, "--download", "-d", 
        help="Download a machine by its name."
    ),
    flag: str = typer.Option(
        None, "--flag", "-f", 
        help="Flag token to submit."
    ),
    vm: str = typer.Option(
        None, "--vm", "-v", 
        help="Target VM name (Required for -f and -w)."
    ),
    writeups: bool = typer.Option(
        False, "--writeups", "-w",
        help="Fetch community writeups for a machine (Requires -v)."
    )
):
    """
    [bold green]Manage and interact[/bold green] with HackMyVM machines.
    """
    async def run():
        session = None
        try:
            session = await auth.get_session()
            if not session: return

            if writeups:
                if not vm:
                    console.print("[bold red][!][/bold red] Error: Target VM name (-v) is required to fetch writeups.")
                else:
                    manager = WriteupManager(session)
                    await manager.get_writeups(vm)
                return

            if flag:
                if not vm:
                    console.print("[bold red][!][/bold red] Error: Target VM name (-v) is required.")
                else:
                    manager = FlagManager(session)
                    await manager.submit(vm, flag)
                return

            if vm and not (flag or writeups):
                console.print(f"[bold red][!][/bold red] Error: Target VM '[bold white]{vm}[/bold white]' specified without an action.")
                console.print("[yellow][*][/yellow] Please provide an action: use [cyan]-f <flag>[/cyan] to submit or [cyan]-w[/cyan] to fetch writeups.")
                return

            if download:
                manager = DownloadManager(session)
                await manager.download_vm(download)
                return

            if list_machines or sort or all_machines or search:
                scraper = MachineScraper(session)
                machines_to_show = []
                info_text = ""

                sem = asyncio.Semaphore(3)
                async def scraper_task(p, level):
                    async with sem:
                        return await scraper.get_machines(page=p, level=level)

                is_fetch_all = all_machines or (sort and sort.lower() == "all") or search

                if is_fetch_all:
                    difficulties = ["beginner", "intermediate", "advanced"]
                    categories_needing_all = difficulties + ["all", "size", "linux", "windows"]
                    
                    if search or (sort and sort.lower() in categories_needing_all) or (all_machines and not sort):
                        target_level = "all"
                    else:
                        target_level = sort 
                    
                    status_msg = "Fetching full machine catalog..."
                    if search: status_msg = f"Searching for '{search}'..."
                    
                    with console.status(f"[bold green]{status_msg}"):
                        first_page, pages_info = await scraper.get_machines(page=1, level=target_level)
                        machines_to_show.extend(first_page)
                        try: total_pages = int(pages_info.split("/")[-1])
                        except: total_pages = 1
                        
                        if total_pages > 1:
                            tasks = [scraper_task(p, target_level) for p in range(2, total_pages + 1)]
                            results = await asyncio.gather(*tasks)
                            for p_machines, _ in results:
                                machines_to_show.extend(p_machines)
                        
                        seen_names = set()
                        unique_machines = []
                        for m in machines_to_show:
                            m_key = m['name'].strip().lower()
                            if m_key not in seen_names:
                                unique_machines.append(m)
                                seen_names.add(m_key)
                        machines_to_show = unique_machines

                        if sort:
                            s_low = sort.lower()
                            if s_low in ["linux", "windows"]:
                                machines_to_show = [m for m in machines_to_show if m.get('os') == s_low]
                            elif s_low in difficulties:
                                machines_to_show = [m for m in machines_to_show if m['difficulty'].lower() == s_low]
                            elif s_low == "size":
                                def parse_size(s):
                                    try: return float(s.split()[0])
                                    except: return 0.0
                                machines_to_show.sort(key=lambda x: parse_size(x['size']))

                        if search:
                            machines_to_show = [
                                m for m in machines_to_show 
                                if search.lower() in m['name'].lower()
                            ]
                        
                        info_text = f"Total Found: {len(machines_to_show)}"
                else:
                    with console.status(f"[bold green]Fetching data..."):
                        machines_to_show, pages_info = await scraper.get_machines(page=page, level=sort)
                    
                    if sort and len(machines_to_show) > 20:
                        per_page = 20
                        total_count = len(machines_to_show)
                        total_pages = (total_count + per_page - 1) // per_page
                        start_idx = (page - 1) * per_page
                        end_idx = start_idx + per_page
                        machines_to_show = machines_to_show[start_idx:end_idx]
                        info_text = f"Page {page}/{total_pages}"
                    else:
                        info_text = f"Page {pages_info}"

                if machines_to_show and (not sort or sort.lower() != "hacked"):
                    with console.status("[bold blue]Syncing pwned status..."):
                        h_first_page, h_pages_info = await scraper.get_machines(page=1, level="hacked")
                        all_hacked = list(h_first_page)
                        try: h_total_pages = int(h_pages_info.split("/")[-1])
                        except: h_total_pages = 1
                        if h_total_pages > 1:
                            h_tasks = [scraper_task(p, "hacked") for p in range(2, h_total_pages + 1)]
                            h_results = await asyncio.gather(*h_tasks)
                            for hp_machines, _ in h_results:
                                all_hacked.extend(hp_machines)
                        
                        hacked_map = {m['name'].strip().lower(): m['status'] for m in all_hacked}
                        for m in machines_to_show:
                            m_name_clean = m['name'].strip().lower()
                            if m_name_clean in hacked_map:
                                m['status'] = hacked_map[m_name_clean]

                if not machines_to_show:
                    console.print(f"[bold red][!][/bold red] No machines found matching your criteria.")
                    return

                from rich.table import Table
                title = f"HMV Machines ({info_text})"
                if sort: title += f" | Filter: {sort.upper()}"
                if search: title += f" | Search: '{search}'"
                
                table = Table(title=title, title_style="bold blue", show_header=True, header_style="white")
                table.add_column("VM Name", style="cyan")
                table.add_column("Difficulty", justify="center")
                table.add_column("Creator", style="magenta")
                table.add_column("Size", style="green")
                table.add_column("Status")

                for m in machines_to_show:
                    diff = m['difficulty'].lower()
                    diff_color = "green" if "beginner" in diff else "orange3" if "inter" in diff else "red" if "adv" in diff else "white"
                    raw_status = m['status'].upper()
                    status_color = "bright_green" if any(s in raw_status for s in ["DONE", "PWNED"]) else "yellow"
                    table.add_row(m['name'], f"[{diff_color}]{m['difficulty'].upper()}[/{diff_color}]", m['creator'], m['size'], f"[{status_color}]{raw_status}[/]")
                console.print(table)
            else:
                console.print(ctx.get_help())

        except Exception as e:
            console.print(f"\n[bold red][!][/bold red] An unexpected error occurred: {e}")
        finally:
            if session:
                await session.aclose()

    asyncio.run(run())

def main():
    app()

if __name__ == "__main__":
    main()