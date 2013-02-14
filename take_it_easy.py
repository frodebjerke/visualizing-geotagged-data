'''
Created on Feb 6, 2013

@author: fredo
'''
import argparse, os
import settings

parser = argparse.ArgumentParser(prog = "videotagging",
                                 description = "")
parser.add_argument("--reset",
                    default = False,
                    action = "store_true",
                    help = "Reset the current db.")
    
parser.add_argument("--resolve",
                    default = False,
                    action = "store_true",
                    help  = "Resolve all .gpx files. Needs dir.")

parser.add_argument("--insert",
                    default = False,
                    action = "store_true",
                    help = "Stores all .geocode files in the db. Needs dir and mode.")

parser.add_argument("--draw-single",
                    default = False,
                    action = "store_true",
                    help = "Draw the graph once. Need mode.")

parser.add_argument("--draw-multiple",
                    default = False,
                    action = "store_true",
                    help = "Draws the graph after every inserted gpx file. Needs mode.")

parser.add_argument("--directory",
                    default = settings.TRACKS_DIR,
                    help = "Path to the .gpx files. Defaults to evaluation dir.")

parser.add_argument("--mode",
                    default = 0,
                    help = "Mode to use for the graph instance.")


parser = parser.parse_args()

assert parser.reset or parser.resolve or parser.insert or parser.draw_single, "You must specify an action."
assert (parser.draw_single) or (not parser.draw_multiple), "You must specify one: draw-single or draw-multiple"
#assert parser.draw_multiple and parser.insert, "draw-multiple is only possible with insert" 

path = os.path.abspath(parser.directory)
mode = parser.mode

def draw(name):
    from geo.script import drawmap
    print "Drawing graph %d..." % mode
    drawmap.drawmap(mode, name)
    
if parser.reset:
    import resyncdb
    print "Resetting database..."
    resyncdb.resetdb()

if parser.resolve:
    from geo.script import gpxtogeocode
    print "Resolving all .gpx files in %s..." % path
    gpxtogeocode.resolvedir(path)
    
if parser.insert:
    from geo.script import filldb
    print "Inserting all .geocode files from %s" % path
    filldb.insertdir(path)
#    filldb.insertall()
    

if parser.draw_single:
    draw("0-single_export")

    
print "Finished."




