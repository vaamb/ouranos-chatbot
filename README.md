Ouranos - Chatbot
=================

This is a chatbot plugin for [Ouranos](https://github.com/vaamb/ouranos-core.git).
It can be used to interact with Ouranos API through a telegram chatbot


Note
----

This plugin requires Ouranos core in order to work.

Ouranos is still in development and might not work properly.


Requirements
------------

- A running [Ouranos](https://github.com/vaamb/ouranos-core) instance
- Python 3.11+ and `uv` (both already installed by Ouranos)
- A Telegram bot token, obtained from [@BotFather](https://t.me/BotFather)


Installation
------------

Ouranos must be installed first. Copy the install script from the `scripts/`
directory into any working directory and run it:

```bash
bash install.sh
```

The script will:
1. Clone the repository into `$OURANOS_DIR/lib/ouranos-chatbot`
2. Install the plugin into Ouranos' virtual environment

The chatbot plugin is enabled automatically once installed. Ouranos will
detect it on the next start.


Configuration
-------------

The chatbot needs a Telegram bot token to run. It can be set in two ways:

- in `$OURANOS_DIR/config.py`, by making the config class subclass
  `ouranos_chatbot.Config`:

  ```python
  from ouranos_chatbot import Config as ChatbotConfig
  from ouranos.core.config.base import BaseConfig


  class DefaultConfig(BaseConfig, ChatbotConfig):
      TELEGRAM_BOT_TOKEN = "your-token-here"
  ```

- or via the `OURANOS_TELEGRAM_BOT_TOKEN` environment variable

Without a token, the plugin logs an error and the chatbot does not start.


Updating
--------

The chatbot is updated together with Ouranos:

```bash
ouranos update
```

This pulls the repository, syncs the virtual environment, and runs
`scripts/update.sh` to check the updated plugin. That script is meant to be
sourced by the Ouranos update script and should not be run on its own.


Running
-------

The plugin is started and stopped by Ouranos:

```bash
ouranos restart          # or: sudo systemctl restart ouranos
```

To disable it without uninstalling, add `chatbot` to the `PLUGINS_OMITTED`
config parameter (or to the `OURANOS_PLUGINS_OMITTED` environment variable).
