#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
CMD="$DIR/.venv/bin/python3 $DIR/main.py"

# Detect shell and pick the right rc file
detect_rc() {
    local shell_name
    shell_name="$(basename "${SHELL:-$0}")"
    case "$shell_name" in
        zsh)   echo "${HOME}/.zshrc" ;;
        bash)  echo "${HOME}/.bashrc" ;;
        fish)  echo "${HOME}/.config/fish/config.fish" ;;
        *)     echo "${HOME}/.profile" ;;
    esac
}

alias_line() {
    local shell_name
    shell_name="$(basename "${SHELL:-$0}")"
    case "$shell_name" in
        fish) echo "alias espresso '$CMD'" ;;
        *)    echo "alias espresso='$CMD'" ;;
    esac
}

RC_FILE="${RC_FILE:-$(detect_rc)}"
ALIAS_LINE="$(alias_line)"

echo "→ Installing Espresso password vault..."
echo "  Shell detected: $(basename "${SHELL:-unknown}")"
echo "  Config file: $RC_FILE"

# Create venv if missing
if [ ! -f "$DIR/.venv/bin/python3" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv "$DIR/.venv"
fi

# Install dependencies
echo "  Installing dependencies..."
"$DIR/.venv/bin/python3" -m pip install --quiet --upgrade pip
"$DIR/.venv/bin/python3" -m pip install --quiet -r "$DIR/requirements.txt"

# Add alias to shell rc (if not already there)
if ! grep -q "alias espresso" "$RC_FILE" 2>/dev/null; then
    {
        echo ""
        echo "# Espresso - password vault"
        echo "$ALIAS_LINE"
    } >> "$RC_FILE"
    echo "→ Added 'espresso' alias to $RC_FILE"
fi

echo ""
echo "Installation Done! Usage:"
echo "    espresso          # launch the vault"
echo ""
echo "  Run 'source $RC_FILE' to update/refresh aliases or open a new terminal."
