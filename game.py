from random import randint
from telebot import types
import telebot
import psycopg2
from eggManGame import *

TOKEN = ''

bot = telebot.TeleBot(TOKEN)
 
 
def games_handler(id_game, message, team_id, user_id, mode):
    match(id_game):
        case 1:
            pass
        case 2:
            pass
        case 3:
            conn = get_conn()
            cursor = conn.cursor()
            match(mode):
                case 'sandbox':
                    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                    if cursor.fetchone() == None:
                        cursor.execute("INSERT INTO users (user_id, best_score, user_state, egg_ammount, correct_ans, round) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, 0, 'NONE', 2, randint(1, 19), 1))
                        message = '/start'
                        conn.commit()
                    elif '/start' in message.lower():
                        set_user_state(user_id, 'NONE')
                    match(get_user_state(user_id)):
                        case 'NONE':
                            if '/start' in message.lower():
                                set_egg_ammount(user_id, 2)
                                clear_user_answers(user_id)
                                set_correct_ans(user_id, randint(1, 19))
                                set_user_state(user_id, 'PLAYING_GAME')
                                return (
                                        'Добро пожаловать в демо!\n'
                                        'Дано 20-этажное здание. Если яйцо сбросить с высоты N-го этажа (или с меньшей высоты), оно останется целым, а иначе разобьётся. У вас есть два яйца. Найдите максимальное N.\n'
                                        'Вам предстоит вводить номер этажа, с которого будет сбрасываться яйцо. Если данное число окажется больше правильного, то яйцо разобьётся, а если наоборот, то останется целым.\n'
                                        'Как только все яйца будут разбиты, то напишите /ans (ответ).\ans'
                                        'Если вы поняли правила, то отправьте что-нибудь'
                                )
                            return 'Игра окончена. Пропишите /start для того чтобы начать заново'
                        case 'PLAYING_GAME':
                            egg_ammount = get_egg_ammount(user_id)
                            set_user_state(user_id, 'WAITING_FOR_INPUT')
                            return (
                                    f'Оставшиеся яйца: {'🥚'*egg_ammount}\n'
                                    'Введите высоту, с которой сбросить яйцо (число от 1 до 20)'
                            )
                        case 'WAITING_FOR_INPUT':
                            correct_ans = get_correct_ans(user_id)
                            egg_ammount = get_egg_ammount(user_id)
                            user_inp = message
                            try:
                                user_inp = int(user_inp)
                                if user_inp > 0 and user_inp < 21:
                                    append_user_answers(user_id, user_inp)
                                    set_user_state(user_id, 'INPUT_GOT')
                                else:
                                    raise ValueError
                            except ValueError:
                                set_user_state(user_id, 'WAITING_FOR_INPUT')
                                if '/ans' in message:
                                    return (
                                        'Ещё рано выводить ответ. Нужно для начала разбить все яйца\n'
                                        'Введите число от 1 до 99'
                                    )
                                return 'Введите число от 1 до 20'
                            user_ans = user_inp
                            match (check_if_broke(user_ans, correct_ans)):
                                case 0:
                                    set_user_state(user_id, 'WAITING_FOR_INPUT')
                                    return (
                                        'Фух, не разбилось 😌\n'
                                        f'Оставшиеся яйца: {'🥚'*egg_ammount}\n'
                                        'Введите следующее число:'
                                    )
                                case 1:
                                    if egg_ammount == 2:
                                        set_egg_ammount(user_id, egg_ammount-1)
                                        set_user_state(user_id, 'WAITING_FOR_INPUT')
                                        return (
                                            'Разбилось 😳\n'
                                            f'Оставшиеся яйца: {'🥚'*(egg_ammount-1)}\n'
                                            'Введите следующее число:'
                                        )
                                    else:
                                        set_user_state(user_id, 'WAITING_FOR_ANSWER')
                                        return (
                                            'Разбилось 😳\n'
                                            'Яйца кончились. Пропишите /ans (ответ) чтобы ответить на вопрос'
                                        )
                        case 'WAITING_FOR_ANSWER':
                            if '/ans' in message:
                                try:
                                    if len(message.split()) > 2:
                                        raise IndexError
                                    cur_ans = int(message.split()[1])
                                    user_last_try = get_user_last_answer(user_id)
                                    if cur_ans > 0 and cur_ans < 21:
                                        if user_last_try - get_correct_ans(user_id) and cur_ans == get_correct_ans(user_id):
                                            score = count_score(user_id)
                                            set_user_best_score(user_id, max(score, get_user_best_score(user_id)))
                                            set_user_state(user_id, 'NONE')
                                            return (
                                                'Поздравляем! Вы ответили правильно!\n'
                                                f'Ваш результат: {score}\n'
                                                'Напишите /start чтобы сыграть ещё раз'
                                            )
                                        else:
                                            set_user_state(user_id, 'NONE')
                                            return (
                                                'Ошибка! Вы ответили неверно!\n'
                                                'Напишите /start чтобы сыграть ещё раз'
                                            )
                                    else:
                                        raise ValueError
                                except ValueError:
                                    return 'Введите /ans (ответ). Ответ - число в пределах от 1 до 20'
                                except IndexError:
                                    return 'Введите /ans (ответ). Ответ - число в пределах от 1 до 20'
 
                            else:
                                return (
                                    'Вам нужно ввести /ans (ответ), а не что-то другое'
                                )
                        case _:
                            return 'Игра окончена. Пропишите /start для того чтобы начать заново'
 
                case 'final_round':
                    cursor.execute("SELECT * FROM users WHERE user_id = %s", (team_id,))
                    if cursor.fetchone() == None:
                        cursor.execute("INSERT INTO users (user_id, best_score, user_state, egg_ammount, correct_ans, round) VALUES (%s, %s, %s, %s, %s, %s)", (team_id, 0, 'NONE', 2, 99, 1))
                        message = '/start'
                        conn.commit()
                    elif '/start' in message.lower():
                        set_user_state(team_id, 'NONE')
                    match(get_user_state(team_id)):
                        case 'NONE':
                            if '/start' in message.lower():
                                set_egg_ammount(team_id, 2)
                                clear_user_answers(team_id)
                                match(get_round(team_id)):
                                    case 1:
                                        set_correct_ans(team_id, randint(1, 10))
                                        set_user_state(team_id, 'PLAYING_GAME')
                                        return (
                                            'Добро пожаловать в игру!\n'
                                            'Однажды, во время летней сессии, на экзамен по алгебре пришла группа нерадивых учеников, среди которых есть ваш друг Никита. Пока другие сдавали контрольные, отвечали и уходили с оценками «хорошо» и «отлично», они сидели и думали, что же им делать. Спустя некоторый (достаточно большой) промежуток времени, преподаватель позвал их к себе и сказал: «Ну что, !!!!!, сейчас будет раздача слонов. Так как никто не может ответить, то мы сыграем в игру. Знаете же задачу о 2 яйцах и 20-этажном здании? Так вот, вам предстоит решить ту же задачу, но только для 2 яиц и 100 этажного здания. Так как вас много, то поставить «удовлетворительно», я смогу только 5 лучшим. Ваш рейтинг будет средним арифметическим очков из пяти раундов. Чем больше отклонение от моего решения, тем меньше очков вы получите.» Вы хотите спасти своего друга от пересдачи, поэтому решили ему помочь. Для этого подсказывайте Никите, с какого этажа бросать яйцо, а он будет говорить, разбилось оно или нет.\n'
                                            'Как только все яйца будут разбиты, то напишите /ans (ответ).\n'
                                            'По окончании 5 раундов вам станет доступна команда /best, которая отобразит 5 лучших учеников и тогда станет понятно, отправится ли Никита на пересдачу или нет\n'
                                            'Раунд 1\n'
                                            'Напишите что-нибудь для продолжения'
                                        )
                                    case 2:
                                        set_correct_ans(team_id, randint(30, 40))
                                    case 3:
                                        set_correct_ans(team_id, randint(70, 80))
                                    case 4:
                                        set_correct_ans(team_id, randint(80, 90))
                                    case 5:
                                        set_correct_ans(team_id, randint(60, 98))
                                    case 6:
                                        return 'Все раунды оконены. Напишите /best, чтобы посмотреть таблицу лидеров'
                                set_user_state(team_id, 'PLAYING_GAME')
                                return (
                                        f'Раунд {get_round(team_id)}\n'
                                        'Напишите что-нибудь для продолжения'
                                )
                            if '/best' in message.lower():
                                if get_round(team_id) == 6:
                                    set_user_best_score(team_id, int(get_user_best_score(team_id)/5))
                                    return print_top(team_id)
                                else:
                                    return 'Ещё рано смотреть результаты. Сначала надо закончить игру'
                            return 'Напишите /start для того чтобы начать раунд'
                        case 'PLAYING_GAME':
                            egg_ammount = get_egg_ammount(team_id)
                            set_user_state(team_id, 'WAITING_FOR_INPUT')
                            return (
                                    f'Оставшиеся яйца: {'🥚'*egg_ammount}\n'
                                    'Введите высоту, с которой сбросить яйцо (число от 1 до 99)'
                            )
                        case 'WAITING_FOR_INPUT':
                            correct_ans = get_correct_ans(team_id)
                            egg_ammount = get_egg_ammount(team_id)
                            user_inp = message
                            try:
                                user_inp = int(user_inp)
                                if user_inp > 0 and user_inp < 100:
                                    append_user_answers(team_id, user_inp)
                                    set_user_state(team_id, 'INPUT_GOT')
                                else:
                                    raise ValueError
                            except ValueError:
                                set_user_state(team_id, 'WAITING_FOR_INPUT')
                                if '/ans' in message:
                                    return (
                                        'Ещё рано выводить ответ. Нужно для начала разбить все яйца\n'
                                        'Введите число от 1 до 99'
                                    )
                                return 'Введите число от 1 до 99'
                            user_ans = user_inp
                            match (check_if_broke(user_ans, correct_ans)):
                                case 0:
                                    set_user_state(team_id, 'WAITING_FOR_INPUT')
                                    return (
                                        'Фух, не разбилось 😌\n'
                                        f'Оставшиеся яйца: {'🥚'*egg_ammount}\n'
                                        'Введите следующее число:'
                                    )
                                case 1:
                                    if egg_ammount == 2:
                                        set_egg_ammount(team_id, egg_ammount-1)
                                        set_user_state(team_id, 'WAITING_FOR_INPUT')
                                        return (
                                            'Разбилось 😳\n'
                                            f'Оставшиеся яйца: {'🥚'*(egg_ammount-1)}\n'
                                            'Введите следующее число:'
                                        )
                                    else:
                                        set_user_state(team_id, 'WAITING_FOR_ANSWER')
                                        return (
                                            'Разбилось 😳\n'
                                            'Яйца кончились. Пропишите /ans (ответ) чтобы ответить на вопрос'
                                        )
                        case 'WAITING_FOR_ANSWER':
                            if '/ans' in message:
                                try:
                                    if len(message.split()) > 2:
                                        raise IndexError
                                    cur_ans = int(message.split()[1])
                                    user_last_try = get_user_last_answer(team_id)
                                    if cur_ans > 0 and cur_ans < 100:
                                        if user_last_try - get_correct_ans(team_id) and cur_ans == get_correct_ans(team_id):
                                            score = count_score(team_id)
                                            set_user_best_score(team_id, score + get_user_best_score(team_id))
                                            set_user_state(team_id, 'NONE')
                                            set_round(team_id, get_round(team_id)+1)
                                            return (
                                                'Поздравляем! Вы ответили правильно!\n'
                                                f'Ваш результат: {score}\n'
                                                'Напишите /start чтобы перейти к следующему ранду'
                                            )
                                        else:
                                            set_user_state(team_id, 'NONE')
                                            set_round(team_id, get_round(team_id)+1)
                                            return (
                                                'Ошибка! Вы ответили неверно!\n'
                                                'Ваш результат: 0\n'
                                                'Напишите /start чтобы перейти к следующему ранду'
                                            )
                                    else:
                                        raise ValueError
                                except ValueError:
                                    return 'Введите /ans (ответ). Ответ - число в пределах от 1 до 99'
                                except IndexError:
                                    return 'Введите /ans (ответ). Ответ - число в пределах от 1 до 99'
 
                            else:
                                return (
                                    'Вам нужно ввести /ans (ответ), а не что-то другое'
                                )
                        case 'FINAL':
                            pass
                        case _:
                            return 'Игра окончена. Пропишите /start для того чтобы начать заново'
 

if __name__ == '__main__':
    while(1):
        print(games_handler(3, input(), 1111, 123, 'final_round'))