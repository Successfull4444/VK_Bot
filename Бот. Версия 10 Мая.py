import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
from flask import Flask

import os
import sys

import pygame
import requests


TOKEN = ''  # Здесь нужно ввести Token

vk = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk)


# ------------------------------------- Далее идёт блок функций для обработки хим. уравнений
NUMBERS = {1: '',
           2: '₂',
           3: '₃',
           4: '₄',
           5: '₅',
           6: '₆',
           7: '₇',
           8: '₈',
           9: '₉'}

PERIODIC_TABLE = {
    'H': 1,
    'He': 2,
    'Li': 3,
    'Be': 4,
    'B': 5,
    'C': 6,
    'N': 7,
    'O': 8,
    'F': 9,
    'Ne': 10,
    'Na': 11,
    'Mg': 12,
    'Al': 13,
    'Si': 14,
    'P': 15,
    'S': 16,
    'Cl': 17,
    'Ar': 18,
    'K': 19,
    'Ca': 20,
    'Sc': 21,
    'Ti': 22,
    'V': 23,
    'Cr': 24,
    'Mn': 25,
    'Fe': 26,
    'Co': 27,
    'Ni': 28,
    'Cu': 29,
    'Zn': 30,
    'Ga': 31,
    'Ge': 32,
    'As': 33,
    'Se': 34,
    'Br': 35,
    'Kr': 36,
    'Rb': 37,
    'Sr': 38,
    'Y': 39,
    'Zr': 40
}


left = [[('S', 1)], [('K', 1), ('O', 1), ('H', 1)]]
right = [[('K', 2), ('S', 1)], [('K', 2), ('S', 1), ('O', 3)], [('H', 2), ('O', 1)]]


def one_word_to_algebraic(compound):
    result = ''
    while compound[0].isdigit():  # Убираем имеющиеся коэффициенты перед формулой.
        compound = compound[1:]

    memory_box = ''  # Ячейка памяти, хранящая в себе предыдущую букву.
    for i in compound:  # Разделяем формулу пробелами на цифры и буквы.
        if not memory_box:
            result += i
            memory_box = i
        elif i.isdigit() and memory_box.isdigit():
            result += i
            memory_box = i
        elif i.isalpha() and memory_box.isalpha():
            result += i
            memory_box = i
        else:
            result += ' ' + i
            memory_box = i

    # Сейчас имеется формула, в которой цифры и буквы уже разделены пробелами,
    # но элементы ещё только предстоит разделить пробелами. Это будет сделано в слитном блоке кода ниже.
    memory_box = ''  # Очищаем ячейку памяти перед использованием.
    element_separated_result = ''
    for i in reversed(result):
        if i.isdigit():
            element_separated_result = i + element_separated_result
        elif i == ' ':
            element_separated_result = ' ' + element_separated_result
        elif i.isalpha():
            if i in PERIODIC_TABLE or (i + memory_box) in PERIODIC_TABLE:
                element_separated_result = ' ' + i + element_separated_result
            else:  # Здесь может возникнуть ошибка. Нужно сделать проверку на допустимость всех символов.
                element_separated_result = i + element_separated_result
        memory_box = i  # После всех действий обновляем ячейку памяти.

    this_compound_list = element_separated_result.split()  # Создаём список, содержащий в себе каждый элемент
    # и индекс по отдельности.
    for i in range(len(this_compound_list)):
        if this_compound_list[i].isdigit():  # Переводим индексы в целочисленный тип int.
            this_compound_list[i] = int(this_compound_list[i])


    # В слитном блоке кода ниже добавляются индексы (единицы)
    all_indexs = []
    memory_box = False
    for i in range(len(this_compound_list)):
        element = this_compound_list[i]
        if type(memory_box) is str and type(element) is str:
            all_indexs.append(1)  # Добавляем в список индекс (единичку) в случае, если она отсутствует.
            all_indexs.append(element)  # Лишь затем добавляем следующий элемент.
        else:
            all_indexs.append(element)
        memory_box = element
    if type(element) is str:  # Добавляем в конец индекс, если он отсутствует.
        all_indexs.append(1)

    final_formula = []
    for i in range(0, len(all_indexs), 2):
        elem_with_index = (all_indexs[i], all_indexs[i + 1])
        final_formula.append(elem_with_index)
    return final_formula


def setting_the_coefficients(left, right):
    coef_left = [1, 1]
    coef_right = [1, 1, 1]


def algebraic_to_word(algebraic):
    def f(n):
        return NUMBERS[str(n)]

    result = ''
    for elem in algebraic:
        result += f'{elem[0]}{f(elem[1])}'
    return result


def show():
    def proc(n):
        return ''

    coef_left = [1, 1]
    coef_right = [1, 1, 1]
    left_result = ''
    rigth_result = ''
    for i in range(len(coef_left)):
        left_result += f"{proc(coef_left[i])}{left[i][0]}{left[i][1]}"
    for i in range(len(coef_right)):
        left_result += f"{proc(coef_right[i])}{right[i][0]}{right[i][1]}"
    return f"{left_result} ⟶ {rigth_result}"


def beautifizing(formula):
    result = ''
    for i in formula:
        if i.isdigit():
            number = int(i)
            result += NUMBERS[number]
        else:
            result += i
    return result


# ------------------------------------------ Блок хим. уравнений окончен. Далее идёт часть,
# отвечающая за получение запросов с сайтов.


def repair():
    api_server = f"http://api.forismatic.com/api/1.0/"

    response = requests.get(api_server)
    data = response.json()

    return data


# ------------------------------------------ Запросная часть окончена. Далее идёт часть,
# отвечающая за показ формул с помощью Flask.


