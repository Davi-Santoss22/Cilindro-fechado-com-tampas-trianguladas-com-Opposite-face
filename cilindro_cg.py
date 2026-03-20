import math

class Face:
    def __init__(self, v1, v2, v3):
        self.vertices = (v1, v2, v3)
        self.opposite = [None, None, None]



def multiply_matrix_vector(matrix, vector):
    result = [0, 0, 0, 0]
    for i in range(4):
        for j in range(4):
            result[i] += matrix[i][j] * vector[j]
    return result

def get_translation_matrix(tx, ty, tz):
    return [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ]

def get_scale_matrix(sx, sy, sz):
    return [
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ]

def get_rotation_y_matrix(angle):
    rad = math.radians(angle)
    c = math.cos(rad)
    s = math.sin(rad)
    return [
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ]

def get_shear_xy_matrix(shx, shy):
    return [
        [1, 0, shx, 0],
        [0, 1, shy, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]

def get_reflection_x_matrix():
    return [
        [-1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]




def create_cylinder(radius, height, segments=6):
    vertices = []
    faces = []

    vertices.append([0, height/2, 0, 1])
    vertices.append([0, -height/2, 0, 1])

    offset = 2

    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)

        vertices.append([x, height/2, z, 1])
        vertices.append([x, -height/2, z, 1])

    for i in range(segments):
        top = offset + i*2
        bot = offset + i*2 + 1
        next_top = offset + ((i+1)%segments)*2
        next_bot = offset + ((i+1)%segments)*2 + 1

        # topo
        faces.append(Face(0, top, next_top))

        # base
        faces.append(Face(1, next_bot, bot))

        # laterais
        faces.append(Face(top, bot, next_bot))
        faces.append(Face(top, next_bot, next_top))

    build_opposites(faces)

    return vertices, faces

# opposite face
def build_opposites(faces):
    edge_map = {}

    for f in faces:
        v = f.vertices
        edges = [(v[0], v[1]), (v[1], v[2]), (v[2], v[0])]

        for i, (a, b) in enumerate(edges):
            key = tuple(sorted((a, b)))

            if key in edge_map:
                other_face, other_i = edge_map[key]
                f.opposite[i] = other_face
                other_face.opposite[other_i] = f
            else:
                edge_map[key] = (f, i)



def project(v):
    x, y, z, _ = v
    iso_x = x * math.cos(math.radians(30)) - z * math.cos(math.radians(30))
    iso_y = y + x * math.sin(math.radians(30)) + z * math.sin(math.radians(30))
    return iso_x, iso_y



def draw_edge(grid, v1, v2, cx, cy, scale):
    x1, y1 = project(v1)
    x2, y2 = project(v2)

    x1 = int(cx + x1 * scale)
    y1 = int(cy - y1 * scale)
    x2 = int(cx + x2 * scale)
    y2 = int(cy - y2 * scale)

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        if 0 <= x1 < len(grid) and 0 <= y1 < len(grid):
            if grid[y1][x1] == '.':
                grid[y1][x1] = '#'

        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

def render(vertices, faces, size=80):
    grid = [['.' for _ in range(size)] for _ in range(size)]
    cx, cy = size//2, size//2
    scale = 3

    # desenha arestas
    for f in faces:
        v = f.vertices
        draw_edge(grid, vertices[v[0]], vertices[v[1]], cx, cy, scale)
        draw_edge(grid, vertices[v[1]], vertices[v[2]], cx, cy, scale)
        draw_edge(grid, vertices[v[2]], vertices[v[0]], cx, cy, scale)

    # desenha vértices numerados
    for i, v in enumerate(vertices):
        x, y = project(v)
        px = int(cx + x * scale)
        py = int(cy - y * scale)

        if 0 <= px < size and 0 <= py < size:
            label = str(i)
            for k, char in enumerate(label):
                if 0 <= px + k < size:
                    grid[py][px + k] = char

    for row in grid:
        print("".join(row))



def apply(vertices, matrix):
    return [multiply_matrix_vector(matrix, v) for v in vertices]

if __name__ == "__main__":

    print("=== CONFIGURAÇÃO DO CILINDRO ===")
    radius = float(input("Raio: "))
    height = float(input("Altura: "))
    segments = int(input("Número de segmentos: "))

    vertices, faces = create_cylinder(radius, height, segments)

    print("\n=== ORIGINAL ===")
    render(vertices, faces)


    print("\n=== TRANSLAÇÃO ===")
    tx = float(input("tx: "))
    ty = float(input("ty: "))
    tz = float(input("tz: "))
    T = get_translation_matrix(tx, ty, tz)
    render(apply(vertices, T), faces)

    print("\n=== ESCALA ===")
    sx = float(input("sx: "))
    sy = float(input("sy: "))
    sz = float(input("sz: "))
    S = get_scale_matrix(sx, sy, sz)
    render(apply(vertices, S), faces)

  
    print("\n=== ROTAÇÃO (eixo Y) ===")
    angle = float(input("Ângulo (graus): "))
    R = get_rotation_y_matrix(angle)
    render(apply(vertices, R), faces)

  
    print("\n=== CISALHAMENTO ===")
    shx = float(input("shx: "))
    shy = float(input("shy: "))
    Sh = get_shear_xy_matrix(shx, shy)
    render(apply(vertices, Sh), faces)

    print("\n=== REFLEXÃO ===")
    op = input("Deseja aplicar reflexão no eixo X? (s/n): ")

    if op.lower() == 's':
        Ref = get_reflection_x_matrix()
        render(apply(vertices, Ref), faces)
    else:
        print("Reflexão não aplicada.")