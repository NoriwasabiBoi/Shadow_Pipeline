import bpy

ex_path='PATH/TO/EXPORT/test.usd'
ex_anim = False
ex_subdiv = 'IGNORE'


bpy.ops.wm.usd_export(
    filepath=ex_path,
    selected_objects_only=True,
    visible_objects_only=True,
    export_animation=ex_anim,
    export_uvmaps=True,
    #export_subdivision='BEST_MATCH'
)
