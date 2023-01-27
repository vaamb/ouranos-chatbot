from ouranos.sdk import Plugin

from ouranos_chatbot import Chatbot, main

plugin = Plugin(
    functionality=Chatbot,
    command=main
)
