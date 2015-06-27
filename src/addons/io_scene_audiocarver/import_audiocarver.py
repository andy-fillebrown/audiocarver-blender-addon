
import bmesh
import bpy
import time
from math import pi, sin, cos
import os.path
import sys

dir_name = ''

current_track = 0
current_track_start_time = 0

pitch_id = 0
modulation_wheel_id = 1
volume_id = 7

note_suffix_number = 2
note_layer = 18
note_scale = 0.01
note_template_object = None
timeline_count = 0
timeline_layer = 17
timeline_text_layer = 16
track_scale = 1.0

pitch_min = 128
pitch_max = 0
velocity_scale = 1.0

#verts_per_second = 1 # use "0" to get start and end points only
verts_per_second = 0 # use "0" to get start and end points only
verts_per_ring = 32
max_note_thickness = 0.025
#max_note_thickness = 0.25
min_note_duration = 0.2

angle_start = 30 / 180 * pi
angle_end = 330 / 180 * pi
angle_increment = 0.0

note_range_distance = 5.0
#note_range_distance = 4.0

track_meshes = [];

i = 0
while i < 12:
    track_meshes.append(bmesh.new())
    i = i + 1


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


def get_note_object_name(chord_number):
    return "Note.Main.1." + str(chord_number)


def get_note_material(chord_number):
    return bpy.data.materials["Note.Material.1." + str(chord_number)]


def get_note_object(chord_number):
    note_material = get_note_material(chord_number)

    note_object = None
    note_object_name = get_note_object_name(chord_number)
    if (note_object_name in bpy.data.objects.keys()):
        note_object = bpy.data.objects[note_object_name]
    else:
        # Select and duplicate the note template object.
        clear_ss()
        note_template_object.select = True
        bpy.ops.object.duplicate()

        # Rename the new note object.
        note_object = bpy.data.objects["Note.Main.001"]
        note_object.name = note_object_name

    # Set the note mesh materials.
    note_object.material_slots[0].material = note_material

    return note_object


def get_note_mesh(chord_number):
    return track_meshes[int(chord_number - 1)]


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


def add_square_note_shape_to_mesh(note, position, mesh):
    x = note._startTime
    y = -position[0]
    z = position[1]
    note_width = note_range_distance / (pitch_max - pitch_min)
    half_note_width = note_width / 2.0
 
    mesh_verts = mesh.verts
    mesh_faces = mesh.faces
 
    x_increment = 10000000000000
    if (0.0 < verts_per_second):
        x_increment = 1.0 / verts_per_second;
 
    x1 = 0.0
    current_thickness = max_note_thickness
 
    # front
    y1 = y - half_note_width
    y2 = y + half_note_width
    z2 = z - (note._velocity * current_thickness)
    v1 = mesh_verts.new((x, y1, z))
    v2 = mesh_verts.new((x, y1, z2))
    v3 = mesh_verts.new((x, y2, z2))
    v4 = mesh_verts.new((x, y2, z))
    mesh_faces.new((v1, v2, v3, v4))
 
    while (x1 < note._duration):
        x2 = x1 + x_increment
        if (note._duration < x2):
            x2 = note._duration
        next_thickness = (1.0 - (x2 / (2 * note._duration))) * max_note_thickness
 
        # top
        y1 = y - half_note_width
        y2 = y + half_note_width
        z1 = z - (note._velocity * current_thickness)
        z2 = z - (note._velocity * next_thickness)
        v1 = mesh_verts.new((x + x1, y1, z1))
        v2 = mesh_verts.new((x + x2, y1, z2))
        v3 = mesh_verts.new((x + x2, y2, z2))
        v4 = mesh_verts.new((x + x1, y2, z1))
        mesh_faces.new((v1, v2, v3, v4))
 
        # right
        y1 = y + half_note_width
        z1 = z - (note._velocity * current_thickness)
        z2 = z - (note._velocity * next_thickness)
        v1 = mesh_verts.new((x + x1, y1, z1))
        v2 = mesh_verts.new((x + x2, y1, z2))
        v3 = mesh_verts.new((x + x2, y1, z))
        v4 = mesh_verts.new((x + x1, y1, z))
        mesh_faces.new((v1, v2, v3, v4))
 
        # bottom
        y1 = y - half_note_width
        y2 = y + half_note_width
        v1 = mesh_verts.new((x + x1, y2, z))
        v2 = mesh_verts.new((x + x2, y2, z))
        v3 = mesh_verts.new((x + x2, y1, z))
        v4 = mesh_verts.new((x + x1, y1, z))
        mesh_faces.new((v1, v2, v3, v4))
 
        # left
        y1 = y - half_note_width
        z1 = z - (note._velocity * current_thickness)        #z2 = z - (note._velocity * current_thickness)
        z2 = z - (note._velocity * next_thickness)        #z4 = z - (note._velocity * next_thickness)
        v1 = mesh_verts.new((x + x1, y1, z))
        v2 = mesh_verts.new((x + x2, y1, z))
        v3 = mesh_verts.new((x + x2, y1, z2))
        v4 = mesh_verts.new((x + x1, y1, z1))
        mesh_faces.new((v1, v2, v3, v4))
 
        x1 = x2
        current_thickness = next_thickness
 
    # back
    y1 = y - half_note_width
    y2 = y + half_note_width    #z1 = z - (note._velocity * current_thickness)
    z1 = z - (note._velocity * current_thickness)
    v1 = mesh_verts.new((x + x1, y2, z))
    v2 = mesh_verts.new((x + x1, y2, z1))
    v3 = mesh_verts.new((x + x1, y1, z1))
    v4 = mesh_verts.new((x + x1, y1, z))
    mesh_faces.new((v1, v2, v3, v4))


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
    track_offset = 1.0
    y = track_offset * sin(pitch_angle)
    z = track_offset * cos(pitch_angle)
 
    add_round_note_shape_to_mesh(note, (y, z), mesh)


