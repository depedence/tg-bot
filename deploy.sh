#!/bin/bash

echo 'Начинаем деплой Quest RPG Bot...'

SERVER_USER='your_user'
SERVER_HOST='your_server_ip'
APP_DIR='/opt/quest_rpg_bot'

echo 'Копируем файлы на сервер...'
rsync -avz --exlude- 'venv' --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' \
    ./ ${SERVER_USER}@${SERVER_HOST}:${APP_DIR}

ssh ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd /opt/quest_rpg_bot

source venv/bin/activate

pip install -r  requirements.txt

sudo systemctl restart quest_bot

sudo systemctl status quest_bot

echo 'Деплой завершен!'
ENDSSH
