from pxr import Usd, UsdGeom, Vt, Gf

def setup_stage(filepath, asset_name):
    '''

    This function

    :param filepath:
    :param asset_name:
    :return: stage and asset_prim
    '''
    unit = 1
    stage = Usd.Stage.CreateNew(filepath)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    UsdGeom.SetStageMetersPerUnit(stage, unit)
    asset_prim = UsdGeom.Xform.Define(stage, f'/{asset_name}')
    stage.SetDefaultPrim({asset_prim})
    return stage, asset_prim

def open_stage(filepath: str):
    stage = Usd.Stage.Open(filepath)

def setup_hierarchy(stage: Usd.Stage,asset_name: str, type: str):
    '''

    :param stage:
    :param asset_name:
    :return:
    '''
    geo = UsdGeom.Xform.Define(stage, f'/{asset_name}+/geo/')
    xform = UsdGeom.Xform.Define(stage, str(geo.GetPath()) + f'/{type}')
    mesh = UsdGeom.Mesh.Define(stage, str(xform.GetPath()) + f'/{type}')
    return mesh

def set_mesh_attr(mesh_data: dict[], mesh: UsdGeom):
    mesh.GetPointsAttr().Set(Vt.Vec3fArray(mesh_data['points']))
    mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray(mesh_data['face_counts']))
    mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray(mesh_data['face_indices']))
    mesh.CreateNormalsAttr().Set(Vt.Vec3fArray(mesh_data['face_normals']))
    mesh.SetNormalsInterpolation("uniform")
    mesh.CreateSubdivisionSchemeAttr().Set("none")

def write_usd(stage: Usd.Stage, asset_name: str, filepath: str):
    setup_stage(filepath=filepath, asset_name=asset_name)
    stage.GetRootLayer().Save()
