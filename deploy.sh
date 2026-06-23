#!/bin/bash
# Deploy do MCP Kawakami em VPS (Ubuntu/Debian)

# Instalar uv se nao tiver
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
fi

cd /opt/kawakami-mcp-server

# Instalar dependencias
uv sync

# Criar servico systemd
cat > /etc/systemd/system/kawakami-mcp.service << 'EOF'
[Unit]
Description=Kawakami MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/kawakami-mcp-server
ExecStart=/root/.local/bin/uv run server.py --transport=streamable-http --host=0.0.0.0 --port=8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kawakami-mcp
systemctl start kawakami-mcp

echo "MCP Kawakami rodando em http://$(hostname -I | awk '{print $1}'):8000/mcp"
