# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Instant Meshes Remesh",
    "description": "Remesh using instant meshes app",
    "author": "knekke, cgvirus",
    "version": (2, 0),
    "blender": (2, 90, 3),
    "category": "Object",
    "wiki_url": "https://github.com/cgvirus/Blender-Instant-Mesh-Bridge-addon"
}

import shutil
import tempfile
import subprocess
import os
import bpy
from bpy.types import AddonPreferences;




class InstantMeshesRemeshPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    filepath: bpy.props.StringProperty(
        name="Instant Meshes Executable",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="""Please specify the path to 'Instant Meshes.exe'
            Get it from https://github.com/wjakob/instant-meshes""")
        layout.prop(self, "filepath")


# class InstantMeshesRemeshBatch(bpy.types.Operator):
#     """Remesh selected objects with last used settings"""
#     bl_idname = "object.instant_meshes_remesh_batch"
#     bl_label = "Instant Meshes Remesh BATCH"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         s = bpy.context.selected_objects
#         for other_obj in bpy.data.objects:
#                     other_obj.select_set(state= False)
#         for i in s:
#             i.select_set(state= True)
#             bpy.context.view_layer.objects.active = i
#             bpy.ops.object.instant_meshes_remesh()
#             for slot, mat in enumerate(i.data.materials):
#                 bpy.data.objects[i.name+'_remesh'].data.materials[slot] = mat.copy()
#                 bpy.data.objects[i.name+'_remesh'].data.materials[slot].diffuse_color = (0.3,1,0.3)
#             i.select_set(state= False)
#             bpy.context.view_layer.objects.active = None
#         return {'FINISHED'}
#########################################
class InstantMeshesRemesh(bpy.types.Operator):
    """Remesh by using the Instant Meshes program"""
    bl_idname = "object.instant_meshes_remesh"
    bl_label = "Instant Meshes Remesh"
    bl_options = {'REGISTER', 'UNDO'}

    exported = False
    deterministic: bpy.props.BoolProperty(name="Deterministic (slower)", description="Prefer (slower) deterministic algorithms", default=False)
    dominant: bpy.props.BoolProperty(name="Dominant", description="Generate a tri/quad dominant mesh instead of a pure tri/quad mesh", default=False)
    intrinsic: bpy.props.BoolProperty(name="Intrinsic", description="Intrinsic mode (extrinsic is the default)", default=False)
    boundaries: bpy.props.BoolProperty(name="Boundaries", description="Align to boundaries (only applies when the mesh is not closed)", default=False)
    crease: bpy.props.IntProperty(name="Crease Degree", description="Dihedral angle threshold for creases", default=0, min=0, max=100)
    verts: bpy.props.IntProperty(name="Vertex Count", description="Desired vertex count of the output mesh", default=2000, min=10, max=50000)
    smooth: bpy.props.IntProperty(name="Smooth iterations", description="Number of smoothing & ray tracing reprojection steps (default: 2)", default=2, min=0, max=10)
    showwire: bpy.props.BoolProperty(name="Show Wireframes", description="Output with wireframe on", default=False)
    temp_objs_to_proj_dirc: bpy.props.BoolProperty(name="Save temp obj in project directory", description="Save temporary objects in project directory", default=False)
    openUI: bpy.props.BoolProperty(name="Open in InstantMeshes", description="Opens the selected object in Instant Meshes and imports the result when you are done.", default=False)
    remeshIt: bpy.props.BoolProperty(name="Start Remeshing", description="Activating it will start Remesh", default=False)


    loc = None
    rot = None
    scl = None
    meshname = None

    def execute(self, context):
        exe = bpy.path.abspath(context.preferences.addons[__package__].preferences.filepath)
        projpath = bpy.data.filepath
        directory = os.path.dirname(projpath)
        if self.temp_objs_to_proj_dirc:
        	if bpy.data.is_saved:
        		dirname = os.path.join(directory,'instantmeshes_temp')
        		if not os.path.exists(dirname):
        			os.makedirs(dirname)
        		else:
        			pass
        		orig = os.path.join(dirname,'original.obj')
        		output = os.path.join(dirname,'out.obj')
        	else:
        		self.report({'ERROR'}, 'File not saved!')
        		return {'CANCELLED'}
        else:
        	orig = os.path.join(tempfile.gettempdir(), 'original.obj')
        	output = os.path.join(tempfile.gettempdir(), 'out.obj')

        if self.remeshIt:

            if not self.exported:
                try:
                    os.remove(orig)
                except:
                    pass
                self.meshname = bpy.context.active_object.name
                mesh = bpy.context.active_object
                # self.loc = mesh.matrix_world.to_translation()
                # self.rot = mesh.matrix_world.to_euler('XYZ')
                # self.scl = mesh.matrix_world.to_scale()
                # bpy.ops.object.location_clear()
                # bpy.ops.object.rotation_clear()
                # bpy.ops.object.scale_clear()
                bpy.ops.export_scene.obj(filepath=orig,
                                         check_existing=False,
                                         axis_forward='-Z', axis_up='Y',
                                         use_selection=True,
                                         use_mesh_modifiers=True,
                                         # use_mesh_modifiers_render=False,
                                         use_edges=True,
                                         use_smooth_groups=False,
                                         use_smooth_groups_bitflags=False,
                                         use_normals=True,
                                         use_uvs=True, )

                self.exported = True
                # mesh.location = self.loc
                # mesh.rotation_euler = self.rot
                # mesh.scale = self.scl

            mesh = bpy.data.objects[self.meshname]
            mesh.hide_viewport = False
            options = ['-c', str(self.crease),
                       '-v', str(self.verts),
                       '-S', str(self.smooth),
                       '-o', output]
            if self.deterministic:
                options.append('-d')
            if self.dominant:
                options.append('-D')
            if self.intrinsic:
                options.append('-i')
            if self.boundaries:
                options.append('-b')

            cmd = [exe] + options + [orig]

            print (cmd)

            if self.openUI:
                os.chdir(os.path.dirname(orig))
                shutil.copy2(orig, output)
                subprocess.run([exe, output])
                self.openUI = False
            else:
                subprocess.run(cmd)

            bpy.ops.import_scene.obj(filepath=output,
                                     use_split_objects=False,
                                     use_smooth_groups=False,
                                     use_image_search=False,
                                     axis_forward='-Z', axis_up='Y')
            imported_mesh = bpy.context.selected_objects[0]
            # imported_mesh.location = self.loc
            # imported_mesh.rotation_euler = self.rot
            # imported_mesh.scale = self.scl
            print(mesh, mesh.name)
            imported_mesh.name = mesh.name + '_remesh'
            for i in mesh.data.materials:
                print('setting mat: ' + i.name)
                imported_mesh.data.materials.append(i)
            for edge in imported_mesh.data.edges:
                edge.use_edge_sharp = False
            for other_obj in bpy.data.objects:
                other_obj.select_set(state=False)
            imported_mesh.select_set(state=True)
            imported_mesh.active_material.use_nodes = False
            imported_mesh.data.use_auto_smooth = False

            bpy.ops.object.shade_flat()
            bpy.ops.mesh.customdata_custom_splitnormals_clear()

            mesh.select_set(state=True)
            bpy.context.view_layer.objects.active = mesh
            bpy.ops.object.data_transfer(use_reverse_transfer=False,
                                         use_freeze=False, data_type='UV', use_create=True, vert_mapping='NEAREST',
                                         edge_mapping='NEAREST', loop_mapping='NEAREST_POLYNOR', poly_mapping='NEAREST',
                                         use_auto_transform=False, use_object_transform=True, use_max_distance=False,
                                         max_distance=1.0, ray_radius=0.0, islands_precision=0.1, layers_select_src='ACTIVE',
                                         layers_select_dst='ACTIVE', mix_mode='REPLACE', mix_factor=1.0)
            mesh.select_set(state=False)
            mesh.hide_viewport = True
            imported_mesh.select_set(state=False)
            os.remove(output)
            if self.showwire:
            	bpy.context.space_data.overlay.show_wireframes = True
            else:
            	bpy.context.space_data.overlay.show_wireframes = False

            return {'FINISHED'}
        else:
            return {'FINISHED'}
##############################################


def menu_func(self, context):
    # self.layout.operator(InstantMeshesRemeshBatch.bl_idname)
    self.layout.operator(InstantMeshesRemesh.bl_idname)


classes = (
    InstantMeshesRemeshPrefs,
    InstantMeshesRemesh
    # InstantMeshesRemeshBatch,
)


def register():
    # add operator
    from bpy.utils import register_class
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.VIEW3D_MT_object.append(menu_func)
    try:
        os.remove(os.path.join(tempfile.gettempdir(), 'original.obj'))
        os.remove(os.path.join(tempfile.gettempdir(), 'out.obj'))
    except:
        pass


def unregister():
    from bpy.utils import unregister_class
    bpy.types.VIEW3D_MT_object.remove(menu_func)

    # remove operator and preferences
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
