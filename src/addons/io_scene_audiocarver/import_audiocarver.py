
import bmesh
import bpy
import xml.dom as Dom
import xml.dom.minidom as Xml
import time
#from math import *
from math import pi, sin, cos
import sys

note_suffix_number = 2
note_layer = 18
note_scale = 0.01
note_template_object = None
track_count = 1
timeline_count = 0
timeline_layer = 17
timeline_text_layer = 16
track_scale = 1.0

pitch_min = 128
pitch_max = 0

verts_per_second = 1 # use "0" to get start and end points only
verts_per_ring = 32
max_note_thickness = 0.075

angle_start = 30 / 180 * pi
angle_end = 330 / 180 * pi
angle_increment = 0.0

note_range_distance = 5.0

timeline_imported = False

# set_cycles_material_color = True

class Note:
    _startTime = -1
    _duration = -1
    _velocity = -1
    _pitch = -1


def print_message(message):
    print(message);
    sys.stdout.flush();


def clear_ss():
    bpy.ops.object.select_all(action = 'DESELECT')


def current_ss():
    return bpy.context.selected_objects


def to_zero_prefixed_string(number):
    zero_prefixed_string = ""
    if number < 100:
        zero_prefixed_string += "0"
    if number < 10:
        zero_prefixed_string += "0"
    zero_prefixed_string += str(int(number))
    return zero_prefixed_string


def create_note_material(color = "#ffffff"):
    return bpy.data.materials["Note.Material.0"]
#     template_material = bpy.data.materials["Note.Material.0"]
#     note_material = template_material.copy()
#     note_material.name = "Note.Material." + str(track_count)
#     note_material.diffuse_color[0] = float((16 * int(color[1:2], 16)) + int(color[2:3], 16)) / 255.0
#     note_material.diffuse_color[1] = float((16 * int(color[3:4], 16)) + int(color[4:5], 16)) / 255.0
#     note_material.diffuse_color[2] = float((16 * int(color[5:6], 16)) + int(color[6:7], 16)) / 255.0
#     r_is_zero = 0.0 == note_material.diffuse_color[0]
#     g_is_zero = 0.0 == note_material.diffuse_color[1]
#     b_is_zero = 0.0 == note_material.diffuse_color[2]
#     if r_is_zero:
#         if g_is_zero or b_is_zero:
#             note_material.diffuse_color[0] = 0.0005
#         else:
#             note_material.diffuse_color[0] = 0.001
#     if g_is_zero:
#         if r_is_zero or b_is_zero:
#             note_material.diffuse_color[1] = 0.0005
#         else:
#             note_material.diffuse_color[1] = 0.001
#     if b_is_zero:
#         if r_is_zero or g_is_zero:
#             note_material.diffuse_color[2] = 0.0005
#         else:
#             note_material.diffuse_color[2] = 0.001
#     if set_cycles_material_color:
#         note_material.node_tree.nodes['Glass BSDF'].inputs['Color'].default_value = (note_material.diffuse_color[0],
#                                                                                      note_material.diffuse_color[1],
#                                                                                      note_material.diffuse_color[2],
#                                                                                      1.0)
#     return note_material


