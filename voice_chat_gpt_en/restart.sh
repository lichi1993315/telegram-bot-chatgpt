cd .. && git pull && cd voice_chat_gpt_en
TELEBOT_PID=`ps aux | grep telegram_chatgpt_en.py | grep -v grep | awk '{ print $2}'`
while [ ! -z "$TELEBOT_PID" ]
do
    echo "killing telegram_chatgpt_en.py ..."
    kill -9 ${TFSERVER_PID}
    TELEBOT_PID=`ps aux | grep telegram_chatgpt_en.py | grep -v grep | awk '{ print $2}'`
done
nohup python telegram_chatgpt_en.py >>nohup.log 2>&1 &