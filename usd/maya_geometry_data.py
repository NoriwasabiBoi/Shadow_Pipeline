import maya.OpenMaya as om

def get_selected_vertices_world_space():
    selection_list = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selection_list)
    
    if selection_list.length() == 0:
        print("No objects selected.")
        return
    
    iter_sel = om.MItSelectionList(selection_list, om.MFn.kMesh)
    
    while not iter_sel.isDone():
        dag_path = om.MDagPath()
        component = om.MObject()
        iter_sel.getDagPath(dag_path, component)

        dag_path.extendToShape()  # Ensure we get the shape node
        mesh_fn = om.MFnMesh(dag_path)
        
        # If components (vertices) are selected
        if not component.isNull():
            iter_vert = om.MItMeshVertex(dag_path, component)
        else:
            iter_vert = om.MItMeshVertex(dag_path)

        print(f"Object: {dag_path.fullPathName()}")
        
        while not iter_vert.isDone():
            pos = iter_vert.position(om.MSpace.kWorld)  # Get world-space position
            print(f"Vertex {iter_vert.index()}: ({pos.x}, {pos.y}, {pos.z})")
            iter_vert.next()
        
        iter_sel.next()

get_selected_vertices_world_space()


# generated code fix later
