# Catalyst Tools for Blender

This is an addon for Blender 2.93+ that contains a collection of utilities that Catalyst has found useful when creating models, rigs, and animations in Blender - particularly for games.

> **Note from Nick Glenn:** This addon effectively encompasses work I did in several smaller add ons for Blender over the past few years. Managing multiple, smaller projects started to become a real hassle to maintain rather than just collecting them all in a single large project. This means that many of my smaller addons may get merged into this one (or my [Command Config addon](https://github.com/NickGlenn/Command-Config-for-Blender)) moving forward.

## Installation

Download this repository and open up Blender, then navigate to your user preferences. Select the "Addons" tab and then click "Install Addon from File". When the file selection dialog pops up, select the `.zip` you downloaded.

## Development

If you wish to contribute to the development of this addon, I've found that the best workflow is to use Jacques Lucke's excellent (though no longer supported) "Blender Development" extension for VS Code. This in addition with the [fake-bpy-module](https://pypi.org/project/fake-bpy-module-2.93/) that can be installed via `pip` allows a much easier and faster development environment than any of the alternatives I've seen.

> If you're working on Windows, be aware that you may have issues with folder permissions when attempting to use the "Build and Start" feature from the "Blender Development" extension. Either change Blender to use your custom installation of `python` or edit the file permissions for Blender's application folder and subfolders to get around these issues.

# Feature Set: Selection Operators

Menu: `Select`

A variety of new selection operators are now available. These _should_ all be available from the "select" menu for the various object modes and may be specific to different types of objects (like meshes, armatures, etc).

> **Note:** Many of these selection operators support alternate modes when activated with alt, shift, or control held. The common pattern used for this "power-user" functionality is as follows...
>
> - Shift: Expands the current selection with the selection from the operator.
> - Alt: Inverts the selection of the operator.
> - Ctrl: Performs a deselect instead of a selection.


## Bone Selection

These selection operators are available when dealing with armatures in either the "Edit Armature" or "Pose" modes.

**Select Deform Bones:** Selects all bones that are currently marked as deform bones.
**Select Bones with Constraints:** Selects all bones that have at least 1 bone constraint in pose mode.
**Select Orphan Bones:** Selects all bones that have no parent assigned. _This will often result in the selection of root bones._
**Select Unreferenced Bones:** Selects all bones aren't referenced by any other bones. This means all bones that aren't a parent of another bone and that have no bone constraints (from within the same rig) targeting them. _This does not currently do a reference check for object constraints or bone constraints from other armatures!_
**Select Root Deform Bones:** Selects all root bones (bones with no parents) that are set to deform the mesh.

# Feature Set: Rigging Utilities

## Convert to Game Ready Rig

Menu: `Object / Convert To / Game Ready Rig`

This feature is intended to assist with conversions of third-party armatures that are not set up correctly for game engines. It does this by creating a duplicate of the selected armature and performing the following operations on the duplicate:

1. Removes all non-deforming bones
1. Removing all bone constraints and custom shapes on the remaining deform bones
1. Disables "Bendy Bones" by setting the bendy bone segments to `1`
1. Ensuring that local rotation, inherit rotation, and inherit scale are enabled
1. Adds a "Copy Transforms" bone constraint for each bone in the duplicate that points to the related bone in the original armature
1. Reparents any meshes that used the control rig's armature to the new game ready duplicate

With the duplicate in hand, you can solve engine specific issues, like multiple root bones or incorrect bone hierarchy, while preserving the original functionality of the control rig.

> The operation will provide a warning if you have more than 1 root bone in the armature. This is important as game engines (like Unreal) won't accept armatures that have more than 1 root bone.

# Feature Set: Mesh Utilities

## Copy + Separate Macro

Menu: `Mesh / Split / Copy + Separate`

Performs a duplication of the current selection and separates it into its own mesh. This is functionally similar to pressing `Shift + D` followed by `P` and choosing "selection". Can be easily added to quick favorites or assigned to a hotkey (like `Shift + Ctrl + P`) to streamline this common operation.

# Feature Set: Animation Utilities

### Add Cycles Modifier

Adds a Cycles modifier to the top of stack of multiple selected channels, _regardless if there are other modifiers_.

### Generate Noise

Generates random noise using pseudo random number generation in conjunction with the noise F-Curve Modifier.

### Add Impact Jitter

Adds a noise modifier to the chosen channels on all selected bones that is configured to create a small burst of "jitter". This is useful if you want to add a sharp, quick shake to an object non-destructively.

### Copy Active Noise to Selected Channels

Copies the settings from the active channel's noise modifiers and adds it as a new modifier to other selected channels.

### Remove F-Curve Modifiers

Removes all F-Curve modifiers from the selected channels.