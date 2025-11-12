#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import sys

from pyrogram import Client
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChannelPrivate, PeerIdInvalid
from pyrogram.types import BotCommand

import config

from ..logging import LOGGER


class YukkiBot(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot")
        super().__init__(
            "YukkiMusicBot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        try:
            # Try to send message directly - this is the most reliable check
            await self.send_message(
                config.LOG_GROUP_ID, "Bot Started"
            )
            LOGGER(__name__).info(f"Successfully sent message to log group/channel (ID: {config.LOG_GROUP_ID})")
        except ValueError as e:
            error_msg = str(e)
            if "Peer id invalid" in error_msg or "peer id invalid" in error_msg.lower():
                LOGGER(__name__).error(
                    f"Invalid or inaccessible LOG_GROUP_ID: {config.LOG_GROUP_ID}\n"
                    "This usually means:\n"
                    "1. The bot has never interacted with this chat/channel before\n"
                    "2. The bot is not a member of the group/channel\n"
                    "3. The LOG_GROUP_ID is incorrect\n\n"
                    "Solutions:\n"
                    "1. Make sure the bot is added to the group/channel\n"
                    "2. Send a message in the group/channel using the bot (e.g., /start)\n"
                    "3. Verify the LOG_GROUP_ID is correct (should start with -100 for supergroups)\n"
                    "4. For channels, make sure the bot is added as an admin"
                )
            else:
                LOGGER(__name__).error(
                    f"ValueError when accessing log group/channel: {e}"
                )
            sys.exit(1)
        except PeerIdInvalid:
            LOGGER(__name__).error(
                f"Invalid LOG_GROUP_ID: {config.LOG_GROUP_ID}\n"
                "Please verify the ID is correct in your .env file."
            )
            sys.exit(1)
        except ChannelPrivate:
            LOGGER(__name__).error(
                f"Bot is not a member of the log group/channel (ID: {config.LOG_GROUP_ID}).\n"
                "Please add the bot to the group/channel first."
            )
            sys.exit(1)
        except ChatAdminRequired:
            LOGGER(__name__).error(
                "Bot needs admin permissions to send messages in the log group/channel.\n"
                "Please promote the bot as admin with permission to send messages."
            )
            sys.exit(1)
        except UserNotParticipant:
            LOGGER(__name__).error(
                "Bot is not a participant in the log group/channel.\n"
                "Please add the bot to the group/channel first."
            )
            sys.exit(1)
        except Exception as e:
            LOGGER(__name__).error(
                f"Failed to send message to log group/channel: {type(e).__name__}: {e}\n"
                "Please ensure:\n"
                "1. Bot is added to the log group/channel\n"
                "2. Bot is promoted as admin (if it's a group)\n"
                "3. Bot has permission to send messages\n"
                "4. LOG_GROUP_ID is correct (should start with -100 for supergroups)\n"
                "5. The bot has interacted with the chat at least once before"
            )
            sys.exit(1)
        if config.SET_CMDS == str(True):
            try:
                await self.set_bot_commands(
                    [
                        BotCommand("ping", "Check that bot is alive or dead"),
                        BotCommand("play", "Starts playing the requested song"),
                        BotCommand("skip", "Moves to the next track in queue"),
                        BotCommand("pause", "Pause the current playing song"),
                        BotCommand("resume", "Resume the paused song"),
                        BotCommand("end", "Clear the queue and leave voice chat"),
                        BotCommand("shuffle", "Randomly shuffles the queued playlist."),
                        BotCommand("playmode", "Allows you to change the default playmode for your chat"),
                        BotCommand("settings", "Open the settings of the music bot for your chat.")
                        ]
                    )
            except:
                pass
        else:
            pass
        try:
            a = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
            if a.status != "administrator":
                LOGGER(__name__).error(
                    "Bot is not an administrator in the log group. "
                    "Please promote the bot as admin in the logger group/channel."
                )
                sys.exit(1)
        except Exception as e:
            LOGGER(__name__).error(
                f"Error checking admin status: {type(e).__name__}: {e}\n"
                "Note: If LOG_GROUP_ID is a channel, admin check may fail. "
                "The bot should still work if it can send messages."
            )
            # Don't exit for channels, as they might not need admin status
            # Only exit if it's clearly a group that needs admin
            try:
                chat = await self.get_chat(config.LOG_GROUP_ID)
                if chat.type in ["group", "supergroup"]:
                    sys.exit(1)
            except:
                pass
        if get_me.last_name:
            self.name = get_me.first_name + " " + get_me.last_name
        else:
            self.name = get_me.first_name
        LOGGER(__name__).info(f"MusicBot Started as {self.name}")
