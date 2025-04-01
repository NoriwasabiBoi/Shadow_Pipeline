import hou
import os
import re
from pxr import Usd, UsdGeom, Sdf, Gf

# Directory where USD assets are stored
usd_base_path = ""

# Output USD file where all assets will be referenced
output_usd_path = "/path/to/Room_Layout_v001.usda"

# Regular expression to match "OUT_asset_TRANS"
pattern = re.compile(r"OUT_(.*)_TRANS")

# Function to find all matching OUT_asset_TRANS nodes in Houdini
def find_transforms():
    transforms = {}

    for node in hou.node("/").allSubChildren():
        match = pattern.match(node.name())
        if node.type().name() == "null" and match:
            asset_name = match.group(1)  # Extract asset name
            transforms[asset_name] = node

    return transforms

# Function to get transform matrix from a Houdini node
def get_transform_matrix(node):
    transform = node.worldTransform()  # Get Houdini world transform
    matrix = Gf.Matrix4d(*transform.asTuple())  # Convert to USD-compatible format
    return matrix

# Function to find the corresponding USD file for an asset
def find_usd_file(asset_name):
    asset_usd_path = f"L:/rauchertofu/rauchertofu/Assets/Prop/{asset_name}/Modeling/proxy/{asset_name}_proxy_Modeling_v001.usda"
    if os.path.exists(asset_usd_path):
        return asset_usd_path
    return None

# Create a new USD stage
stage = Usd.Stage.CreateNew(output_usd_path)

# Define a root Xform for organizing the assets
root_xform = UsdGeom.Xform.Define(stage, "/Room")

# Find all OUT_asset_TRANS nodes
asset_transforms = find_transforms()

for asset_name, node in asset_transforms.items():
    usd_asset_path = find_usd_file(asset_name)

    if usd_asset_path:
        # Create a reference in USD
        asset_prim = UsdGeom.Xform.Define(stage, f"/Room/{asset_name}")
        asset_prim.GetPrim().GetReferences().AddReference(usd_asset_path)

        # Apply the transformation from Houdini
        transform_matrix = get_transform_matrix(node)
        asset_prim.AddTransformOp().Set(transform_matrix)

        print(f"Referenced {asset_name} from {usd_asset_path} with transformation applied.")
    else:
        print(f"WARNING: USD file for {asset_name} not found.")

# Save the final USD file
stage.GetRootLayer().Save()

print(f"Final USD scene saved at: {output_usd_path}")
