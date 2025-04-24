bl_info = {
    "name": "Subdivision Controller",
    "author": "Awaken Idiotic",
    "version": (1, 0, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Object > Subdivision Controller",
    "description": "Create an object to control subdivision settings for multiple objects",
    "category": "Object",
}

import bpy
from bpy.props import IntProperty, StringProperty, PointerProperty

# Modified function to get objects from a target name
def get_objects_from_target(target_name):
    objects_to_process = []
    
    # Strip whitespace
    target_name = target_name.strip()
    
    # Check if it's a collection
    if target_name in bpy.data.collections:
        # Get all mesh objects in the collection and its child collections
        objects_to_process.extend(get_collection_objects(bpy.data.collections[target_name]))
    
    # Or if it's an object
    elif target_name in bpy.data.objects:
        obj = bpy.data.objects[target_name]
        if obj.type == 'MESH':
            objects_to_process.append(obj)
        
        # Also process all children meshes
        for child in obj.children_recursive:
            if child.type == 'MESH':
                objects_to_process.append(child)
    
    return objects_to_process
    
# Helper function to get all objects in a collection (unchanged)
def get_collection_objects(collection):
    objects = []
    for obj in collection.objects:
        if obj.type == 'MESH':
            objects.append(obj)
    for child in collection.children:
        objects.extend(get_collection_objects(child))
    return objects
    
# Function to count objects in a collection with subdivision (unchanged)
def count_collection_objects(collection):
    count = 0
    subd_count = 0
    for obj in collection.objects:
        if obj.type == 'MESH':
            count += 1
            if any(mod.type == 'SUBSURF' for mod in obj.modifiers):
                subd_count += 1
    for child in collection.children:
        c, s = count_collection_objects(child)
        count += c
        subd_count += s
    return count, subd_count
    
def get_selected_outliner_items():
    # Find Outliner area
    area = next((a for a in bpy.context.window.screen.areas if a.type == 'OUTLINER'), None)
    if not area:
        print("No Outliner area found.")
        return

    region = next((r for r in area.regions if r.type == 'WINDOW'), None)
    if not region:
        print("No Outliner region found.")
        return

    allselection = []
    with bpy.context.temp_override(
        window=bpy.context.window,
        area=area,
        region=region
    ):
        ids = bpy.context.selected_ids

        collections = [item.name for item in ids if isinstance(item, bpy.types.Collection)]
        objects = [item.name for item in ids if isinstance(item, bpy.types.Object)]

        print("Selected Collections:")
        for col in collections:
            print("  -", col)

        print("Selected Objects:")
        for obj in objects:
            print("  -", obj)

        # ✅ Correct way to add to list
        allselection.extend(collections)
        allselection.extend(objects)

    return allselection

def convert_listtostring(list):
    slist = [str(element) for element in list]
    slist = ", ".join(list)
    
    return slist

# Property group for subdivision control properties
class SubdivisionControlProperties(bpy.types.PropertyGroup):
    subdivision_levels: IntProperty(
        name="Viewport",
        description="Subdivision level for viewport display",
        min=0,
        max=6,
        default=1
    )
    subdivision_render_levels: IntProperty(
        name="Render",
        description="Subdivision level for rendering",
        min=0,
        max=6,
        default=2
    )
    subdivision_object: StringProperty(
        name="",
        description="Collections or objects to control subdivision for (comma separated)",
        default=""
    )
    show_only_control_edges: bpy.props.BoolProperty(
        name="Optimize Display",
        description="Display only control edges in the viewport",
        default=False
    )

# Operator to create a subdivision controller
class OBJECT_OT_create_subdivision_controller(bpy.types.Operator):
    """Create a subdivision controller object for selected objects"""
    bl_idname = "object.create_subdivision_controller"
    bl_label = "Create Subdivision Controller"
    bl_description = "Create a controller object to manage subdivision levels"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Create a new empty object
        control_obj = bpy.data.objects.new("SubdController", None)
        
        # Set the display type to PLAIN_AXES
        control_obj.empty_display_type = 'PLAIN_AXES'
        control_obj.empty_display_size = 1.0
        
        # Link to scene collection
        bpy.context.scene.collection.objects.link(control_obj)
        
        # Make the object active
        context.view_layer.objects.active = control_obj
        control_obj.select_set(True)
        
        # Set initial property values
        control_obj.subdivision_control.subdivision_levels = 1
        control_obj.subdivision_control.subdivision_render_levels = 2
        control_obj.subdivision_control.subdivision_object = ''
        
        self.report({'INFO'}, f"Created subdivision controller")
        return {'FINISHED'}

# Operator to update subdivision levels
class OBJECT_OT_update_subdivision_levels(bpy.types.Operator):
    """Update subdivision levels for all objects"""
    bl_idname = "object.update_subdivision_levels"
    bl_label = "Update Subdivision Levels"
    bl_description = "Update subdivision levels for all objects in the specified collections or objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        control_obj = context.object
        props = control_obj.subdivision_control
        
        # Get the current subdivision levels
        viewport_level = props.subdivision_levels
        render_level = props.subdivision_render_levels
        only_control_edges = props.show_only_control_edges
        
        # Get the target collection or object name
        targets_str = props.subdivision_object
        if not targets_str:
            self.report({'ERROR'}, "No target collections or objects specified")
            return {'CANCELLED'}
        
        # Split the targets string by commas
        target_names = [name.strip() for name in targets_str.split(',')]
        
        # Find objects to update based on all target names
        objects_to_update = []
        for target_name in target_names:
            objects_to_update.extend(get_objects_from_target(target_name))
        
        # Update subdivision modifiers for all found objects
        updated_count = 0
        for obj in objects_to_update:
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.levels = viewport_level
                    mod.render_levels = render_level
                    mod.show_only_control_edges = only_control_edges
                    updated_count += 1
                    break
        
        if updated_count == 0:
            self.report({'WARNING'}, f"No objects with subdivision modifiers found in specified targets")
        else:
            self.report({'INFO'}, f"Updated subdivision levels for {updated_count} objects")
        
        return {'FINISHED'}
        
# Operator to add subdivision modifiers to objects without them
class OBJECT_OT_add_subdivision_modifiers(bpy.types.Operator):
    """Add subdivision modifiers to objects that don't have them"""
    bl_idname = "object.add_subdivision_modifiers"
    bl_label = "Add Missing Modifiers"
    bl_description = "Add subdivision modifiers to objects that don't have them"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        control_obj = context.object
        props = control_obj.subdivision_control
        
        # Get the target collection or object names
        targets_str = props.subdivision_object
        if not targets_str:
            self.report({'ERROR'}, "No target collections or objects specified")
            return {'CANCELLED'}
        
        # Get the current subdivision levels
        viewport_level = props.subdivision_levels
        render_level = props.subdivision_render_levels
        only_control_edges = props.show_only_control_edges
        
        # Split the targets string by commas
        target_names = [name.strip() for name in targets_str.split(',')]
        
        # Find objects to process based on all target names
        objects_to_process = []
        for target_name in target_names:
            objects_to_process.extend(get_objects_from_target(target_name))
        
        # Add subdivision modifiers to objects that don't have them
        added_count = 0
        for obj in objects_to_process:
            # Check if the object already has a subdivision modifier
            has_subd = False
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    has_subd = True
                    break
            
            # If it doesn't have a subdivision modifier, add one
            if not has_subd:
                mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
                mod.levels = viewport_level
                mod.render_levels = render_level
                mod.show_only_control_edges = only_control_edges
                added_count += 1
        
        if added_count == 0:
            self.report({'INFO'}, "All objects already have subdivision modifiers")
        else:
            self.report({'INFO'}, f"Added subdivision modifiers to {added_count} objects")
        
        return {'FINISHED'}
        
# Operator to delete subdivision modifiers
class OBJECT_OT_delete_subdivision_modifiers(bpy.types.Operator):
    """Delete subdivision modifiers from target objects"""
    bl_idname = "object.delete_subdivision_modifiers"
    bl_label = "Delete Subdivision Modifiers"
    bl_description = "Remove subdivision modifiers from all objects in the specified targets"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        control_obj = context.object
        props = control_obj.subdivision_control
        
        # Get the target collection or object names
        targets_str = props.subdivision_object
        if not targets_str:
            self.report({'ERROR'}, "No target collections or objects specified")
            return {'CANCELLED'}
        
        # Split the targets string by commas
        target_names = [name.strip() for name in targets_str.split(',')]
        
        # Find objects to process based on all target names
        objects_to_process = []
        for target_name in target_names:
            objects_to_process.extend(get_objects_from_target(target_name))
        
        # Delete subdivision modifiers from objects
        deleted_count = 0
        for obj in objects_to_process:
            # Find and remove any subdivision modifiers
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    obj.modifiers.remove(mod)
                    deleted_count += 1
        
        if deleted_count == 0:
            self.report({'INFO'}, "No subdivision modifiers found to delete")
        else:
            self.report({'INFO'}, f"Deleted {deleted_count} subdivision modifiers")
        
        return {'FINISHED'}

# shade_smooth operators        
class OBJECT_OT_shade_smooth_objects(bpy.types.Operator):
    """Set shading to smooth for all target objects"""
    bl_idname = "object.shade_smooth_objects"
    bl_label = "Shade Smooth Objects"
    bl_description = "Set all target objects to shade smooth"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        control_obj = context.object
        props = control_obj.subdivision_control
        
        # Get the target objects
        targets_str = props.subdivision_object
        if not targets_str:
            self.report({'ERROR'}, "No target collections or objects specified")
            return {'CANCELLED'}
        
        # Split the targets string by commas
        target_names = [name.strip() for name in targets_str.split(',')]
        
        # Find objects to process
        objects_to_process = []
        for target_name in target_names:
            objects_to_process.extend(get_objects_from_target(target_name))
        
        # Set shade smooth for all objects
        count = 0
        for obj in objects_to_process:
            if obj.type == 'MESH':
                for polygon in obj.data.polygons:
                    polygon.use_smooth = True
                count += 1
        
        self.report({'INFO'}, f"Set {count} objects to shade smooth")
        return {'FINISHED'}

# shade_flat operators  
class OBJECT_OT_shade_flat_objects(bpy.types.Operator):
    """Set shading to flat for all target objects"""
    bl_idname = "object.shade_flat_objects"
    bl_label = "Shade Flat Objects"
    bl_description = "Set all target objects to shade flat"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        control_obj = context.object
        props = control_obj.subdivision_control
        
        # Get the target objects
        targets_str = props.subdivision_object
        if not targets_str:
            self.report({'ERROR'}, "No target collections or objects specified")
            return {'CANCELLED'}
        
        # Split the targets string by commas
        target_names = [name.strip() for name in targets_str.split(',')]
        
        # Find objects to process
        objects_to_process = []
        for target_name in target_names:
            objects_to_process.extend(get_objects_from_target(target_name))
        
        # Set shade flat for all objects
        count = 0
        for obj in objects_to_process:
            if obj.type == 'MESH':
                for polygon in obj.data.polygons:
                    polygon.use_smooth = False
                count += 1
        
        self.report({'INFO'}, f"Set {count} objects to shade flat")
        return {'FINISHED'}
        
# Operator to add selected objects to target list
class OBJECT_OT_add_targets_from_selection(bpy.types.Operator):
    """Add selected objects and active collection to target list"""
    bl_idname = "object.add_targets_from_selection"
    bl_label = "Add Targets From Selection"
    bl_description = "Add all selected objects and active collection to target list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        control_obj = context.object
        props = control_obj.subdivision_control
        
        # Get Selected Outliner Items
        lSelected = get_selected_outliner_items()
        lSelected.pop() # Remove Last Item
        
        # Join back with commas
        props.subdivision_object = convert_listtostring(lSelected)
        
        self.report({'INFO'}, f"Added {len(lSelected)} items to targets")
        return {'FINISHED'}

# Panel for subdivision controller properties
class OBJECT_PT_subdivision_control(bpy.types.Panel):
    """Panel for controlling subdivision levels"""
    bl_label = "Subdivision Controller"
    bl_idname = "OBJECT_PT_subdivision_control"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    @classmethod
    def poll(cls, context):
        # Only show for objects named *SubdController
        return context.object and "SubdController" in context.object.name
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        props = obj.subdivision_control
        
        # Calculate scale based on region width
        #region_width = context.region.width
        #field_scale = min(4.0, region_width / 100)  # Adjust scale based on panel width
        
        # Create UI for changing levels
        box = layout.box()
        box.label(text="Subdivision Levels:")
        
        # Simple row with manual scaling
        split = box.split(factor=0.10, align=True)
        split.label(text="Targets:")

        row = split.row(align=True)
        row.prop(props, "subdivision_object", text="")

        # Add spacing before button (optional)
        row.separator()

        # Create a sub-row to stretch the button a bit
        btn_row = row.row(align=True)
        btn_row.scale_x = 1.5
        btn_row.operator("object.add_targets_from_selection", text="", icon='EYEDROPPER')
        
        row = box.row()
        row.prop(props, "subdivision_levels")
        row.prop(props, "subdivision_render_levels")
        
        # Add checkbox for show_only_control_edges
        row = box.row()
        row.prop(props, "show_only_control_edges")
        
        # Add and Delete button
        op_row = box.row()
        op_row.operator("object.add_subdivision_modifiers", text="Add Subdiv Modifiers", icon='PLUS')
        op_row.operator("object.delete_subdivision_modifiers", text="Delete Subdiv Modifiers", icon='CANCEL')
        
        # Add update button
        op_row = box.row()
        op_row.operator("object.update_subdivision_levels", text="Update All Objects", icon='IMPORT')
        
        # Add shade smooth/flat buttons
        smooth_box = layout.box()
        smooth_box.label(text="Shading:")
        row = smooth_box.row(align=True)
        row.operator("object.shade_smooth_objects", text="Shade Smooth", icon='SMOOTHCURVE')
        row.operator("object.shade_flat_objects", text="Shade Flat", icon='SHARPCURVE')
        
        # Show statistics for all targets
        targets_str = props.subdivision_object
        if targets_str:
            target_names = [name.strip() for name in targets_str.split(',')]
            
            # Create a box for the statistics
            stats_box = layout.box()
            stats_box.label(text="Target Statistics:")
            
            total_mesh_count = 0
            total_subd_count = 0
            
            for target_name in target_names:
                if target_name in bpy.data.collections:
                    mesh_count, subd_count = count_collection_objects(bpy.data.collections[target_name])
                    stats_box.label(text=f"'{target_name}': {mesh_count} mesh, {subd_count} subdivision", icon='GROUP')
                    total_mesh_count += mesh_count
                    total_subd_count += subd_count
                    
                elif target_name in bpy.data.objects:
                    obj = bpy.data.objects[target_name]
                    if obj.type == 'MESH':
                        has_subd = any(mod.type == 'SUBSURF' for mod in obj.modifiers)
                        stats_box.label(text=f"'{obj.name}': {'has' if has_subd else 'no'} subdivision", icon='OBJECT_DATA')
                        total_mesh_count += 1
                        if has_subd:
                            total_subd_count += 1
                            
                    # Count children if it has any
                    child_mesh_count = 0
                    child_subd_count = 0
                    for child in obj.children_recursive:
                        if child.type == 'MESH':
                            child_mesh_count += 1
                            if any(mod.type == 'SUBSURF' for mod in child.modifiers):
                                child_subd_count += 1
                    
                    if child_mesh_count > 0:
                        stats_box.label(text=f"'{obj.name}': {child_mesh_count} mesh, {child_subd_count} subdivision", icon='OUTLINER')
                        total_mesh_count += child_mesh_count
                        total_subd_count += child_subd_count
                else:
                    stats_box.label(text=f"'{target_name}' not found", icon='ERROR')
            
            # Show totals
            if len(target_names) > 1:
                stats_box.label(text=f"Total: {total_mesh_count} mesh, {total_subd_count} subdivision")

# Function to add the operator to the Object menu
def add_subdivision_controller_menu(self, context):
    self.layout.operator("object.create_subdivision_controller", icon='MOD_SUBSURF')

# Registration
classes = (
    SubdivisionControlProperties,
    OBJECT_OT_create_subdivision_controller,
    OBJECT_OT_update_subdivision_levels,
    OBJECT_OT_add_subdivision_modifiers,
    OBJECT_OT_delete_subdivision_modifiers,
    OBJECT_OT_add_targets_from_selection,
    OBJECT_OT_shade_smooth_objects,
    OBJECT_OT_shade_flat_objects,
    OBJECT_PT_subdivision_control,
)

# Registration functions
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Object.subdivision_control = PointerProperty(type=SubdivisionControlProperties)
    
    # Add to the Add menu instead of Object menu
    bpy.types.VIEW3D_MT_add.append(add_subdivision_controller_menu)

def unregister():
    # Remove from the Add menu
    bpy.types.VIEW3D_MT_add.remove(add_subdivision_controller_menu)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Object.subdivision_control

# For testing directly in Blender's text editor
if __name__ == "__main__":
    register()