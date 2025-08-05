#!/usr/bin/env python3
import asyncio
import subprocess
import logging
from slixmpp import ClientXMPP

# Configure domain/room
XMPP_DOMAIN = "jitsi.local"
ROOM = f"testroom@conference.{XMPP_DOMAIN}"
NICK = "MediaBot"

logging.basicConfig(level=logging.INFO)

class JitsiBot(ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)

        # Register required plugins
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0045')  # MUC
        self.register_plugin('xep_0199')  # XMPP Ping

        # Event handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.muc_message)

        self.media_proc = None



    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        # Join room
        await self['xep_0045'].join_muc(ROOM, NICK)
        logging.info(f"Joined room {ROOM} as {NICK}")

    async def muc_message(self, msg):
        if msg['mucnick'] == NICK:
            return  # ignore self
        body = msg['body'].strip()
        logging.info(f"{msg['mucnick']}: {body}")

        if body == "!start" and not self.media_proc:
            logging.info("→ Starting media pipeline.")
            self.media_proc = subprocess.Popen(["./launch-media.sh"])
        elif body == "!stop" and self.media_proc:
            logging.info("→ Stopping media pipeline.")
            self.media_proc.terminate()
            self.media_proc = None


if __name__ == "__main__":
    jid = f"bot@{XMPP_DOMAIN}"
    password = "botpassword"

    xmpp = JitsiBot(jid, password)
    xmpp.connect()
    asyncio.get_event_loop().run_forever()