def add_round_note_shape_to_mesh(note, position, mesh):
    global max_note_thickness

    x = note._startTime
    y = position[0]
    z = position[1]

    mesh_verts = mesh.verts
    mesh_faces = mesh.faces
    x_increment = 10000000000000
    if (0.0 < verts_per_second):
        x_increment = 1.0 / verts_per_second;
    mesh_angle_increment = 2 * pi / verts_per_ring
    x1 = 0.0
    current_thickness = max_note_thickness
    while (x1 < note._duration):
        x2 = x1 + x_increment
        if (note._duration < x2):
            x2 = note._duration
        angle = 0
        next_thickness = (1.0 - (x2 / (2 * note._duration))) * max_note_thickness
        while (angle < (2 * pi)):
            y1 = note._velocity * sin(angle)
            z1 = note._velocity * cos(angle)
            angle = angle + mesh_angle_increment
            y2 = note._velocity * sin(angle)
            z2 = note._velocity * cos(angle)
            v1 = mesh_verts.new((x + x1, y + y1 * current_thickness, z + z1 * current_thickness))
            v2 = mesh_verts.new((x + x2, y + y1 * next_thickness, z + z1 * next_thickness))
            v3 = mesh_verts.new((x + x2, y + y2 * next_thickness, z + z2 * next_thickness))
            v4 = mesh_verts.new((x + x1, y + y2 * current_thickness, z + z2 * current_thickness))
            mesh_faces.new((v1, v2, v3, v4))
        x1 = x2
        current_thickness = next_thickness


# def add_square_note_shape_to_mesh(note, position, mesh):
#     x = note._startTime
#     y = position[0]
#     z = position[1]
#     note_width = note_range_distance / (pitch_max - pitch_min)
#     half_note_width = note_width / 2.0
# 
#     mesh_verts = mesh.verts
#     mesh_faces = mesh.faces
# 
#     x_increment = 10000000000000
#     if (0.0 < verts_per_second):
#         x_increment = 1.0 / verts_per_second;
# 
#     x1 = 0.0
#     current_thickness = max_note_thickness
# 
#     # front
#     y1 = y - half_note_width
#     y2 = y + half_note_width
#     z1 = z - (note._velocity * current_thickness)
#     z2 = z + (note._velocity * current_thickness)
#     v1 = mesh_verts.new((x, y1, z1))
#     v2 = mesh_verts.new((x, y1, z2))
#     v3 = mesh_verts.new((x, y2, z2))
#     v4 = mesh_verts.new((x, y2, z1))
#     mesh_faces.new((v1, v2, v3, v4))
# 
#     while (x1 < note._duration):
#         x2 = x1 + x_increment
#         if (note._duration < x2):
#             x2 = note._duration
#         next_thickness = (1.0 - (x2 / (2 * note._duration))) * max_note_thickness
# 
#         # top
#         y1 = y - half_note_width
#         y2 = y + half_note_width
#         z1 = z + (note._velocity * current_thickness)
#         z2 = z + (note._velocity * next_thickness)
#         v1 = mesh_verts.new((x + x1, y1, z1))
#         v2 = mesh_verts.new((x + x2, y1, z2))
#         v3 = mesh_verts.new((x + x2, y2, z2))
#         v4 = mesh_verts.new((x + x1, y2, z1))
#         mesh_faces.new((v1, v2, v3, v4))
# 
#         # right
#         y1 = y + half_note_width
#         z1 = z + (note._velocity * current_thickness)
#         z2 = z - (note._velocity * current_thickness)
#         z3 = z + (note._velocity * next_thickness)
#         z4 = z - (note._velocity * next_thickness)
#         v1 = mesh_verts.new((x + x1, y1, z1))
#         v2 = mesh_verts.new((x + x2, y1, z3))
#         v3 = mesh_verts.new((x + x2, y1, z4))
#         v4 = mesh_verts.new((x + x1, y1, z2))
#         mesh_faces.new((v1, v2, v3, v4))
# 
#         # bottom
#         y1 = y - half_note_width
#         y2 = y + half_note_width
#         z1 = z - (note._velocity * current_thickness)
#         z2 = z - (note._velocity * next_thickness)
#         v1 = mesh_verts.new((x + x1, y2, z1))
#         v2 = mesh_verts.new((x + x2, y2, z2))
#         v3 = mesh_verts.new((x + x2, y1, z2))
#         v4 = mesh_verts.new((x + x1, y1, z1))
#         mesh_faces.new((v1, v2, v3, v4))
# 
#         # left
#         y1 = y - half_note_width
#         z1 = z + (note._velocity * current_thickness)
#         z2 = z - (note._velocity * current_thickness)
#         z3 = z + (note._velocity * next_thickness)
#         z4 = z - (note._velocity * next_thickness)
#         v1 = mesh_verts.new((x + x1, y1, z2))
#         v2 = mesh_verts.new((x + x2, y1, z4))
#         v3 = mesh_verts.new((x + x2, y1, z3))
#         v4 = mesh_verts.new((x + x1, y1, z1))
#         mesh_faces.new((v1, v2, v3, v4))
# 
#         x1 = x2
#         current_thickness = next_thickness
# 
#     # back
#     y1 = y - half_note_width
#     y2 = y + half_note_width
#     z1 = z - (note._velocity * current_thickness)
#     z2 = z + (note._velocity * current_thickness)
#     v1 = mesh_verts.new((x + x1, y2, z1))
#     v2 = mesh_verts.new((x + x1, y2, z2))
#     v3 = mesh_verts.new((x + x1, y1, z2))
#     v4 = mesh_verts.new((x + x1, y1, z1))
#     mesh_faces.new((v1, v2, v3, v4))


