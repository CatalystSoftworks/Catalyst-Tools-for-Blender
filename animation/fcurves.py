import bpy
import random


class RemoveModifiers(bpy.types.Operator):
    """Removes all F-Curve modifiers from the selected channels."""
    bl_idname = "catalyst.bulk_remove_fcurve_modifiers"
    bl_label = "Remove F-Curve Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "GRAPH_EDITOR" or context.area.type == "DOPESHEET_EDITOR"

    def execute(self, context):
        curves = bpy.context.selected_editable_fcurves

        for c in curves:
            for m in c.modifiers:
                c.modifiers.remove(m)

        return {"FINISHED"}


class LoopChannels(bpy.types.Operator):
    """Adds a Cycles modifier to the top of stack of multiple selected channels, regardless if there are other modifiers."""
    bl_idname = "catalyst.bulk_add_cycles_modifier"
    bl_label = "Add Cycles Modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "GRAPH_EDITOR" or context.area.type == "DOPESHEET_EDITOR"

    def execute(self, context):
        curves = bpy.context.selected_editable_fcurves

        for c in curves:
            if "CYCLES" not in [m.type for m in c.modifiers]:
                if len(c.modifiers) == 0:
                    c.modifiers.new("CYCLES")
                else:
                    mod_data = []

                    for m in c.modifiers:
                        keys = dir(m)
                        mod_data.append({k: getattr(m, k) for k in keys})
                        c.modifiers.remove(m)

                    c.modifiers.new("CYCLES")

                    for m in mod_data:
                        mod = c.modifiers.new(m["type"])
                        for k in m:
                            if k != "type":
                                try:
                                    setattr(mod, k, m[k])
                                except:
                                    pass

        return {"FINISHED"}


