# HMV-CLI 

### HackMyVM Advanced Versatile Operations CLI Toolkit

**HMV-CLI** is a modern command-line toolkit designed specifically for the HackMyVM community. It allows you to search for machines, download VMs, submit flags, and view community writeups efficiently directly from your terminal with fast performance and an intuitive interface.

---

## Key Features

*  **Secure Auth**: Securely stores your credentials using the system vault (Windows Credentials Manager/macOS Keychain) via the `keyring` library.
*  **Machine Management**:
    * Smart paginated machine listing.
    * Instant machine search by name.
    * Filters for difficulty (beginner, intermediate, advanced) or OS (linux/windows).
    * Global "Pwned" status synchronization to track your progress.
*  **High-Speed Downloader**: Downloads VMs directly from MEGA with accurate progress bars and robust error handling.
*  **Flag Submission**: Submit flags from the terminal with clear visual feedback.
*  **Writeups Access**: View community writeups (articles or videos) without opening a browser.

---

## Prerequisites

* Python 3.11 or newer.
* An active account on [HackMyVM](https://hackmyvm.eu/).
* **OS**: Windows, Linux, or macOS.

---

## Installation

I highly recommend using `pipx` or `uv` to keep the tool isolated and prevent dependency conflicts with other Python projects.

### 1. Using pipx (Recommended)
```bash
pipx install git+https://github.com/setyanoegraha/hackmyvm-commandlineinterface.git
```

### 2. Using uv (Fastest)
```bash
uv tool install git+https://github.com/setyanoegraha/hackmyvm-commandlineinterface.git
```

### 3. Manual Installation (Developer Mode)
```bash
git clone https://github.com/setyanoegraha/hackmyvm-commandlineinterface.git
cd hackmyvm-commandlineinterface
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -e .
```
---

## Initial Configuration
After installation, you must run the configuration command to save your account:
```bash
hmv config
```

**NOTE:** Your password is encrypted by the operating system and is not stored in plain text.

---

## Usage Guide

### General Commands

| Command | Function |
| :--- | :--- |
| `hmv --help` | Show help menu and banner. |
| `hmv machine -l` | Show the latest 20 machines from HackMyVM. |
| `hmv machine -a` | Show the entire machine catalog in one large table. |
| `hmv machine -n <name>` | Search for machines by name (e.g., `hmv machine -n hunter`). |
| `hmv machine -s <filter>` | Sorting / Filtering the machines by some category (e.g., `hmv machine -s beginner`). |
| `hmv machine -d <name>` | Download for machine by name (e.g., `hmv machine -d victorique`). |
| `hmv machine -v <name> -f <flag>` | Submit flag for some machine (e.g, `hmv machine -v fuzzz -f flag{abc}`). |
| `hmv machine -v <name> -w` | See write-up for machine from community (e.g., `hmv machine -v skid -w`). |

### VM Interaction

* **Download VM:** 
    ```bash
    hmv machine -d <vm_name>
    ```
* **View Writeups:** 
    ```bash
    hmv machine -v <vm_name> -w
    ```
* **Submit Flag:** 
    ```bash
    hmv machine -v <vm_name> -f <flag_token>
    ```

### Show All Machine based on Filtering & Sorting

* **By OS:** `hmv machine -s linux -a`
* **By Difficulty:** `hmv machine -s beginner -a`
* **By Size:** `hmv machine -s size -a`

### Updating

Get the latest features with a single command:

```bash
# If installed via pipx
pipx upgrade hmv

# If installed via uv
uv tool upgrade hmv
```

### Uninstallation & Cleanup

Removing the tool:
```bash
# If installed via pipx
pipx uninstall hmv

# If installed via uv
uv tool uninstall hmv

# If installed via pip
pip uninstall hmv
```

Cleaning up Remaining Data

HMV stores cache and configuration in the `~/.hmv/` directory. Delete this folder to clear all local data:
- Windows: `$HOME\.hmv\`
- Linux/macOS: `~/.hmv`

---

## Official Links

- Website: [hackmyvm.eu](https://hackmyvm.eu)
- Discord: [Official HackMyVM](https://discord.com/invite/DxDFQrJ)

## Acknowledgements

A massive thanks and maximum respect to the HackMyVM community, the staff, and all the machine creators. This toolkit exists because of the incredible platform and community you've built for cybersecurity enthusiasts to learn, share, and grow.

---

Made with ❤️ by [Ouba](https://github.com/setyanoegraha).

*Happy Hacking on HackMyVM!*