# def add_arc_note_shape_to_mesh(note, start_radius, start_angle, end_radius, end_angle, mesh):
#     global max_note_thickness
# 
#     x = note._startTime
# 
#     mesh_verts = mesh.verts
#     mesh_faces = mesh.faces
#     x_increment = 10000000000000
#     if (0.0 < verts_per_second):
#         x_increment = 1.0 / verts_per_second;
#     x1 = 0.0
#     radius_increment = (end_radius - start_radius) / verts_per_ring
#     angle_increment = (end_angle - start_angle) / verts_per_ring
#     while (x1 < note._duration):
#         x2 = x1 + x_increment
#         if (note._duration < x2):
#             x2 = note._duration
#         radius = start_radius
#         angle = start_angle
#         i = 0
#         while (i < verts_per_ring):
#             y1 = radius * sin(angle)
#             z1 = radius * cos(angle)
#             radius = radius + radius_increment
#             angle = angle + angle_increment
#             y2 = radius * sin(angle)
#             z2 = radius * cos(angle)
#             v1 = mesh_verts.new((x + x1, y1, z1))
#             v2 = mesh_verts.new((x + x2, y1, z1))
#             v3 = mesh_verts.new((x + x2, y2, z2))
#             v4 = mesh_verts.new((x + x1, y2, z2))
#             mesh_faces.new((v1, v2, v3, v4))
#             i = i + 1
#         x1 = x2


def add_circular_ring_note_to_mesh(note, mesh):
    global pitch_min
    global pitch_max
 
    # Calculate the note's location on the ring.
    pitch_delta = note._pitch - pitch_min
    pitch_angle = angle_start + (pitch_delta * angle_increment)
    y = sin(pitch_angle)
    z = cos(pitch_angle)
 
    add_round_note_shape_to_mesh(note, (y, z), mesh)


# def add_flat_note_to_mesh(note, mesh):
#     global pitch_min
#     global pitch_max
#     y = 0
#     z = -0.1 * track_count
#     pitch_offset = note._pitch - pitch_min
#     if (0.0 < pitch_offset):
#         y = -(note_range_distance / 2.0) + (pitch_offset * (note_range_distance / (pitch_max - pitch_min)))
#     add_square_note_shape_to_mesh(note, (y, z), mesh)


# def add_spiral_ring_note_to_mesh(note, mesh):
#     pitch_key = (note._pitch % 12.0) - 9.0 # 9 == A
#     pitch_8va = int(note._pitch / 12.0)
# 
#     # Calculate the note's location.
#     start_radius = 1.5 - (4.0 * max_note_thickness * (pitch_8va + ((pitch_key - 1.0) / 12.0)))
#     end_radius = 1.5 - (4.0 * max_note_thickness * (pitch_8va + ((pitch_key) / 12.0)))
#     pitch_angle = pitch_key * pi / 6.0 # key * 2pi / 12
#     start_angle = (pitch_key * 2 * pi / 12.0) - (0.5 * 2 * pi / 12.0)
#     end_angle = (pitch_key * 2 * pi / 12.0) + (0.5 * 2 * pi / 12.0)
# 
#     #add_round_note_shape_to_mesh(note, (y, z), mesh)
#     add_arc_note_shape_to_mesh(note, start_radius, start_angle + 0.01, end_radius, end_angle - 0.01, mesh)


