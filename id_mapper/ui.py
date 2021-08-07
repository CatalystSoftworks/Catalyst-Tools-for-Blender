import bpy
from .op_assign import ID_AssignGroup, ID_AssignActiveGroup
from .op_create import ID_CreateGroup
from .op_remove import ID_RemoveGroup
from .op_select import ID_SelectByActiveGroup
from .types import ID_UL_IDGroupsList
from .utils import check_selection_mode


class DATA_PT_idmap_groups(bpy.types.Panel):
    bl_label = "ID Map Groups"
    bl_space_type = "PROPERTIES"
    bl_idname = "DATA_PT_id_groups"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object != None and context.object.type == "MESH"

    def draw(self, context):
        layout = self.layout
        mesh = context.object.data

        row = layout.row()
        row.template_list(ID_UL_IDGroupsList.__name__, "",
                          mesh.id_map, "groups", mesh.id_map, "active_index")
        col = row.column(align=True)
        col.ui_units_x = 1
        col.operator_context = "EXEC_DEFAULT"
        col.operator(ID_CreateGroup.bl_idname, text="", icon="ADD")
        col.operator(ID_RemoveGroup.bl_idname, text="", icon="REMOVE")

        row = layout.row()

        sub = row.row(align=True)
        sub.operator_context = "EXEC_DEFAULT"
        sub.operator(ID_AssignActiveGroup.bl_idname, text="Assign")
        sub.label(text="Unassign")

        sub = row.row(align=True)
        sub.operator_context = "EXEC_DEFAULT"
        # sub.operator(ID_SelectByActiveGroup.bl_idname, text="Select")
        sub.label(text="Select")
        sub.label(text="Deselect")


class VIEW3D_MT_idmap_menu(bpy.types.Menu):
    bl_label = "ID Mapper"
    bl_description = "Quickly add ID groups to the current selection"

    def draw(self, context):
        layout = self.layout
        active = context.object
        groups = active.data.id_map.groups

        layout.operator_context = "INVOKE_REGION_WIN"

        op = layout.operator(ID_CreateGroup.bl_idname, text="New Group")
        op.assign_selected = True

        if len(groups) > 0:
            layout.separator()
            layout.label(text="Assign Existing Groups")
            col = layout.column()
            col.operator_context = "EXEC_DEFAULT"
            for group in groups:
                op = col.operator(ID_AssignGroup.bl_idname, text=group.name)
                op.group_name = group.name


def edit_faces_menu(self, context):
    layout: bpy.types.UILayout = self.layout
    layout.menu(VIEW3D_MT_idmap_menu.__name__)


def edit_faces_context_menu(self, context):
    layout: bpy.types.UILayout = self.layout

    if check_selection_mode(False, False, True):
        layout.menu(VIEW3D_MT_idmap_menu.__name__)


def register():
    bpy.types.VIEW3D_MT_edit_mesh_faces.append(edit_faces_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(edit_faces_context_menu)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_faces.remove(edit_faces_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(edit_faces_context_menu)
