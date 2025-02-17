#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-2020 Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from typing import Union

import pyrogram
from pyrogram.api import functions, types
from ...ext import BaseClient


class SendMessage(BaseClient):
    def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Union[str, None] = object,
        disable_web_page_preview: bool = None,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        schedule_date: int = None,
        reply_markup: Union[
            "pyrogram.InlineKeyboardMarkup",
            "pyrogram.ReplyKeyboardMarkup",
            "pyrogram.ReplyKeyboardRemove",
            "pyrogram.ForceReply"
        ] = None
    ) -> "pyrogram.Message":
        """Send text messages.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            text (``str``):
                Text of the message to be sent.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (``int``, *optional*):
                Date when the message will be automatically sent. Unix time.

            reply_markup (:obj:`InlineKeyboardMarkup` | :obj:`ReplyKeyboardMarkup` | :obj:`ReplyKeyboardRemove` | :obj:`ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`Message`: On success, the sent text message is returned.

        Example:
            .. code-block:: python
                :emphasize-lines: 2,5,8,11,21-23,26-33

                # Simple example
                app.send_message("haskell", "Thanks for creating **Pyrogram**!")

                # Disable web page previews
                app.send_message("me", "https://docs.pyrogram.org", disable_web_page_preview=True)

                # Reply to a message using its id
                app.send_message("me", "this is a reply", reply_to_message_id=12345)

                # Force HTML-only styles for this request only
                app.send_message("me", "**not bold**, <i>italic<i>", parse_mode="html")

                ##
                # For bots only, send messages with keyboards attached
                ##

                from pyrogram import (
                    ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton)

                # Send a normal keyboard
                app.send_message(
                    chat_id, "Look at that button!",
                    reply_markup=ReplyKeyboardMarkup([["Nice!"]]))

                # Send an inline keyboard
                app.send_message(
                    chat_id, "These are inline buttons",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Data", callback_data="hidden_callback_data")],
                            [InlineKeyboardButton("Docs", url="https://docs.pyrogram.org")]
                        ]))
        """

        message, entities = self.parser.parse(text, parse_mode).values()

        r = self.send(
            functions.messages.SendMessage(
                peer=self.resolve_peer(chat_id),
                no_webpage=disable_web_page_preview or None,
                silent=disable_notification or None,
                reply_to_msg_id=reply_to_message_id,
                random_id=self.rnd_id(),
                schedule_date=schedule_date,
                reply_markup=reply_markup.write() if reply_markup else None,
                message=message,
                entities=entities
            )
        )

        if isinstance(r, types.UpdateShortSentMessage):
            peer = self.resolve_peer(chat_id)

            peer_id = (
                peer.user_id
                if isinstance(peer, types.InputPeerUser)
                else -peer.chat_id
            )

            return pyrogram.Message(
                message_id=r.id,
                chat=pyrogram.Chat(
                    id=peer_id,
                    type="private",
                    client=self
                ),
                text=message,
                date=r.date,
                outgoing=r.out,
                entities=entities,
                client=self
            )

        for i in r.updates:
            if isinstance(i, (types.UpdateNewMessage, types.UpdateNewChannelMessage, types.UpdateNewScheduledMessage)):
                return pyrogram.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, types.UpdateNewScheduledMessage)
                )
