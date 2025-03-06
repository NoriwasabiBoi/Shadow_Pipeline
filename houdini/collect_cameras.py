root = hou.node('/')
camera_nodes = root.recursiveGlob('SHOT_\d\d\d_\d\d\d', hou.nodeTypeFilter.ObjCamera) # replace * with camera naming pattern
