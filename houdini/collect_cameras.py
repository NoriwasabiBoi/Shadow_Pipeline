# recursive globs all camis in scene
def collect_render_camis():
  root = hou.node('/')
  camera_nodes = root.recursiveGlob('SHOT_\d\d\d_\d\d\d', hou.nodeTypeFilter.ObjCamera) # make regex nicer
