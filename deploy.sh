#!/bin/bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

install -m 0755 "$(command -v uv)" /usr/local/bin/uv
cd /opt/kawakami-mcp-server
/usr/local/bin/uv sync --frozen --no-dev

cat > /etc/systemd/system/kawakami-mcp.service <<'EOF'
[Unit]
Description=Kawakami MCP Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/kawakami-mcp-server
EnvironmentFile=/opt/kawakami-mcp-server/.env
Environment=KWK_SESSION_DB_PATH=/var/lib/kawakami-mcp/kawakami_sessions.db
Environment=KWK_TOKEN_FILE_PATH=/var/lib/kawakami-mcp/.kawakami_token.json
StateDirectory=kawakami-mcp
ExecStart=/usr/local/bin/uv run python -m src.main --transport=streamable-http --host=0.0.0.0 --port=8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now kawakami-mcp

echo "MCP Kawakami rodando em http://$(hostname -I | awk '{print $1}'):8000/mcp"