def import_note(note_node, note_mesh):
    if "Note" != note_node.nodeName:
        print_message("Xml node is not a note.")
        return

    # Get the first and last pitch point positions.
    pitch_curve_node = Dom.Node
    first_pt_node = Dom.Node
    last_pt_node = Dom.Node
    first_pt_pos_value = 0
    last_pt_pos_value = 0
    for child_node in note_node.childNodes:
        if "PitchCurve" == child_node.nodeName:
            pitch_curve_node = child_node
            break
    for point_node in pitch_curve_node.childNodes:
        if "Point" == point_node.nodeName:
            first_pt_node = point_node
            break
    for point_node in pitch_curve_node.childNodes:
        if "Point" == point_node.nodeName:
            last_pt_node = point_node
    i = 0
    while i < first_pt_node.attributes.length:
        attribute = first_pt_node.attributes.item(i)
        if "position" == attribute.name:
            first_pt_pos_value = attribute.value.split(" ")
            break
        i += 1
    i = 0
    while i < last_pt_node.attributes.length:
        attribute = last_pt_node.attributes.item(i)
        if "position" == attribute.name:
            last_pt_pos_value = attribute.value.split(" ")
            break

    first_pt_x = track_scale * float(first_pt_pos_value[0])
    first_pt_y = float(first_pt_pos_value[1])
    duration = (track_scale * float(last_pt_pos_value[0])) - first_pt_x

    # Get the note's velocity/volume.
    velocity = 1.0
    i = 0
    while i < note_node.attributes.length:
        attribute = note_node.attributes.item(i)
        if "volume" == attribute.name:
            velocity = float(attribute.value)
            break;
        i += 1

    note = Note()
    note._startTime = first_pt_x
    note._duration = duration
    note._velocity = velocity
    note._pitch = first_pt_y

    add_circular_ring_note_to_mesh(note, note_mesh)
    #add_flat_note_to_mesh(note, note_mesh)
    #add_spiral_ring_note_to_mesh(note, note_mesh)


def import_track(track_node):
    global note_suffix_number
    global track_count

    # Read the track's attributes.
    color = "#ffffff"
    track_name = ""
    i = 0
    attributes = track_node.attributes
    while i < attributes.length:
        attribute = attributes.item(i)
        if "color" == attribute.name:
            color = attribute.value
        if "name" == attribute.name:
            track_name = attribute.value
        i += 1

    print_message(" \"" + track_name + "\"")

    # Create the track's note material.
    note_material = create_note_material(color)

    # Select and duplicate the note template object.
    clear_ss()
    note_template_object.select = True
    bpy.ops.object.duplicate()

    # Rename the new note object.
    note_object = bpy.data.objects["Note.001"]
    note_object.name = note_object.name[0 : -3] + to_zero_prefixed_string(note_suffix_number)

    # Set the note mesh materials.
    note_object.material_slots[0].material = note_material

    note_bmesh = bmesh.new();

    # Read the track's note list.
    for child_node in track_node.childNodes:
        if "NoteList" == child_node.nodeName:
            for note_node in child_node.childNodes:
                if "Note" == note_node.nodeName:
                    import_note(note_node, note_bmesh)

    note_bmesh.to_mesh(note_object.data)

    note_suffix_number += 1
    track_count += 1


