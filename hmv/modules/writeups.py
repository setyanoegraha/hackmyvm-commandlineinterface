from selectolax.lexbor import LexborHTMLParser
import httpx
from rich.console import Console
from rich.table import Table

console = Console()

class WriteupManager:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def get_writeups(self, vm_name: str):
        """
        Fetch and display community writeups for a specific VM.
        Parses the table structure containing Date, Author (Poet), Link, and Language.
        """
        url = f"/machines/machine.php?vm={vm_name}"
        
        try:
            with console.status(f"[bold yellow][*][/bold yellow] Fetching writeup list for {vm_name}..."):
                resp = await self.client.get(url)
                
                if resp.status_code != 200:
                    console.print(f"[bold red][!][/bold red] Error: Server returned status {resp.status_code}")
                    return

                if "machine not found" in resp.text.lower():
                    console.print(f"[bold red][!][/bold red] Error: Machine '[white]{vm_name}[/white]' not found.")
                    return

                parser = LexborHTMLParser(resp.text)

                writeups = []
                for row in parser.css("table.table-striped tbody tr"):
                    date_node = row.css_first("th[scope='row']")
                    date_val = date_node.text(strip=True) if date_node else "N/A"

                    author_node = row.css_first("a.creator")
                    author_name = author_node.text(strip=True) if author_node else "Unknown"

                    link_node = row.css_first("a.download")
                    lang_node = row.css_first("span.size")
                    
                    if link_node:
                        href = str(link_node.attributes.get("href") or "")
                        format_val = link_node.text(strip=True).replace("!", "")
                        language = lang_node.text(strip=True) if lang_node else "Unknown"
                        
                        writeups.append({
                            "date": date_val,
                            "author": author_name,
                            "language": language,
                            "format": format_val,
                            "url": href
                        })

                if not writeups:
                    console.print(f"[bold yellow][!][/bold yellow] No community writeups found for [white]{vm_name}[/white].")
                    return

                table = Table(
                    title=f"Community Writeups: {vm_name}", 
                    title_style="bold magenta", 
                    header_style="bold cyan",
                    box=None,
                    padding=(0, 2)
                )
                
                table.add_column("Date", style="dim")
                table.add_column("Author (Poet)", style="bold white")
                table.add_column("Language", justify="center")
                table.add_column("Format", justify="center")
                table.add_column("Link", style="blue")

                for w in writeups:
                    lang_color = "green" if "English" in w['language'] else "yellow"
 
                    format_color = "cyan" if "Read" in w['format'] else "magenta"
                    
                    table.add_row(
                        w['date'],
                        w['author'],
                        f"[{lang_color}]{w['language']}[/{lang_color}]",
                        f"[{format_color}]{w['format'].upper()}[/{format_color}]",
                        w['url']
                    )

                console.print(table)

        except httpx.RequestError as e:
            console.print(f"[bold red][!][/bold red] Network error while fetching writeups: {e}")
        except Exception as e:
            console.print(f"[bold red][!][/bold red] An unexpected error occurred: {e}")