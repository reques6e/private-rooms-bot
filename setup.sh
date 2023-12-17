#!/bin/bash

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

SERVICE_FILE="/etc/systemd/system/privateroomsbot.service"

SERVICE_CONTENT="[Unit]
Description=TicketBot
After=network.target

[Service]
Type=simple
WorkingDirectory=$SCRIPT_PATH
ExecStart=/usr/bin/python3 $SCRIPT_PATH/main.py
Restart=always

[Install]
WantedBy=multi-user.target"

echo "$SERVICE_CONTENT" | sudo tee "$SERVICE_FILE" > /dev/null

sudo systemctl start profileactivity.service

if [ $? -eq 0 ]; then
    echo "Установка успешно завершена. Служба profileactivity успешно запущена.."
    sudo systemctl status privateroomsbot.service
    echo "github.com/reques6e/private-rooms-bot - privateroomsbot"
else
    echo "Произошла ошибка при установке."
fi