class GenerateNoise(bpy.types.Operator):
    """Generates random noise using pseudo random number generation and the noise F-Curve Modifier"""
    bl_idname = "catalyst.generate_fcurve_noise"
    bl_label = "Generate Noise"
    bl_options = {"REGISTER", "UNDO"}

    loop: bpy.props.BoolProperty(
        name="Loop Animation (Adds Cycles Modifier)",
        description="Loops the entire curve for the animation via the cycles modifier",
        default=False,
    )

    seed: bpy.props.IntProperty(
        name="Seed",
        min=0,
        default=12345,
    )

    use_scale_range: bpy.props.BoolProperty(
        name="Use Frequency Range",
        default=True,
    )

    scale: bpy.props.FloatProperty(
        name="Frequency",
        default=0.1,
    )

    scale_range: bpy.props.FloatVectorProperty(
        name="Frequency Range",
        size=2,
        default=[0.0, 0.1],
    )

    strength: bpy.props.FloatProperty(
        name="Strength",
        default=0.1,
    )

    depth: bpy.props.IntProperty(
        name="Depth",
        min=0,
        max=32767,
        default=0,
    )

    random_phase: bpy.props.BoolProperty(
        name="Random Phase Range",
        default=False,
    )

    blend_type: bpy.props.EnumProperty(
        name="Blend Type",
        items=[
            ("REPLACE", "Replace", ""),
            ("ADD", "Add", ""),
            ("SUBTRACT", "Subtract", ""),
            ("MULTIPLY", "Multiply", ""),
        ],
        default="ADD",
    )

    use_restricted_range: bpy.props.BoolProperty(
        name="Restrict Frame Range",
        description="F-Curve Modifier is only applied for the specified frame range to help mask off effects in order to chain them",
        default=False,
    )

    auto_frame_range: bpy.props.BoolProperty(
        name="Automatically Set Frame Range",
        default=True,
    )

    frame_range: bpy.props.FloatVectorProperty(
        name="Frame Range (Start, End)",
        size=2,
    )

    auto_blend: bpy.props.EnumProperty(
        name="Blend Range Mode",
        items=[
            ("NONE", "None", "Don't set a blend range"),
            ("EXPLICIT", "Explicit", "Set the blend range"),
            ("AUTO", "Automatic (Equal)", "Set the blend range to be 50/50 of the frame range"),
            ("AUTO_IN", "Automatic (In)", "Set the blend range to fade in over the total frame range"),
            ("AUTO_OUT", "Automatic (Out)", "Set the blend range to fade out over the total frame range"),
            ("RANDOM_EVEN", "Random (Even)", "Completely randomizes the blend range between the blend in and blend out"),
            ("RANDOM_ODD", "Random (Odd)", "Completely randomizes the blend range with deadzone of no blending"),
        ],
        default="NONE",
    )

    blend_range: bpy.props.FloatVectorProperty(
        name="Blend Range (Blind In, Blend Out)",
        size=2,
    )

    random_influence: bpy.props.BoolProperty(
        name="Randomize Influence",
        default=True,
    )

    influence_range: bpy.props.FloatVectorProperty(
        name="Influence Range",
        min=0,
        max=1,
        size=2,
        default=[0, 1],
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == "GRAPH_EDITOR" or context.area.type == "DOPESHEET_EDITOR"

    def execute(self, context):
        curves = bpy.context.selected_editable_fcurves
        rand = random.Random(self.seed)

        if self.loop:
            bpy.ops.catalyst.bulk_add_cycles_modifier()

        for c in curves:
            noise: bpy.types.FModifierNoise = c.modifiers.new("NOISE")
            noise.strength = self.strength
            noise.phase = random.uniform(0, 999999)
            noise.depth = self.depth
            noise.scale = rand.uniform(self.scale_range[0], self.scale_range[1]) if self.use_scale_range else self.scale
            noise.offset = round(rand.uniform(0, 9999999))

            if self.random_influence:
                noise.use_influence = True
                noise.influence = rand.uniform(self.influence_range[0], self.influence_range[1])

            noise.use_restricted_range = self.use_restricted_range

            if self.use_restricted_range:
                if self.auto_frame_range:
                    frames = bpy.context.object.animation_data.action.frame_range
                    noise.frame_start = frames[0] # bpy.context.scene.frame_start
                    noise.frame_end = frames[1] # bpy.context.scene.frame_end
                else:
                    noise.frame_start = self.frame_range[0]
                    noise.frame_end = self.frame_range[1]

                if self.auto_blend == "EXPLICIT":
                    noise.blend_in = self.blend_range[0]
                    noise.blend_out = self.blend_range[1]
                else:
                    range = noise.frame_end - noise.frame_start

                    if self.auto_blend == "AUTO":
                        noise.blend_in = (range / 2)
                        noise.blend_out = (range / 2)
                    elif self.auto_blend == "AUTO_IN":
                        noise.blend_in = range
                    elif self.auto_blend == "AUTO_OUT":
                        noise.blend_out = range
                    elif self.auto_blend == "RANDOM_EVEN":
                        noise.blend_in = rand.uniform(0, range)
                        noise.blend_out = range - noise.blend_in
                    elif self.auto_blend == "RANDOM_ODD":
                        deadzone = rand.uniform(0, range)
                        range = range - deadzone
                        noise.blend_in = rand.uniform(0, range)
                        noise.blend_out = range - noise.blend_in

        self.report({"INFO"}, "Added noise modifier to %d selected channels" % (len(curves)))

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "seed")
        layout.prop(self, "loop")

        layout.separator()

        layout.label(text="Scale")
        row = layout.row(align=True)
        row.prop(self, "scale_range" if self.use_scale_range else "scale")
        row.prop(self, "use_scale_range", text="Range", emboss=True, toggle=1)

        layout.prop(self, "strength")
        layout.prop(self, "depth")
        layout.prop(self, "random_phase")

        layout.prop(self, "random_influence")
        layout.prop(self, "blend_type")

        layout.separator()

        layout.prop(self, "use_restricted_range")

        if self.use_restricted_range:
            box = layout.box()
            box.prop(self, "auto_frame_range")

            if not self.auto_frame_range:
                box.prop(self, "frame_range")

            box.prop(self, "auto_blend")

            if self.auto_blend == "EXPLICIT":
                box.prop(self, "blend_range")

        layout.separator()


