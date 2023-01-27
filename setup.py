from setuptools import setup

setup(
    entry_points={
        "ouranos.plugins":
            ["chatbot=ouranos_chatbot.plugin_setup:plugin"]
    },
)
