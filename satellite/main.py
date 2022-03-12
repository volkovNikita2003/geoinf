from pyorbital.orbital import Orbital
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import math

# ----- график -----
# отрисовка окружностей
def drawCircles(axes):
    start_koord = (0, 0)
    radius = [90 - i for i in range(0, 100, 10)]

    for i in range(len(radius)):
        if radius[i] == 0:
            circle = plt.Circle(start_koord,
                                 radius=1,
                                 fill=True,
                                 color="black")
        else:
            circle = plt.Circle(start_koord,
                                radius=radius[i],
                                fill=False,
                                color="black")
        axes.add_patch(circle)
        plt.text(0, radius[i]+1, str(90 - radius[i]), horizontalalignment="center")

# создание графика
def draw_graph(x, y):
    # Задаем размеры графика
    plt.xlim(-100, 100)
    plt.ylim(-100, 100)

    # Получим текущие оси
    axes = plt.gca()
    axes.set_aspect("equal")

    # Отрисовка окружностей
    drawCircles(axes)

    # Скрываем горизонтальные оси графика
    plt.axis('off')

    # строим точечный график
    plt.scatter(x, y, s=1)


# ----- работа со спутником -----

# время через которое пересчитывать положение спутника и антенны (сек)
dt_ = 1

# задаем спутник
noaa19 = Orbital("NOAA-19")

# начальные параметры для вычисления периодов видимости спутника
utc_time = datetime(2022, 3, 13, 0, 0, 0) # начало наблюдения
length = 24 # кол-во часов, которое надо наблюдать
lon = 55.93025287726114 # долгота наблюдателя на Земле
lat = 37.518133949435345 # широта наблюдателя на Земле
alt = 0.192 # Высота над уровнем моря положения наблюдателя на земле (км)

# информация о периодах видимости спутника
# формат данных (время начала видимости, время конца видимости, время масимального подъема спутника над горизонтом)
visibility_time = noaa19.get_next_passes(utc_time, length, lon, lat, alt)

for i in range(len (visibility_time)):
    # время видимости спутника в секундах
    dt_sec = int(visibility_time[i][1].timestamp() - visibility_time[i][0].timestamp())

    mass_x = []
    mass_y = []
    for j in range(0, dt_sec, dt_):
        # момент времени, в который нужно определить положение антенны
        current_datetime = visibility_time[i][0] + timedelta(seconds=j)

        # координаты спутника в момент current_datetime
        # polar_coordinates[0] -- азимут; polar_coordinates[1] -- высота подъема спутника над горризонтом
        polar_coordinates = noaa19.get_observer_look(current_datetime, lon, lat, alt)
        # вычислени координат спутника на графике по polar_coordinates (подробнее в "пересчет координат.png")
        r = 90 - polar_coordinates[1]
        x = r * math.cos(polar_coordinates[0] / 180 * math.pi - math.pi / 2)
        y = r * math.sin(polar_coordinates[0] / 180 * math.pi - math.pi / 2)
        mass_x.append(x)
        mass_y.append(y)

    # отрисовываем график
    draw_graph(mass_x, mass_y)
    # сохраняем график
    title_str = visibility_time[i][0].isoformat()
    title_str = title_str.split(".")[0]
    title_str = title_str.replace(":", ".")
    plt.savefig("graphics/{}.png".format(title_str))
    # показываем график
    #plt.show()

# сохранение данных о начале и конце видимости спутника в файл
with open("data.txt", "w") as file:
    count = 0
    file.write("{:^1}  {:^35}   {:^35}   {:^35}\n".format("#", "Start of satellite visibility", "End of satellite visibility", "Satellite visibility time"))
    for i in range(len(visibility_time)):
        count += 1
        file.write("{:^1}. {:^35}   {:^35}   {:^35}\n".format(str(count),
                                                              str(visibility_time[i][0]),
                                                              str(visibility_time[i][1]),
                                                              str(visibility_time[i][1] - visibility_time[i][0])
                                                              ))