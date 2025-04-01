import hou
from pxr import USd, UsdGeom, Vt, Gf

def get_geometry_data(geometry):
    # Get mesh geometry data including normals
    points = []  # List of point positions (point3f[] points)
    normals = []  # List of normals (normal3f[] normals)
    face_vertex_counts = []  # List of vertex count per face (int[] faceVertexCounts)
    face_vertex_indices = []  # List of vertex indices (int[] faceVertexIndices)

    # Collect points and normals
    for point in geometry.points():
        position = point.position()
        points.append(Gf.Vec3f(position[0], position[1], position[2]))

    # Collect face data
    for primitive in geometry.prims():
        vertices = primitive.vertices()
        face_vertex_counts.append(len(vertices))

        for vertex in reversed(vertices):
            face_vertex_indices.append(vertex.point().number())

            # Get Normals data
            if geometry.findVertexAttrib("N") is not None:
                normal = vertex.attribValue("N")
                normals.append(Gf.Vec3f(normal[0], normal[1], normal[2]))

    return points, normals, face_vertex_counts, face_vertex_indices


def export_usd(filepath, option, geometry):
    """
    Creates a USD stage and writes a mesh with vertex positions, topology,
    and face normals (using 'uniform' interpolation).
    """
    # Collect data from the selected mesh in Maya.
    mesh_data = get_geometry_data(geometry=geometry)

    # Create a new USD stage.
    stage = Usd.Stage.CreateNew(filepath)
    # Create a top-level transform prim.
    xformPrim = UsdGeom.Xform.Define(stage, f'/')

    # Create a mesh under a "proxy" layer.
    meshPrim = UsdGeom.Mesh.Define(stage, f'/{option}')

    # Set vertex positions.
    meshPrim.GetPointsAttr().Set(Vt.Vec3fArray(mesh_data[0]))

    # Set topology: face vertex counts and face vertex indices.
    meshPrim.GetFaceVertexCountsAttr().Set(Vt.IntArray(mesh_data[2]))
    meshPrim.GetFaceVertexIndicesAttr().Set(Vt.IntArray(mesh_data[3]))

    # Set face normals.
    # With one normal per face, we use "uniform" interpolation.
    meshPrim.CreateNormalsAttr().Set(Vt.Vec3fArray(mesh_data[1]))
    meshPrim.SetNormalsInterpolation("uniform")

    # Set subdivision scheme (here "none" disables smoothing).
    meshPrim.CreateSubdivisionSchemeAttr().Set("none")

    # set defualt prim
    defaultPrim = meshPrim.GetPrim()
    stage.SetDefaultPrim(defaultPrim)

    # Save the USD file.
    stage.GetRootLayer().Save()
    print("USD file exported: to ", filepath)

def proxy_export():
    node = hou.pwd()
    geometry = node.geometry()
    export_usd(f"L:/rauchertofu/rauchertofu/Assets/Prop", "proxy", geometry)