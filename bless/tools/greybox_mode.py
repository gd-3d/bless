import bpy
import gpu
import blf
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils
from mathutils import Vector
import bmesh
from bpy.props import BoolProperty, EnumProperty

def get_cuboid_vertices(start, end):
    """Generate vertices for a cuboid given start and end points"""
    x1, y1, z1 = start
    x2, y2, z2 = end
    
    vertices = []
    # Bottom face
    vertices.extend([(x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1)])
    # Top face
    vertices.extend([(x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2)])
    return vertices

def get_cuboid_edges():
    """Get edge indices for cuboid wireframe"""
    return [(0,1), (1,2), (2,3), (3,0),  # bottom face
            (4,5), (5,6), (6,7), (7,4),  # top face
            (0,4), (1,5), (2,6), (3,7)]  # vertical edges

def draw_wireframe(context, vertices, color=(0.0, 1.0, 0.0, 0.8)):
    """Draw wireframe preview of cuboid"""
    # Convert vertices to screen space
    screen_verts = []
    for v in vertices:
        screen_co = view3d_utils.location_3d_to_region_2d(
            context.region, 
            context.space_data.region_3d,
            Vector(v)
        )
        if screen_co:
            screen_verts.append(screen_co)
    
    if len(screen_verts) == 8:  # Only draw if all vertices are visible
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(2.0)
        
        for i1, i2 in get_cuboid_edges():
            batch = batch_for_shader(shader, 'LINES', {
                "pos": [screen_verts[i1], screen_verts[i2]]
            })
            shader.uniform_float("color", color)
            batch.draw(shader)

def draw_dimensions(context, start, end):
    """Draw dimension text overlay"""
    font_id = 0
    dims = [abs(end[i] - start[i]) for i in range(3)]
    blf.position(font_id, 15, 30, 0)
    blf.size(font_id, 20.0)
    blf.draw(font_id, f"Size: {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f}")

def intersect_line_plane(ray_origin, ray_target, plane_point, plane_normal):
    """Find intersection point of a line and a plane"""
    ray_direction = ray_target - ray_origin
    denominator = plane_normal.dot(ray_direction)
    if denominator > 0:
        t = (plane_point - ray_origin).dot(plane_normal) / denominator
        return ray_origin + t * ray_direction
    return None

def mouse_to_3d_point(context, mouse_pos):
    """Convert mouse position to 3D point on grid"""
    region = context.region
    region_3d = context.space_data.region_3d
    
    # Get the ray from the viewport to the mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, region_3d, mouse_pos)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, mouse_pos)
    
    # Try to find surface intersection first
    result, location, normal, index, obj, matrix = context.scene.ray_cast(
        context.view_layer.depsgraph,
        ray_origin,
        view_vector
    )
    
    if result:
        # Found a surface point, return it
        return location
    
    # If no surface hit, intersect with XY plane at nearest grid height
    grid_size = context.scene.unit_settings.scale_length
    
    # Use XY plane at Z=0 as default drawing plane
    plane_normal = Vector((0, 0, 1))
    plane_point = Vector((0, 0, 0))
    
    # Calculate intersection with plane
    denominator = view_vector.dot(plane_normal)
    if abs(denominator) > 1e-6:  # Check if not parallel
        t = (plane_point - ray_origin).dot(plane_normal) / denominator
        intersection = ray_origin + t * view_vector
        return intersection
        
    # Fallback if view is parallel to XY plane
    return Vector((ray_origin.x, ray_origin.y, 0))

def snap_to_grid(point, grid_size):
    """Snap a point to the nearest grid point"""
    # Round each component to nearest grid unit
    x = round(point.x / grid_size) * grid_size
    y = round(point.y / grid_size) * grid_size
    z = round(point.z / grid_size) * grid_size
    return Vector((x, y, z))

