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

import bpy
from . import Instant_Meshes_Remesh


modules = Instant_Meshes_Remesh


def register():
    from bpy.utils import register_class
    modules.register()


def unregister():
    from bpy.utils import unregister_class
    modules.unregister()


if __name__ == "__main__":
    register()