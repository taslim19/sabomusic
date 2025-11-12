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
        # Try to send message to log group, but don't exit if it fails
        # The bot can still work without log group access
        try:
            await self.send_message(
                config.LOG_GROUP_ID, "Bot Started"
            )
            LOGGER(__name__).info(f"Successfully sent message to log group/channel (ID: {config.LOG_GROUP_ID})")
        except ValueError as e:
            error_msg = str(e)
            if "Peer id invalid" in error_msg or "peer id invalid" in error_msg.lower():
                LOGGER(__name__).warning(
                    f"⚠️  Cannot access log group/channel (ID: {config.LOG_GROUP_ID})\n"
                    "The bot will continue running, but logging to the group will be disabled.\n"
                    "To fix this:\n"
                    "1. Make sure the bot is added to the group/channel\n"
                    "2. Send a message in the group/channel using the bot (e.g., /start)\n"
                    "3. Verify the LOG_GROUP_ID is correct (should start with -100 for supergroups)\n"
                    "4. For channels, make sure the bot is added as an admin"
                )
            else:
                LOGGER(__name__).warning(
                    f"⚠️  ValueError when accessing log group/channel: {e}\n"
                    "The bot will continue running without log group access."
                )
        except PeerIdInvalid:
            LOGGER(__name__).warning(
                f"⚠️  Invalid LOG_GROUP_ID: {config.LOG_GROUP_ID}\n"
                "Please verify the ID is correct in your .env file.\n"
                "The bot will continue running without log group access."
            )
        except ChannelPrivate:
            LOGGER(__name__).warning(
                f"⚠️  Bot is not a member of the log group/channel (ID: {config.LOG_GROUP_ID}).\n"
                "Please add the bot to the group/channel to enable logging.\n"
                "The bot will continue running without log group access."
            )
        except ChatAdminRequired:
            LOGGER(__name__).warning(
                "⚠️  Bot needs admin permissions to send messages in the log group/channel.\n"
                "Please promote the bot as admin with permission to send messages.\n"
                "The bot will continue running without log group access."
            )
        except UserNotParticipant:
            LOGGER(__name__).warning(
                "⚠️  Bot is not a participant in the log group/channel.\n"
                "Please add the bot to the group/channel to enable logging.\n"
                "The bot will continue running without log group access."
            )
        except Exception as e:
            LOGGER(__name__).warning(
                f"⚠️  Failed to send message to log group/channel: {type(e).__name__}: {e}\n"
                "The bot will continue running without log group access.\n"
                "To enable logging, ensure:\n"
                "1. Bot is added to the log group/channel\n"
                "2. Bot is promoted as admin (if it's a group)\n"
                "3. Bot has permission to send messages\n"
                "4. LOG_GROUP_ID is correct (should start with -100 for supergroups)\n"
                "5. The bot has interacted with the chat at least once before"
            )
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
        # Check admin status, but don't exit if it fails
        try:
            a = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
            if a.status != "administrator":
                LOGGER(__name__).warning(
                    "⚠️  Bot is not an administrator in the log group. "
                    "Please promote the bot as admin in the logger group/channel for full functionality."
                )
        except Exception as e:
            # Admin check is optional, just log a warning
            LOGGER(__name__).debug(
                f"Could not check admin status in log group: {type(e).__name__}: {e}\n"
                "This is not critical - the bot will continue running."
            )
        if get_me.last_name:
            self.name = get_me.first_name + " " + get_me.last_name
        else:
            self.name = get_me.first_name
        LOGGER(__name__).info(f"MusicBot Started as {self.name}")
