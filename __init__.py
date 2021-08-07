# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Catalyst Tools",
    "author" : "Nicholas Glenn",
    "description" : "A random assortment of new features meant to assist with a variety of tasks, particularly around games.",
    "blender" : (2, 93, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "wiki_url": "https://github.com/CatalystSoftworks/Catalyst-Tools-for-Blender",
    "support": "COMMUNITY",
    "warning" : "",
    "category" : "Generic"
}


from . import auto_load, icons


auto_load.init()


def register():
    icons.register_icons()
    auto_load.register()


def unregister():
    auto_load.unregister()
    icons.unregister_icons()
