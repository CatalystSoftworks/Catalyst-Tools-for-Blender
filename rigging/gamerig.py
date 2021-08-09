import bpy
from ..icons import get_icon_id


# inspired by https://youtu.be/6nCriSbfHjc
class ConvertToGameRig(bpy.types.Operator):
    """Creates a copy of all deform bones and prepares the rig for use in game engines"""
    bl_idname = "catalyst.convert_to_game_rig"
    bl_label = "Convert to Game Ready Rig"
    bl_options = {"UNDO", "REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.object.type == "ARMATURE"

    def execute(self, context: bpy.types.Context):
        obj: bpy.types.Object = context.object
        rig: bpy.types.Armature = obj.data
        root_bone_count = 0
        def_bone_layers = [i == 31 for i in range(32)]

        # get the associated meshes
        meshes = [o for o in context.blend_data.objects if o.type == "MESH" and o.parent == obj]

        # ensure that the last bone layer is empty - this is where we'll put the actual
        # deform bones for the rig
        for b in rig.bones:
            if b.layers[31]:
                self.report({"ERROR"}, "Layer 32 must be empty! This is where deform bones will be put")
                return {"CANCELLED"}

        # create a new list of all the current bones - this is because looping on rig.bones directly can
        # result in us looping back on ourselves as we add more bones!
        bone_names = [b.name for b in rig.bones]

        # create a copy of all deform bones and prep them for use in a game engine - also ensure
        # that the bones have proper names and are in a new bone group for the deform bones
        for bone_name in bone_names:

            tgt_bone: bpy.types.Bone = rig.bones.get(bone_name)

            if not tgt_bone.use_deform:
                continue

            if not tgt_bone.parent:
                root_bone_count += 1

            # start editing bones
            bpy.ops.object.mode_set(mode="EDIT", toggle=False)

            # define the new names for the target and deform bones
            def_name: str = bone_name
            tgt_name: str = "TGT_{}".format(def_name)

            # get the edito bone for the target bone
            tgt_edit_bone = rig.edit_bones.get(def_name)
            if tgt_edit_bone is None:
                print("FAILED TO FIND EDIT BONE FOR %s" % def_name)
                continue

            # update the target bone
            tgt_bone.name = tgt_name
            tgt_edit_bone.use_deform = False

            # create a copy of the deform bone
            def_bone = rig.edit_bones.new(def_name)
            def_bone.head = tgt_edit_bone.head
            def_bone.tail = tgt_edit_bone.tail
            def_bone.matrix = tgt_edit_bone.matrix
            def_bone.parent = tgt_edit_bone.parent
            def_bone.layers = def_bone_layers
            def_bone.bbone_segments = 1
            def_bone.use_local_location = True
            def_bone.use_inherit_rotation = True
            def_bone.use_inherit_scale = True

            # add the copy transforms constraint
            bpy.ops.object.mode_set(mode="POSE", toggle=False)

            pb = obj.pose.bones.get(def_name)

            c: bpy.types.CopyTransformsConstraint = pb.constraints.new(type="COPY_TRANSFORMS")
            c.target = obj
            c.subtarget = tgt_name

            # rename vertex groups
            for m in meshes:
                # m: bpy.types.Object = m
                if tgt_name in m.vertex_groups:
                    m.vertex_groups[tgt_name].name = def_name

            print("{} -> {}".format(def_name, tgt_name))

        # check to see how many root bones we have and report to use if there are more than 1
        if root_bone_count > 1:
            warning = "Found a total of %d root bones - this will be an issue in engines like Unreal" % root_bone_count
            self.report({"WARNING"}, warning)

        # go back to object mode
        bpy.ops.object.mode_set(mode="OBJECT")

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