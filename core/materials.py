import bpy

standard_texture_channels = {
    # Common PBR material texture types
    "albedo"        : ["albedo", "basecolor", "basecolour", "base", "color", "colour", "diffuse", "diff", "c", "d", "col", "alb", "dif"],
    "normal"        : ["normal", "normalgl", "local", "norm", "nor", "nor_gl", "nor_dx", "n"], # NOTE: "normaldx" removed for now.
    "roughness"     : ["roughness", "rough", "rgh", "r"],
    "metallic"      : ["metallic", "metalness", "met", "m"],
    "ao"            : ["ao", "ambientocclusion", "ambient", "occlusion", "a", "o"],
    "emission"      : ["emission", "emissive", "glow", "luma", "g"],
    "height"        : ["height", "displacement", "disp", "h", "z"],

    # Combined maps
    "orm"           : ["orm", "arm"], 

    # Less common maps
    "rim"           : ["rim"],
    "clearcoat"     : ["clearcoat"],
    "anisotropy"    : ["anisotropy", "aniso", "flowmap", "flow"],
    "subsurface"    : ["subsurface", "subsurf", "scattering", "scatter", "sss"],
    "transmission"  : ["transmittance", "transmission", "transmissive"],
    "backlight"     : ["backlighting", "backlight"],
    "refraction"    : ["refraction", "refract"],
    "detail"        : ["detail"]
}
