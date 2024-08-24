bl_info = {
    "name": "Export to MuJoCo XML",
    "blender": (2, 82, 1),  # Adjust this to match your Blender version
    "category": "Import-Export",
    "description": "Exports selected objects to MuJoCo XML format with position, quaternion rotation, and scale",
    "author": "peteblank",
}

import bpy
import os
import math  # Import the math module for angle conversion

def get_mujoco_transform_matrix(obj):
    """Converts Blender object's transformation to MuJoCo format"""
    loc, rot, scale = obj.matrix_world.decompose()
    
    # Get quaternion components
    quat = rot
    x, y, z, w = quat.x, quat.y, quat.z, quat.w

    # Debugging: Print the extracted values
    print(f"Object: {obj.name}")
    print(f"Location: {loc}")
    print(f"Quaternion Rotation (w, x, y, z): {w}, {x}, {y}, {z}")
    print(f"Scale: {scale}")

    return loc, quat, scale

def export_mujoco_xml(filepath):
    """Exports selected objects to a MuJoCo XML file"""
    # Extract base name for use in asset file paths
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    
    with open(filepath, 'w') as file:
        file.write('<?xml version="1.0"?>\n')
        file.write(f'<mujoco model="{base_name}">\n')
        
        # Default section
        file.write('  <default>\n')
        file.write('    <default class="visual">\n')
        file.write('      <geom group="2" type="mesh" contype="0" conaffinity="0"/>\n')
        file.write('    </default>\n')
        file.write('    <default class="collision">\n')
        file.write('      <geom group="3" type="mesh"/>\n')
        file.write('    </default>\n')
        file.write('  </default>\n')
        
        # Asset section
        file.write('  <asset>\n')
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                # Assuming the OBJ file names are the same as the object names
                obj_name = obj.name
                file.write(f'    <mesh file="{obj_name}.obj"/>\n')
        file.write('  </asset>\n')
        
        # Worldbody section
        file.write('  <worldbody>\n')
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                loc, quat, scale = get_mujoco_transform_matrix(obj)
                
                # Write <body> element
                file.write(f'    <body name="{obj.name}">\n')
                file.write(f'      <geom mesh="{obj.name}" class="visual" quat="{quat.w} {quat.x} {quat.y} {quat.z}" pos="{loc.x} {loc.y} {loc.z}"/>\n')
                file.write(f'      <geom mesh="{obj.name}" class="collision" quat="{quat.w} {quat.x} {quat.y} {quat.z}" pos="{loc.x} {loc.y} {loc.z}"/>\n')
                file.write('    </body>\n')
        
        file.write('  </worldbody>\n')
        file.write('</mujoco>\n')

class ExportToMuJoCoOperator(bpy.types.Operator):
    """Export selected objects to MuJoCo XML"""
    bl_idname = "export_scene.mujoco_xml"
    bl_label = "Export to MuJoCo XML"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        export_mujoco_xml(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_export(self, context):
    self.layout.operator(ExportToMuJoCoOperator.bl_idname, text="MuJoCo XML (.xml)")

def register():
    bpy.utils.register_class(ExportToMuJoCoOperator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportToMuJoCoOperator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
