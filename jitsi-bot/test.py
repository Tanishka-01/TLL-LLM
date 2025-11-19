#!/usr/bin/env python3

import slixmpp
import asyncio
import ssl
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

class JitsiBot(slixmpp.ClientXMPP):
    def __init__(self, jid, password, room, nickname, websocket_url):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        
        self.room = room
        self.nickname = nickname
        self.websocket_url = websocket_url
        
        # Register plugins
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0045')  # Multi-User Chat
        self.register_plugin('xep_0199')  # XMPP Ping
        
        # Handle connection events
        self.add_event_handler("session_start", self.session_start)
        
    def session_start(self, event):
        print("Session started")
        self.send_presence()
        self.plugin['xep_0045'].join_muc(self.room, self.nickname)
        print(f"Joined room {self.room} as {self.nickname}")
        
        # Send message
        msg = self.Message()
        msg['to'] = self.room
        msg['type'] = 'groupchat'
        msg['body'] = 'Hello from Jitsi Bot!'
        msg.send()
        print("Message sent!")
        
        # Disconnect after sending
        self.disconnect()

def main():
    # Configuration
    XMPP_DOMAIN = "meet.jitsi.local"
    ROOM = "testroom"
    NICKNAME = "bot"
    PASSWORD = ""  # Empty for anonymous
    
    # JID format for Jitsi MUC
    jid = f"{NICKNAME}@{XMPP_DOMAIN}"
    
    # Create bot instance
    bot = JitsiBot(
        jid, 
        PASSWORD, 
        f"{ROOM}@conference.{XMPP_DOMAIN}", 
        NICKNAME,
        f"wss://{XMPP_DOMAIN}/xmpp-websocket?room={ROOM}"
    )
    
    # Set up TLS context (disable verification for self-signed certs)
    bot.ssl_context.check_hostname = False
    bot.ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        print("Connecting to Jitsi server...")
        # Connect using WebSocket
        bot.connect(
            address=(XMPP_DOMAIN, 443),
            use_tls=True,
            use_ssl=True,
            force_starttls=False
        )
        
        # Process events
        while True:
            if not bot.is_connected():
                break
            asyncio.sleep(0.1)
            
    except KeyboardInterrupt:
        print("Interrupted by user")
        bot.disconnect()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Import ssl for the context
    import ssl
    
    main()