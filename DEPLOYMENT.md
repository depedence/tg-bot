# Инструкция по деплою Quest RPG Bot

## Вариант 1: Деплой с Docker Compose (рекомендуется)

### Требования
- Ubuntu 20.04+ или Debian 11+
- Docker и Docker Compose установлены
- Доступ по SSH

### Шаги

1. Подключитесь к серверу:
```bash
ssh user@your_server_ip
```

2. Клонируйте репозиторий:
```bash
cd /opt
sudo git clone <repository-url> quest_rpg_bot
cd quest_rpg_bot
```

3. Создайте .env файл:
```bash
sudo nano .env
```

Заполните:
```env
BOT_TOKEN=your_bot_token
API_KEY=your_groq_key
DB_PASSWORD=strong_password_here
```

4. Запустите контейнеры:
```bash
sudo docker-compose up -d
```

5. Проверьте логи:
```bash
sudo docker-compose logs -f bot
```

### Управление

- Остановить: `sudo docker-compose stop`
- Запустить: `sudo docker-compose start`
- Перезапустить: `sudo docker-compose restart`
- Просмотр логов: `sudo docker-compose logs -f`
- Обновление:
```bash
git pull
sudo docker-compose down
sudo docker-compose up -d --build
```

---

## Вариант 2: Нативная установка с systemd

### Требования
- Ubuntu 20.04+ или Debian 11+
- Python 3.11+
- PostgreSQL 14+

### Шаги

1. Установите PostgreSQL:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

2. Создайте базу данных:
```bash
sudo -u postgres psql
CREATE DATABASE quest_bot;
CREATE USER quest_bot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE quest_bot TO quest_bot_user;
\q
```

3. Создайте пользователя для бота:
```bash
sudo useradd -r -s /bin/bash -d /opt/quest_rpg_bot quest_bot
```

4. Клонируйте репозиторий:
```bash
cd /opt
sudo git clone <repository-url> quest_rpg_bot
sudo chown -R quest_bot:quest_bot quest_rpg_bot
```

5. Установите зависимости:
```bash
cd quest_rpg_bot
sudo -u quest_bot python3.11 -m venv venv
sudo -u quest_bot venv/bin/pip install -r requirements.txt
```

6. Создайте .env:
```bash
sudo -u quest_bot nano .env
```

Заполните с `DATABASE_TYPE=postgresql`.

7. Установите systemd service:
```bash
sudo cp quest_bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable quest_bot
sudo systemctl start quest_bot
```

8. Проверьте статус:
```bash
sudo systemctl status quest_bot
sudo journalctl -u quest_bot -f
```

---

## Настройка Nginx (опционально)

Если планируете добавить веб-интерфейс:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Мониторинг

Рекомендуется настроить:
- Logrotate для ротации логов
- Monitoring (Prometheus + Grafana)
- Alerting (Telegram уведомления при падении)

---

## Безопасность

1. Настройте firewall:
```bash
sudo ufw allow 22/tcp
sudo ufw allow 5432/tcp  # только для локальных подключений
sudo ufw enable
```

2. Регулярно обновляйте систему:
```bash
sudo apt update && sudo apt upgrade
```

3. Используйте SSL для PostgreSQL в продакшене
4. Регулярно делайте бэкапы БД:
```bash
pg_dump quest_bot > backup_$(date +%Y%m%d).sql
```
