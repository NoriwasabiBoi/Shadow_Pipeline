import bpy

# Get the currently active object in the scene
obj = bpy.context.active_object

# Ensure the object is a mesh (not a curve, camera, etc.)
if obj and obj.type == 'MESH':
    mesh = obj.data

def collect_vertices():
        # --- Vertices ---
        print("Vertices:")
        for v in mesh.vertices:
            # v.co is the vertex coordinate (x, y, z)
            print(f"  Index: {v.index}, Coords: {v.co}")

def collect_edges():
    # --- Edges ---
    print("\nEdges:")
    for e in mesh.edges:
        # e.vertices is a tuple of the two vertex indices in this edge
        print(f"  Index: {e.index}, Vertices: {e.vertices}")

def collect_faces():
    # --- Polygons (Faces) ---
    print("\nPolygons (Faces):")
    for p in mesh.polygons:
        # p.vertices is a tuple of the vertex indices forming this face
        print(f"  Index: {p.index}, Vertices: {p.vertices}")

def collect_uvs():
    # --- UVs (if any) ---
    # If you want to gather UV coordinates, you can do something like:
    if len(mesh.uv_layers) > 0:
        uv_layer = mesh.uv_layers.active.data
        print("\nUV coordinates (first UV layer):")
        for poly in mesh.polygons:
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                print(f"  Loop index: {loop_index}, UV: {uv_layer[loop_index].uv}")
