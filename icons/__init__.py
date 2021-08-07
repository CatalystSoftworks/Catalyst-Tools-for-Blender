import os
import bpy
import bpy.utils.previews

icons_collection = None
icons_directory = os.path.dirname(__file__)
preload_icons = {}


def register_icons():
    global icons_collection
    icons_collection = bpy.utils.previews.new()

    # preload icons at registration time
    for file in os.listdir(icons_directory):
        if file.endswith(".png"):
            identifier = file[:-4]
            icons_collection.load(identifier, os.path.join(icons_directory, file), "IMAGE")


def unregister_icons():
    global icons_collection
    bpy.utils.previews.remove(icons_collection)


def get_icon(identifier):
    if identifier in icons_collection:
        return icons_collection[identifier]
    return icons_collection.load(identifier, os.path.join(icons_directory, identifier + ".png"), "IMAGE")


def get_icon_id(identifier):
    return get_icon(identifier).icon_id
