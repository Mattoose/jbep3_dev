""" Small module to store bitmap images. Might be merged with another module later """
from vgui.controls import BitmapImage

imagedb = {}

def GetImage(path):
    try:
        return imagedb[path]
    except KeyError:
        imagedb[path] = BitmapImage(0, path)
        return imagedb[path]