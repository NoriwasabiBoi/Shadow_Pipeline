import hou
from pxr import Usd, UsdGeom, Vt, Sdf
import os

def get_geo_data_houdini():
    """
    (unchanged)
    Extracts geometry data from the selected SOP in Houdini.
    Returns a dict with:
      - name: node path
      - points: list of (x,y,z) tuples
      - face_counts, face_indices, uvs, uv_indices, normals
    """
    sel = hou.selectedNodes()
    if not sel:
        raise hou.Error("Please select a SOP node.")
    node = sel[0]
    node.cook(force=True)           # ensure fresh, per‐frame geometry
    geo = node.geometry()
    
    points = [(pt.position()[0], pt.position()[1], pt.position()[2])
              for pt in geo.points()]

    face_counts = []
    face_indices = []
    for prim in geo.prims():
        face_counts.append(prim.numVertices())
        for vtx in prim.vertices():
            face_indices.append(vtx.point().number())

    uv_attrib = geo.findVertexAttrib("uv") or geo.findPointAttrib("uv")
    unique_uvs, uv_index_map, uv_indices = [], {}, []
    for prim in geo.prims():
        for vtx in prim.vertices():
            uv = vtx.attribValue(uv_attrib) if uv_attrib else (0.0, 0.0)
            key = (round(uv[0],6), round(uv[1],6))
            if key not in uv_index_map:
                uv_index_map[key] = len(unique_uvs)
                unique_uvs.append(key)
            uv_indices.append(uv_index_map[key])

    norm_attrib = geo.findPointAttrib("N")
    normals = []
    for prim in geo.prims():
        for vtx in prim.vertices():
            n = vtx.point().attribValue(norm_attrib) if norm_attrib else (0.0,0.0,0.0)
            normals.append((n[0], n[1], n[2]))

    return {
        "name":      node.path(),
        "points":    points,
        "face_counts":  face_counts,
        "face_indices": face_indices,
        "uvs":       unique_uvs,
        "uv_indices":  uv_indices,
        "normals":   normals,
    }

def export_usd(filepath, option):
    """
    Time‐samples the selected SOP over the playbar range and writes out
    a USDA with animated points (and normals), static topology and UVs.
    """
    # Determine frame range
    start_frame, end_frame = hou.playbar.frameRange()
    start, end = int(start_frame), int(end_frame)

    # Sample the first frame to get static topology & primvars
    hou.setFrame(start)
    base = get_geo_data_houdini()

    asset_name = "Nachtnudel"
    export_path = filepath + asset_name + ".usda"
    stage = Usd.Stage.CreateNew(export_path)
    UsdGeom.Xform.Define(stage, "/")
    meshPrim = UsdGeom.Mesh.Define(stage, f'/{asset_name}')

    # Static topology
    meshPrim.GetFaceVertexCountsAttr().Set(Vt.IntArray(base['face_counts']))
    meshPrim.GetFaceVertexIndicesAttr().Set(Vt.IntArray(base['face_indices']))

    # Static UVs
    if base.get('uvs') and base.get('uv_indices'):
        # Create primvars:st
        stAttr = meshPrim.GetPrim().CreateAttribute("primvars:st", Sdf.ValueTypeNames.TexCoord2fArray)
        stAttr.Set(Vt.Vec2fArray(base['uvs']))
        stAttr.SetMetadata("interpolation", "faceVarying")

        # Create primvars:st:indices
        stIndicesAttr = meshPrim.GetPrim().CreateAttribute("primvars:st:indices", Sdf.ValueTypeNames.IntArray)
        stIndicesAttr.Set(Vt.IntArray(base['uv_indices']))

    # Purpose & visibility
    img = UsdGeom.Imageable(meshPrim)
    img.GetPurposeAttr().Set(option)
    img.GetVisibilityAttr().Set(UsdGeom.Tokens.inherited)

    # Time‐sampled points and normals
    pts_attr = meshPrim.GetPointsAttr()
    norm_attr = meshPrim.CreateNormalsAttr()
    #norm_attr.SetInterpolation(UsdGeom.Tokens.faceVarying)

    for f in range(start, end+1):
        hou.setFrame(f)
        data = get_geo_data_houdini()
        # sanity check
        if len(data['points']) != len(base['points']):
            raise ValueError(f"Point count mismatch at frame {f}")
        pts_attr.Set(Vt.Vec3fArray(data['points']), time=f)
        #norm_attr.Set(Vt.Vec3fArray(data['normals']), time=f)
        print(f"Exported: {f}")

    # finalize
    stage.SetDefaultPrim(meshPrim.GetPrim())
    stage.GetRootLayer().Export(export_path)
    print("USD animated export saved to:", export_path)


# Usage remains exactly the same:
file = "PATH"
option = "render"
export_usd(file, option)
