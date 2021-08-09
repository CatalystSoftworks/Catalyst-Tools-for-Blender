import bpy

class RemoveEmptyVertexGroups(bpy.types.Operator):
    """Removes all vertex groups that have no vertices assigned to them."""
    bl_idname = "catalyst.remove_empty_vertex_groups"
    bl_label = "Remove Empty Vertex Groups"
    bl_options = {"UNDO", "REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "MESH"

    def execute(self, context):

        obj: bpy.types.Object = context.object
        mesh: bpy.types.Mesh = obj.data

        empty_groups = dict([(vg.index, vg) for vg in obj.vertex_groups])

        # loop through each vert and remove any groups from the "empty_groups" set if
        # weight is greater than 0
        # TODO: this operation is pretty slow, would be good to explore alternatives
        for v in mesh.vertices:
            for g in v.groups:
                if g.weight > 0:
                    empty_groups.pop(g.group, None)

        # loop through the empty groups and remove them
        for eg in empty_groups.values():
            print("Removing vertex group: %s" % eg.name)
            obj.vertex_groups.remove(eg)

        return {"FINISHED"}


def add_op_to_menu(self, context):
    layout: bpy.types.UILayout = self.layout
    layout.separator()
    layout.operator(RemoveEmptyVertexGroups.bl_idname)


def register():
    bpy.types.MESH_MT_vertex_group_context_menu.append(add_op_to_menu)


def unregister():
    bpy.types.MESH_MT_vertex_group_context_menu.remove(add_op_to_menu)