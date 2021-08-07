import bpy
from mathutils import Color
from bpy.props import IntProperty, FloatVectorProperty, StringProperty, CollectionProperty
from random import uniform


class ID_Group(bpy.types.PropertyGroup):
    name: StringProperty(name="Group Name")
    color: FloatVectorProperty(name="Group Color", size=4)


class ID_Map(bpy.types.PropertyGroup):
    active_index: IntProperty(name="Active Index", default=-1)
    groups: CollectionProperty(name="ID Groups", type=ID_Group)

    @property
    def active(self):
        """Returns the current group with the index that matches the set 'active_index_id' or None if one can't be found."""
        return self.get_group_by_index(self.active_index)

    def find_or_create_group(self, name):
        """Will attempt to find and return a group with the specified name, otherwise a new group will be created and returned."""
        group = self.get_group_by_name(name)
        if group == None:
            group = self.new_group(name)
        return group

    def get_group_by_name(self, name):
        """Will attempt to find and return a group with the specified name, otherwise None will be returned."""
        for group in self.groups:
            if group.name == name:
                return group
        return None

    def get_group_by_index(self, index):
        """Returns the group that exists at the corresponding index if found, otherwise None is returned."""
        count = len(self.groups)
        if count == 0 or index < 0 or index >= count:
            return None
        return self.groups[index]

    def new_group(self, name, make_active=False):
        """Create and returns a new ID group with a unique color."""
        names = self.get_group_names()

        if len(names) == 0:
            pass

        elif name in names:
            count = 1
            while True:
                new_name = "{}.{:03d}".format(name, count)
                if new_name not in names:
                    name = new_name
                    break

        new_group = self.groups.add()
        new_group.name = name
        new_group.color = self.get_unique_color()

        if make_active or self.active_index < 0 or self.active_index >= len(self.groups):
            self.active_index = len(self.groups) - 1

        return new_group

    def get_unique_color(self):
        """Generates a unique color for the ID map."""
        colors = [group.color for group in self.groups]

        while True:
            color = (uniform(0, 1), uniform(0, 1), uniform(0, 1), 1)
            if color not in colors and color != (0, 0, 0, 1):
                return color

    def get_group_names(self):
        """Returns a list containing the names of each group."""
        return [group.name for group in self.groups]

    def remove_active(self):
        """Removes the current, active group."""
        idx = self.active_index
        count = len(self.groups)
        if idx < 0 or count == 0:
            idx = -1
            return

        if idx >= count:
            self.active_index = count - 1
            return

        self.groups.remove(idx)
        self.active_index = len(self.groups) - 1


class ID_UL_IDGroupsList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_props):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.prop(item, "name", text="", emboss=False, icon_value=icon)
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


def register():
    bpy.types.Mesh.id_map = bpy.props.PointerProperty(name="ID Map", type=ID_Map)


def unregister():
    del bpy.types.Mesh.id_map