def add_flat_note_to_mesh(note, mesh):
    global pitch_min
    global pitch_max
    y = 0
    z = -0.1 * float(current_super_track)
    pitch_offset = note._pitch - pitch_min
    if (0.0 < pitch_offset):
        y = -(note_range_distance / 2.0) + (pitch_offset * (note_range_distance / (pitch_max - pitch_min)))
    add_square_note_shape_to_mesh(note, (y, z), mesh)


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


def update_ranges(file_name):
    global pitch_min
    global pitch_max
    
    # Read each line in the file and update global max and min values.
    file = open(dir_name + file_name);
    for line in file:
        line = line.rstrip('\r\n').split(', ')
        line_id = float(line[0])
        line_value = float(line[2])
        if (pitch_id == line_id):
            if (line_value < pitch_min):
                pitch_min = line_value
            if (pitch_max < line_value):
                pitch_max = line_value


def update_current_track_start_time(file_name):
    global current_track_start_time
    
    # Read the first line's time parameter.
    file = open(dir_name + file_name);
    for line in file:
        line = line.rstrip('\r\n').split(', ')
        current_track_start_time = float(line[1])
    

def import_file(file_name):
    chord = -1
    start_time = -1
    end_time = -1
    pitch = -1
    volume = -1

    file = open(dir_name + file_name);
    for line in file:
        line = line.rstrip('\r\n').split(', ')
        line_id = float(line[0])
        line_time = float(line[1])
        line_value = float(line[2])
        if (-1 == start_time):
            start_time = line_time
        else:
            end_time = line_time
        if (pitch_id == line_id):
            if (-1 == pitch):
                pitch = line_value
        elif (volume_id == line_id):
            if (volume < line_value):
                volume = line_value
        elif (modulation_wheel_id == line_id):
            if (-1 == chord):
                chord = line_value
    
    start_time -= current_track_start_time
    end_time -= current_track_start_time

    note = Note()
    note._startTime = start_time
    note._duration = end_time - start_time
    note._velocity = 0.01 + (velocity_scale * volume)
    note._pitch = pitch
    note_mesh = get_note_mesh(chord)
    add_circular_ring_note_to_mesh(note, note_mesh)


def load(operator,
         context,
         file_name):
    global angle_increment
    global current_track
    global current_super_track
    global dir_name
    global note_layer
    global note_template_object
    global pitch_min
    global pitch_max
    global velocity_min
    global velocity_max
    global velocity_scale
    global track_scale

    # Reset global variables.
    pitch_min = 128
    pitch_max = 0
    current_track = 0

    dir_name = os.path.dirname(file_name) + '/'
    print_message("\nImporting Csound Log Directory" + dir_name + "/ ...")

    start_time = time.time()

    # Store the current selection set so it can be restored later.
    cur_active_obj = bpy.context.scene.objects.active
    cur_ss = current_ss()

    # Turn on the note layers.
    bpy.context.scene.layers[note_layer] = True

    # Set the note template object.
    note_template_object = bpy.data.objects["Note.Main"]

    # Set the track scale.
    track_scale = bpy.data.objects[".Track.Scale.X"].scale[0]

    print_message("\nImporting tracks ...")

    for file_name in os.listdir(dir_name):
        if (file_name.endswith(".txt")):
            file_info = file_name.split('-')
            #note_id = int(file_info[1])
            note_number = int(file_info[4].split('.')[0])
            # The first note is the track time reference.  Skip it.
            if (1 < note_number):
                update_ranges(file_name)
    
    # Calculate the global angle increment.
    angle_increment = (angle_end - angle_start) / (pitch_max - pitch_min)

    # Import tracks and notes.
    for file_name in os.listdir(dir_name):
        if (file_name.endswith(".txt")):
            file_info = file_name.split('-')
            note_number = int(file_info[4].split('.')[0])
            if (1 == note_number):
                current_track = int(file_info[1])
                update_current_track_start_time(file_name)
            else:
                import_file(file_name)

    # Add each mesh to it's note.
    i = 1
    while i <= 12:
        note = get_note_object(i)
        mesh = get_note_mesh(i)
        mesh.to_mesh(note.data)
        i = i + 1

    # Delete the note template objects.
    clear_ss()
    note_template_object.select = True
    bpy.ops.object.delete()

    # Restore the original selection set.
    clear_ss()
    for obj in cur_ss:
        obj.select = True
    bpy.context.scene.objects.active = cur_active_obj

    print_message("\n... done in %.3f seconds\n" % (time.time() - start_time))

    return {'FINISHED'}
