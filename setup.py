'''
Created on Mar 7, 2013

@author: fredo
'''

import os
import settings
import shutil
import sqlite3

if not os.path.isdir(settings.VIDEO_DIR):
    print "Please unzip the videos.zip to videos/"
    exit()
    
DATABASE_OLD_PATH = os.path.join(settings.RES_DIR, "seminar.sqlite3")
DATABASE_NEW_PATH = os.path.join(settings.PROJECT_PATH, "seminar.sqlite3")

try:
    shutil.copy(DATABASE_OLD_PATH, DATABASE_NEW_PATH)
    # query all videos
    connection = sqlite3.connect(DATABASE_NEW_PATH)
    # access fields by names
    connection.row_factory = sqlite3.Row
    select_cursor = connection.cursor()
    select_cursor.execute("select * from geo_video")
    # we need to fetch all records before update individual ones
    videos = select_cursor.fetchall()
#    update_cursor = connection.cursor()
    
    for video in videos:
        trace_name = video["video"]
        video_path = os.path.join(settings.VIDEO_DIR, trace_name)
        
        if not os.path.isfile(video_path):
            print "%s does not exist. Did you unzip the whole videos.zip archive?" % video_path
            exit()
            
        upload_path = os.path.join(settings.UPLOAD_DIR, trace_name)
        # copy the video to the upload dir
        print "Copying %s to %s..." % (video_path, upload_path)
        shutil.copy(video_path, upload_path )
        # link the new path
        connection.execute("update geo_video set video = ? where id = ?", (upload_path, video["id"]))
        connection.commit()
except Exception, e:
    print "Something unexpected happened: %s" % str(e)