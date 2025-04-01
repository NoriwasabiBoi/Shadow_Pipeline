from pxr import Usd, UsdGeom

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

def reference_layers(stage: Usd.Stage, asset_prim: UsdGeom.Xform):
    # create geolayer
    geo_layer = UsdGeom.Xform.Define(stage, asset_prim.GetPath()+"/geo")
    # create proxy layer and ref proxy file
    proxy_layer = UsdGeom.Xform.Define(stage, geo_layer.GetPath()+"/proxy")
    proxy_ref = stage.OverridePrim(proxy_layer.GetPath())
    proxy_ref.GetReferences().AddReference('./Modeling/proxy/versions/')

    render_layer = UsdGeom.Xform.Define(stage, proxy_layer.GetPath()+"/render")


def reference_file(refStage):
    refSphere = refStage.OverridePrim(type)
    print(refStage.GetRootLayer().ExportToString())
    refSphere.GetReferences().AddReference('./HelloWorld.usda')
    print(refStage.GetRootLayer().ExportToString())
    refStage.GetRootLayer().Save()

def get_newest_fíle(folder):
        scene_path = path
        path, file = os.path.split(scene_path)
        file = file.split('.')
        file_name = file[0].split('_v')
        version = 1
        if len(file_name) > 1:
            version = int(file_name[-1]) + 1
        name = os.path.join(path, '{}_{}.{}'.format(file_name[0], str(version).rjust(4, '0'), file[-1]))
        while os.path.exists(name):
            version += 1
            name = os.path.join(path, '{}_{}.{}'.format(file_name[0], str(version).rjust(3, '0'), file[-1]))
        name = os.path.join(path, '{}_{}.{}'.format(file_name[0], str(version).rjust(3, '0'), file[-1]))
        return name

    path = cmds.file(q=True, sceneName=True)
    cmds.file(rename=incremental_save(path))
    cmds.file(save=True)