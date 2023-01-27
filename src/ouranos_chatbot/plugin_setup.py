from ouranos.sdk import Plugin

from ouranos_chatbot import Chatbot, main

plugin = Plugin(
    name="chatbot",
    functionality=Chatbot,
    command=main
)