def create_cuboid_mesh(start, end, name="Cuboid"):
    """Create a cuboid mesh between two points"""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    
    # Link object to scene
    bpy.context.scene.collection.objects.link(obj)
    
    # Create mesh data
    bm = bmesh.new()
    
    # Create vertices
    x1, y1, z1 = start
    x2, y2, z2 = end
    
    v1 = bm.verts.new((x1, y1, z1))
    v2 = bm.verts.new((x2, y1, z1))
    v3 = bm.verts.new((x2, y2, z1))
    v4 = bm.verts.new((x1, y2, z1))
    v5 = bm.verts.new((x1, y1, z2))
    v6 = bm.verts.new((x2, y1, z2))
    v7 = bm.verts.new((x2, y2, z2))
    v8 = bm.verts.new((x1, y2, z2))
    
    # Create faces
    bm.faces.new((v1, v2, v3, v4))  # bottom
    bm.faces.new((v5, v6, v7, v8))  # top
    bm.faces.new((v1, v2, v6, v5))  # front
    bm.faces.new((v2, v3, v7, v6))  # right
    bm.faces.new((v3, v4, v8, v7))  # back
    bm.faces.new((v4, v1, v5, v8))  # left
    
    # Update mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Select the new object and make it active
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Set origin to center of mass
    bpy.ops.object.autoorigin()
    
    return obj

def draw_callback_px(self, context):
    """Main drawing callback"""
    if len(self.points) >= 1 and self.is_drawing:
        start = self.points[0]
        end = self.current_point
        
        # Create preview vertices
        vertices = get_cuboid_vertices(start, end)
        draw_wireframe(context, vertices)
        draw_dimensions(context, start, end)
        
        # restore opengl defaults
        gpu.state.line_width_set(1.0)
        gpu.state.blend_set('NONE')

def draw_face_highlight(context, vertices, color=(0.2, 0.6, 1.0, 0.3)):
    """Draw highlighted face overlay"""
    if len(vertices) < 3:
        return
        
    print(f"Drawing face with {len(vertices)} vertices")
        
    # Convert vertices to screen space
    screen_verts = []
    for v in vertices:
        screen_co = view3d_utils.location_3d_to_region_2d(
            context.region, 
            context.space_data.region_3d,
            v
        )
        if screen_co:
            screen_verts.append(screen_co)
            print(f"Screen vert: {screen_co}")
    
    if len(screen_verts) >= 3:
        print("Drawing face highlight")
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        
        # Draw face fill
        batch = batch_for_shader(shader, 'TRIS', {
            "pos": screen_verts[:3]  # Just use first 3 verts for triangle
        })
        shader.uniform_float("color", color)
        batch.draw(shader)
        
        # Draw face outline
        gpu.state.line_width_set(2.0)
        outline_verts = screen_verts + [screen_verts[0]]  # Close the loop
        batch = batch_for_shader(shader, 'LINE_STRIP', {
            "pos": outline_verts
        })
        shader.uniform_float("color", (color[0], color[1], color[2], 0.8))
        batch.draw(shader)
        
        # Restore defaults
        gpu.state.line_width_set(1.0)
        gpu.state.blend_set('NONE')

def get_face_under_mouse(context, mouse_pos):
    """Get face and its vertices under mouse cursor"""
    if not context.active_object or context.active_object.type != 'MESH':
        return None, []
    
    print(f"Mouse pos: {mouse_pos}")
    
    # Get the ray from the viewport to the mouse
    region = context.region
    region_3d = context.space_data.region_3d
    view_vector = view3d_utils.region_2d_to_vector_3d(region, region_3d, mouse_pos)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, mouse_pos)
    
    print(f"Ray origin: {ray_origin}, vector: {view_vector}")
    
    # Ray cast in world space
    result, location, normal, index, obj, matrix = context.scene.ray_cast(
        context.view_layer.depsgraph,
        ray_origin,
        view_vector
    )
    
    print(f"Ray hit: {result}, obj: {obj}, index: {index}")
    
    hit_face = None
    hit_vertices = []
    
    if result and obj == context.active_object:
        print("Hit active object")
        # Get mesh data
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        
        # Get face from hit index
        hit_face = bm.faces[index]
        # Get world space vertices
        hit_vertices = [matrix @ v.co for v in hit_face.verts]
        print(f"Found face with {len(hit_vertices)} vertices")
        
        bm.free()
    
    return hit_face, hit_vertices

