import httpx
from rich.console import Console

console = Console()

class FlagManager:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def submit(self, vm: str, flag: str):
        """Submit a flag for a specific VM and handle various server responses."""
        data = {"vm": vm, "flag": flag}
        try:
            resp = await self.client.post("/machines/checkflag.php", data=data)
            msg = resp.text.lower()

            if "correct" in msg:
                console.print(f"[bold green][✓] Correct![/bold green] You hacked {vm}!")

            elif "wrong" in msg:
                console.print("[bold red][!][/bold red] Wrong flag. Try harder!")

            elif "<link" in msg or "stylesheet" in msg or "<html" in msg:
                console.print(f"[bold red][!][/bold red] Error: Machine '[bold white]{vm}[/bold white]' was not found.")
                console.print("[yellow][*][/yellow] Please check the VM name spelling.")

            else:
                clean_resp = resp.text.strip()
                console.print(f"[bold yellow][?][/bold yellow] Unknown server response: {clean_resp}")
                
        except Exception as e:
            console.print(f"[bold red][!][/bold red] Error submitting flag: {e}")