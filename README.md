# Blender Level Editor Software Suite
## B.l.e.s.s

Bless is a level editor addon for blender, made primarily for Godot, but has hopes in the future to support more engines (please get in touch!)

Using this addon you will be able to design full 3D levels that are game-ready, including addng scripts and scenes from your
game engine to your `.blend` level file.

All exports are handled with `.gltf` and some reasearch has done into nested glTF files - so that will likely be supported in the near future for instancing scenes.

Bless is under heavy construction. Check for the 0.2 milestone, that is when Bless will be "production ready".

--

# for bless developers:
if you want to work on Bless, you will need to: 
- symlink the reponame/bless directory to blenders addon directory.
- example, Blender 4.2 on Windows: run Command Prompt as admin and then run: `mklink /D "C:\Program Files\Blender Foundation\Blender 4.2\4.2\scripts\addons_core\bless" "C:\repofolder\bless"`
- `bless` should show up as a Built-In addon after restarting Blender

all exporting logic is done in `gltf_export.py`. it will export all meshes and attach shapes and bodies in the gltf file.

![bless](https://github.com/gd-3d/bless/blob/4367949e2e3b77bc53d203e79a29a8738974d94e/bless/assets/logo/logo.png)


### Thank you
A big thank you to these contributers: 
- Valy Arlhal -- for the blender expertise, autoregistration scripts and the release pipeline and all the extra help with bpy
- michael jared -- the OG blender-godot-pipeline toolsmith, figured out the extension hooking and just a general chad
- Aaron Franke, OMI group -- maintainer of godot gltf, as well as writing glTF extensions used in Bless
- dogman35 -- the 3D bless logo asset and 
- unfa -- for adopting bless into Liblast, the first game to officially do so! the blueprint! 
