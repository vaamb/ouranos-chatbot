#!/bin/bash

# Exit on error, unset variable, and pipefail
set -euo pipefail

# Check if ouranos has been installed
if [[ -z "${OURANOS_DIR:-}" || ! -d "${OURANOS_DIR}" ]]; then
    echo "OURANOS_DIR is not set or does not exist. Please install Ouranos first." >&2
    exit 1
fi

# Version requirements
readonly OURANOS_CHATBOT_VERSION="0.1.0"
# Overridable so the installation can be tested, or run from a fork or a local
# mirror, without reaching for GitHub
readonly OURANOS_CHATBOT_REPO="${OURANOS_CHATBOT_REPO:-https://github.com/vaamb/ouranos-chatbot.git}"

# Whether this run created the repository directory. Used by `cleanup` to tell a
# failed install apart from one that stopped on an already installed chatbot.
CLONED=false

setup_logging() {
    # Load logging functions
    readonly DATETIME=$(date +%Y%m%d_%H%M%S)
    readonly LOG_FILE="/tmp/ouranos_chatbot_install_${DATETIME}.log"
    . "${OURANOS_DIR}/scripts/utils/logging.sh"
}

install_ouranos_chatbot() {
    # Change to Ouranos lib directory
    cd "${OURANOS_DIR}/lib" ||
        die "Failed to change to directory: ${OURANOS_DIR}/lib"

    # Check if ouranos-chatbot already exists
    if [[ -d "ouranos-chatbot" ]]; then
        die "Ouranos-chatbot installation detected at ${OURANOS_DIR}/lib/ouranos-chatbot. Please update using the update script."
    fi

    # Clone the repository
    log INFO "Cloning Ouranos chatbot repository..."
    git clone --branch "${OURANOS_CHATBOT_VERSION}" "${OURANOS_CHATBOT_REPO}" \
            "${OURANOS_DIR}/lib/ouranos-chatbot" ||
        die "Failed to clone Ouranos chatbot repository"
    CLONED=true

    # Install the plugin. It is picked up as a uv workspace member as it sits in
    # `${OURANOS_DIR}/lib` and is named `ouranos-*`
    log INFO "Installing the plugin in Ouranos' virtual environment..."
    cd "${OURANOS_DIR}" ||
        die "Failed to change to directory: ${OURANOS_DIR}"
    uv lock --upgrade ||
        die "Failed to update uv lock"
    # use --inexact to keep packages not defined in pyproject.toml such as the DB drivers
    uv sync --all-packages --inexact ||
        die "Failed to update Python virtual environment"
}

# Cleanup function to run on exit
cleanup() {
    local exit_code=$?

    if [[ "${exit_code}" -ne 0 ]]; then
        log WARN "Installation failed. Check the log file for details: ${LOG_FILE}"
        if [[ "${CLONED}" == true ]]; then
            log WARN "Partial installation may remain at ${OURANOS_DIR}/lib/ouranos-chatbot. Remove it manually before retrying."
        fi
    else
        log SUCCESS "Installation completed successfully!"
    fi

    # Reset terminal colors
    echo -e "${NC}"
}

main() {
    setup_logging

    # Set trap to run cleanup function on exit
    trap cleanup EXIT

    log INFO "Installing Ouranos chatbot..."
    install_ouranos_chatbot
    log SUCCESS "Ouranos chatbot installed successfully!"

    echo -e "\n${GREEN}✔ Installation completed successfully!${NC}"
    echo -e "\n${YELLOW}The chatbot needs a Telegram bot token to run. Set it either:${NC}"
    echo -e "  - in ${OURANOS_DIR}/config.py, by making your config class subclass"
    echo -e "    'ouranos_chatbot.Config' and setting 'TELEGRAM_BOT_TOKEN'"
    echo -e "  - or via the 'OURANOS_TELEGRAM_BOT_TOKEN' environment variable"
    echo -e "\n${YELLOW}Once the token is set, restart Ouranos with one of those,${NC}"
    echo -e "${YELLOW}depending on how you started it:${NC}"
    echo -e "  ouranos restart"
    echo -e "  sudo systemctl restart ouranos"
}

main "$@"
