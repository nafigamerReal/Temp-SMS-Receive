‎#!/usr/bin/env python3
‎# -*- coding: utf-8 -*-
‎
‎"""
‎Temp SMS Receiver
‎By Nafi Gamer DC-nafigamer
‎"""
‎
‎import os
‎import sys
‎import asyncio
‎import random
‎import base64
‎import subprocess  # Added missing import
‎from typing import Dict, List, Tuple, Optional, Any
‎from dataclasses import dataclass
‎from enum import Enum, auto
‎from pathlib import Path
‎
‎try:
‎    import requests
‎    from Crypto.Cipher import AES
‎    from Crypto.Util.Padding import unpad
‎    import colorama
‎    import pyfiglet
‎    import pyperclip
‎    from aiohttp import ClientSession
‎    from rich.console import Console
‎    from rich.panel import Panel
‎    from rich.progress import Progress
‎    from rich.table import Table
‎    from rich.style import Style
‎except ImportError as e:
‎    print(f"Missing dependencies: {e}")
‎    if input("Install dependencies? (y/n): ").lower() == 'y':
‎        try:
‎            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
‎            print("Dependencies installed successfully. Please run the program again.")
‎        except subprocess.CalledProcessError:
‎            print("Failed to install dependencies. Please install them manually.")
‎    sys.exit(1)
‎
‎# Initialize colorama
‎colorama.init(autoreset=True)
‎
‎# Constants
‎CLEAR = "cls" if os.name == "nt" else "clear"
‎BASE_URL = "https://api-1.online"
‎AES_KEY = "9e8986a75ffa32aa187b7f34394c70ea".encode()
‎HEADERS = {
‎    "accept-encoding": "gzip",
‎    "user-agent": "okhttp/4.9.2"
‎}
‎
‎# Rich console setup
‎console = Console()
‎
‎# Color definitions using rich Styles
‎class Color:
‎    BLUE = Style(color="blue", bold=True)
‎    CYAN = Style(color="cyan", bold=True)
‎    GREEN = Style(color="green", bold=True)
‎    YELLOW = Style(color="yellow", bold=True)
‎    RED = Style(color="red", bold=True)
‎    MAGENTA = Style(color="magenta", bold=True)
‎    LIGHT_YELLOW = Style(color="yellow3", bold=True)
‎    LIGHT_RED = Style(color="red3", bold=True)
‎    LIGHT_MAGENTA = Style(color="magenta3", bold=True)
‎    LIGHT_BLUE = Style(color="blue3", bold=True)
‎    LIGHT_CYAN = Style(color="cyan3", bold=True)
‎    LIGHT_GREEN = Style(color="green3", bold=True)
‎    BOLD = Style(bold=True)
‎
‎    @classmethod
‎    def random(cls) -> Style:
‎        colors = [
‎            cls.BLUE, cls.CYAN, cls.GREEN, cls.YELLOW, cls.RED, cls.MAGENTA,
‎            cls.LIGHT_YELLOW, cls.LIGHT_RED, cls.LIGHT_MAGENTA,
‎            cls.LIGHT_BLUE, cls.LIGHT_CYAN, cls.LIGHT_GREEN
‎        ]
‎        return random.choice(colors)
‎
‎# Font options
‎FONTS = (
‎    "basic", "o8", "cosmic", "graffiti", "chunky", 
‎    "epic", "doom", "avatar"
‎)
‎
‎@dataclass
‎class Country:
‎    code: str
‎    name: str
‎
‎@dataclass
‎class PhoneNumber:
‎    e164: str
‎    time: str
‎    country: str
‎
‎@dataclass
‎class SMSMessage:
‎    from_number: str
‎    body: str
‎    time: str
‎
‎class ClipboardResult(Enum):
‎    SUCCESS = auto()
‎    TERMUX_API_NOT_INSTALLED = auto()
‎    TERMUX_APP_NOT_INSTALLED = auto()
‎    UNKNOWN_ENVIRONMENT = auto()
‎
‎def clear_screen() -> None:
‎    """Clear the terminal screen."""
‎    os.system(CLEAR)
‎
‎def print_centered(text: str, color: Style = Color.BOLD) -> None:
‎    """Print centered text with optional color."""
‎    console.print(text.center(os.get_terminal_size().columns), style=color)
‎
‎def print_warning(message: str) -> None:
‎    """Print a warning message."""
‎    print_centered(f"[!] {message}", Color.RED)
‎
‎def print_success(message: str) -> None:
‎    """Print a success message."""
‎    print_centered(f"[+] {message}", Color.GREEN)
‎
‎def print_info(message: str) -> None:
‎    """Print an informational message."""
‎    print_centered(f"[*] {message}", Color.BLUE)
‎
‎def show_logo() -> None:
‎    """Display the program logo."""
‎    clear_screen()
‎    color1 = Color.random()
‎    color2 = Color.random()
‎    while color1 == color2:
‎        color2 = Color.random()
‎    
‎    # Create a rich panel for the logo
‎    logo_text = pyfiglet.figlet_format(
‎        "Temp\nSMS",
‎        font=random.choice(FONTS),
‎        justify="center",
‎        width=os.get_terminal_size().columns,
‎    )
‎    
‎    panel = Panel(
‎        logo_text,
‎        title="[bold]Temporary SMS Receiver",
‎        subtitle="By Nafi Gamer",
‎        border_style=color1,
‎        title_align="center",
‎        width=os.get_terminal_size().columns - 4
‎    )
‎    
‎    console.print(panel)
‎
‎async def fetch_auth_key(session: ClientSession) -> str:
‎    """Fetch the encrypted API key."""
‎    url = f"{BASE_URL}/post/"
‎    params = {"action": "get_encrypted_api_key", "type": "user"}
‎    json_data = {"api": "111"}
‎    
‎    async with session.post(url, params=params, headers=HEADERS, json=json_data) as response:
‎        response.raise_for_status()
‎        data = await response.json()
‎        return data["api_key"]
‎
‎def decrypt_key(encrypted_str: str) -> str:
‎    """Decrypt the API key using AES."""
‎    decoded = base64.b64decode(encrypted_str)
‎    iv = decoded[:16]
‎    encrypted_data = decoded[16:]
‎    
‎    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
‎    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
‎    return decrypted_data.decode()
‎
‎async def get_auth_key() -> str:
‎    """Get the decrypted auth key."""
‎    async with ClientSession() as session:
‎        encrypted_key = await fetch_auth_key(session)
‎        return decrypt_key(encrypted_key)
‎
‎async def copy_to_clipboard(text: str) -> Tuple[bool, Optional[str]]:
‎    """Copy text to clipboard with fallback methods."""
‎    try:
‎        pyperclip.copy(text)
‎        return True, None
‎    except Exception:
‎        if sys.platform == "linux":
‎            try:
‎                if b"Android" in subprocess.check_output(["uname", "-o"]):
‎                    try:
‎                        result = subprocess.run(
‎                            ["termux-clipboard-set", text],
‎                            stderr=subprocess.DEVNULL,
‎                            stdout=subprocess.DEVNULL,
‎                            timeout=4,
‎                            check=True
‎                        )
‎                        return True, None
‎                    except subprocess.CalledProcessError:
‎                        return False, 'Install termux-api: "pkg install termux-api"'
‎                    except subprocess.TimeoutExpired:
‎                        return False, 'Install Termux-API app from Play Store'
‎                    except FileNotFoundError:
‎                        return False, "Termux clipboard utility not found"
‎            except subprocess.CalledProcessError:
‎                pass
‎        
‎        # Try xclip/xsel as fallback for Linux
‎        for cmd in ["xclip", "xsel"]:
‎            try:
‎                subprocess.run(
‎                    [cmd, "-i"],
‎                    input=text.encode(),
‎                    check=True,
‎                    stdout=subprocess.DEVNULL,
‎                    stderr=subprocess.DEVNULL
‎                )
‎                return True, None
‎            except (subprocess.CalledProcessError, FileNotFoundError):
‎                continue
‎        
‎        return False, "Clipboard access not available"
‎
‎async def fetch_countries(session: ClientSession) -> List[Country]:
‎    """Fetch available countries."""
‎    url = f"{BASE_URL}/get/"
‎    params = {"action": "country"}
‎    
‎    async with session.post(url, params=params, headers=HEADERS) as response:
‎        response.raise_for_status()
‎        data = await response.json()
‎        return [Country(code=item["country_code"], name=item["Country_Name"]) 
‎                for item in data["records"]]
‎
‎async def fetch_numbers(session: ClientSession, country: str, page: int, auth_key: str) -> Dict[str, Any]:
‎    """Fetch available numbers for a country."""
‎    url = f"{BASE_URL}/post/"
‎    params = {"action": "GetFreeNumbers", "type": "user"}
‎    headers = HEADERS.copy()
‎    headers["authorization"] = f"Bearer {auth_key}"
‎    json_data = {"country_name": country, "limit": 10, "page": page}
‎    
‎    async with session.post(url, params=params, headers=headers, json=json_data) as response:
‎        response.raise_for_status()
‎        return await response.json()
‎
‎async def fetch_sms(session: ClientSession, number: str, auth_key: str) -> List[SMSMessage]:
‎    """Fetch SMS messages for a number."""
‎    url = f"{BASE_URL}/post/getFreeMessages"
‎    headers = HEADERS.copy()
‎    headers["authorization"] = f"Bearer {auth_key}"
‎    json_data = {"no": number, "page": "1"}
‎    
‎    async with session.post(url, headers=headers, json=json_data) as response:
‎        response.raise_for_status()
‎        data = await response.json()
‎        return [SMSMessage(
‎            from_number=msg["FromNumber"],
‎            body=msg["Messagebody"],
‎            time=msg["message_time"]
‎        ) for msg in data["messages"]]
‎
‎async def display_sms(number: str, auth_key: str) -> None:
‎    """Display SMS messages for a number."""
‎    async with ClientSession() as session:
‎        messages = await fetch_sms(session, number, auth_key)
‎        
‎        if not messages:
‎            print_warning("No messages found")
‎            return
‎        
‎        table = Table(title=f"SMS Messages for {number}", show_header=True, header_style="bold magenta")
‎        table.add_column("From", style="cyan")
‎        table.add_column("Message", style="green")
‎        table.add_column("Time", style="yellow")
‎        
‎        for msg in messages:
‎            table.add_row(msg.from_number, repr(msg.body), msg.time)
‎        
‎        console.print(table)
‎
‎async def check_update() -> Tuple[bool, str]:
‎    """Check for updates."""
‎    try:
‎        async with ClientSession() as session:
‎            async with session.get(
‎                "https://raw.githubusercontent.com/nafiop122/Temp-SMS-Receive/refs/heads/main/.version"
‎            ) as response:
‎                response.raise_for_status()
‎                latest = (await response.text()).strip()
‎                
‎                version_file = Path(".version")
‎                if version_file.exists():
‎                    current = version_file.read_text().strip()
‎                    return (current != latest, latest)
‎                return (True, latest)
‎    except Exception:
‎        return (False, "0")
‎
‎async def perform_update() -> bool:
‎    """Perform program update."""
‎    if ".git" not in os.listdir():
‎        return False
‎    
‎    try:
‎        # Stash any local changes
‎        subprocess.run(
‎            ["git", "stash"],
‎            check=True,
‎            stdout=subprocess.DEVNULL,
‎            stderr=subprocess.DEVNULL
‎        )
‎        
‎        # Pull latest changes
‎        subprocess.run(
‎            ["git", "pull"],
‎            check=True,
‎            stdout=subprocess.DEVNULL,
‎            stderr=subprocess.DEVNULL
‎        )
‎        return True
‎    except subprocess.CalledProcessError:
‎        return False
‎
‎async def select_country(countries: List[Country]) -> Country:
‎    """Prompt user to select a country."""
‎    while True:
‎        try:
‎            # Display countries in a table
‎            table = Table(title="Available Countries", show_header=True, header_style="bold blue")
‎            table.add_column("No.", style="cyan")
‎            table.add_column("Code", style="green")
‎            table.add_column("Country", style="yellow")
‎            
‎            for idx, country in enumerate(countries, 1):
‎                table.add_row(str(idx), country.code, country.name)
‎            
‎            console.print(table)
‎            
‎            choice = await asyncio.to_thread(
‎                input, 
‎                f"Enter country number (1-{len(countries)}): "
‎            )
‎            
‎            if not choice.isdigit():
‎                print_warning("Please enter a number")
‎                continue
‎                
‎            choice_idx = int(choice) - 1
‎            if 0 <= choice_idx < len(countries):
‎                return countries[choice_idx]
‎            
‎            print_warning("Invalid selection")
‎        except KeyboardInterrupt:
‎            print_info("Returning to main menu...")
‎            raise
‎
‎async def select_number(numbers: List[PhoneNumber]) -> str:
‎    """Prompt user to select a phone number."""
‎    while True:
‎        try:
‎            # Display numbers in a table
‎            table = Table(title="Available Numbers", show_header=True, header_style="bold green")
‎            table.add_column("No.", style="cyan")
‎            table.add_column("Number", style="green")
‎            table.add_column("Time", style="yellow")
‎            
‎            for idx, num in enumerate(numbers, 1):
‎                table.add_row(str(idx), num.e164, num.time)
‎            
‎            console.print(table)
‎            
‎            choice = await asyncio.to_thread(
‎                input, 
‎                f"Enter number (1-{len(numbers)}) or 'R' for random: "
‎            )
‎            
‎            if choice.upper() == "R":
‎                # Weight recent numbers higher (20% of numbers get double weight)
‎                recent_count = max(1, int(len(numbers) * 0.2))
‎                weights = [2] * recent_count + [1] * (len(numbers) - recent_count)
‎                return random.choices(numbers, weights=weights, k=1)[0].e164
‎            
‎            if not choice.isdigit():
‎                print_warning("Please enter a number or 'R'")
‎                continue
‎                
‎            choice_idx = int(choice) - 1
‎            if 0 <= choice_idx < len(numbers):
‎                return numbers[choice_idx].e164
‎            
‎            print_warning("Invalid selection")
‎        except KeyboardInterrupt:
‎            print_info("Returning to country selection...")
‎            raise
‎
‎async def main_flow(auth_key: str) -> None:
‎    """Main program flow."""
‎    while True:
‎        try:
‎            show_logo()
‎            
‎            async with ClientSession() as session:
‎                # Fetch countries with progress indicator
‎                with Progress() as progress:
‎                    task = progress.add_task("[cyan]Loading countries...", total=1)
‎                    countries = await fetch_countries(session)
‎                    progress.update(task, advance=1)
‎                
‎                if not countries:
‎                    print_warning("No countries available")
‎                    await asyncio.sleep(2)
‎                    continue
‎                
‎                # Select country
‎                selected_country = await select_country(countries)
‎                
‎                # Fetch numbers with progress
‎                with Progress() as progress:
‎                    task = progress.add_task(
‎                        f"[green]Loading numbers for {selected_country.name}...",
‎                        total=1
‎                    )
‎                    
‎                    first_page = await fetch_numbers(
‎                        session, selected_country.name, 1, auth_key
‎                    )
‎                    progress.update(task, advance=0.3)
‎                    
‎                    if first_page["Total_Pages"] == 0:
‎                        progress.update(task, advance=1)
‎                        print_warning("No numbers available for this country")
‎                        await asyncio.sleep(2)
‎                        continue
‎                    
‎                    # Process first page
‎                    numbers = [
‎                        PhoneNumber(
‎                            e164=num["E.164"],
‎                            time=num["time"],
‎                            country=selected_country.name
‎                        )
‎                        for num in first_page["Available_numbers"]
‎                    ]
‎                    progress.update(task, advance=0.3)
‎                    
‎                    # Fetch additional pages if needed (but limit to 150 numbers)
‎                    if first_page["Total_Pages"] > 1 and len(numbers) < 150:
‎                        remaining_pages = min(15, first_page["Total_Pages"] - 1)
‎                        for page_num in range(2, 2 + remaining_pages):
‎                            page_data = await fetch_numbers(
‎                                session, selected_country.name, page_num, auth_key
‎                            )
‎                            numbers.extend([
‎                                PhoneNumber(
‎                                    e164=num["E.164"],
‎                                    time=num["time"],
‎                                    country=selected_country.name
‎                                )
‎                                for num in page_data["Available_numbers"]
‎                            ])
‎                            progress.update(task, advance=0.4/remaining_pages)
‎                            
‎                            if len(numbers) >= 150:
‎                                break
‎                    
‎                    progress.update(task, completed=1)
‎                
‎                # Select number
‎                selected_number = await select_number(numbers)
‎                
‎                # Copy to clipboard
‎                success, message = await copy_to_clipboard(selected_number)
‎                if success:
‎                    print_success("Number copied to clipboard!")
‎                else:
‎                    print_warning(f"Clipboard error: {message}")
‎                
‎                # Main SMS viewing loop
‎                while True:
‎                    try:
‎                        await display_sms(selected_number, auth_key)
‎                        
‎                        print_centered(
‎                            "Press Enter to refresh or Ctrl+C to return to main menu",
‎                            Color.LIGHT_CYAN
‎                        )
‎                        
‎                        try:
‎                            await asyncio.to_thread(input)
‎                        except KeyboardInterrupt:
‎                            break
‎                            
‎                    except KeyboardInterrupt:
‎                        break
‎                    except Exception as e:
‎                        print_warning(f"Error fetching messages: {e}")
‎                        await asyncio.sleep(2)
‎                        break
‎        
‎        except KeyboardInterrupt:
‎            print_info("\nReturning to main menu...")
‎            await asyncio.sleep(1)
‎        except Exception as e:
‎            print_warning(f"An error occurred: {e}")
‎            await asyncio.sleep(2)
‎
‎async def main() -> None:
‎    """Entry point."""
‎    try:
‎        # Check for updates
‎        update_available, latest_version = await check_update()
‎        if update_available:
‎            print_warning(f"Update available (version {latest_version})")
‎            print_info("Updating...")
‎            
‎            if await perform_update():
‎                print_success("Update successful! Please restart the program.")
‎            else:
‎                print_warning("Update failed - please update manually")
‎            
‎            return
‎        
‎        # Get auth key
‎        with console.status("[bold green]Authenticating..."):
‎            auth_key = await get_auth_key()
‎        
‎        # Start main flow
‎        await main_flow(auth_key)
‎    
‎    except KeyboardInterrupt:
‎        print_info("\nExiting...")
‎    except Exception as e:
‎        print_warning(f"Fatal error: {e}")
‎        if input("Show traceback? (y/n): ").lower() == 'y':
‎            import traceback
‎            traceback.print_exc()
‎
‎if __name__ == "__main__":
‎    try:
‎        asyncio.run(main())
‎    except KeyboardInterrupt:
‎        os.system('cls' if os.name == 'nt' else 'clear')
‎        subprocess.run([sys.executable, "tempsms.py"])
‎
