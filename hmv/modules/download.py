import httpx
import os
import asyncio
import time
import tempfile
import glob
from rich.prompt import Confirm

if not hasattr(asyncio, "coroutine"):
    def coroutine_dummy(f):
        return f
    setattr(asyncio, "coroutine", coroutine_dummy) # type: ignore

from mega import Mega
from rich.console import Console
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)

console = Console()

class DownloadManager:
    def __init__(self, client: httpx.AsyncClient):
        """
        Initialize the Download Manager.
        """
        self.client = client
        self.mega = Mega()

    async def download_vm(self, vm_name: str):
        """
        Download a VM machine with an accurate progress bar and robust error handling
        for both Windows and Linux.
        """
        hmv_url = f"https://downloads.hackmyvm.eu/{vm_name.lower()}.zip"

        mega_url = ""
        with console.status(f"[bold yellow][*][/bold yellow] Resolving download link for {vm_name}..."):
            try:
                response = await self.client.get(hmv_url, follow_redirects=True)
                mega_url = str(response.url)
                if "mega.nz" not in mega_url:
                    console.print(f"[bold red][!][/bold red] Error: Valid MEGA link not found.")
                    return
            except Exception as e:
                console.print(f"[bold red][!][/bold red] URL resolution failed: {e}")
                return

        console.print(f"[bold blue][*][/bold blue] Resolved Link: [cyan]{mega_url}[/cyan]")

        try:
            with console.status("[bold blue][*][/bold blue] Fetching file metadata..."):
                info = self.mega.get_public_url_info(mega_url)
                if info:
                    total_size = info.get('size', 0)
                    file_name = info.get('name', f"{vm_name}.zip").replace("/", "").replace("\\", "")
                else:
                    total_size = 0
                    file_name = f"{vm_name}.zip"
        except Exception:
            total_size = 0
            file_name = f"{vm_name}.zip"

        if os.path.exists(file_name):
            console.print(f"[bold red][!][/bold red] Error: File '[white]{file_name}[/white]' already exists.")
            return

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            transient=True 
        )

        original_temp = tempfile.tempdir
        tempfile.tempdir = os.getcwd()
        
        start_time = time.time()

        try:
            with progress:
                task_id = progress.add_task(f"Initializing {vm_name}...", total=total_size or None)

                download_task = asyncio.to_thread(
                    self.mega.download_url, 
                    mega_url, 
                    dest_path=".", 
                    dest_filename=file_name
                )
                actual_coro = asyncio.create_task(download_task)
                
                while not actual_coro.done():
                    try:
                        current_bytes = 0

                        local_temps = glob.glob("megapy_*")
                        local_dot_get = f"{file_name}.get"
                        
                        if os.path.exists(local_dot_get):
                            current_bytes = os.path.getsize(local_dot_get)
                        
                        if current_bytes == 0 and local_temps:
                            for f_path in local_temps:
                                try:
                                    if os.path.getmtime(f_path) >= (start_time - 1):
                                        with open(f_path, 'ab') as f:
                                            current_bytes = f.tell()
                                        break
                                except:
                                    continue

                        if current_bytes > 0:
                            progress.update(
                                task_id, 
                                description=f"Downloading {vm_name}",
                                completed=min(current_bytes, total_size) if total_size else current_bytes
                            )
                        
                        await asyncio.sleep(0.5)

                    except (KeyboardInterrupt, asyncio.CancelledError):
                        progress.stop()
                        console.print("\n")
                        if Confirm.ask("[bold red][?][/bold red] Interruption detected. Abort download?"):
                            console.print("[bold red][!][/bold red] Aborted by user.")
                            for f in glob.glob("megapy_*"):
                                try: os.remove(f)
                                except: pass
                            os._exit(0)
                        else:
                            console.print("[bold green][*][/bold green] Resuming...")
                            progress.start()
                
                try:
                    await actual_coro
                except Exception as e:
                    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
                        pass
                    else:
                        raise e
                
                if total_size:
                    progress.update(task_id, completed=total_size)

            console.print(f"[bold green][✓][/bold green] Successfully downloaded: [white]{file_name}[/white]")

        except Exception as e:
            console.print(f"[bold red][!][/bold red] Download failed: {e}")
        finally:
            tempfile.tempdir = original_temp
            time.sleep(0.5)
            for f in glob.glob("megapy_*"):
                if f != file_name:
                    try: os.remove(f)
                    except: pass