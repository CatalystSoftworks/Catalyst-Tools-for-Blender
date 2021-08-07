import bpy
from mathutils import Color


def set_active(obj=None):
    """Sets the given object as the currently active object."""
    bpy.context.view_layer.objects.active = obj


def check_selection_mode(vert=True, edge=False, face=False):
    """Returns true if the context mode is EDIT_MESH and the specified elements are selected."""
    return bpy.context.mode == "EDIT_MESH" and tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (vert, edge, face)


def get_selected_faces(context, indexes=False):
    obj = context.object

    if obj == None or obj.type != "MESH":
        return []

    mesh = obj.data
    obj.update_from_editmode()  # Loads edit-mode data into object data
    return [(p.index if indexes else p) for p in mesh.polygons if p.select]


def select_faces_by_color(context, color):
    """Will find the faces of the active mesh that have the assigned color and select them."""

    if context.object == None or context.mode != "EDIT_MESH":
        return

    context.tool_settings.mesh_select_mode = (False, False, True)
    bpy.ops.mesh.select_all(action="DESELECT")

    mesh = context.object.data

    if "ID" not in mesh.vertex_colors:
        mesh.vertex_colors.new(name="ID")
    colormap = mesh.vertex_colors["ID"]

    print(colormap.data)

    for poly in mesh.polygons:
        lix = poly.loop_indices[0]
        # Only look at first vertex as all should have same color
        if (0 <= lix < len(colormap.data)) and colormap.data[lix].color == Color(color[0:3]):
            poly.select = True
            print("face selected!")


def get_vertex_color(mesh, vertid):
    for loop in mesh.loops:
        if loop.vertex_index == vertid:
            return mesh.vertex_colors[0].data[loop.index].color
    return (0.0, 0.0, 0.0)


def paint_selected_faces(context, color):
    """Paints the selected faces with the given color."""
    mode = context.mode
    obj = context.object
    mesh = obj.data

    # use active color map, create one if none available
    if "ID" not in mesh.vertex_colors:
        id_map = mesh.vertex_colors.new(name="ID")
        mesh.vertex_colors.active = id_map
    else:
        id_map = mesh.vertex_colors["ID"]

    bpy.ops.object.mode_set(mode="VERTEX_PAINT")

    prev_masking = mesh.use_paint_mask
    prev_color_map = mesh.vertex_colors.active
    prev_color = bpy.data.brushes["Draw"].color

    mesh.use_paint_mask = True
    mesh.vertex_colors.active = id_map
    bpy.data.brushes["Draw"].color = color[:3]
    bpy.ops.paint.vertex_color_set()

    mesh.vertex_colors.active = prev_color_map
    bpy.data.brushes["Draw"].color = prev_color

    mesh.use_paint_mask = prev_masking

    if mode != "VERTEX_PAINT":
        if mode == "EDIT_MESH":
            bpy.ops.object.mode_set(mode="EDIT")
        else:
            bpy.ops.object.mode_set(mode=mode)


def assign_material_to_selection(context, mat, assign_to_faces=False, select_all=False):
    """Appends the material the mesh objects in the selection."""
    active = context.object
    mode = context.mode

    for obj in context.selected_objects:
        if obj.type != "MESH":
            continue

        set_active(obj)

        if mode != "EDIT_MESH":
            bpy.ops.object.mode_set(mode="EDIT")

        if mat.name not in obj.data.materials:
            obj.data.materials.append(mat)
            obj.active_material_index = len(obj.data.materials)-1
        else:
            obj.active_material_index = [*obj.data.materials].index(mat)

        if assign_to_faces:
            if select_all:
                bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.object.material_slot_assign()

        if mode != "EDIT_MESH":
            bpy.ops.object.mode_set(mode=mode)

    set_active(active)
