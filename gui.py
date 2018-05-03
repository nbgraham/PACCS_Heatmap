from tkinter import *
from tkinter import filedialog
import os

from analysis import analyze
from plot import plot_heat_map, plot_room_efficiency
from run import get_room_occ, get_buildings_with_sections_for_time


class FileEntry:
    def __init__(self, master, name="Choose File", on_open=None, default_value=None, display_length=45):
        self.file_label = Label(master, text=name)
        self.file_entry = Entry(master, width=50)
        self.file_button = Button(master, text="...", command=self.open_file)
        self.on_open = on_open
        self.file_path = None
        self.display_length = display_length

        self.set_value(default_value)

    def set_value(self, file_path):
        self.file_path = file_path

        truncated_file_path = file_path
        if len(truncated_file_path) > self.display_length:
            truncated_file_path = "..." + truncated_file_path[-1*self.display_length:]

        self.file_entry.delete(0, END)
        self.file_entry.insert(0, truncated_file_path)

        if self.on_open is not None:
            self.on_open(file_path)

    def place(self, row=None):
        self.file_label.grid(row=row, column=0, sticky=E)
        self.file_entry.grid(row=row, column=1)
        self.file_button.grid(row=row, column=2)

    def open_file(self):
        file_path = filedialog.askopenfilename()
        self.set_value(file_path)


class OptionalEntry:
    def __init__(self, master, text, value=0):
        self.enabled = False

        def toggle_enabled():
            self.enabled = ~self.enabled
            self.entry.config(state=(NORMAL if self.enabled else DISABLED))

        self.checkbox = Checkbutton(master, command=toggle_enabled)
        self.label = Label(master, text=text)
        self.entry = Spinbox(master, from_=0, to=1000, state=DISABLED, value=value)

    def place(self, row=None):
        self.checkbox.grid(row=row, column=0, sticky=E)
        self.label.grid(row=row, column=0)
        self.entry.grid(row=row, column=1)

    def value(self):
        return int(self.entry.get()) if self.enabled else None


