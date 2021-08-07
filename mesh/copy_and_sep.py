import bpy
import bmesh

class CopyAndSeparate(bpy.types.Operator):
    """Macro that extracts a copy of the current selection to a new mesh object."""
    bl_idname = "catalyst.copy_and_separate"
    bl_label = "Copy + Separate"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.mode == "EDIT_MESH" and context.active_object != None

    def execute(self, context: bpy.types.Context):
        obj: bpy.types.Object = context.active_object
        bm: bmesh.types.BMesh = bmesh.from_edit_mesh(obj.data)
        bm_new: bmesh.types.BMesh = bmesh.new()

        name = obj.name

        onm = {}  # old index to new vert map
        for v in bm.verts:
            if v.select:
                nv = bm_new.verts.new(v.co)
                onm[v.index] = nv

        for e in bm.edges:
            if e.select:
                everts = [onm[v.index] for v in e.verts]
                bm_new.edges.new(everts)

        for f in bm.faces:
            if f.select:
                fverts = [onm[v.index] for v in f.verts]
                bm_new.faces.new(fverts)

        new_data: bpy.types.Mesh = bpy.data.meshes.new(name + " Data")
        bm_new.to_mesh(new_data)
        new_obj: bpy.types.Object = bpy.data.objects.new(name, new_data)
        context.scene.collection.objects.link(new_obj)

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        new_obj.select_set(True)
        context.view_layer.objects.active = new_obj
        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}


def add_op_split_menu(self, context):
    layout: bpy.types.UILayout = self.layout
    layout.operator(CopyAndSeparate.bl_idname)


def register():
    bpy.types.VIEW3D_MT_edit_mesh_split.append(add_op_split_menu)


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_split.remove(add_op_split_menu)