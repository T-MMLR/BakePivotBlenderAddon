bl_info = {
    "name": "Bake Pivot into Vertex Colors",
    "blender": (2, 90, 0),
    "author": "T-MMLR",
    "version": (1, 0),
    "location": "Side Panel (N) > Bake Pivot",
    "category": "Object",
}

import bpy
import random
from bpy.props import (BoolProperty,
                       PointerProperty
                       )
                       
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )

class BakePivotSettings(PropertyGroup):
    join_after: BoolProperty(
        name="Join Objects after baking",
        description="Enable this option to join meshes (like CTRL+J) after clicking the 'Bake Pivot' button.",
        default=False
    )

# https://blender.stackexchange.com/questions/57306/how-to-create-a-custom-ui
class BakePivot(Operator):
    bl_idname = "scene.bake_pivot"
    bl_label = "Bake Pivot"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return len(bpy.context.selected_objects) > 0 and bpy.context.object.mode == 'OBJECT'

    def execute(self, context):
        modified = []
        for object in bpy.context.selected_objects:
            if object.type != 'MESH':
                print(f"{object.name} is not a mesh. Not baking pivot.")
                continue
            
            nb_vertex_colors = len(object.data.vertex_colors)
            vertex_colors = None
            if nb_vertex_colors > 0:
                print(f"{object.name} has {nb_vertex_colors} vertex colors channels. Using the first one.")
                vertex_colors = object.data.vertex_colors[0]
            else:
                print(f"{object.name} has {nb_vertex_colors} vertex colors channels. Creating a new one.")
                vertex_colors = object.data.vertex_colors.new(name='Pivot', do_init=True)
            
            pivot_color = (object.location.x, object.location.y, object.location.z, 1)
            
            i = 0
            for poly in object.data.polygons:
                for idx in poly.loop_indices:
                    vertex_colors.data[i].color = pivot_color
                    i += 1
            
            modified.append(object)
        
        scene = context.scene
        bake_pivot_settings = scene.bake_pivot_settings
        if bake_pivot_settings.join_after:
            bpy.ops.object.select_all(action='DESELECT')
            for object in modified:
                object.select_set(True)
            
            context.view_layer.objects.active = modified[0]
            bpy.ops.object.join()

        # if len(modified) > 0:
            # set to vertex paint mode to see the result
            # bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        self.report({'INFO'}, f"Modified {len(modified)} objects.")
        return {'FINISHED'}

class OBJECT_PT_BakePivotPanel(Panel):
    bl_label = "Bake Pivot"
    bl_category = "Bake Pivot"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bake_pivot_settings = scene.bake_pivot_settings

        layout.label(text=str(len(bpy.context.selected_objects)) + " object(s) selected")
        layout.operator("scene.bake_pivot")

        layout.prop(bake_pivot_settings, "join_after")
    

def register():
    bpy.utils.register_class(BakePivotSettings)
    bpy.utils.register_class(OBJECT_PT_BakePivotPanel)
    bpy.utils.register_class(BakePivot)
    bpy.types.Scene.bake_pivot_settings = PointerProperty(type=BakePivotSettings)

def unregister():
    bpy.utils.unregister_class(BakePivotSettings)
    bpy.utils.unregister_class(OBJECT_PT_BakePivotPanel)
    bpy.utils.unregister_class(BakePivot)
    del bpy.types.Scene.bake_pivot_settings
    


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
