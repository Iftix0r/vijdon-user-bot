#!/bin/bash
set -e

cd /root/Iftixor/Bot/vijdon-user-bot
git pull origin main

export PYTHONPATH=/root/Iftixor/Bot/vijdon-user-bot
source venv/bin/activate
pip install -r requirements.txt -q

pkill -f 'python.*src/main.py' || true
sleep 2

nohup python3 src/main.py > bot.log 2>&1 &
sleep 1

echo "✅ Bot deployed successfully"
exit 0
