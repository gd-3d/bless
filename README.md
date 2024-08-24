# Bless
## Blender Level Editor Software Suite


# for bless users:

not working yet! come back later.

# for bless developers:
if you want to work on Bless, you will need to: 
- symlink the reponame/bless directory to blenders addon directory.
- example, Blender 4.2 on Windows: run Command Prompt as admin and then run: `mklink /D "C:\Program Files\Blender Foundation\Blender 4.2\4.2\scripts\addons_core\bless" "C:\repofolder\bless"`
- `bless` should show up as a Built-In addon after restarting Blender

all exporting logic is done in `gltf_export.py`. it will export all meshes and attach shapes and bodies in the gltf file.

some issues:
- textured materials seem to break the export, keep the export simple for now (just meshes)
- for exporting, make sure full heirarchy in the gltf exporter is not selected (will be fixing this at some point)
- convex shapes are generated incorrectly sometimes.

![bless](https://github.com/gd-3d/bless/blob/4367949e2e3b77bc53d203e79a29a8738974d94e/bless/assets/logo/logo.png)
