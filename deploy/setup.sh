#!/bin/bash
set -e

APP_DIR="/opt/sales-dashboard"
APP_USER="dashboard"
REPO_URL="https://gitlab.technation.kz/n.kurmangaliev/sales-dashboard.git"
PORT=8501

echo "=== Sales Dashboard: установка ==="

# System packages
echo "[1/6] Установка системных пакетов..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git

# Create user
if ! id "$APP_USER" &>/dev/null; then
    echo "[2/6] Создание пользователя $APP_USER..."
    useradd -r -m -s /bin/bash "$APP_USER"
else
    echo "[2/6] Пользователь $APP_USER уже существует"
fi

# Clone repo
if [ -d "$APP_DIR" ]; then
    echo "[3/6] Обновление кода..."
    cd "$APP_DIR" && git pull
else
    echo "[3/6] Клонирование репозитория..."
    git clone "$REPO_URL" "$APP_DIR"
fi

chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# Python venv
echo "[4/6] Установка Python-зависимостей..."
sudo -u "$APP_USER" bash -c "
    cd $APP_DIR
    python3 -m venv venv
    source venv/bin/activate
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
"

# Systemd service
echo "[5/6] Настройка systemd-сервиса..."
cat > /etc/systemd/system/sales-dashboard.service << UNIT
[Unit]
Description=Sales Analytics Dashboard (Streamlit)
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/streamlit run app.py --server.port=$PORT --server.headless=true --server.address=0.0.0.0
Restart=always
RestartSec=5
Environment="PATH=$APP_DIR/venv/bin:/usr/bin"

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable sales-dashboard
systemctl restart sales-dashboard

echo "[6/6] Готово!"
echo ""
echo "==================================="
echo "  Dashboard запущен!"
echo "  Откройте: http://$(hostname -I | awk '{print $1}'):$PORT"
echo "==================================="
echo ""
echo "Полезные команды:"
echo "  systemctl status sales-dashboard   — статус"
echo "  systemctl restart sales-dashboard  — перезапуск"
echo "  journalctl -u sales-dashboard -f   — логи"
echo ""
echo "Для обновления:"
echo "  cd $APP_DIR && git pull && systemctl restart sales-dashboard"
