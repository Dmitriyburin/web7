import sys
import requests
from geocoder import get_coordinates, get_ll_span


class Search:
    def __init__(self, toponym_to_find="пр-т Кузнецова, 25к3"):
        self.ll, self.spn = get_ll_span(toponym_to_find)
        self.point_param = {
            "ll": ",".join(map(str, self.ll)),
            "spn": ",".join(map(str, self.spn)),
            "l": "map",
            "pt": ",".join(map(str, self.ll))
        }

    def map_api(self, params):
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print(f"Http статус: {response.status_code} ({response.reason})")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        map_file = "map.png"
        try:
            with open(map_file, "wb") as file:
                file.write(response.content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)

        return map_file
