import numpy as np
from math import pi

def create_ring(inner_radius, outer_radius, height, segments=100):
    vertices = []
    faces = []

    for i in range(segments):
        theta1 = 2.0 * pi * i / segments
        theta2 = 2.0 * pi * (i + 1) / segments

        # Inner vertices
        x1_in = inner_radius * np.cos(theta1)
        y1_in = inner_radius * np.sin(theta1)
        x2_in = inner_radius * np.cos(theta2)
        y2_in = inner_radius * np.sin(theta2)

        # Outer vertices
        x1_out = outer_radius * np.cos(theta1)
        y1_out = outer_radius * np.sin(theta1)
        x2_out = outer_radius * np.cos(theta2)
        y2_out = outer_radius * np.sin(theta2)
        
        # Bottom face
        vertices.extend([[x1_in, y1_in, 0], [x2_in, y2_in, 0], [x1_out, y1_out, 0]])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])
        vertices.extend([[x2_in, y2_in, 0], [x2_out, y2_out, 0], [x1_out, y1_out, 0]])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])

        # Top face
        vertices.extend([[x1_in, y1_in, height], [x2_in, y2_in, height], [x1_out, y1_out, height]])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])
        vertices.extend([[x2_in, y2_in, height], [x2_out, y2_out, height], [x1_out, y1_out, height]])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])

        # Side faces (inner)
        vertices.extend([[x1_in, y1_in, 0], [x2_in, y2_in, 0], [x1_in, y1_in, height]])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])
        vertices.extend([[x2_in, y2_in, 0], [x2_in, y2_in, height], [x1_in, y1_in, height]])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])

        # Side faces (outer)
        vertices.extend([[x1_out, y1_out, 0], [x2_out, y2_out, 0], [x1_out, y1_out, height]])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])
        vertices.extend([[x2_out, y2_out, 0], [x2_out, y2_out, height], [x1_out, y1_out, height]])
        faces.append([len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])

    return np.array(vertices), np.array(faces)

def create_conveyor_screw(diameter, length, shaft_inner_diameter, shaft_outer_diameter, num_turns, blade_thickness_at_shaft, blade_thickness_at_shaft_end, turn_direction, segments=1000):
    radius = diameter / 2
    ring_inner_radius = shaft_inner_diameter / 2
    ring_outer_radius = shaft_outer_diameter / 2
    turn_height = length / num_turns
    total_points = segments * num_turns

    vertices = []
    faces = []

    # Create the screw blade
    for i in range(total_points):
        angle = (-2 * pi * i) / segments
        z = (i / total_points) * (length-blade_thickness_at_shaft)
        if turn_direction:
            outer_x = radius * np.sin(angle)
            outer_y = radius * np.cos(angle)
            ring_x = ring_outer_radius * np.sin(angle)
            ring_y = ring_outer_radius * np.cos(angle)
        else:
            outer_x = radius * np.cos(angle)
            outer_y = radius * np.sin(angle)
            ring_x = ring_outer_radius * np.cos(angle)
            ring_y = ring_outer_radius * np.sin(angle)
        blade_thickness_at_shaft_difference = (blade_thickness_at_shaft - blade_thickness_at_shaft_end) / 2

        vertices.extend([[outer_x, outer_y, z + blade_thickness_at_shaft_difference], [ring_x, ring_y, z], [outer_x, outer_y, z + blade_thickness_at_shaft_end + blade_thickness_at_shaft_difference], [ring_x, ring_y, z + blade_thickness_at_shaft]])

    for i in range(total_points - 1):
        bottom_outer1 = i * 4
        bottom_inner1 = i * 4 + 1
        top_outer1 = i * 4 + 2
        top_inner1 = i * 4 + 3
        bottom_outer2 = (i + 1) * 4
        bottom_inner2 = (i + 1) * 4 + 1
        top_outer2 = (i + 1) * 4 + 2
        top_inner2 = (i + 1) * 4 + 3

        faces.append([bottom_outer1, bottom_inner1, bottom_outer2])
        faces.append([bottom_inner1, bottom_inner2, bottom_outer2])
        faces.append([top_outer1, top_inner1, top_outer2])
        faces.append([top_inner1, top_inner2, top_outer2])

        faces.append([bottom_outer1, top_outer1, bottom_outer2])
        faces.append([top_outer1, top_outer2, bottom_outer2])
        faces.append([bottom_inner1, top_inner1, bottom_inner2])
        faces.append([top_inner1, top_inner2, bottom_inner2])

    # Close the ends of the blade
    for end in [0, total_points - 1]:
        bottom_outer = end * 4
        bottom_inner = end * 4 + 1
        top_outer = end * 4 + 2
        top_inner = end * 4 + 3
        faces.append([bottom_outer, bottom_inner, top_inner])
        faces.append([bottom_outer, top_inner, top_outer])

    # Create the ring
    ring_height = length
    ring_vertices, ring_faces = create_ring(ring_inner_radius, ring_outer_radius, ring_height, segments)

    vertices = np.vstack((vertices, ring_vertices))
    ring_faces_shifted = ring_faces + len(vertices) - len(ring_vertices)
    faces.extend(ring_faces_shifted)

    return np.array(vertices), np.array(faces)

def save_stl(vertices, faces, filename):
    with open(filename, 'w') as file:
        file.write("solid OpenSCAD_Model\n")
        for face in faces:
            v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            normal = np.cross(v2 - v1, v3 - v1)
            norm_length = np.linalg.norm(normal)
            if norm_length != 0:
                normal /= norm_length
            file.write(f"  facet normal {normal[0]} {normal[1]} {normal[2]}\n")
            file.write("    outer loop\n")
            file.write(f"      vertex {v1[0]} {v1[1]} {v1[2]}\n")
            file.write(f"      vertex {v2[0]} {v2[1]} {v2[2]}\n")
            file.write(f"      vertex {v3[0]} {v3[1]} {v3[2]}\n")
            file.write("    endloop\n")
            file.write("  endfacet\n")
        file.write("endsolid OpenSCAD_Model\n")

# Parameters
diameter = 42
length = 102
shaft_inner_diameter = 6
shaft_outer_diameter = 18
num_turns = 3
blade_thickness_at_shaft = 15
blade_thickness_at_shaft_end = 4

turn_direction = False

# Generate vertices and faces
vertices, faces = create_conveyor_screw(diameter, length, shaft_inner_diameter, shaft_outer_diameter, num_turns, blade_thickness_at_shaft, blade_thickness_at_shaft_end,turn_direction)

# Save the STL file
file_path = "conveyor_screw.stl"
save_stl(vertices, faces, file_path)
