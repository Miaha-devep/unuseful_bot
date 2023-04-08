from telebot import TeleBot, types

from main_backend import *

TOKEN = "TOKEN"
bot = TeleBot(TOKEN)
GREETINGS = """Здравствуйте, введите команду /help, чтобы узнать функции бота"""

HELP = """
Отслеживается только цена.
/start_tracking - дает возможность начать отслеживать чай
/all - выводит все чаи, и отслеживаемые в данный момент, и чаи не отслеживаемые в данный момент
/tracked - выводит все, отслеживаемые в данный момент чаи(по ним Вы получаете уведомления)
/untracked - выводит все, НЕ отслеживаемые в данный момент чаи(по ним Вы НЕ получаете уведомления)
/senddata
"""

flag_is_start_tracking = False
flag_is_delete_from_tracking = False
flag_is_resume_tracking = False
list_of_tracked_ever_teas = []  # чаи, которые  когда-либо отслеживались
list_of_tracked_teas_now = []
list_of_untracked_teas_now = []
dict_of_flags = {"flag_is_start_tracking": flag_is_start_tracking,
                 "flag_is_delete_from_tracking": flag_is_delete_from_tracking,
                 "flag_is_resume_tracking": flag_is_resume_tracking}


@bot.message_handler(commands=['start'])
def start_message(message: types.Message):
    bot.send_message(message.chat.id, GREETINGS)


@bot.message_handler(commands=['help'])
def send_help(message: types.Message):
    bot.send_message(message.chat.id, HELP)


@bot.message_handler(commands=['start_tracking'])
def start_track(message: types.Message):
    global flag_is_start_tracking
    msg = "Введите ссылку на чай из перекрестка. На подобии: https://www.perekrestok.ru/cat/какой-то_адрес"
    bot.send_message(message.chat.id, msg)
    flag_is_start_tracking = True
    dict_of_flags["flag_is_start_tracking"] = flag_is_start_tracking


@bot.message_handler(commands=['all'])
def list_of_all_products(message: types.Message):
    msg = list_of_products_output(list_of_tracked_ever_teas)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['untracked'])
def untracked_now(message: types.Message):
    global dict_of_flags, flag_is_delete_from_tracking, flag_is_start_tracking, list_of_untracked_teas_now, flag_is_resume_tracking
    flag_is_delete_from_tracking = False
    flag_is_start_tracking = False
    list_of_untracked_teas_now = list(filter(lambda tracked_obj: not tracked_obj.ready, list_of_tracked_ever_teas))
    msg = list_of_products_output(list_of_untracked_teas_now)
    bot.send_message(message.chat.id, msg)
    bot.send_message(message.chat.id,
                     "Теперь Вы можете запомнить номер чая, который хотите снова отслеживать, после ввести номер(цифру), который вы запомнили и этот чай сново будет отслеживаться")
    flag_is_resume_tracking = True
    dict_of_flags["flag_is_start_tracking"] = flag_is_start_tracking
    dict_of_flags["flag_is_delete_from_tracking"] = flag_is_delete_from_tracking
    dict_of_flags["flag_is_resume_tracking"] = flag_is_resume_tracking


@bot.message_handler(commands=['tracked'])
def tracking_now(message: types.Message):
    global dict_of_flags, flag_is_start_tracking, flag_is_resume_tracking, list_of_tracked_teas_now, flag_is_delete_from_tracking
    flag_is_start_tracking = False
    flag_is_resume_tracking = False
    list_of_tracked_teas_now = list(filter(lambda tracked_obj: tracked_obj.ready, list_of_tracked_ever_teas))
    msg = list_of_products_output(list_of_tracked_teas_now)
    bot.send_message(message.chat.id, msg)
    bot.send_message(message.chat.id,
                     "Теперь Вы можете запомнить номер чая, который хотите удалить, после ввести номер(цифру), который вы запомнили и этот чай не будет отслеживаться")
    flag_is_delete_from_tracking = True
    dict_of_flags["flag_is_start_tracking"] = flag_is_start_tracking
    dict_of_flags["flag_is_delete_from_tracking"] = flag_is_delete_from_tracking
    dict_of_flags["flag_is_resume_tracking"] = flag_is_resume_tracking


