# B.L.E.S.S
## Blender Level Editor Software Suite


# for bless users:
there will be docs at some point soon. still getting it all set up. 

## v0.1 - collisions
convex collisions will be added for each object in the blender scene. enable the addon and export to gltf as normal. The gltf file will contain the convex shapes and static bodies for each mesh, and the hierarchy should work as expected.

## v0.1.1
there will be working interface to setup collisions based on per-collection or per-object basis, including making meshes other bodies (not static) and using primitive shapes, also includes being able to remove collisions with this setup. this way you can manage the collision system from a top-down level and only things you set will be overrided. 

## v0.1.2
coming soon.

--

# for bless developers:
if you want to work on Bless, you will need to: 
- symlink the reponame/bless directory to blenders addon directory.
- example, Blender 4.2 on Windows: run Command Prompt as admin and then run: `mklink /D "C:\Program Files\Blender Foundation\Blender 4.2\4.2\scripts\addons_core\bless" "C:\repofolder\bless"`
- `bless` should show up as a Built-In addon after restarting Blender

all exporting logic is done in `gltf_export.py`. it will export all meshes and attach shapes and bodies in the gltf file.

![bless](https://github.com/gd-3d/bless/blob/4367949e2e3b77bc53d203e79a29a8738974d94e/bless/assets/logo/logo.png)
