from pxr import Usd, UsdShade, UsdGeom, Sdf

# File paths
asset_usd_path = "myAsset.usd"        # The asset (geometry) file
material_usd_path = "myMaterial.usd"  # The material file
mesh_prim_path = "/World/Geom/MyMesh" # Path to the mesh on the asset stage
material_prim_path = "/World/Materials/MyMaterial"  # Path of the material in the material file

# 1) Open or create the stage for the asset
stage = Usd.Stage.Open(asset_usd_path)
if not stage:
    stage = Usd.Stage.CreateNew(asset_usd_path)

# 2) Sublayer or reference the material file
root_layer = stage.GetRootLayer()
if material_usd_path not in root_layer.subLayerPaths:
    root_layer.subLayerPaths.append(material_usd_path)

# Alternatively, you could reference just the material prim:
# material_prim = stage.DefinePrim(material_prim_path)
# material_prim.GetReferences().AddReference(
#     assetPath=material_usd_path,
#     primPath=material_prim_path
# )

# 3) Bind the material to the mesh
mesh_prim = stage.GetPrimAtPath(mesh_prim_path)
if not mesh_prim.IsValid():
    print(f"Warning: Mesh prim {mesh_prim_path} not found. Creating a dummy mesh for demo.")
    UsdGeom.Mesh.Define(stage, mesh_prim_path)
    mesh_prim = stage.GetPrimAtPath(mesh_prim_path)

binding_api = UsdShade.MaterialBindingAPI(mesh_prim)

material_prim = stage.GetPrimAtPath(material_prim_path)
material = UsdShade.Material(material_prim)
if not material_prim.IsValid():
    print(f"Warning: Material prim {material_prim_path} not found. Make sure it exists in {material_usd_path}.")

binding_api.Bind(material)

# 4) Save the result
stage.GetRootLayer().Save()
print(f"Material bound successfully and saved to {asset_usd_path}")
