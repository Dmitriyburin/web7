from requests import get

API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'


def geocode(address):
    # Собираем запрос для геокодера.
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}

    # Выполняем запрос.
    response = get(geocoder_request, params=geocoder_params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {geocoder_request}
            Http статус: {response.status_code} ({response.reason})""")

    # Получаем первый топоним из ответа геокодера.
    # Согласно описанию ответа он находится по следующему пути:
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


# Получаем координаты объекта по его адресу.
def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Широта, преобразованная в плавающее число:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


# Получаем параметры объекта для рисования карты вокруг него.
def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return (None, None)
    full_name = (toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted'],
                 toponym['metaDataProperty']['GeocoderMetaData']['Address'].get('postal_code', False))
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    # Собираем координаты в параметр ll
    ll = (float(toponym_longitude), float(toponym_lattitude))

    # Рамка вокруг объекта:
    envelope = toponym["boundedBy"]["Envelope"]
    # левая, нижняя, правая и верхняя границы из координат углов:
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")

    # Вычисляем полуразмеры по вертикали и горизонтали
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0

    # Собираем размеры в параметр span
    span = (dx, dy)

    return ll, span, full_name


# Находим организации
def get_nearest_object(point, name='магазин'):
    ll = "{0},{1}".format(point[0], point[1])
    print(ll)
    geocoder_request = "https://search-maps.yandex.ru/v1/"
    params = {
        "apikey": 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3',
        "lang": 'RU',
        "ll": ll,
        "text": name,
        "spn": "0.0005, 0.0005",
        "rspn": '1',
        "results": '1',
        'type': 'biz'
    }
    # Выполняем запрос к геокодеру, анализируем ответ.
    response = get(geocoder_request, params=params)
    if not response:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {geocoder_request}
            Http статус: {response.status_code,} ({response.reason})""")

    # Преобразуем ответ в json-объект
    json_response = response.json()
    print(json_response)
    # Получаем первый топоним из ответа геокодера.
    try:
        return json_response['features'][0]['properties']['name']
    except IndexError:
        return 'Организации не найдены'
