import matplotlib.pyplot as plt
import numpy as np

from sections import add_sections_to_rooms
from time_dec import dec_to_time


def heat_map_class(start_time, end_time, interval, building_codes=[]):
    sections = add_sections_to_rooms(building_codes)

    results = []
    titles = []
    for i in range(10):
        section = sections[i]
        section_time = []
        interval_time = []

        titles.append(section.title)

        interval_end = start_time
        while interval_end <= end_time:
            interval_start = dec_to_time(interval_end)
            interval_end = dec_to_time(interval_start + interval)

            interval_time.append(interval_start)

            class_during_interval = int(section.start_time) < interval_end and int(section.end_time) > interval_start

            if class_during_interval:
                section_time.append(1)
            else:
                section_time.append(0)
        results.append(section_time)

        print(section)
        print(interval_time)
        print(section_time)

    a = np.vstack(results)

    plt.imshow(a)
    plt.yticks(np.arange(len(titles)), titles)
    plt.xticks(np.arange(len(interval_time)), interval_time)
    plt.show()
