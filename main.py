import sys, logging, io, subprocess
exit = sys.exit
from modules.pip_install import install
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s[%(name)s] %(message)s")
log = logging.getLogger(__name__ == "__main__" and "MainScript" or __name__)
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackContext
from telegram.ext.filters import Filters
from telegram.error import InvalidToken, BadRequest
from telegram import ParseMode, Update, Bot
from telegram.utils.helpers import escape_markdown, mention_markdown

def em(s):
    return escape_markdown(text=s,version=2)

remote = "Canot get git remote infomation\!"
try:
    remote = em(subprocess.run(["/usr/bin/git", "remote", "-v"], capture_output=True).stdout.decode('utf-8'))
except subprocess.CalledProcessError:
    pass

try:
    import clamd
except ImportError as e:
    log.warning("Module `clamd` not found, installing.")
    install("clamd")
    import clamd
cd = clamd.ClamdUnixSocket()

def str2io(s):
    return io.BytesIO(bytes(s,'utf-8'))

def bytes2io(b):
    return io.BytesIO(b)

def token():
    try:
        with open("token.txt","r") as f:
            return f.read().rstrip('\n')
    except FileNotFoundError:
        log.error("No token.txt!")
        return ""
def checkvirus(i):
    ans = cd.instream(i)["stream"]
    if ans[0] == "FOUND":
        return True, ans[1]
    else:
        return False, ""

def delete(message):
    try:
        return message.delete()
    except BadRequest:
        return False

def texthandler(update, context):
    msg = update.message.text
    stat, virus = checkvirus(str2io(msg))
    if stat == True:
        log.warning("Virus from {}, virus name is {}!".format(update.message.from_user,virus))
        if delete(update.message):
            rusr = update.message.from_user["first_name"]
            if rusr == "":
                rusr = "_Blank Name_"
            context.bot.sendMessage(update.message.chat_id, "Virus found\! Deleted the origional message sent by {}, Virus name is `{}`\!".format(mention_markdown(user_id=update.message.from_user["id"],name=rusr,version=2),em(virus)),parse_mode=ParseMode.MARKDOWN_V2)
        else:
            update.message.reply_text(em("Virus found but the bot cannot delete that message automacily! Virus name: `{}`".format(virus)),parse_mode=ParseMode.MARKDOWN_V2)

def filehandler(update, context):
    file = context.bot.get_file(update.message.document).download_as_bytearray()
    stat, virus = checkvirus(bytes2io(file))
    if stat == True:
        log.warning("Virus from {}, virus name is {}!".format(update.message.from_user,virus))
        if delete(update.message):
            rusr = update.message.from_user["first_name"]
            if rusr == "":
                rusr = "_Blank Name_"
            context.bot.sendMessage(update.message.chat_id, "Virus found\! Deleted the origional message sent by {}, Virus name is `{}`\!".format(mention_markdown(user_id=update.message.from_user["id"],name=rusr,version=2),em(virus)),parse_mode=ParseMode.MARKDOWN_V2)
        else:
            update.message.reply_text(em("Virus found but the bot cannot delete that message automacily! Virus name: `{}`".format(virus)),parse_mode=ParseMode.MARKDOWN_V2)

def photohandler(update,context):
    vir = []
    for p in update.message.photo:
        file = context.bot.getFile(p.file_id).download_as_bytearray()
        stat, virus = checkvirus(bytes2io(file))
        if stat == True:
            vir.append((p,virus))
            log.warning("Virus from {}, virus name is {}!".format(update.message.from_user,virus))
    if len(vir) != 0:
        if delete(update.message):
            rusr = update.message.from_user["first_name"]
            if rusr == "":
                rusr = "_Blank Name_"
            context.bot.sendMessage(update.message.chat_id, "Virus found\! Deleted the origional message sent by {}\!".format(mention_markdown(user_id=update.message.from_user["id"],name=rusr,version=2)),parse_mode=ParseMode.MARKDOWN_V2)
        else:
            update.message.reply_text("Virus found but the bot cannot delete that message automacily!")
        wstr = "Virus list:"
        for a in vir:
            wstr = wstr + "Photo {}: `{}`".format(str(a[0]+1,a[1]))
        context.bot.sendMessage(update.message.chat_id, wstr)

def starthandler(update,context):
    log.info("Got start command from {}!".format(update.message.from_user))
    update.message.reply_text("Hi, I am the antivirus bot\! Send me something to check virus\!\nThanks for clamav to provide the virus scanning service\!\n\nThis bot's code was relased under GPLv3 License\.",parse_mode=ParseMode.MARKDOWN_V2)
    texthandler(update, context)

def pinghandler(update,context):
    log.info("Got ping command from {}!".format(update.message.from_user))
    update.message.reply_text("PONG!")
    texthandler(update, context)

def testfilehandler(update,context):
    update.message.reply_document(clamd.EICAR,filename="EICAR_TEST_FILE.txt")
    texthandler(update, context)

def teststringhandler(update,context):
    update.message.reply_text(clamd.EICAR.decode('utf-8'))
    texthandler(update, context)

def remotehandler(update,context):
    update.message.reply_text("```\n{}\n```".format(remote),parse_mode=ParseMode.MARKDOWN_V2)

def main(tok):
    if tok == "":
        log.critical("No token!")
        exit(3)
    try:
        bot = Bot(token=tok)
        updater = Updater(bot=bot, use_context=True)
        log.info("Get updater success!")
    except InvalidToken:
        log.critical("Invalid Token! Plase edit token.txt and fill in a valid token.")
        raise
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", starthandler))
    dp.add_handler(CommandHandler("ping", pinghandler))
    dp.add_handler(CommandHandler("testfile", testfilehandler))
    dp.add_handler(CommandHandler("teststring", teststringhandler))
    dp.add_handler(CommandHandler("remote", remotehandler))
    dp.add_handler(MessageHandler(Filters.document,filehandler))
    dp.add_handler(MessageHandler(Filters.photo,photohandler))
    dp.add_handler(MessageHandler(Filters.text,texthandler))
    updater.start_polling()
    log.info("Started the bot! Use Ctrl-C to stop it.")
    updater.idle()

if __name__ == '__main__':
    main(token())