def list_of_products_output(list_of_products: list):
    output = ""
    if len(list_of_products) != 0:
        msg = list(
            map(lambda tracked_obj: {"Ссылка": tracked_obj.url, "Отслеживается": "Да" if tracked_obj.ready else "Нет"},
                list_of_products))
        for item in msg:
            item_str = f"{item}"
            output = output + "\n" + item_str
    else:
        output = "Нет элементов данного вида"
    return output


def find_true_flag(dict_of_items: dict) -> str:
    for key in dict_of_items.keys():
        if dict_of_items[key]:
            return key
    return "None"


def is_index_valid(index, list_of_items: list) -> bool:
    try:
        if 1 <= int(index) <= len(list_of_items):
            return True
        return False
    except ValueError:
        return False


def is_url_valid(url: str) -> bool:
    match = re.findall(r"https://www.perekrestok.ru/cat/.+", url)
    if len(match) != 0:
        return True
    return False


def find_index_of_changed_product(product, list_of_products: list):
    for i in range(len(list_of_products)):
        if list_of_products[i] == product:
            return i
    return None


@bot.message_handler(content_types=['text'])
def create_tracked_tea(message: types.Message):
    global dict_of_flags, flag_is_start_tracking, flag_is_delete_from_tracking, flag_is_resume_tracking, list_of_tracked_teas_now, list_of_untracked_teas_now, list_of_tracked_ever_teas
    match1 = find_true_flag(dict_of_flags)
    match match1:
        case "flag_is_start_tracking":
            is_message_url_valid = is_url_valid(message.text)

            match is_message_url_valid:
                case True:
                    tracked_1 = TrackedTea(message.text)
                    tracked_1.get_data()
                    if tracked_1.price_new or tracked_1.price_old:
                        list_of_tracked_ever_teas.append(tracked_1)
                        list_of_tracked_teas_now.append(tracked_1)
                        msg = f"{tracked_1.price_new} - цена сейчас, {tracked_1.price_old}, - цена раньше."
                        bot.send_message(message.chat.id, msg)
                    else:
                        bot.send_message(message.chat.id,
                                         "Этот адрес бот не обрабатывает или Вы неправильно ввели адрес. Бот вас не понимает")

                case False:
                    msg = """Вы ввели недопустимый url.Заново введите команду /start_tracking. После введите допустимый url на подобии: https://www.perekrestok.ru/cat/какой-то_адрес
                    """
                    bot.send_message(message.chat.id, msg)

        case "flag_is_delete_from_tracking":
            is_message_index_valid = is_index_valid(message.text, list_of_tracked_teas_now)
            match is_message_index_valid:
                case True:
                    index = int(message.text) - 1
                    deleted_item = list_of_tracked_teas_now[index]
                    index_of_deleted_item_in_ever_tracked_list = find_index_of_changed_product(deleted_item,
                                                                                               list_of_tracked_ever_teas)
                    deleted_item.ready = False
                    list_of_tracked_ever_teas[index_of_deleted_item_in_ever_tracked_list] = deleted_item
                    msg = "Чай теперь не отслеживается"
                    bot.send_message(message.chat.id, msg)
                case False:
                    msg = """Вы ввели номер элемента, которого нет. Введите заново команду /tracked
                    """
                    bot.send_message(message.chat.id, msg)

        case "flag_is_resume_tracking":
            is_message_index_valid = is_index_valid(message.text, list_of_untracked_teas_now)
            match is_message_index_valid:
                case True:
                    index = int(message.text) - 1
                    deleted_item = list_of_untracked_teas_now[index]
                    index_of_resumed_item_in_ever_tracked_list = find_index_of_changed_product(deleted_item,
                                                                                               list_of_tracked_ever_teas)
                    deleted_item.ready = True
                    list_of_tracked_ever_teas[index_of_resumed_item_in_ever_tracked_list] = deleted_item
                    msg = "Чай теперь отслеживается"
                    bot.send_message(message.chat.id, msg)
                case False:
                    msg = """Вы ввели номер элемента, которого нет. Введите заново команду /untracked
                    """
                    bot.send_message(message.chat.id, msg)
        case "None":
            bot.send_message(message.chat.id, "Введите /help и/или какую-то команду из /help")
    flag_is_start_tracking = False
    flag_is_delete_from_tracking = False
    flag_is_resume_tracking = False
    dict_of_flags["flag_is_start_tracking"] = flag_is_start_tracking
    dict_of_flags["flag_is_delete_from_tracking"] = flag_is_delete_from_tracking
    dict_of_flags["flag_is_resume_tracking"] = flag_is_resume_tracking


def main():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()
