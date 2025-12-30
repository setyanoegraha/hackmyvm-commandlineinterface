import httpx
import keyring
import os
import json
from rich.console import Console

console = Console()

class AuthManager:
    def __init__(self):
        self.app_name = "hmv-cli-pro"
        self.config_dir = os.path.expanduser("~/.hmv")
        self.config_file = os.path.join(self.config_dir, "config.json")

        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def save_credentials(self, username, password):
        """Save username to file and password to system keychain."""
        with open(self.config_file, "w") as f:
            json.dump({"username": username}, f)

        keyring.set_password(self.app_name, username, password)
        console.print("[bold green][+][/bold green] Credentials saved successfully to system vault!")

    async def get_session(self):
        """Establish and return an authenticated HTTPX session."""
        if not os.path.exists(self.config_file):
            console.print("[bold red][!][/bold red] Configuration missing. Please run 'hmv config' first.")
            return None
        
        with open(self.config_file, "r") as f:
            username = json.load(f).get("username")

        password = keyring.get_password(self.app_name, username)

        timeout = httpx.Timeout(60.0, connect=15.0)
        client = httpx.AsyncClient(
            base_url="https://hackmyvm.eu", 
            follow_redirects=True, 
            timeout=timeout,
            headers={"User-Agent": "HMV-CLI-Pro/0.1.0"}
        )
        
        try:
            resp = await client.post("/login/auth.php", data={
                "admin": username, 
                "password_usuario": password
            })
            
            if "Logout" in resp.text:
                return client
            
            console.print("[bold red][!][/bold red] Authentication failed. Check your credentials.")
            await client.aclose()
            return None
        except httpx.TimeoutException:
            console.print("[bold red][!][/bold red] Authentication timed out. The server is being slow.")
            await client.aclose()
            return None
        except Exception as e:
            console.print(f"[bold red][!][/bold red] Connection error during auth: {e}")
            await client.aclose()
            return None