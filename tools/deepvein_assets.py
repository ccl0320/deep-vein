"""
Deep Vein 深坑淘金 — Blender asset generator
Generates original low-poly assets and exports them to one GLB.

Run (headless):
    blender -b -P deepvein_assets.py -- out.glb
or with the pip `bpy` module:
    python deepvein_assets.py out.glb

Objects exported (by name, loaded by the Three.js game):
    Miner, MinerHelmetLamp, Cart, Pickaxe, Lantern, Gold, Coal, Rock
"""
import sys, math, random
import bpy, bmesh
from mathutils import Vector

random.seed(7)
argv = sys.argv
out = argv[argv.index("--") + 1] if "--" in argv else (argv[1] if len(argv) > 1 and argv[1].endswith(".glb") else "deepvein_assets.glb")

# ---------- scene reset ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

_mats = {}
def mat(name, rgb, rough=0.7, metal=0.0, emit=None, emit_strength=0.0):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    _mats[name] = m
    return m

def assign(obj, m):
    obj.data.materials.clear()
    obj.data.materials.append(m)

def shade_flat(obj):
    for p in obj.data.polygons:
        p.use_smooth = False

def apply_all(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)

def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = name
    o.data.name = name
    return o

def cube(size, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    apply_all(o); assign(o, m); return o

def cyl(r, depth, loc, m, rot=(0, 0, 0), verts=12, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object; apply_all(o); assign(o, m); return o

def sphere(r, loc, m, scale=(1, 1, 1), subdiv=2):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, location=loc, subdivisions=subdiv)
    o = bpy.context.object; o.scale = scale; apply_all(o); assign(o, m); return o

def jitter(obj, amt):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    for v in bm.verts:
        v.co += Vector((random.uniform(-amt, amt), random.uniform(-amt, amt), random.uniform(-amt, amt)))
    bm.to_mesh(obj.data); bm.free()

# ---------- materials ----------
M = dict(
    skin=mat("Skin", (0.86, 0.62, 0.48)),
    beard=mat("Beard", (0.55, 0.30, 0.15), 0.9),
    tunic=mat("Tunic", (0.80, 0.80, 0.80), 0.8),          # tinted per player in Three.js
    belt=mat("Belt", (0.25, 0.15, 0.08)),
    boots=mat("Boots", (0.18, 0.12, 0.08)),
    helmet=mat("Helmet", (0.95, 0.72, 0.18), 0.35, 0.3),
    lamp=mat("LampGlow", (1.0, 0.95, 0.7), 0.2, 0, (1.0, 0.85, 0.5), 4.0),
    wood=mat("Wood", (0.45, 0.28, 0.14), 0.85),
    iron=mat("Iron", (0.35, 0.36, 0.38), 0.45, 0.8),
    gold=mat("Gold", (1.0, 0.76, 0.2), 0.25, 1.0, (0.6, 0.4, 0.05), 0.6),
    coal=mat("Coal", (0.06, 0.06, 0.07), 0.6, 0.2),
    rock=mat("Rock", (0.42, 0.36, 0.30), 0.95),
    eye=mat("Eye", (0.05, 0.05, 0.05), 0.3),
)

# ---------- Miner (original stylized character, ~1.0 unit tall) ----------
def build_miner():
    parts = []
    parts.append(cyl(0.11, 0.12, (-0.1, 0, 0.06), M["boots"]))
    parts.append(cyl(0.11, 0.12, (0.1, 0, 0.06), M["boots"]))
    parts.append(cyl(0.22, 0.42, (0, 0, 0.33), M["tunic"], r2=0.17, verts=10))
    parts.append(cyl(0.225, 0.06, (0, 0, 0.30), M["belt"], verts=10))
    parts.append(cube((0.07, 0.03, 0.06), (0, -0.22, 0.30), M["helmet"]))      # buckle
    parts.append(sphere(0.17, (0, 0, 0.68), M["skin"], subdiv=2))
    parts.append(sphere(0.045, (0, -0.17, 0.66), M["skin"], subdiv=1))         # nose
    parts.append(sphere(0.022, (-0.065, -0.15, 0.72), M["eye"], subdiv=1))
    parts.append(sphere(0.022, (0.065, -0.15, 0.72), M["eye"], subdiv=1))
    beard = cyl(0.15, 0.28, (0, -0.07, 0.52), M["beard"], rot=(math.radians(12), 0, 0), verts=8, r2=0.02)
    beard.rotation_euler = (math.pi + math.radians(15), 0, 0); apply_all(beard); jitter(beard, 0.01)
    parts.append(beard)
    helm = sphere(0.19, (0, 0, 0.74), M["helmet"], scale=(1, 1, 0.75), subdiv=2)
    parts.append(helm)
    parts.append(cyl(0.23, 0.025, (0, 0, 0.75), M["helmet"], verts=14))         # brim
    parts.append(cyl(0.03, 0.06, (0, -0.06, 0.32), M["belt"]))
    # arms
    parts.append(cyl(0.055, 0.30, (-0.24, 0, 0.42), M["tunic"], rot=(0, math.radians(-20), 0), verts=8))
    parts.append(cyl(0.055, 0.30, (0.24, 0, 0.42), M["tunic"], rot=(0, math.radians(20), 0), verts=8))
    parts.append(sphere(0.06, (-0.29, 0, 0.28), M["skin"], subdiv=1))
    parts.append(sphere(0.06, (0.29, 0, 0.28), M["skin"], subdiv=1))
    miner = join(parts, "Miner")
    shade_flat(miner)
    lamp = cyl(0.05, 0.05, (0, -0.17, 0.82), M["lamp"], rot=(math.radians(80), 0, 0), verts=10)
    lamp.name = "MinerHelmetLamp"; lamp.data.name = "MinerHelmetLamp"
    return miner, lamp

# ---------- Mine cart ----------
def build_cart():
    p = []
    p.append(cyl(0.34, 0.28, (0, 0, 0.30), M["wood"], verts=4, r2=0.27))
    tub = p[-1]; tub.rotation_euler = (0, 0, math.radians(45)); apply_all(tub)
    tub.scale = (1.25, 0.9, 1); apply_all(tub)
    for x in (-0.25, 0.25):
        for y in (-0.22, 0.22):
            p.append(cyl(0.09, 0.04, (x, y, 0.1), M["iron"], rot=(math.radians(90), 0, 0), verts=12))
    p.append(cube((0.62, 0.02, 0.03), (0, -0.26, 0.42), M["iron"]))
    p.append(cube((0.62, 0.02, 0.03), (0, 0.26, 0.42), M["iron"]))
    for i in range(5):
        n = sphere(0.07, (random.uniform(-0.15, 0.15), random.uniform(-0.1, 0.1), 0.44), M["gold"], subdiv=1)
        jitter(n, 0.015); p.append(n)
    c = join(p, "Cart"); shade_flat(c); return c

def build_pickaxe():
    p = [cyl(0.025, 0.6, (0, 0, 0.3), M["wood"], verts=8)]
    head = cyl(0.04, 0.42, (0, 0, 0.58), M["iron"], rot=(0, math.radians(90), 0), verts=6, r2=0.01)
    p.append(head)
    p.append(cyl(0.04, 0.2, (-0.1, 0, 0.58), M["iron"], rot=(0, math.radians(-90), 0), verts=6, r2=0.01))
    o = join(p, "Pickaxe"); shade_flat(o); return o

def build_lantern():
    p = [cyl(0.1, 0.03, (0, 0, 0.015), M["iron"], verts=8),
         cyl(0.07, 0.18, (0, 0, 0.12), M["lamp"], verts=8),
         cyl(0.1, 0.06, (0, 0, 0.24), M["iron"], verts=8, r2=0.03)]
    for a in range(4):
        ang = a * math.pi / 2
        p.append(cube((0.015, 0.015, 0.2), (math.cos(ang) * 0.08, math.sin(ang) * 0.08, 0.12), M["iron"]))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.05, minor_radius=0.01, location=(0, 0, 0.3), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object; assign(t, M["iron"]); p.append(t)
    o = join(p, "Lantern"); shade_flat(o); return o

def lump(name, m, r, amt):
    o = sphere(r, (0, 0, r * 0.8), m, subdiv=2); jitter(o, amt)
    o.name = name; o.data.name = name; shade_flat(o); return o

miner, lamp = build_miner()
cart = build_cart()
pick = build_pickaxe()
lant = build_lantern()
gold = lump("Gold", M["gold"], 0.22, 0.05)
coal = lump("Coal", M["coal"], 0.22, 0.06)
rock = lump("Rock", M["rock"], 0.25, 0.07)

# put every origin at world origin (feet / base), so the game can place them directly
scene.cursor.location = (0, 0, 0)
for o in [miner, lamp, cart, pick, lant, gold, coal, rock]:
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

# spread out for preview in Blender
for i, o in enumerate([miner, lamp, cart, pick, lant, gold, coal, rock]):
    if o is lamp:
        continue
    o.location.x = i * 1.2
lamp.location.x = miner.location.x

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True,
                          export_apply=True, export_yup=True)
print("Exported", out)