def formulas_showing(formula):
    app = Flask(__name__)

    @app.route('/')
    @app.route('/index')
    def index():
        return formula

    if __name__ == '__main__':
        app.run(port=8080, host='127.0.0.1')
    return "http://127.0.0.1:5000/"


# ------------------------------------------- Flask-часть окончена. Далее идёт часть Яндекс.Карт.


def yandex_maps():
    def using_geocoder(city):  # Получение координат объекта по названию.
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={city}&format=json"

        df_response = requests.get(geocoder_request)
        if df_response:
            json_response = df_response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            toponym_coordinates = toponym["Point"]["pos"]
            print(f"{toponym_address} имеет координаты: {toponym_coordinates}")
            return toponym_coordinates
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", df_response.status_code, "(", df_response.reason, ")")

    while True:
        city_name = input()
        scale_coefficient = 0.002  # Коэффициент масштабирования
        scale_x = 1 * scale_coefficient
        scale_y = 1 * scale_coefficient
        k = 8

        coords_list = using_geocoder(city_name).split()
        coords_str = ','.join(coords_list)
        print(coords_str)

        def getting_coordinates_of_place(df_coords):
            map_request = f"http://static-maps.yandex.ru/1.x/?ll={df_coords}&spn={scale_x},{scale_y}&l=sat,skl"
            response = requests.get(map_request)

            if not response:
                print("Ошибка выполнения запроса:")
                print(map_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)

            map_file = "map.png"
            with open(map_file, "wb") as file:
                file.write(response.content)
            return map_file

        image = getting_coordinates_of_place(coords_str)
        pygame.init()
        screen = pygame.display.set_mode((600, 450))
        screen.blit(pygame.image.load(image), (0, 0))
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                print(8)
                if event.type == pygame.QUIT:
                    running = False

                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    motion_step = scale_y / k
                    print(coords_list)
                    coords_list = [float(number) for number in coords_list]
                    coords_list[1] += motion_step  # Меняем список с координатами, а за ним и строку с координатами.
                    coords_list = [str(number) for number in coords_list]
                    coords_str = ','.join(coords_list)

                    image = getting_coordinates_of_place(coords_str)
                    screen.fill((0, 0, 0))
                    screen.blit(pygame.image.load(image), (0, 0))
                    pygame.display.flip()
                    down_key = True
                if keys[pygame.K_DOWN]:
                    motion_step = -scale_y / k
                    print(coords_list)
                    coords_list = [float(number) for number in coords_list]
                    coords_list[1] += motion_step  # Меняем список с координатами, а за ним и строку с координатами.
                    coords_list = [str(number) for number in coords_list]
                    coords_str = ','.join(coords_list)

                    image = getting_coordinates_of_place(coords_str)
                    screen.fill((0, 0, 0))
                    screen.blit(pygame.image.load(image), (0, 0))
                    pygame.display.flip()
                    down_key = True
                if keys[pygame.K_RIGHT]:
                    motion_step = scale_x / k
                    print(coords_list)
                    coords_list = [float(number) for number in coords_list]
                    coords_list[0] += motion_step  # Меняем список с координатами, а за ним и строку с координатами.
                    coords_list = [str(number) for number in coords_list]
                    coords_str = ','.join(coords_list)

                    image = getting_coordinates_of_place(coords_str)
                    screen.fill((0, 0, 0))
                    screen.blit(pygame.image.load(image), (0, 0))
                    pygame.display.flip()
                    down_key = True
                if keys[pygame.K_LEFT]:
                    motion_step = -scale_x / k
                    print(coords_list)
                    coords_list = [float(number) for number in coords_list]
                    coords_list[0] += motion_step  # Меняем список с координатами, а за ним и строку с координатами.
                    coords_list = [str(number) for number in coords_list]
                    coords_str = ','.join(coords_list)

                    image = getting_coordinates_of_place(coords_str)
                    screen.fill((0, 0, 0))
                    screen.blit(pygame.image.load(image), (0, 0))
                    pygame.display.flip()
                    down_key = True
        pygame.quit()
        os.remove(image)


# -------------------------------------------- Часть Яндекс.Карт окончена. Далее идёт цитатная часть.




QUOTES = ['Необычное направление мысли!',
                          'Интересно!',
                          'Вы ошибаетесь, дорогой друг!',
                          'Точно!',
                          'Да.',
                          'Нет.',
                          'Что-то?',
                          'Вот это да!',
                          'Приятно слышать такие слова!',
                          'Аудиозапись тишины полностью заглушила шум вскрытия сейфа, и похитители остались незамеченными.',
                          'Слово - серебро, молчание - золото.']


def random_quote():
    global QUOTES
    mode = 'random'
    api_server = f"https://zenquotes.io/api/{mode}/"

    response = requests.get(api_server)
    data = response.json()
    phrase = data[0]['q'] + '\n\n\t\t' + data[0]['a']
    return phrase


# ---------------------------------------------


def send_messages(df_chat_id, text):
    random_id = random.randint(0, 1000000000)
    vk.method('messages.send', {'chat_id': df_chat_id, 'message': text, 'random_id': random_id})


def clearing():  # Нужно доработать эту функцию.
    vk.method('messages.deleteConversation', {'peer_id': peer_id, 'user_id': user_id})


def messages_processing(input_msg):  # Эта функция отвечает за создание ответа на сообщение.
    if input_msg == 'Очистка':
        clearing()
    if 'УРАВНЯТЬ' in input_msg.upper():
        return beautifizing(input_msg)
    return random_quote()


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            if event.from_chat:
                msg = event.text
                chat_id = event.chat_id
                peer_id = event.peer_id
                user_id = event.user_id
                reply = messages_processing(msg)
                send_messages(chat_id, reply)
