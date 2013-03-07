##################### SEMINAR INSTRUCTIONS #############################

- Get the videos.zip and extract it to videos/
- If you want to use a virtualenv, you must make sure that your mod_wsgi is compiled against the same python verison. If it is not, don't use one.
- Install necessary dependencies (requirements/seminar-requirements.pip) with pip
- Run the setup script, 'python setup.py'
- Make sure your username is not 'fredo' or 'claus'. If it is, then take a look into the settings.py
- You can start django now (python manage.py runserver). The service should run without problems.
- Django does not support a byte range request, which is necessary for streaming videos correctly and determining the position in the video
- install apache2 & and libapache2-mod-wsgi (Note: The exact names might be different on your platform)

########################################################################





Install dependencies

pip install -r requirements.pip

Run tests to ensure all dependencies are in place

python manage.py test geo

Setup Postgres according to connection in settings.py

python manage.py syncdb

Copy demo videos to static/upload and make sure the traces 1-6 are in res/test

python geo/script/filldb.py

will insert the data into the db.


