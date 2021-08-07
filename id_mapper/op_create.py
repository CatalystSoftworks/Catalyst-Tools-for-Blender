import bpy
from .utils import paint_selected_faces


class ID_CreateGroup(bpy.types.Operator):
    """Creates a new ID group for the active mesh object"""
    bl_label = "Create ID Group"
    bl_idname = "idmap.create_id_group"
    bl_options = {"REGISTER", "UNDO"}

    group_name: bpy.props.StringProperty(
        name="Group Name",
        description="The desired name for the new ID group",
    )

    assign_selected: bpy.props.BoolProperty(
        name="Assign Selected Faces",
        description="Assigns any currently selected faces to the new ID group",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return context.object != None and context.object.type == "MESH"

    def execute(self, context):
        id_map = context.object.data.id_map

        # create the group
        group = id_map.new_group(self.group_name, make_active=True)

        # assign the group to the selected faces
        if self.assign_selected and context.mode == "EDIT_MESH":
            # paint the group with the color for the faces
            paint_selected_faces(context, group.color)

        return {"FINISHED"}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "group_name")
        if context.mode == "EDIT_MESH":
            layout.prop(self, "assign_selected")