class ScheduleExplorer:
    def __init__(self):
        self.building_codes = []

        self.buildings = {}
        self.intervals_dec = {}

        self.building_listbox = None
        self.min_size_entry = None
        self.max_size_entry = None
        self.seat_utilization_var = None
        self.colorbar_var = None
        self.bldg_abbrv_file_entry = None
        self.central_rooms_file_entry = None
        self.class_list_file_entry = None

        self.create_gui()

    def has_all_files(self):
        return self.bldg_abbrv_file_entry is not None and self.central_rooms_file_entry is not None and self.class_list_file_entry is not None

    def all_files_valid(self):
        return os.path.exists(self.bldg_abbrv_file_entry.file_path) and os.path.exists(self.central_rooms_file_entry.file_path) and os.path.exists(self.class_list_file_entry.file_path)

    def update_buildings_code_listbox(self):
        self.building_listbox.delete(0, END)
        for code in self.building_codes:
            self.building_listbox.insert(END, code)

    def update_buildings(self, _=""):
        if self.has_all_files() and self.all_files_valid():
            self.intervals_dec, self.buildings, self.building_codes = \
                analyze(self.bldg_abbrv_file_entry.file_path, self.central_rooms_file_entry.file_path, self.class_list_file_entry.file_path)
            self.update_buildings_code_listbox()

    def get_selections(self):
        selected_building_codes = [self.building_listbox.get(i) for i in self.building_listbox.curselection()]
        seat_utilization = self.seat_utilization_var.get() == 1
        colorbar = self.colorbar_var.get() == 1
        min_room_size = self.min_size_entry.value()
        max_room_size = self.max_size_entry.value()

        return selected_building_codes, seat_utilization, colorbar, min_room_size, max_room_size

    def heat_map(self):
        selected_building_codes, seat_utilization, colorbar, min_room_size, max_room_size = self.get_selections()

        print('\n\n')
        status = plot_heat_map(self.buildings, self.intervals_dec,
                               colorbar=colorbar,
                               building_codes=selected_building_codes,
                               min_room_size=min_room_size, max_room_size=max_room_size,
                               seat_utilization=seat_utilization)
        if status == -1:
            self.no_building_popup()

    def interval_usage(self):
        selected_building_codes, seat_utilization, colorbar, min_room_size, max_room_size = self.get_selections()

        print('\n\n')

        def _get_room_occ(room, intervals_dec):
            return get_room_occ(room, intervals_dec, seat_utilization=seat_utilization,
                                seat_utilization_by_room_occ=True, debug=DEBUG)
        status = plot_room_efficiency(self.buildings, self.intervals_dec, _get_room_occ,
                                      colorbar=colorbar,
                                      building_codes=selected_building_codes,
                                      min_room_size=min_room_size, max_room_size=max_room_size,
                                      seat_utilization=seat_utilization)
        if status == -1:
            self.no_building_popup()

    def no_building_popup(self):
        popup = Tk()
        popup.title("No matching buildings")

        Label(popup, text="No buildings match your criteria", width=50, height=10).pack()

        popup.mainloop()

    def create_gui(self):
        top = Tk()
        top.title("Classroom Scheduling")

        building_label = Label(top, text="Buildings:")
        self.building_listbox = Listbox(top, selectmode=MULTIPLE, exportselection=False)

        self.min_size_entry = OptionalEntry(top, "Min room size", value=30)
        self.max_size_entry = OptionalEntry(top, "Max room size", value=100)

        self.seat_utilization_var = IntVar()
        seat_utilization_cb = Checkbutton(top, text="Seat Utilization", variable=self.seat_utilization_var)

        self.colorbar_var = IntVar()
        colorbar_cb = Checkbutton(top, text="Show Colorbar", variable=self.colorbar_var)

        self.bldg_abbrv_file_entry = FileEntry(top, name="Choose Building Abbrv", on_open=self.update_buildings,
                                               # default_value=r'C:\Users\nickb\Google Drive\Career\PACCS\building_abbreviations.csv')
                                                default_value = r'/home/nick/Developer/PACCS/uploads/building_abbreviations.csv')
        self.central_rooms_file_entry = FileEntry(top, name="Choose Centrally Scheduled Classrooms",
                                                  on_open=self.update_buildings,
                                                # default_value = r'C:\Users\nickb\Google Drive\Career\PACCS\centrally_scheduled_classrooms.csv')
                                                default_value = r'/home/nick/Developer/PACCS/uploads/centrally_scheduled_classrooms.csv')
        self.class_list_file_entry = FileEntry(top, name="Choose Class List", on_open=self.update_buildings,
                                               # default_value=r'C:\Users\nickb\Google Drive\Career\PACCS\ClassSchedule-23_comma.csv')
                                                default_value = r'/home/nick/Developer/PACCS/uploads/ClassSchedule-23_comma.csv')
        self.update_buildings()

        heat_map_btn = Button(top, text="Show heat map", command=self.heat_map)
        interval_usage_btn = Button(top, text="Show interval usage", command=self.interval_usage)

        self.bldg_abbrv_file_entry.place(row=1)
        self.central_rooms_file_entry.place(row=2)
        self.class_list_file_entry.place(row=3)

        building_label.grid(row=4, column=0)
        self.building_listbox.grid(row=4, column=1, columnspan=2)
        self.min_size_entry.place(row=5)
        self.max_size_entry.place(row=6)

        colorbar_cb.grid(row=7, column=1)
        seat_utilization_cb.grid(row=7, column=2)

        heat_map_btn.grid(row=8, column=0)
        interval_usage_btn.grid(row=8, column=2)

        top.mainloop()


if __name__ == "__main__":
    DEBUG = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "-d":
            DEBUG = True
    ScheduleExplorer()