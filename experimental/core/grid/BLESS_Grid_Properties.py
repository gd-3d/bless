# import bpy

# from .BLESS_Grid_Utils import update_grid_scale


# class BLESS_GridData(bpy.types.PropertyGroup):

#     unit_size = bpy.props.FloatProperty(
#         name="Unit Size",
#         description="Size of the grid units in meters",
#         default=1.0,
#         min=0.0625,
#         max=1024.0,
#         step=0.25,
#         precision=2,
#         subtype="DISTANCE",
#         update=lambda self, context: update_grid_scale(context, self.unit_size))
