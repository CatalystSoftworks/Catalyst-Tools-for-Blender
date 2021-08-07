import bpy
from .utils import paint_selected_faces, select_faces_by_color


class ID_RemoveGroup(bpy.types.Operator):
    """Removes an ID group from the active mesh object"""
    bl_label = "Remove ID Group"
    bl_idname = "idmap.remove_id_group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object != None and context.object.type == "MESH"

    def execute(self, context):
        id_map = context.object.data.id_map

        # get the group that we're going to remove
        group = id_map.active
        if group == None:
            return {"FINISHED"}

        # remove the map
        id_map.remove_active()

        # paint away the colors for the group
        select_faces_by_color(context, group.color)
        paint_selected_faces(context, (0, 0, 0, 1))

        return {"FINISHED"}
