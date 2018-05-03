# Classroom Heatmap

## Data
Some data has been removed for security reasons.

How to get data:
- `uploads/centrally_scheduled_classrooms.csv` should be downloaded from the Google Sheet of Centrally Scheduled classrooms (`OU - Central Classroom List w/ Technology`
)
- `uploads/ClassSchedule-23_comma.csv` should be downloaded from The Book.

## Local GUI
`python3 gui.py`

## Web app
**Starting server**
1. Create venv and install dependencies
 - `pipenv install`
2. Find venv path
 - `pipenv --venv`
3. Start the venv
 - `. <path_to_venv>/bin/activate`
4. Run the server
 - `export FLASK_APP=server.py`
 - `python -m flask run`

## Dockerizing
1. Update requirements file  
`pipenv -r > requirements.txt`
2. Build docker from project directory  
`docker build -t paccs-flask .`
3. Run docker image, forwarding port 5000  
`docker run -p 5000:5000 paccs-flask`
