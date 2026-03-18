import math

# ==========================================
# 1. ESTRUTURAS MATEMÁTICAS E MATRIZES
# ==========================================

def multiply_matrix_vector(matrix, vector):
    """Multiplica uma matriz 4x4 por um vetor 4x1 (coordenadas homogêneas)."""
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
        [0, 0, 0,  1]
    ]

def get_rotation_y_matrix(angle_degrees):
    rad = math.radians(angle_degrees)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    return [
        [cos_a,  0, sin_a, 0],
        [0,      1, 0,     0],
        [-sin_a, 0, cos_a, 0],
        [0,      0, 0,     1]
    ]

def get_shear_xy_matrix(shx, shy):
    """Cisalhamento no plano XY em função de Z"""
    return [
        [1, 0, shx, 0],
        [0, 1, shy, 0],
        [0, 0, 1,   0],
        [0, 0, 0,   1]
    ]
    
def get_reflection_x_matrix():
    """Reflete (espelha) o objeto em relação ao eixo X."""
    return [
        [-1, 0,  0, 0],
        [0,  1,  0, 0],
        [0,  0,  1, 0],
        [0,  0,  0, 1]
    ]

# ==========================================
# 2. MODELAGEM DO CILINDRO
# ==========================================

def create_cylinder(radius, height, segments=8):
    """
    Cria os vértices e arestas de um cilindro.
    A tampa é triangulada (centro até as bordas).
    Faces laterais conectam topo e base (opposite-faces).
    """
    vertices = []
    edges = []
    
    # Vértices centrais para triangulação das tampas
    top_center_idx = 0
    bot_center_idx = 1
    vertices.append([0, height/2, 0, 1])  # Topo
    vertices.append([0, -height/2, 0, 1]) # Base
    
    offset = 2
    # Gerando os vértices das bordas
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        
        vertices.append([x, height/2, z, 1])   # Vértice Topo
        vertices.append([x, -height/2, z, 1])  # Vértice Base correspondente
        
    # Gerando as arestas (Wireframe para renderização)
    for i in range(segments):
        top_idx = offset + (i * 2)
        bot_idx = offset + (i * 2) + 1
        
        next_top_idx = offset + (((i + 1) % segments) * 2)
        next_bot_idx = offset + (((i + 1) % segments) * 2) + 1
        
        # Tampas Trianguladas (Centro até a borda)
        edges.append((top_center_idx, top_idx))
        edges.append((bot_center_idx, bot_idx))
        
        # Bordas das tampas
        edges.append((top_idx, next_top_idx))
        edges.append((bot_idx, next_bot_idx))
        
        # Faces Opostas (Conectando topo e base)
        edges.append((top_idx, bot_idx))
        # Para triangular completamente a face lateral:
        edges.append((top_idx, next_bot_idx)) 

    return vertices, edges

# ==========================================
# 3. RENDERIZAÇÃO EM MODO TEXTO (SRU)
# ==========================================

def project_3d_to_2d(vertex):
    """Projeção isométrica simples para visualização."""
    x, y, z, _ = vertex
    # Ângulo isométrico padrão
    iso_x = x * math.cos(math.radians(30)) - z * math.cos(math.radians(30))
    iso_y = y + x * math.sin(math.radians(30)) + z * math.sin(math.radians(30))
    return iso_x, iso_y

def draw_line(grid, x0, y0, x1, y1, width, height):
    """Algoritmo de Bresenham para desenhar linhas na matriz de caracteres."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        # Verifica se está dentro dos limites da matriz
        if 0 <= x0 < width and 0 <= y0 < height:
            grid[y0][x0] = '#'
            
        if x0 == x1 and y0 == y1:
            break
            
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def render_object(vertices, edges, grid_size=50):
    """Renderiza os vértices e arestas em uma matriz de texto simulando o SRU."""
    # Cria matriz vazia (caractere de espaço ou ponto)
    grid = [['.' for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Coordenadas do centro da matriz
    cx, cy = grid_size // 2, grid_size // 2
    scale_factor = 2  # Fator para ampliar a visualização no grid

    # Desenha os eixos cartesianos no grid (opcional, para contexto)
    for i in range(grid_size):
        grid[cy][i] = '-'
        grid[i][cx] = '|'
    grid[cy][cx] = '+'

    for edge in edges:
        v1 = vertices[edge[0]]
        v2 = vertices[edge[1]]
        
        x1_2d, y1_2d = project_3d_to_2d(v1)
        x2_2d, y2_2d = project_3d_to_2d(v2)
        
        # Mapeamento para coordenadas da matriz (inverte Y para visualização correta)
        px1 = int(cx + x1_2d * scale_factor)
        py1 = int(cy - y1_2d * scale_factor) # Y cresce para baixo na matriz
        px2 = int(cx + x2_2d * scale_factor)
        py2 = int(cy - y2_2d * scale_factor)
        
        draw_line(grid, px1, py1, px2, py2, grid_size, grid_size)

    # Imprime a matriz
    for row in grid:
        print("".join(row))

def print_coordinates(vertices):
    print("Coordenadas dos Vértices (x, y, z):")
    for i, v in enumerate(vertices):
        print(f"V{i}: ({v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f})")
    print("-" * 30)

# ==========================================
# 4. EXECUÇÃO PRINCIPAL
# ==========================================


if __name__ == "__main__":
    # Cria o cilindro original
    orig_vertices, edges = create_cylinder(radius=4, height=8, segments=6)
    
    # Função auxiliar para não repetir código de impressão
    def apply_and_render(matrix, title):
        transformed_vertices = []
        for v in orig_vertices:
            transformed_vertices.append(multiply_matrix_vector(matrix, v))
        
        print("\n" + "="*60)
        print(f"{title}")
        print("="*60)
        print_coordinates(transformed_vertices)
        render_object(transformed_vertices, edges)
        print("\n" + "."*60 + "\n")

    # 0. ORIGINAL
    print("\n" + "="*60)
    print("0. OBJETO ORIGINAL (ANTES)")
    print("="*60)
    print_coordinates(orig_vertices)
    render_object(orig_vertices, edges)
    print("\n" + "."*60 + "\n")

    # 1. TRANSLAÇÃO
    # Desloca o cilindro para a direita (+8 em X) e para cima (+5 em Y)
    mat_trans = get_translation_matrix(8, 5, 0)
    apply_and_render(mat_trans, "1. DEPOIS: TRANSLAÇÃO (X=+8, Y=+5)")

    # 2. ESCALA
    # Reduz o tamanho do cilindro pela metade em todos os eixos
    mat_scale = get_scale_matrix(0.5, 0.5, 0.5)
    apply_and_render(mat_scale, "2. DEPOIS: ESCALA (Fator 0.5x)")

    # 3. ROTAÇÃO
    # Gira o cilindro 45 graus no eixo Y
    mat_rot = get_rotation_y_matrix(45)
    apply_and_render(mat_rot, "3. DEPOIS: ROTAÇÃO (45 graus no eixo Y)")

    # 4. CISALHAMENTO
    # Inclina o topo do cilindro para a direita em relação ao eixo Z
    mat_shear = get_shear_xy_matrix(0.5, 0.0)
    apply_and_render(mat_shear, "4. DEPOIS: CISALHAMENTO (Inclinação no eixo X)")

    # 5. REFLEXÃO (BÔNUS)
    # Espelha o objeto invertendo o eixo X
    mat_refl = get_reflection_x_matrix()
    apply_and_render(mat_refl, "5. DEPOIS: REFLEXÃO (Espelhamento no eixo X - Bônus)")