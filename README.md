visualizing-geotagged-data

If these instructions are not complete, write my an email please. I will add missing instructions to this Readme or correct faulty ones.

##################### SEMINAR INSTRUCTIONS #############################

- Get the videos.zip from here http://www.wuala.com/fclaus/public/hiwi/videos.zip/ and extract them to videos/
- If you want to use a virtualenv, you must make sure that your mod_wsgi is compiled against the same python verison. If it is not, don't use one. I recommend trying virtualenv first because it is the cleaner way.
- Install necessary dependencies ((sudo) pip install -r install/seminar-requirements.pip) with pip. I have removed all 'difficult' dependencies, namely ones that require compiling of native code.
- Test dependencies with python manage.py test geo. If it does not say 'Ran XX test in XX secs. OK', some dependencies cannot be imported.
- Run the setup script, 'python setup.py'. The setup script will take the sqlite3 db from res/ and update the path to the videos, which are copied from videos/ to /static/upload. The path is absolute atm.
- Make sure your username is not 'fredo' or 'claus'. If it is, then take a look into the settings.py
- For writing more effective css. I use sass. Try installing sass by typing sass into your command line, it might tell you what you need to install. If sass is a problem, you can convert all css (it is not that much) to plain css. Don't forget to remove sass from the COMPRESS_PRECOMPILERS in the settings.py.
- You can start django now (python manage.py runserver). The service should run without problems. If it still does not work, read me an email so I can add instructions here.


Django does not support a byte range request, which is necessary for streaming videos correctly and determining the position in the video. You'll notice this, when you playback a video and look at the current position in seconds and the total seconds. I will explain a setup for apache which supports byte range requests. If you want to use another webserver feel free to choose whichever one you like.
- Install apache2 & and libapache2-mod-wsgi (Note: The exact names might be different on your platform). If you can't or don't want to install mod_wsgi you can also use mod_python. mod_python does not support the selection of a different python interpreter, mod_wsgi does under certain circumstances (see above).
- Go to the install/ folder open the httpd.conf, copy it to /etc/apache2/ and adjust all paths to fit your local setup. PLEASE make sure you changed all of your pathes. In addition to that you will need a emtpy virtualhost:80 configuration in sites-enabled, don't forget to raise the debug level. If you used virtualenv in one of the steps above add WSGIPYTHONHOME to your httpd.conf, for details see http://code.google.com/p/modwsgi/wiki/VirtualEnvironments.
- Create a folder called CACHE in static with read+write permissions for the user that your apache daemon uses. In case of doubt use chmod -R a+rw static/CACHE/. Be aware that the -R is important (if there is already stuff in the folder), because CACHE will contain compressed css + js files (in their subfolders).
- Restart your apache and browser to localhost, you should see the app running again. If you select a video now, you will notice that the total time in seconds is in a more believable range than earlier. If you see the blue marker highlighting the current section your done! If you get some error (Acess denied, etc..), the page comes without styling something went wrong. Consult your apache log, recheck all the steps and write me an email.
########################################################################


!!!EVERYTHING BELOW HERE IS DEPRECATED!!!

#####################  INSTRUCTIONS #############################
Install dependencies
pip install -r requirements.pip
Run tests to ensure all dependencies are in place
python manage.py test geo
Setup Postgres according to connection in settings.py
python manage.py syncdb
Copy demo videos to static/upload and make sure the traces 1-6 are in res/test
python geo/script/filldb.py
will insert the data into the db.
########################################################################