class GreyboxDraw(bpy.types.Operator):
    """Draw a cuboid: Click and drag for base rectangle, hold Alt and move mouse up/down for height"""
    bl_idname = "bless.greybox_draw"
    bl_label = "Draw Greybox Cuboid"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        context.area.tag_redraw()
        
        # Track Alt key state
        if event.type in {'LEFT_ALT', 'RIGHT_ALT'}:
            if event.value == 'PRESS':
                self.is_alt_pressed = True
                # Store current mouse position for height reference
                self.height_reference = (event.mouse_region_x, event.mouse_region_y)
            elif event.value == 'RELEASE':
                self.is_alt_pressed = False
            return {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            
            if self.is_alt_pressed and len(self.points) > 0:
                # Alt is pressed - adjust height based on vertical mouse movement
                if not hasattr(self, 'height_reference'):
                    self.height_reference = mouse_pos
                
                # Calculate height change based on vertical mouse movement
                delta_y = mouse_pos[1] - self.height_reference[1]
                grid_size = context.scene.unit_settings.scale_length
                height_change = round(delta_y * grid_size / 20) * grid_size  # Adjust sensitivity here
                
                # Update height while maintaining minimum
                new_height = max(
                    grid_size,  # Minimum height of one grid unit
                    self.base_height + height_change  # Current height + change
                )
                
                # Snap height to grid
                new_height = round(new_height / grid_size) * grid_size
                
                # Update current point with new height
                self.current_point = Vector((
                    self.current_point.x,
                    self.current_point.y,
                    new_height
                ))
            else:
                # Normal drawing - use grid plane
                point = mouse_to_3d_point(context, mouse_pos)
                if point:
                    grid_size = context.scene.unit_settings.scale_length
                    snapped_point = snap_to_grid(point, grid_size)
                    
                    # Update position while maintaining current height
                    self.current_point = Vector((
                        snapped_point.x,
                        snapped_point.y,
                        self.current_point.z if len(self.points) > 0 else snapped_point.z
                    ))
            
            self.is_drawing = True
            return {'RUNNING_MODAL'}

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if len(self.points) == 0:
                    # First click - start drawing
                    mouse_pos = (event.mouse_region_x, event.mouse_region_y)
                    point = mouse_to_3d_point(context, mouse_pos)
                    if point:
                        grid_size = context.scene.unit_settings.scale_length
                        snapped_point = snap_to_grid(point, grid_size)
                        self.points.append(snapped_point)
                        self.current_point = snapped_point.copy()
                        # Set initial height one grid unit above base
                        self.current_point.z += grid_size
                        self.base_height = self.current_point.z  # Store base height for Alt adjustments
                        self.is_drawing = True
                else:
                    # Second click - create the cuboid
                    obj = create_cuboid_mesh(self.points[0], self.current_point)
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)
                    bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                    return {'FINISHED'}
            
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            # Initialize variables
            self.points = []
            self.current_point = Vector((0, 0, 0))
            self.is_drawing = False
            self.is_alt_pressed = False
            self.base_height = 0
            
            # Add the drawing callback
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback_px, args, 'WINDOW', 'POST_PIXEL'
            )
            
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

class GreyboxFaceTransform(bpy.types.Operator):
    """Transform faces by clicking and dragging"""
    bl_idname = "bless.greybox_extrude"
    bl_label = "Greybox Face Transform"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == 'MOUSEMOVE':
            # Update highlighted face
            self.hit_face, self.hit_vertices = get_face_under_mouse(
                context, 
                (event.mouse_region_x, event.mouse_region_y)
            )
            return {'RUNNING_MODAL'}
            
        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if self.hit_face:
                    # TODO: Start face transformation
                    pass
            
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("Removing draw handler")
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            except ValueError:
                pass  # Handler might already be removed
            return {'CANCELLED'}
            
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            print("Starting face transform operator")
            # Initialize variables
            self.hit_face = None
            self.hit_vertices = []
            
            # Make sure we're in object mode
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Add the drawing callback
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_callback_px, args, 'WINDOW', 'POST_PIXEL'
            )
            print("Added draw handler")
            
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
    
    @staticmethod
    def draw_callback_px(self, context, _region=None):
        """Draw callback for face highlighting"""
        if self.hit_vertices:
            print("Drawing callback")
            draw_face_highlight(context, self.hit_vertices)

class GreyboxTransform(bpy.types.Operator):
    """Transform object in Trenchbroom style"""
    bl_idname = "bless.greybox_transform"
    bl_label = "Greybox Transform"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties to track state
    is_active: BoolProperty(default=False)
    alt_pressed: BoolProperty(default=False)

class GreyboxSnap(bpy.types.Operator):
    """Snap to grid in Trenchbroom style"""
    bl_idname = "bless.greybox_snap"
    bl_label = "Greybox Snap"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}
