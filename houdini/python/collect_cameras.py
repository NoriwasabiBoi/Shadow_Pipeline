import hou
from pxr import Usd, UsdGeom

# Set your export directory path here
export_dir = "%EXPORT_PATH"

# Get all cameras
root = hou.node('/')
camera_nodes = root.recursiveGlob('SHOT_\d\d\d_\d\d\d', hou.nodeTypeFilter.ObjCamera)

for cam in camera_nodes:
    # Build a filename based on the camera's name
    usd_filename = "{}{}.usd".format(export_dir, cam.name())
    
    # Create a new USD stage
    stage = Usd.Stage.CreateNew(usd_filename)
    
    # Create a USD camera prim at the default path '/Camera'
    usd_cam = UsdGeom.Camera.Define(stage, '/Camera')
    
    # Example: Set the focal length from Houdini’s camera parameter (if available)
    if cam.parm("focal"):
        focal_length = cam.parm("focal").eval()
        usd_cam.GetFocalLengthAttr().Set(focal_length)
    
    # Optionally, set other camera attributes like aperture, clipping ranges, etc.
    if cam.parm("aperture"):
        aperture = cam.parm("aperture").eval()
        usd_cam.GetHorizontalApertureAttr().Set(aperture)
    
    # Save the USD stage to write the file to disk
    stage.GetRootLayer().Save()
    print("Exported USD for camera:", cam.name(), "to", usd_filename)
