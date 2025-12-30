"""
Constants and UI elements for the HMV-CLI toolkit.
"""

BANNER_ART = r"""
[bold cyan]
 ___  ___  _____ ______   ___      ___ 
|\  \|\  \|\   _ \  _   \|\  \    /  /|
\ \  \\\  \ \  \\\__\ \  \ \  \  /  / /
 \ \   __  \ \  \\|__| \  \ \  \/  / / 
  \ \  \ \  \ \  \    \ \  \ \    / /  
   \ \__\ \__\ \__\    \ \__\ \__/ /   
    \|__|\|__|\|__|     \|__|\|__|/    
                                       
                                       
                                       [/bold cyan]"""

def get_banner(version: str, author: str, github: str) -> str:
    """
    Combines the project logo with metadata.
    Provides a high-impact visual presence while remaining efficient 
    for terminal displays.
    """
    return (
        f"{BANNER_ART}\n"
        f"[bold white]   HackMyVM Command Line Interface [/bold white][bold green]v{version}[/bold green]\n"
        f"[dim]   Created by {author} | {github}[/dim]\n"
    )