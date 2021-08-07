import bpy
from .utils import assign_material_to_selection


class ID_AddIDMapMaterial(bpy.types.Operator):
    """Applies a material to the active object for previewing ID maps outside of vertex painting mode"""
    bl_label = "Assign ID Map Material"
    bl_idname = "idmap.assign_id_map_material"
    bl_options = {"REGISTER", "UNDO"}

    mat_name: bpy.props.StringProperty(
        name="Material Name",
        description="Name applied to the material created for this ID map.",
        default="ID Map",
    )

    override: bpy.props.BoolProperty(
        name="Assign to Faces",
        description="Automatically assigns the material to the faces of the selected object(s)",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH"} and context.object != None and context.object.type == "MESH"

    def execute(self, context):
        mat = bpy.data.materials.get(self.mat_name)
        if mat == None:
            mat = bpy.data.materials.new(name=self.mat_name)
            mat.use_nodes = True
            tree = mat.node_tree

            for node in tree.nodes.values():
                tree.nodes.remove(node)

            attr = tree.nodes.new("ShaderNodeAttribute")
            attr.location = (0, 0)
            attr.attribute_name = "ID"

            shader = tree.nodes.new("ShaderNodeEmission")
            shader.location = (200, 0)

            output = tree.nodes.new("ShaderNodeOutputMaterial")
            output.location = (400, 0)

            tree.links.new(shader.inputs[0], attr.outputs[0])
            tree.links.new(output.inputs[0], shader.outputs[0])

        assign_material_to_selection(context, mat, self.override, True)

        return {"FINISHED"}
