# Changelog

---

## Unreleased

### Added
- New Telegram commands. Those reporting on ecosystems take an optional list of
  ecosystem names, and fall back to every ecosystem when none is given:
  - `/ecosystems` — name the ecosystems available (#3)
  - `/sensors` — current sensor readings, with their units (#3)
  - `/actuators_state` — actuator states (#3)
  - `/warnings` — unsolved warnings, if any (#6)
  - `/recap` — status, sensor data, actuator states and warnings in a single
    message (#7)
  - `/switch_actuator <ecosystem> <actuator> <mode> [countdown]` — switch an actuator on
    or off; requires the `OPERATE` permission (#3)
- `Config` class holding `TELEGRAM_BOT_TOKEN`, to be subclassed by the Ouranos config
  class; it falls back to the `OURANOS_TELEGRAM_BOT_TOKEN` environment variable, and the
  chatbot logs a warning when it has to (#2)
- `scripts/update.sh`, sourced by Ouranos' update script, checking that the updated
  plugin still loads (#11)
- README covering the requirements, the installation, the token configuration and the
  update procedure (#12)

### Changed
- `Chatbot` follows Ouranos' `Functionality` (#1), then its reworked `Plugin` system (#4),
  and declares its `contract_versions` (#5)
- Messages moved from `messages/__init__.py` to Jinja templates rendered from the
  ecosystem data; the ecosystem, lights, weather, calendar and tree templates were
  dropped along the way (#3)
- `/ecosystem_status` renamed `/ecosystems_status`, and account linking renamed
  `/link_account`; both were rewritten along with the rest of the command set (#3)
- `install.sh` moved to `scripts/install.sh` and rewritten along the lines of the other
  Ouranos packages: pinned clone into `$OURANOS_DIR/lib`, `uv`-based installation, shared
  logging, and a summary of what to configure next (#11)
- The token environment variable is renamed `TELEGRAM_BOT_TOKEN` →
  `OURANOS_TELEGRAM_BOT_TOKEN`, and the token is no longer looked up in Ouranos core's
  own config, which does not define it (#2)
- Packaging moved from `setup.py` / `requirements.txt` to `pyproject.toml`, and the
  project migrated from GitLab to GitHub

### Fixed
- The `/actuators_state` message announced an overview of an empty list of ecosystems
  when none was connected; it now says that none is (#9)

### Development
- Test suite covering the command handlers, and a GitHub Actions workflow running it on
  Python 3.11, 3.12 and 3.13 (#10)

---

## 0.1.0 — 2023-01-28

Initial version, extracted from the
[gaia-ouranos](https://github.com/vaamb/gaia-ouranos) project and turned into a
standalone Ouranos plugin.

### Added
- `Chatbot` functionality, exposed to Ouranos through the `ouranos.plugins` entry point,
  plus a command to run it on its own
- Telegram commands: `/start`, `/ecosystem_status`, `/help`, and an answer for unknown
  commands
- Account linking and the `activation_required` / `permission_required` decorators,
  gating the commands on Ouranos' users and permissions
- Jinja message templates for the ecosystem, sensors, lights, weather, recap, warnings
  and calendar messages, moved over from Ouranos
- `TELEGRAM_BOT_TOKEN` config option, moved out of Ouranos core; read from Ouranos'
  config, or from the environment variable of the same name
- `install.sh`, cloning the plugin into Ouranos' `lib` directory and installing it into
  its virtual environment