def import_timeline(timeline_node):
    global timeline_count
    global timeline_imported

    if 0 == timeline_count:
        timeline_count += 1
        timeline_imported = True
        return

    timeline_label = ""
    timeline_location = 0.0
    attributes = timeline_node.attributes
    i = 0
    while i < attributes.length:
        attribute = attributes.item(i)
        if "label" == attribute.name:
            timeline_label = attribute.value
        elif "location" == attribute.name:
            timeline_location = float(attribute.value)
        i += 1

    if "" == timeline_label:
        return
    if -1 != timeline_label.find("."):
        return
    if 0.0 == timeline_location:
        return

    timeline_count += 1
    timeline_count_string = to_zero_prefixed_string(timeline_count + 1)

    # Create the time line.
    clear_ss()
    bpy.data.objects["TimeLine.0"].select = True
    bpy.ops.object.duplicate(linked = True)
    timeline = bpy.data.objects["TimeLine.001"]
    timeline.name = timeline.name[0:-3] + timeline_count_string
    timeline.location[0] = timeline_location

    # Create the time line text.
    clear_ss()
    bpy.data.objects["TimeLine.Text.0"].select = True
    bpy.ops.object.duplicate(linked = False)
    timeline_text = bpy.data.objects["TimeLine.Text.001"]
    timeline_text.name = timeline_text.name[0:-3] + timeline_count_string
    timeline_text.location[0] = timeline_location
    timeline_text.data.body = timeline_label

    timeline_imported = True


def import_timelines(timelines_node):
    global timeline_layer

    print_message("\nImporting time lines ...")

    bpy.context.scene.layers[timeline_layer] = True
    bpy.context.scene.layers[timeline_text_layer] = True

    for child_node in timelines_node.childNodes:
        if "TimeGridLine" == child_node.nodeName:
            import_timeline(child_node)


def update_pitch_range(xml_node):
    global angle_increment
    global pitch_min
    global pitch_max

    if Dom.Node.TEXT_NODE == xml_node.nodeType:
        return
    if "Track" == xml_node.nodeName:
        for child_node in xml_node.childNodes:
            if "NoteList" == child_node.nodeName:
                for note_node in child_node.childNodes:
                    if "Note" == note_node.nodeName:
                        pitch_curve_node = Dom.Node
                        first_pt_node = Dom.Node
#                         last_pt_node = Dom.Node
                        first_pt_pos_value = 0
#                         last_pt_pos_value = 0
                        for child_node in note_node.childNodes:
                            if "PitchCurve" == child_node.nodeName:
                                pitch_curve_node = child_node
                                break
                        for point_node in pitch_curve_node.childNodes:
                            if "Point" == point_node.nodeName:
                                first_pt_node = point_node
                                break
                        i = 0
                        while i < first_pt_node.attributes.length:
                            attribute = first_pt_node.attributes.item(i)
                            if "position" == attribute.name:
                                first_pt_pos_value = attribute.value.split(" ")
                                break
                            i += 1
                        pitch = float(first_pt_pos_value[1])
                        if (pitch < pitch_min):
                            pitch_min = pitch
                        if (pitch_max < pitch):
                            pitch_max = pitch
    else:
        for child_node in xml_node.childNodes:
            update_pitch_range(child_node)


def import_node(xml_node):
    if Dom.Node.TEXT_NODE == xml_node.nodeType:
        return
    if "Track" == xml_node.nodeName:
        import_track(xml_node)
    elif "TimeGridLineList" == xml_node.nodeName:
        #import_timelines(xml_node)
        return
    else:
        for child_node in xml_node.childNodes:
            import_node(child_node)


def note_string(note_number):
    mod = int(note_number) % 12
    if 0 == mod:
        return "C"
    if 2 == mod:
        return "D"
    if 4 == mod:
        return "E"
    if 5 == mod:
        return "F"
    if 7 == mod:
        return "G"
    if 9 == mod:
        return "A"
    if 11 == mod:
        return "B"
    return ""


