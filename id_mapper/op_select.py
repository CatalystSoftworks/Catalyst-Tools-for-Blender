import bpy
from .utils import select_faces_by_color

actions = [
    ("SELECT", "Select by ID Group", ""),
]


class ID_SelectByActiveGroup(bpy.types.Operator):
    """Makes a selection of faces based on the ID groups and their assigned colors"""
    bl_idname = "idmap.select_by_id_group"
    bl_label = "Select by Active ID Group"
    bl_options = {"REGISTER", "UNDO"}

    # TODO: use selection mode to select by, unselect by or invert by the group
    action: bpy.props.EnumProperty(items=actions, name="Selection Mode", default="SELECT")

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def execute(self, context):
        id_map = context.object.data.id_map

        # get the currently active group
        group = id_map.active
        if group == None:
            return {"CANCELLED"}

        # select by the group color
        select_faces_by_color(context, group.color)

        return {"FINISHED"}
