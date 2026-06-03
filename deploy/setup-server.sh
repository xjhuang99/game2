#!/usr/bin/env bash
# One-time server setup for game2 @ game.xjhuang.com (same host as group.xjhuang.com).
# Run on Ubuntu as a user with sudo. Requires DNS: game.xjhuang.com → this server.

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/xjhuang99/game2.git}"
GIT_REF="${GIT_REF:-4feeea9}"
INSTALL_DIR="${INSTALL_DIR:-/opt/pd-game}"
GROUP_ENV="${GROUP_ENV:-/opt/group_ai_chat_bot/.env}"

echo "==> Install dir: $INSTALL_DIR (ref $GIT_REF)"

if [[ ! -d "$INSTALL_DIR/.git" ]]; then
  sudo mkdir -p "$INSTALL_DIR"
  sudo git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
sudo git fetch origin
sudo git checkout "$GIT_REF"

echo "==> Python venv"
sudo python3 -m venv .venv
sudo .venv/bin/pip install -U pip
sudo .venv/bin/pip install -r requirements.txt

echo "==> .env from group"
if [[ ! -f "$GROUP_ENV" ]]; then
  echo "Set GROUP_ENV to your group chat .env path (default $GROUP_ENV)" >&2
  exit 1
fi
sudo bash deploy/build-env-from-group.sh "$GROUP_ENV" "$INSTALL_DIR/.env"

echo "==> Permissions"
sudo chown -R www-data:www-data "$INSTALL_DIR"
sudo chmod 600 "$INSTALL_DIR/.env"

echo "==> systemd"
sudo cp deploy/pd-game.service /etc/systemd/system/pd-game.service
sudo systemctl daemon-reload
sudo systemctl enable pd-game
sudo systemctl restart pd-game
sudo systemctl status pd-game --no-pager || true

echo "==> nginx"
if [[ -f /etc/nginx/sites-available/game.xjhuang.com ]]; then
  echo "nginx site already exists; reload only"
else
  sudo cp deploy/nginx-game.xjhuang.com.conf /etc/nginx/sites-available/game.xjhuang.com
  sudo ln -sf /etc/nginx/sites-available/game.xjhuang.com /etc/nginx/sites-enabled/
fi
sudo nginx -t
sudo systemctl reload nginx

echo ""
echo "Done. Next steps:"
echo "  1. DNS A record: game.xjhuang.com → this server IP (same as group.xjhuang.com)"
echo "  2. HTTPS: sudo certbot --nginx -d game.xjhuang.com"
echo "  3. Test: curl -sI https://game.xjhuang.com/admin"
echo "  4. Updates: cd $INSTALL_DIR && sudo git pull && sudo systemctl restart pd-game"
