import os
import hou
from PySide2 import QtWidgets
from pxr import Usd, UsdGeom, Vt, Gf


class AssetDialog(QtWidgets.QDialog):
    def __init__(self, asset_folder, parent=None):
        super(AssetDialog, self).__init__(parent)
        self.setWindowTitle("Select Asset")
        self.asset_folder = asset_folder
        self.selected_asset = None

        # Set up layout and widgets
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("Choose an asset from the dropdown:")
        layout.addWidget(label)

        # Create and populate the combo box with folder names
        self.combo = QtWidgets.QComboBox(self)
        # List only directories (assets) from the given folder
        asset_names = [name for name in os.listdir(asset_folder)
                       if os.path.isdir(os.path.join(asset_folder, name))]
        self.combo.addItems(asset_names)
        layout.addWidget(self.combo)

        # Create OK and Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def getSelectedAsset(self):
        return self.combo.currentText()


def show_asset_dialog(asset_folder):
    # Use Houdini's main Qt window as the parent if available
    parent = hou.ui.mainQtWindow() if hou.ui.mainQtWindow() else None
    dialog = AssetDialog(asset_folder, parent)

    # Execute the dialog and check if OK was pressed
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        asset_name = dialog.getSelectedAsset()
        print("Selected asset:", asset_name)
        # Call your asset processing function
        process_asset(asset_name)
        return asset_name
    else:
        print("Dialog canceled.")


def process_asset(asset_name):
    # Replace this function with your actual processing code.
    print("Processing asset:", asset_name)
    # For example, you might pass the asset name to your export functions or other pipeline logic.


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


def proxy_export(asset, node):
    geometry = node.geometry()
    export_usd("L:/rauchertofu/rauchertofu/Assets/Prop/" + asset + "/Modeling/proxy/" + asset + "_proxy_Modeling_v001.usda",
               "proxy", geometry)


import hou
import re

# Regular expression pattern to match "OUT_{asset}_REST"
pattern = re.compile(r"OUT_.*_REST")


# Function to find matching NULL nodes in the entire Houdini scene
def find_matching_nulls():
    matching_nodes = []

    # Loop through all nodes in the scene
    for node in hou.node("/").allSubChildren():
        # Check if the node is a NULL and matches the pattern
        if node.type().name() == "null" and pattern.match(node.name()):
            matching_nodes.append(node)

    return matching_nodes


# Get the list of matching NULL nodes
matching_nulls = find_matching_nulls()
# Example usage: set the folder path where asset folders are stored.
asset_folder_path = f"L:/rauchertofu/rauchertofu/Assets/Prop"  # Update with your actual asset folder path.
# Print results
if matching_nulls:
    print("Found matching NULL nodes:")
    for null_node in matching_nulls:
        print(null_node.path())  # Print full node path
        asset = null_node.name().split("_")[1]
        proxy_export(asset, null_node)