class CopyActiveNoiseToSelectedChannels(bpy.types.Operator):
    """Copies the settings from the active channel's noise modifiers and adds it as a new modifier to other selected
    channels."""
    bl_idname = "catalyst.copy_active_noise_to_selected"
    bl_label = "Copy Active Noise to Selected Channels"
    bl_options = {"INTERNAL", "UNDO", "REGISTER"}

    only_active_modifier: bpy.props.BoolProperty(
        name="Only Active Modifier",
        default=False,
    )

    randomize_phase: bpy.props.BoolProperty(
        name="Randomize Phase",
        default=True,
    )

    randomize_offset: bpy.props.BoolProperty(
        name="Randomize Offset",
        default=False,
    )

    randomize_influence: bpy.props.BoolProperty(
        name="Randomize Influence",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        if not (context.area.type == "GRAPH_EDITOR" or context.area.type == "DOPESHEET_EDITOR"):
            return False
        if context.active_editable_fcurve is None:
            return False
        return "NOISE" in [m.type for m in context.active_editable_fcurve.modifiers]

    def execute(self, context):
        selected_curves = bpy.context.selected_editable_fcurves
        active_curve = bpy.context.active_editable_fcurve
        sources = [m for m in active_curve.modifiers if m.type == "NOISE" and (m.active or not self.only_active_modifier)]

        if len(sources) == 0:
            self.report({"WARNING"}, "Unable to find active noise modifier")
            return {"CANCELLED"}

        for c in selected_curves:
            if c == active_curve:
                continue

            for source in sources:
                clone: bpy.types.FModifierNoise = c.modifiers.new("NOISE")
                clone.scale = source.scale
                clone.strength = source.strength
                clone.offset = random.uniform(0, 999999) if self.randomize_offset else source.offset
                clone.phase = random.uniform(0, 999999) if self.randomize_phase else source.phase
                clone.depth = source.depth
                clone.use_restricted_range = source.use_restricted_range
                clone.frame_start = source.frame_start
                clone.frame_end = source.frame_end
                clone.blend_in = source.blend_in
                clone.blend_out = source.blend_out
                clone.use_influence = source.use_influence or self.randomize_influence
                clone.influence = random.uniform(0, 1) if self.randomize_influence else source.influence

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        active_curve = context.active_editable_fcurve

        if (
                active_curve is not None and
                active_curve.modifiers.active is not None and
                active_curve.modifiers.active.type == "NOISE"
        ):
            layout.prop(self, "only_active_modifier")

        layout.prop(self, "randomize_phase")
        layout.prop(self, "randomize_offset")
        layout.prop(self, "randomize_influence")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class ImpactJitter(bpy.types.Operator):
    """Adds a noise modifier to the chosen channels on all selected bones."""
    bl_idname = "catalyst.add_impact_jitter"
    bl_label = "Add Impact Jitter"
    bl_options = {"REGISTER", "UNDO"}

    seed: bpy.props.IntProperty(
        name="Seed",
        description="Random seed used for the pseudo random number generator",
        min=0,
        default=8675309,
    )

    scale_range: bpy.props.FloatVectorProperty(
        name="Frequency Range",
        description="Used to populate the scale value randomly per channel",
        size=2,
        default=[0.0, 0.1],
    )

    strength: bpy.props.FloatProperty(
        name="Max Strength",
        description="Strength applied to all channels",
        default=0.1,
    )

    influence_range: bpy.props.FloatVectorProperty(
        name="Influence Range",
        description="Range used to control random influence per channel",
        min=0,
        max=1,
        size=2,
        default=[0, 1],
    )

    lead_frames: bpy.props.IntProperty(
        name="Fade-In Frames",
        description="Number of frames to fade the noise in",
        min=0,
        default=2,
    )

    sustain_frames: bpy.props.IntProperty(
        name="Sustain Frames",
        description="Number of frames to keep the noise at a constant level",
        min=0,
        default=0,
    )

    tail_frames: bpy.props.IntProperty(
        name="Fade-Out Frames",
        description="Number of frames to fade the noise out",
        min=0,
        default=5,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "seed")
        layout.prop(self, "strength")
        layout.prop(self, "scale_range")
        layout.prop(self, "influence_range")

        row = layout.row()
        row.prop(self, "lead_frames")
        row.prop(self, "sustain_frames")
        row.prop(self, "tail_frames")

    @classmethod
    def poll(cls, context):
        return context.area.type == "GRAPH_EDITOR" or context.area.type == "DOPESHEET_EDITOR"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        curves = bpy.context.selected_editable_fcurves
        rand = random.Random(self.seed)

        current_frame = bpy.context.scene.frame_current

        for c in curves:
            noise: bpy.types.FModifierNoise = c.modifiers.new("NOISE")

            noise.scale = rand.uniform(self.scale_range[0], self.scale_range[1])
            noise.strength = self.strength
            noise.offset = rand.uniform(0, 9999999)
            noise.use_influence = True
            noise.influence = random.uniform(self.influence_range[0], self.influence_range[1])

            noise.use_restricted_range = True
            noise.frame_start = current_frame - self.lead_frames
            noise.frame_end = current_frame + self.sustain_frames + self.tail_frames
            noise.blend_in = self.lead_frames
            noise.blend_out = self.tail_frames

        self.report({"INFO"}, "Added noise modifier to %d selected channels" % (len(curves)))

        return {"FINISHED"}


def fcurve_tools_submenu(self, context):
    layout: bpy.types.UILayout = self.layout
    layout.separator()
    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator(LoopChannels.bl_idname)
    layout.operator(CopyActiveNoiseToSelectedChannels.bl_idname)
    layout.operator(GenerateNoise.bl_idname)
    layout.operator(ImpactJitter.bl_idname)
    layout.operator(RemoveModifiers.bl_idname)


def register():
    bpy.types.DOPESHEET_MT_context_menu.append(fcurve_tools_submenu)
    bpy.types.DOPESHEET_MT_channel_context_menu.append(fcurve_tools_submenu)


def unregister():
    bpy.types.DOPESHEET_MT_context_menu.remove(fcurve_tools_submenu)
    bpy.types.DOPESHEET_MT_channel_context_menu.remove(fcurve_tools_submenu)
