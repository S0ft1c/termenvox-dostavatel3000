from requests import get, post
from flask import Flask, jsonify, request
from flask import Flask, render_template_string, flash, redirect, url_for, render_template
from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms.validators import DataRequired
from pprint import pprint

app = Flask(__name__)
app.config['SECRET_KEY'] = '1111'

TOKEN = 'ppo_11_30006'
HEADERS = {'X-Auth-Token': TOKEN, 'Content-Type': 'application/json'}


def get_date():
    req = get('https://olimp.miet.ru/ppo_it_final/date', headers=HEADERS)
    date_list = req.json()['message']

    return date_list


def get_date_info(day, month, year):
    stroka = \
        f'https://olimp.miet.ru/ppo_it_final?day={
            day}&month={month}&year={year}'

    print(stroka)
    req = get(stroka, headers=HEADERS)
    print(req)
    if req.status_code != 200:
        return
    data = req.json()['message']
    print(data)
    rooms_count = data['flats_count']['data']
    windows_for_room_list = data['windows_for_flat']['data']
    windows_dict = data['windows']['data']

    return_data = {
        'rooms_count': rooms_count,
        'windows_for_room_list': windows_for_room_list,
        'windows_dict': windows_dict
    }

    return return_data


def post_answer(rooms: list, date: str):
    count = len(rooms)
    data = {
        "data": {
            "count": count,
            "rooms": rooms
        },
        "date": date
    }
    print(data)
    req = post(f'https://olimp.miet.ru/ppo_it_final',
               headers={'X-Auth-Token': TOKEN, 'Content-Type': 'application/json'}, data=data)
    print(req)

    answer = req.json()['message']

    return answer


def formula(cnt_rooms: int, cnt_winds: list, lights: dict):
    lights = list(lights.values())
    print(lights)
    ans = set()

    for i in range(len(lights)):
        for j in range(len(lights[i])):
            if lights[i][j] == True:
                p = j
                room_num = (3 * i) + 1
                wids_idx = 0
                while p - cnt_winds[wids_idx] >= 0 and wids_idx < len(cnt_winds):
                    p -= cnt_winds[wids_idx]
                    wids_idx += 1
                    room_num += 1
                ans.add(room_num)

    ans = sorted(list(ans))

    return ans


def get_all_dates():
    date_list = get_date()

    return date_list


def get_info(date: str):
    day = date.split('-')[0]
    month = date.split('-')[1]
    year = date.split('-')[2]

    data = get_date_info(day, month, year)
    rooms = formula(data['rooms_count'], data['windows_for_room_list'], {
        "floor_1": data['windows_dict']['floor_1'],
        "floor_2": data['windows_dict']['floor_2'],
        "floor_3": data['windows_dict']['floor_3'],
        "floor_4": data['windows_dict']['floor_4']
    })
    server_answer = post_answer(rooms, date)
    # server_answer = False

    window_list = []
    room = 0
    for _ in range(1, 5):
        room_list = []
        for windows_for_room in data['windows_for_room_list']:
            room += 1
            for __ in range(windows_for_room):
                room_list.append(room)
        window_list.append(room_list)

    data_to_return = {
        'window_list': window_list,
        'true_rooms': list(map(str, rooms)),
        'num_true_rooms': rooms,
        'true_rooms_count': len(rooms),
        'rooms_count': data['rooms_count'],
        'windows': list(map(str, data['windows_for_room_list'])),
        'server_answer': server_answer,
        'date': date
    }

    return data_to_return


class DateForm(FlaskForm):
    date = DateField('Выберите дату', format='%Y-%m-%d',
                     validators=[DataRequired()])

#  -- - -- -- -- -- - - - - routes


@app.route('/choose_date', methods=['GET', 'POST'])
def choose_date():
    form = DateForm()
    if form.validate_on_submit():
        # Если форма успешна, можно здесь обработать данные

        year, month, day = str(form.date.data).split('-')
        year = year[-2:]
        data = get_info(f'{day}-{month}-{year}')
        pprint(data)

        return render_template('result_date.html', **data)

    return render_template('choose_date.html', form=form)


@app.route('/all_days', methods=['GET'])
def alldays():
    days = [str(el) for el in get_date()]
    return render_template('all_days.html', days=days)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()

    # print(get_info('25-01-23'))

    # print(get_date())
    # print(get_date_info(day='30', month='10', year='23'))
    # print(post_answer(count=4, rooms=[3, 5, 9, 10], date='01-05-21'))
    # print(formula(3, [3, 2, 1],
    #               {
    #     "floor_1": [False, True, False, True, False, False],
    #     "floor_2": [True, False, True, False, False, True],
    #     "floor_3": [False, False, True, False, True, False],
    #     "floor_4": [False, False, False, True, False, True]
    # }))
