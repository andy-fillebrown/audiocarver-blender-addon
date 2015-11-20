
from . import audiocarver_test
from . import import_audiocarver

import bpy
from bpy.props import (FloatProperty,
                       StringProperty
                       )

bl_info = {
    "name": "AudioCarver format",
    "author": "Andrew Fillebrown, Andy",
    "blender": (2, 5, 7),
    "location": "File > Import",
    "description": "Import AudioCarver",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Import"}

if "bpy" in locals():
    import imp
    if "import_audiocarver" in locals():
        imp.reload(import_audiocarver)


from bpy_extras.io_utils import (ImportHelper,
                                 axis_conversion,
                                 path_reference_mode,
                                 )


class ImportAudioCarver(bpy.types.Operator, ImportHelper):
    '''Import an AudioCarver file'''
    bl_idname = "import_scene.audiocarver"
    bl_label = "Import AudioCarver"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt", options={'HIDDEN'})

    def execute(self, context):
        return import_audiocarver.load(self, context, self.filepath)


def menu_func_import(self, context):
    self.layout.operator(ImportAudioCarver.bl_idname,
                         text="Csound Log (.txt)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
