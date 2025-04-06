import bpy
from bpy_extras import view3d_utils


def is_mouse_in_view3d_bounds(mouse_pos: tuple[int, int], view3d_x, view3d_y, view3d_height, view3d_width):
    if ((mouse_pos[0] > view3d_x) and (mouse_pos[0] < view3d_x + view3d_width) and
            (mouse_pos[1] > view3d_y) and (mouse_pos[1] < view3d_y + view3d_height)):
        return True
    return False


def GET_context_view3d_and_region3d(context: bpy.types.Context) -> bpy.types.Area | bpy.types.RegionView3D:
    view3d = None
    region = None
    region_view3d = None
    for area in context.screen.areas:
        if (area.type == "VIEW_3D"):
            view3d = area
            for region in area.regions:
                if (region.type == "WINDOW"):
                    region = region
                    region_view3d = region.data
                    break
            break

    return view3d, region, region_view3d


def mouse_to_3d_point(context: bpy.types.Context, mouse_pos: tuple[int, int]) -> list[float, float, float]:
    """Convert mouse position to 3D point on grid"""

    view3d, region, region_view3d = GET_context_view3d_and_region3d(context)

    if (is_mouse_in_view3d_bounds(mouse_pos, view3d.x, view3d.y, view3d.height, view3d.width)):
        view_vector = view3d_utils.region_2d_to_vector_3d(region, region_view3d, mouse_pos)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_view3d, mouse_pos)

        result, location, normal, index, obj, matrix = context.scene.ray_cast(
            context.view_layer.depsgraph,
            ray_origin,
            view_vector
        )

        if (result is not None):
            return location

        denominator = view_vector.dot((0, 0, 1))
        if abs(denominator) > 1e-6:
            t = ((0, 0, 0) - ray_origin).dot((0, 0, 1)) / denominator
            intersection = ray_origin + t * view_vector
            return intersection

        return (ray_origin.x, ray_origin.y, 0)
    return [0, 0, 0]
