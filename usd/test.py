import bpy
from pxr import Usd, UsdGeom, Vt, Gf


def write_usd_file(filepath, asset_name):
    unit = 1
    stage = Usd.Stage.CreateNew(filepath)
    stage.SetDefaultPrim({asset_name})
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    UsdGeom.SetStageMetersPerUnit(stage, unit)
    xformPrim = UsdGeom.Xform.Define(stage, f'/{asset_name}')
    return stage, xformPrim


def create_proxy_layer(stage, asset_name):
    proxy = UsdGeom.Xform.Define(stage, f'/{asset_name}/geo/proxy')
    proxy_geo = UsdGeom.Mesh.Define(stage, str(proxy.GetPath())+"/proxy")
    get_geometry_data(proxy_geo)
    return proxy.GetPath()


def create_render_layer(stage, asset_name):
    render = UsdGeom.Xform.Define(stage, f'/{asset_name}/geo/render')
    return render.GetPath()

def reference_file():
    refStage = Usd.Stage.CreateNew('RefExample.usda')
    refSphere = refStage.OverridePrim('/refSphere')
    print(refStage.GetRootLayer().ExportToString())
    refSphere.GetReferences().AddReference('./HelloWorld.usda')
    print(refStage.GetRootLayer().ExportToString())
    refStage.GetRootLayer().Save()

def get_normals(obj):
    """ Get face normals and convert them to tuples. """
    normals = [(poly.normal.x, poly.normal.y, poly.normal.z) for poly in obj.data.polygons]
    return normals

def get_geometry_data(usdgeom):
    # Get the active mesh object
    obj = bpy.context.object
    if obj is None or obj.type != 'MESH':
        raise ValueError("Select a mesh object")

    mesh = obj.data
    mesh.calc_loop_triangles()  # Ensure triangulation data is updated

    # Get vertex positions
    points = [vert.co for vert in mesh.vertices]
    points_array = [(v.x, v.y, v.z) for v in points]

    # Get face vertex counts
    face_vertex_counts = [len(p.vertices) for p in mesh.polygons]

    # Get face vertex indices
    face_vertex_indices = [vert_idx for poly in mesh.polygons for vert_idx in poly.vertices]

    normals_array = get_normals(obj)

    # Set USD attributes using Vt arrays
    usdgeom.GetPointsAttr().Set(Vt.Vec3fArray(points_array))
    usdgeom.GetFaceVertexCountsAttr().Set(Vt.IntArray(face_vertex_counts))
    usdgeom.GetFaceVertexIndicesAttr().Set(Vt.IntArray(face_vertex_indices))

    # Set normals (face-varying) and specify the interpolation
    usdgeom.GetNormalsAttr().Set(Vt.Vec3fArray(normals_array))
    usdgeom.SetNormalsInterpolation("uniform")  # Change to "vertex" if needed

    # Set subdivision scheme (set to "none" to disable smoothing, or "catmullClark" if desired)
    usdgeom.CreateSubdivisionSchemeAttr().Set("none")


stage = write_usd_file("/Users/robin/Desktop/test_09.usda", "capybara")
create_proxy_layer(stage, "capybara")
create_render_layer(stage, "capybara")
stage.GetRootLayer().Save()
