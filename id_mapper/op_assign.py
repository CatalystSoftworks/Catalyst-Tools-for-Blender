import bpy
from .utils import paint_selected_faces, get_selected_faces
from .types import ID_UL_IDGroupsList


def get_groups_enum(self, context):
    output = []
    for name in context.object.data.id_map.get_group_names():
        output.append((name, name, "", ""))
    return output


class ID_AssignGroup(bpy.types.Operator):
    """Assigns an ID group to the selected faces by group name"""
    bl_label = "Assign ID Group by Name"
    bl_idname = "idmap.assign_id_group"
    bl_options = {"REGISTER", "UNDO"}

    group_name: bpy.props.StringProperty(
        name="Group Name",
        description="Name of the ID group to assign",
    )

    @classmethod
    def poll(cls, context):
        faces = get_selected_faces(context)
        has_group = context.object.data.id_map.active != None
        return context.mode == "EDIT_MESH" and len(faces) > 0 and has_group

    def execute(self, context):
        mesh = context.object.data

        # get the group that we want to assign the color for
        group = mesh.id_map.get_group_by_name(self.group_name)
        if (group == None):
            # self.report({"ERROR"}, "Failed to find group with name: %s" %
            #             self.group_name)
            return {"CANCELLED"}

        # paint the group with the color for the faces
        paint_selected_faces(context, group.color)

        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        id_map = context.object.data.id_map
        layout = self.layout
        layout.template_list(ID_UL_IDGroupsList.__name__,
                             "", id_map, "groups", id_map, "active_index")


class ID_AssignActiveGroup(bpy.types.Operator):
    """Assigns the selected/active ID group index to the selected faces"""
    bl_label = "Assign ID Group"
    bl_idname = "idmap.assign_active_id_group"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        faces = get_selected_faces(context)
        has_group = context.object.data.id_map.active != None
        return context.mode == "EDIT_MESH" and len(faces) > 0 and has_group

    def execute(self, context):
        mesh = context.object.data

        # get the group that we want to assign the color for
        group = mesh.id_map.active
        if group == None:
            group = mesh.id_map.find_or_create_group("Default")

        # paint the group with the color for the faces
        paint_selected_faces(context, group.color)

        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        id_map = context.object.data.id_map
        layout = self.layout
        layout.template_list(ID_UL_IDGroupsList.__name__,
                             "", id_map, "groups", id_map, "active_index")
