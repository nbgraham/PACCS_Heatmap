import numpy as np

from time_dec import get_time_interval_name, DAYS
from time_span_length import get_total_possible, get_total_possible_all


class TimeWindow:
    def __init__(self, label, intervals_dec, start_time, end_time, m_to_f=False, days=DAYS):
        self.label = label
        self.start_time = start_time
        self.end_time = end_time
        self.m_to_f = m_to_f
        self.days = days

        self.total_slots = get_total_possible(intervals_dec, start_time, end_time, total_days=days) \
            if not m_to_f \
            else get_total_possible_all(intervals_dec, start_time=start_time, end_time=end_time)

        self.interval_names = TimeWindow.get_interval_names(self.total_slots, intervals_dec)

    def time_included(self, day_time_str):
        (day, time) = day_time_str.split(' ')
        if not self.m_to_f:
            included = day in self.days and self.end_time > int(time) >= self.start_time
        else:
            not_included = (day == 'M' and int(time) < self.start_time) or (day == 'F' and int(time) >= self.end_time)
            included = ~not_included
        return included

    def get_interval_names(total_slots, intervals_dec):
        interval_names = []

        indices_of_intervals_window_covers = np.transpose(total_slots.nonzero())
        for indices in indices_of_intervals_window_covers:
            i_day = indices[0]
            i_interval = indices[1]

            interval_name = get_time_interval_name(i_interval, i_day, intervals_dec)
            interval_names.append(interval_name)

        return interval_names


def get_default_time_windows(intervals_dec):
    normal = TimeWindow('8:30-4:30', intervals_dec, start_time=830, end_time=1630)
    prime_time = TimeWindow('Prime time', intervals_dec, start_time=900, end_time=1600)
    prime_time_mwf = TimeWindow('Prime time MWF', intervals_dec, start_time=900, end_time=1600, days=['M', 'W', 'F'])
    prime_time_tr = TimeWindow('Prime time TR', intervals_dec, start_time=900, end_time=1600, days=['T', 'R'])
    all = TimeWindow('All', intervals_dec, start_time=730, end_time=1630, m_to_f=True)

    windows = [normal, prime_time, prime_time_mwf, prime_time_tr, all]

    return windows