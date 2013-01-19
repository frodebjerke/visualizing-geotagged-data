Install dependencies

pip install -r requirements.pip

Run tests to ensure all dependencies are in place

python manage.py test geo

Setup Postgres according to connection in settings.py

python manage.py syncdb

Copy demo videos to static/upload and make sure the traces 1-6 are in res/test

python geo/script/filldb.py

will insert the data into the db.


