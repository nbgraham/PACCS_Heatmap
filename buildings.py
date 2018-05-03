import csv
from math import sqrt

from str_dist import str_distance

LETTERS = ['A','B','C','D','E','F','G','H','I','J','K','L','M']
class Building:
    def __init__(self, code, name, number):
        self.code = code
        self.name = name
        self.number = number
        self.rooms = {}
        self.filtered_rooms = {}
        self.grid = None

    def __str__(self):
        return self.code + " " + str(self.name if self.name else "NO_NAME") + " " + (self.number if self.number else "NO_NUMBER")

    def __eq__(self,other):
        if other is None:
            return False
        return self.code == other.code and self.name == other.name and self.number == other.number

    def add_room(self, room):
        self.rooms[room.number] = room

    def get_room(self, room_number):
        return self.rooms.get(room_number)

    def get_rooms(self, filtered=False):
        return list(self.filtered_rooms.values()) if filtered else list(self.rooms.values())

    def get_sorted_rooms(self, filtered=False):
        rooms = self.get_rooms(filtered)
        rooms.sort(key=str)
        return rooms

    def filter_rooms(self, min_room_size, max_room_size):
        return {interval_name: room for interval_name, room in self.rooms.items()
                      if (min_room_size is None or min_room_size < room.seat_count) and (
                              max_room_size is None or max_room_size > room.seat_count)}

    def asdict(self):
        dict = {}
        dict['name'] = self.name
        dict['number'] = self.number
        dict['rooms'] = {number: room.asdict() for number, room in self.rooms.items()}
        dict['filtered_rooms'] = {number: room.asdict() for number, room in self.filtered_rooms.items()}
        return dict
        
    def dist(self, grid):
        if self.grid is None:
            return 10**10

        self_letter_num = LETTERS.index(self.grid[0])
        other_letter_num = LETTERS.index(grid[0])

        self_grid_num = int(self.grid[1:])
        other_grid_num = int(grid[1:])

        return sqrt((self_letter_num-other_letter_num)**2 + (self_grid_num - other_grid_num)**2)

    def dist_b(self, building):
        return self.dist(building.grid)
        
    
def get_building_list(building_codes, filename):
    buildings = {}
    with open(filename, 'rt', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip the header

        for row in reader:
            code = row[0]
            description = row[1].split(' (') # Name (Code) e.g. Devon Energy Hall (007)
            name = description[0]

            if len(description) > 1:
                number = description[1].replace(')','')
            else:
                number = None

            building = Building(code, name, number)

            if len(building_codes) == 0 or code in building_codes:
            # Dict on code because that is what the class_csv uses and there are much more classes than anything else
                buildings[code] = building

    return buildings


def get_building_by_code(buildings, code):
    return buildings.get(code) #return None if code is not in dict


def get_building_by_name(buildings, name, excluded_building_codes=['AC']):
    min_dist = 1.5
    best_match = None
    for code, building in buildings.items():
        if code in excluded_building_codes:
            continue
        d = str_distance(name, building.name.replace(" Hall","").replace(" Center","").replace(" Building",""))/len(name.replace(" Hall","").replace(" Center","").replace(" Building",""))
        if name in building.name:
            d /= 2
        if d < min_dist:
            min_dist = d
            best_match = building
        if building.code == 'SCI':
            alternate_name = "Old Science"
            if name in alternate_name:
                return building
            if str_distance(name, alternate_name) / len(name) < 0.3:
                return building

    return best_match


if __name__ == "__main__":
    get_building_list()