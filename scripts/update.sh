#!/bin/bash

# Exit on error, unset variable, and pipefail
set -euo pipefail

check_ouranos_chatbot() {
    # Check if ouranos-chatbot exists
    if [[ ! -d "${OURANOS_DIR}/lib/ouranos-chatbot" ]]; then
        die "Ouranos-chatbot installation not found at ${OURANOS_DIR}/lib/ouranos-chatbot. Please install using the install script."
    fi


}

update_ouranos_chatbot() {
    # The repository itself and the virtual environment are updated by the
    # Ouranos update script. As the chatbot is a pure Python plugin, all that
    # is left is to check that the updated plugin is usable.
    log INFO "Checking the updated plugin..."
    if [[ "$DRY_RUN" == false ]]; then
        cd "${OURANOS_DIR}" ||
            die "Failed to change to directory: ${OURANOS_DIR}"

        # Activate virtual environment
        # shellcheck source=/dev/null
        if ! source "${OURANOS_DIR}/.venv/bin/activate"; then
            die "Failed to activate Python virtual environment"
        fi

        python -c "from ouranos_chatbot.plugin_setup import plugin" ||
            die "Failed to load the Ouranos chatbot plugin"
        deactivate
    fi
}

main() {
    # Check if ouranos-chatbot exists
    log INFO "Checking if Ouranos chatbot is installed..."
    check_ouranos_chatbot
    log SUCCESS "Ouranos chatbot installation found"

    log INFO "Updating Ouranos chatbot..."
    update_ouranos_chatbot
    log SUCCESS "Ouranos chatbot updated successfully!"
}

if [[ "${BASH_SOURCE[0]}" -ef "$0" ]]; then
    echo "This script should be run from the Ouranos update script."
    exit 1
else
    main "$@"
fi
