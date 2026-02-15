#!/bin/bash

# Ubuntu Server uchun o'rnatish skripti
echo "--- Telegram Dynamic Avatar O'rnatilmoqda ---"

# 1. Tizimni yangilash va kerakli paketlarni o'rnatish
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git libfreetype6-dev libjpeg62-turbo-dev zlib1g-dev

# 2. Virtual muhit yaratish
python3 -m venv venv
source venv/bin/activate

# 3. Kutubxonalarni o'rnatish
pip install -r requirements.txt

echo "--- O'rnatish yakunlandi ---"
echo "Endi .env faylini to'ldiring va 'python3 main.py' buyrug'i bilan login qiling."
