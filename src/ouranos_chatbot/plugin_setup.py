from ouranos.sdk import Plugin

from ouranos_chatbot import Chatbot


plugin = Plugin(
    functionality=Chatbot,
    description="""Launch Ouranos' Chatbot

    The Chatbot provides a way that allows users to interact with Ouranos through
    a Telegram chatbot.
    """,
)
