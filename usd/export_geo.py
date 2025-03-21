from pxr import Usd, UsdGeom

def write_usd_file(filepath, asset_name):
    """

    :param filepath:
    :return:
    """
    stage = Usd.Stage.CreateNew(filepath)
    xformPrim = UsdGeom.Xform.Define(stage, f'/{asset_name}')
    return stage

def create_proxy_layer(stage, asset_name):
    """
    :return:
    """
    proxy = UsdGeom.Xform.Define(stage, f'/{asset_name}/proxy')
    #proxy_mesh = UsdGeom.Mesh.
    return proxy.GetPath()

def create_render_layer(stage, asset_name):
    """

    :return:
    """
    render = UsdGeom.Xform.Define(stage, f'/{asset_name}/render')
    return render.GetPath()

stage = write_usd_file("L:/rauchertofu/01_assets/pipeline/test.usda", "capybara")
create_proxy_layer(stage=stage, asset_name="capybara")
create_render_layer(stage=stage, asset_name="capybara")
stage.GetRootLayer().Save()