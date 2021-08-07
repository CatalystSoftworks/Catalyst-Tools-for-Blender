import bpy
from typing import List


class SelectBonesMixin:
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.object.type == "ARMATURE"

    def filter_bones(self, object: bpy.types.Object, bones: List[bpy.types.Bone]) -> List[bpy.types.Bone]:
        return []

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        mode = context.mode if context.mode != "EDIT_ARMATURE" else "EDIT"
        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.pose.reveal(False)

        if not event.shift and not event.ctrl:
            bpy.ops.pose.select_all(action="DESELECT")

        obj = context.object
        all_bones = obj.data.bones
        selected_bones = self.filter_bones(obj, all_bones)

        if event.alt:
            selected_bones = list(set(all_bones) - set(selected_bones))

        for bone in selected_bones:
            bone.select = not event.ctrl

        bpy.ops.object.mode_set(mode = mode)

        return {"FINISHED"}


class SelectDeformBones(bpy.types.Operator, SelectBonesMixin):
    """
    Selects all bones that are currently marked as deform bones.

    Shift:  Expand current selection
    Ctrl: Deselect from current selection
    Alt:  Invert selection
    """

    bl_idname = "catalyst.select_deform_bones"
    bl_label = "Select Deform Bones"

    def filter_bones(self, obj: bpy.types.Object, bones: List[bpy.types.Bone]) -> List[bpy.types.Bone]:
        return [b for b in bones if b.use_deform]


class SelectBonesWithConstraints(bpy.types.Operator, SelectBonesMixin):
    """
    Selects all bones that have at least 1 constraint.

    Shift:  Expand current selection
    Ctrl: Deselect from current selection
    Alt:  Invert selection
    """

    bl_idname = "catalayst.select_bones_with_constraints"
    bl_label = "Select Bones with Constraints"

    def filter_bones(self, obj: bpy.types.Object, bones: List[bpy.types.Bone]) -> List[bpy.types.Bone]:
        output = []

        for b in bones:
            pb = obj.pose.bones.get(b.name)
            if pb is not None and len(pb.constraints) > 0:
                output.append(b)

        return output


class SelectOrphanBones(bpy.types.Operator, SelectBonesMixin):
    """
    Selects all bones that have no parent assigned.

    Shift:  Expand current selection
    Ctrl: Deselect from current selection
    Alt:  Invert selection
    """

    bl_idname = "catalyst.select_orphan_bones"
    bl_label = "Select Orphan Bones"

    def filter_bones(self, obj: bpy.types.Object, bones: List[bpy.types.Bone]) -> List[bpy.types.Bone]:
        return [b for b in bones if not b.parent]


class SelectUnreferencedBones(bpy.types.Operator, SelectBonesMixin):
    """
    Selects all bones aren't referenced by any other bones.

    Shift:  Expand current selection
    Ctrl: Deselect from current selection
    Alt:  Invert selection
    """

    bl_idname = "catalyst.select_unref_bones"
    bl_label = "Select Unreferenced Bones"

    def filter_bones(self, obj: bpy.types.Object, bones: List[bpy.types.Bone]) -> List[bpy.types.Bone]:
        output = slice(bones)

        for b in bones:

            # remove the parent bone from the list
            output = [o for o in output if b.parent != o]

            # look at the targeted bones in the pose bone constraints to determine if the bone is referenced
            pb = obj.pose.bones.get(b.name)
            if pb is not None:
                for c in pb.constraints:
                    output = [o for o in output if c.subtarget != b.name]

        return output


class SelectRootDeformBones(bpy.types.Operator, SelectBonesMixin):
    """
    Selects all root bones (bones with no parents) that are set to deform the mesh.

    Shift:  Expand current selection
    Ctrl: Deselect from current selection
    Alt:  Invert selection
    """

    bl_idname = "catalyst.select_root_deform_bones"
    bl_label = "Select Root Deform Bones"

    def filter_bones(self, obj: bpy.types.Object, bones: List[bpy.types.Bone]) -> List[bpy.types.Bone]:
        return [b for b in bones if not b.parent and b.use_deform]


def add_submenu_to_select_menu(self, context):
    layout: bpy.types.UILayout = self.layout
    layout.separator()
    layout.operator(SelectOrphanBones.bl_idname, text="Orphaned Bones")
    layout.operator(SelectUnreferencedBones.bl_idname, text="Unreferenced Bones")
    layout.operator(SelectDeformBones.bl_idname, text="Deform Bones")
    layout.operator(SelectRootDeformBones.bl_idname, text="Root Deform Bones")
    layout.operator(SelectBonesWithConstraints.bl_idname, text="Bones w/ Constraints")


def register():
    bpy.types.VIEW3D_MT_select_edit_armature.append(add_submenu_to_select_menu)
    bpy.types.VIEW3D_MT_select_pose.append(add_submenu_to_select_menu)


def unregister():
    bpy.types.VIEW3D_MT_select_pose.remove(add_submenu_to_select_menu)
    bpy.types.VIEW3D_MT_select_edit_armature.remove(add_submenu_to_select_menu)