import discord
import asyncio
from datetime import datetime
from colorama import Fore, Style

def load_tokens(filename="tokens.txt"):
    with open(filename, "r") as file:
        tokens = [line.strip() for line in file.readlines() if line.strip()]
    return tokens

def log_info(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.GREEN}[INFO] [{timestamp}] {Style.RESET_ALL}{message}")

def log_warning(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.YELLOW}[WARNING] [{timestamp}] {Style.RESET_ALL}{message}")

def log_error(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.RED}[ERROR] [{timestamp}] {Style.RESET_ALL}{message}")

async def validate_token(token):
    client = discord.Client(self_bot=True)
    try:
        await client.login(token)
        await client.close()
        log_info(f"Validated token ending in {token[-4:]}")
        return True
    except discord.errors.LoginFailure:
        log_error(f"Invalid token: {token[-4:]}")
        return False

ALLOWED_USER_IDS = [642321844170653729, 1196731325193928724]
TRIGGER_MESSAGE = "..."

async def on_message_handler(client, message):
    if message.author.id not in ALLOWED_USER_IDS:
        return

    if message.content.startswith("!repeat"):
        try:
            parts = message.content.split(maxsplit=3)

            if len(parts) < 3:
                repeat_mode = 0
                repeat_count = int(parts[1])
                repeat_string = parts[2]
            elif len(parts) == 4:
                repeat_mode = int(parts[1])
                repeat_count = int(parts[2])
                repeat_string = parts[3]
            else:
                raise ValueError("Wrong format. Use `!repeat [0/1] n string`.")

            guild = message.guild

            if repeat_mode == 1:
                text_channels = [
                    channel for channel in guild.text_channels
                    if channel.permissions_for(guild.me).send_messages
                ]

                if not text_channels:
                    await message.channel.send("No accessible text channels found!")
                    return

                log_info(f"Executing command '!repeat {repeat_mode} {repeat_count} {repeat_string}' in guild '{guild.name}'")

                for channel in text_channels:
                    for _ in range(repeat_count):
                        await channel.send(repeat_string)
                        log_info(f"Message sent in channel '{channel.name}'")
                        await asyncio.sleep(1)

            else:
                log_info(f"Executing command '!repeat {repeat_mode} {repeat_count} {repeat_string}' in channel '{message.channel.name}'")

                for _ in range(repeat_count):
                    await message.channel.send(repeat_string)
                    log_info(f"Message sent in channel '{message.channel.name}'")
                    await asyncio.sleep(1)

        except ValueError as e:
            log_error(str(e))
            await message.channel.send(f"Error: {str(e)}")
        except discord.errors.HTTPException as e:
            log_error(f"HTTP error: {str(e)}")
            await message.channel.send("An error occurred while sending messages. Please try again later.")

async def create_client(token):
    client = discord.Client(self_bot=True)

    @client.event
    async def on_ready():
        log_info(f"[{client.user}] Logged in as {client.user} (ID: {client.user.id}) with token ending in {token[-4:]}")

    @client.event
    async def on_message(message):
        await on_message_handler(client, message)

    try:
        await client.start(token)
    except Exception as e:
        log_error(f"Unexpected error occurred: {e}")

async def main():
    tokens = load_tokens("tokens.txt")

    valid_tokens = []
    for token in tokens:
        if await validate_token(token):
            valid_tokens.append(token)

    if not valid_tokens:
        log_error("No valid tokens found. Exiting...")
        return

    tasks = [create_client(token) for token in valid_tokens]
    await asyncio.gather(*tasks)

asyncio.run(main())
