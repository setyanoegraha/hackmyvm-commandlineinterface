import httpx
import keyring
import os
import json
from rich.console import Console
from keyring.errors import NoKeyringError

console = Console()

class AuthManager:
    def __init__(self):
        self.app_name = "hmv-cli"
        self.config_dir = os.path.expanduser("~/.hmv")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def save_credentials(self, username, password):
        try:
            with open(self.config_file, "w") as f:
                json.dump({"username": username}, f)
            
            keyring.set_password(self.app_name, username, password)
            console.print("[bold green][✓][/bold green] Configuration saved successfully!")
            
        except NoKeyringError:
            console.print("[bold red][!][/bold red] Error: Keyring storage system not found.")
            console.print("[yellow][*][/yellow] Linux users, please use the following commands:")
            console.print("\n    [bold cyan]If using pipx:[/bold cyan]")
            console.print("    [white]pipx inject hmv keyrings.alt[/white]")
            console.print("\n    [bold cyan]If using uv:[/bold cyan]")
            console.print("    [white]uv tool install --with keyrings.alt git+https://github.com/setyanoegraha/hackmyvm-commandlineinterface.git[/white]")
            
        except Exception as e:
            console.print(f"[bold red][!][/bold red] Failed to save configuration to system vault.")
            console.print(f"[dim]Error Detail: {e}[/dim]")

    async def get_session(self):
        if not os.path.exists(self.config_file):
            console.print("[bold red][!][/bold red] Configuration not found. Run '[cyan]hmv config[/cyan]' first.")
            return None
        
        try:
            with open(self.config_file, "r") as f:
                username = json.load(f).get("username")
            
            password = keyring.get_password(self.app_name, username)
        except NoKeyringError:
            console.print("[bold red][!][/bold red] Keyring backend not found.")
            console.print("[yellow][*][/yellow] Run: [white]pipx inject hmv keyrings.alt[/white]")
            return None
        except Exception as e:
            console.print(f"[bold red][!][/bold red] Error while accessing vault: {e}")
            return None

        if not password:
            console.print("[bold red][!][/bold red] Password not found. Please run '[cyan]hmv config[/cyan]' again.")
            return None

        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36 HMV-CLI/0.1.2"
        )

        timeout = httpx.Timeout(60.0, connect=15.0)
        client = httpx.AsyncClient(
            base_url="https://hackmyvm.eu", 
            follow_redirects=True, 
            timeout=timeout,
            headers={"User-Agent": user_agent}
        )
        
        try:
            resp = await client.post("/login/auth.php", data={
                "admin": username, 
                "password_usuario": password
            })
            
            if "Logout" in resp.text:
                return client
            
            console.print("[bold red][!][/bold red] Authentication failed. Please check your username and password.")
            await client.aclose()
            return None
        except Exception as e:
            console.print(f"[bold red][!][/bold red] Connection error: {e}")
            await client.aclose()
            return None