def create_pitch_lines():
    global angle_increment
    global angle_start
    global angle_end
    global pitch_min
    global pitch_max

    print_message("\nCreating pitch lines ...")

    # Create pitch line text objects for each note in the note pitch range.
    i = pitch_min
    while i <= pitch_max:
        angle = angle_start + (angle_increment * (pitch_max - i))
        x = sin(angle)
        y = cos(angle)

        i_string = str(int(i))
        text_string = note_string(i)
        has_text = "" != text_string

        # Duplicate pitch line text template objects.
        clear_ss()
        bpy.data.objects["PitchLine.Text.Arrow.0"].select = True
        bpy.ops.object.duplicate()

        # Setup pitch line text arrow.
        obj = bpy.data.objects["PitchLine.Text.Arrow.001"]
        obj.rotation_euler[0] = -angle
        obj.location[1] = x
        obj.location[2] = y
        obj.name = "PitchLine.Text.Arrow.." + i_string

        if has_text:
            clear_ss()
            bpy.data.objects["PitchLine.Text.0"].select = True
            bpy.ops.object.duplicate()

            radius = 1.1
            location = (0, radius * sin(angle), radius * cos(angle))

            # Setup pitch line text.
            obj = bpy.data.objects["PitchLine.Text.001"]
            obj.location = location
            obj.data.body = note_string(i)
            obj.name = "PitchLine.Text.." + i_string

            # Center pitch line text.
            bbox = obj.bound_box
            x_offset = bbox[0][1] + ((bbox[2][1] - bbox[0][1]) / 2.0)
            y_offset = bbox[0][0] + (bbox[4][0] - bbox[0][0])
            obj.location[1] += y_offset
            obj.location[2] -= x_offset

        i += 1

    # Delete pitch line text template objects.
    clear_ss()
    bpy.data.objects["PitchLine.Text.0"].select = True
    bpy.data.objects["PitchLine.Text.Arrow.0"].select = True
    bpy.ops.object.delete()


def load(operator,
         context,
         file_name):
    global angle_increment
    global note_layer
    global note_template_object
    global pitch_min
    global pitch_max
    global timeline_imported
    global track_count
    global track_scale

    print_message("\nImporting AudioCarver file" + file_name + "...")

    start_time = time.time()

    pitch_min = 128
    pitch_max = 0
    timeline_imported = False

    # Store the current selection set so it can be restored later.
    cur_active_obj = bpy.context.scene.objects.active
    cur_ss = current_ss()

    # Turn on the note layers.
    bpy.context.scene.layers[note_layer] = True

    # Set the note template object.
    note_template_object = bpy.data.objects["Note.0"]

    # Set the track scale.
    track_scale = bpy.data.objects[".Track.Scale.X"].scale[0]

    print_message("\nImporting tracks ...")
    track_count = 1

    dom = Xml.parse(file_name)

    # Read all nodes and update pitch range.
    for xml_node in dom.childNodes:
        update_pitch_range(xml_node)

    # Calculate the global angle increment.
    angle_increment = (angle_end - angle_start) / (pitch_max - pitch_min)

    # Import tracks, notes, and time lines.
    for xml_node in dom.childNodes:
        import_node(xml_node)

    # Delete the note template objects.
    clear_ss()
    note_template_object.select = True
    bpy.ops.object.delete()

    # Delete the time line template object if no time lines were imported.
    if (not timeline_imported):
        print_message("\nNo time lines imported.")
        clear_ss()
        bpy.data.objects["TimeLine.0"].select = True
        bpy.data.objects["TimeLine.Text.0"].select = True
        bpy.ops.object.delete()

    # Create pitch lines
    create_pitch_lines()

    # Restore the original selection set.
    clear_ss()
    for obj in cur_ss:
        obj.select = True
    bpy.context.scene.objects.active = cur_active_obj

    print_message("\n... done in %.3f seconds\n" % (time.time() - start_time))

    return {'FINISHED'}
