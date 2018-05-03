import os

from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
from werkzeug.utils import secure_filename

from analysis import analyze
from time_dec import get_intervals_dec, DAYS

UPLOAD_FOLDER = r'C:\Users\nickb\PycharmProjects\PACCS\uploads'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.secret_key = 'super secret key'


@app.route('/')
def hello_world():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/filter', methods=['GET'])
def filter():
    saved_files = {}
    for file_name in [('buildings_file','building_abbreviations.csv'), ('central_file','centrally_scheduled_classrooms.csv'), ('schedule_file','ClassSchedule-23_comma.csv')]:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name[1])
        saved_files[file_name[0]] = file_path

    intervals_dec, buildings, building_codes = \
        analyze(saved_files['buildings_file'], saved_files['central_file'], saved_files['schedule_file'])

    dict_buildings = {code: building.asdict() for code, building in buildings.items()}

    return render_template('filter.html', intervals_dec=intervals_dec, buildings=dict_buildings,
                           building_codes=building_codes)


@app.route('/deh120', methods=['GET'])
def deh120():
    saved_files = {}
    for file_name in [('buildings_file','building_abbreviations.csv'), ('central_file','centrally_scheduled_classrooms.csv'), ('schedule_file','ClassSchedule-23_comma.csv')]:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name[1])
        saved_files[file_name[0]] = file_path

    intervals_dec, buildings, building_codes = \
        analyze(saved_files['buildings_file'], saved_files['central_file'], saved_files['schedule_file'])

    dict_buildings = {code: building.asdict() for code, building in buildings.items()}

    deh120 = dict_buildings['DEH']['rooms']['120']['occupancy_matrix']

    intervals_dec = get_intervals_dec(800, 1600, 30)
    days = DAYS

    open_times = []
    for day_i, day in enumerate(deh120):
        for int_i, occupied in enumerate(day):
            if occupied == 0:
                open_event = {
                    'title': 'DEH - 120 Open',
                    'start': intervals_dec[int_i],
                    'end': intervals_dec[int_i+1] if int_i + 1 < len(intervals_dec) else intervals_dec[int_i] + 30,
                    'dow': days[day_i],
                    'location': 'DEH - 120',
                }
                open_times.append(open_event)

    return str(open_times)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        saved_files = {}
        for file_name in ['buildings_file', 'central_file', 'schedule_file']:
            # check if the post request has the file part
            if file_name not in request.files:
                flash('No ' + file_name + 'part')
                return redirect(request.url)

            file = request.files[file_name]
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                saved_files[file_name] = file_path
                file.save(file_path)

        intervals_dec, buildings, buildings_seat, building_codes = \
            analyze(saved_files['buildings_file'], saved_files['central_file'], saved_files['schedule_file'])

        dict_buildings = {code: building.asdict() for code, building in buildings.items()}
        return render_template('filter.html', intervals_dec=intervals_dec, buildings=dict_buildings, building_codes=building_codes)
    return render_template('submit_files.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')