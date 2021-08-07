import bpy
from ..icons import get_icon_id


# inspired by https://youtu.be/6nCriSbfHjc
class ConvertToGameRig(bpy.types.Operator):
    """Creates a copy of the currently selected armature and attempts to clean it up for use in game engines"""
    bl_idname = "catalyst.convert_to_game_rig"
    bl_label = "Convert to Game Ready Rig"
    bl_options = {"UNDO", "REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.object.type == "ARMATURE"

    def execute(self, context: bpy.types.Context):
        src_obj: bpy.types.Object = context.object
        root_bone_count = 0

        # create a duplicate of the active object
        def_obj: bpy.types.Object = src_obj.copy()
        def_obj.data = src_obj.data.copy()
        def_obj.animation_data_clear()
        def_obj.name = "%s GAME RIG" % src_obj.name
        context.collection.objects.link(def_obj)

        def_rig: bpy.types.Armature = def_obj.data

        # set the duplicate as the now active object
        bpy.context.view_layer.objects.active = def_obj

        # remove constraints
        bpy.ops.object.mode_set(mode="POSE")

        # remove non-deform bones and disable bendy bones + custom shapes and add the copy transforms
        # constraint pointing at the same bone on the source object
        bpy.ops.object.mode_set(mode="EDIT")
        for b in def_rig.bones:
            # b:bpy.types.Bone
            if not b.use_deform:
                def_rig.edit_bones.remove(def_rig.edit_bones.get(b.name))
            else:
                b.bbone_segments = 1
                b.use_local_location = True
                b.use_inherit_rotation = True
                b.use_inherit_scale = True
                # b.layers = [0]

                pb = def_obj.pose.bones.get(b.name)
                pb.custom_shape = None

                pb.constraints.clear()

                c: bpy.types.CopyTransformsConstraint = pb.constraints.new(type="COPY_TRANSFORMS")
                c.target = src_obj
                c.subtarget = b.name

        # reparent the related mesh(es) from the source object to the game ready one
        for o in context.collection.objects:
            if o.parent == src_obj:
                o.parent = def_obj

            for mod in o.modifiers:
                if mod.object == src_obj:
                    mod.object = def_obj

        # check to see how many root bones we have and report to use if there are more than 1
        if root_bone_count > 1:
            warning = "Found a total of %d root bones - this will be an issue in engines like Unreal" % root_bone_count
            print(warning)
            self.report({"WARNING"}, warning)

        # go back to object mode
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.view_layer.objects.active = src_obj

        return {"FINISHED"}


def add_operator_to_menu(self, context):
    layout: bpy.types.UILayout = self.layout

    if context.object.type == "ARMATURE":
        layout.operator(ConvertToGameRig.bl_idname, text="Game Ready Rig", icon_value=get_icon_id("gamepad"))


def register():
    # bpy.types.VIEW3D_MT_object.append(add_operator_to_object_menu)
    bpy.types.VIEW3D_MT_object_convert.append(add_operator_to_menu)


def unregister():
    # bpy.types.VIEW3D_MT_object.remove(add_operator_to_object_menu)
    bpy.types.VIEW3D_MT_object_convert.remove(add_operator_to_menu)