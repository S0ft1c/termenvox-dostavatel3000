from requests import get, post

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

    return sorted(list(ans))


def get_all_dates():
    date_list = get_date()

    return date_list


def get_info(date: str):  # dd-mm-yy ВЫДАЕТ ВСЕ ДАННЫЕ ДЛЯ ФРОНТА ПО ДНЮ
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
        'true_rooms': rooms,
        'true_rooms_count': len(rooms),
        'rooms_count': data['rooms_count'],
        'windows': data['windows_for_room_list'],
        'server_answer': server_answer,
        'date': date
    }

    return data_to_return


print(get_info('25-01-23'))
