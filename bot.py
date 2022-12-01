from pexpect import pxssh
import telebot
from datetime import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
from const import TOKEN, SSH_IP, SSH_USERNAME, SSH_PASSWORD

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler()

conf = {"first_message": True, "last_check": "OFFLINE"}


def pi_is_online():
    try:
        ssh = pxssh.pxssh()
        login = ssh.login(SSH_IP, SSH_USERNAME, SSH_PASSWORD)
        time.sleep(5)
        if login:
            ssh.logout()
            return True
        else:
            return False
    except:
        return False


def send_update(message):
    status = "ONLINE" if pi_is_online() else "OFFLINE"
    if conf.get("first_message"):
        text = f"Pi is {status} as of {str(datetime.now())}"
        conf["first_message"] = False
        conf["last_check"] = status
        bot.send_message(message.from_user.id, text)
        print(text)
    else:
        if conf.get("last_check") != status:
            text = f"Pi went {status} at {str(datetime.now())}"
            conf["last_check"] = status
            bot.send_message(message.from_user.id, text)
            print(text)


@bot.message_handler(commands=["start"])
def start_message(message):
    scheduler.add_job(send_update, args=(message,), trigger="interval", minutes=3)
    print('Job added')
    bot.send_message(message.from_user.id, "Welcome to Pi check")
    send_update(message)
    print('Initial check')


if __name__ == "__main__":
    # for local run
    scheduler.start()
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True, interval=1)
