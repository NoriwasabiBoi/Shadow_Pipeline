import pymel.core as pm
from pxr import Usd, UsdGeom, Vt, Gf

def get_selected_mesh_data_face_normals():
    """
    Collects mesh data from the first selected mesh, including:
      - Vertex positions in world space
      - Topology (face vertex counts and face vertex indices)
      - Face normals (one normal per face, computed in world space)
    Returns a dictionary with keys: 
      'name', 'points', 'face_counts', 'face_indices', 'face_normals'
    """
    selection = pm.selected(type='transform')
    if not selection:
        raise Exception("No objects selected.")
    
    # Use the first selected transform node.
    obj = selection[0]
    # Get the shape node; ensure it is a mesh.
    shape = obj.getShape()
    if not shape or shape.nodeType() != 'mesh':
        raise Exception("Selected object is not a mesh.")
    
    mesh_name = shape.name()
    
    # Get vertex positions in world space.
    pts = shape.getPoints(space='world')
    points_array = [(pt.x, pt.y, pt.z) for pt in pts]
    
    # Get topology: face vertex counts and indices.
    face_counts = []
    face_indices = []
    for face in shape.faces:
        verts = face.getVertices()  # list of vertex indices for this face
        face_counts.append(len(verts))
        face_indices.extend(verts)
    
    # Get face normals (one normal per face) in world space.
    face_normals = []
    for face in shape.faces:
        # getNormal returns an MVector in world space
        normal = face.getNormal(space='world')
        face_normals.append((normal.x, normal.y, normal.z))
    
    return {
        'name': mesh_name,
        'points': points_array,
        'face_counts': face_counts,
        'face_indices': face_indices,
        'face_normals': face_normals
    }

def export_usd_face_normals(filepath):
    """
    Creates a USD stage and writes a mesh with vertex positions, topology,
    and face normals (using 'uniform' interpolation).
    """
    # Collect data from the selected mesh in Maya.
    mesh_data = get_selected_mesh_data_face_normals()
    # Use the last part of the full DAG path as the asset name.
    asset_name = mesh_data['name'].split('|')[-1]
    
    # Create a new USD stage.
    stage = Usd.Stage.CreateNew(filepath)
    # Create a top-level transform prim.
    xformPrim = UsdGeom.Xform.Define(stage, f'/{asset_name}')
    
    # Create a top-level transform prim.
    xformProxy = UsdGeom.Xform.Define(stage, f'/{asset_name}/proxy')
    
    # Create a mesh under a "proxy" layer.
    meshPrim = UsdGeom.Mesh.Define(stage, f'/{asset_name}/proxy/proxy')
    
    # Set vertex positions.
    meshPrim.GetPointsAttr().Set(Vt.Vec3fArray(mesh_data['points']))
    
    # Set topology: face vertex counts and face vertex indices.
    meshPrim.GetFaceVertexCountsAttr().Set(Vt.IntArray(mesh_data['face_counts']))
    meshPrim.GetFaceVertexIndicesAttr().Set(Vt.IntArray(mesh_data['face_indices']))
    
    # Set face normals.
    # With one normal per face, we use "uniform" interpolation.
    meshPrim.CreateNormalsAttr().Set(Vt.Vec3fArray(mesh_data['face_normals']))
    meshPrim.SetNormalsInterpolation("uniform")
    
    # Set subdivision scheme (here "none" disables smoothing).
    meshPrim.CreateSubdivisionSchemeAttr().Set("none")
    
    # Save the USD file.
    stage.GetRootLayer().Save()
    print("USD file exported:", asset_name, " to ", filepath)

# Example usage:
export_usd_face_normals("C:/Users/rlemke/Desktop/mesh_pymel_03.usda")
