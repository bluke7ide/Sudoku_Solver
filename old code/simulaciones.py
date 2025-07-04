import time
import random
import copy

# Dificultades y celdas reveladas
DIFFICULTY_REVEALED = {
    'Fácil': 38,
    'Medio': 30,
    'Difícil': 23,
    'Máximo': 17
}

def is_valid_move(board, r, c, n):
    """
    Verifica si un número `n` se puede colocar en la posición (r, c)
    sin violar las reglas del Sudoku.
    """
    for i in range(9):
        if board[r][i] == n or board[i][c] == n:
            return False
    br, bc = 3*(r//3), 3*(c//3)
    for i in range(3):
        for j in range(3):
            if board[br+i][bc+j] == n:
                return False
    return True

def fill_board(board):
    """
    Rellena completamente el tablero usando backtracking.
    
    Args:
        board (list): Matriz 9x9 con None para celdas vacías.

    Returns:
        bool: True si se pudo llenar, False si no hay solución.
    """
    for r in range(9):
        for c in range(9):
            if board[r][c] is None:
                nums = list(range(1,10))
                random.shuffle(nums)
                for n in nums:
                    if is_valid_move(board, r, c, n):
                        board[r][c] = n
                        if fill_board(board):
                            return True
                        board[r][c] = None
                return False
    return True

def generate_puzzle(revealed_count):
    """
    Genera un tablero de Sudoku con una cantidad específica de celdas reveladas.

    Args:
        revealed_count (int): Número de celdas visibles en el tablero.

    Returns:
        list: Tablero 9x9 parcialmente lleno.
    """
    board = [[None]*9 for _ in range(9)]
    fill_board(board)
    revealed = set()
    while len(revealed) < revealed_count:
        revealed.add((random.randint(0,8), random.randint(0,8)))
    return [
        [board[r][c] if (r,c) in revealed else None for c in range(9)]
        for r in range(9)
    ]

def solver_backtrack(board):
    """
    Resuelve un tablero de Sudoku usando backtracking puro.

    Args:
        board (list): Tablero 9x9 a resolver (modificado in-place).
    """
    def solve():
        for r in range(9):
            for c in range(9):
                if board[r][c] is None:
                    for n in range(1,10):
                        if is_valid_move(board, r, c, n):
                            board[r][c] = n
                            if solve():
                                return True
                            board[r][c] = None
                    return False
        return True
    solve()

def solver_hybrid(board):
    """
    Resuelve un tablero de Sudoku usando una estrategia híbrida:
    inicializa notas, coloca obvios, elimina candidatos y finalmente aplica backtracking MRV.

    Args:
        board (list): Tablero 9x9 a resolver (modificado in-place).
    """
    notes = [[set() for _ in range(9)] for _ in range(9)]

    def init_notes():
        """Inicializa notas posibles para cada celda vacía."""
        for r in range(9):
            for c in range(9):
                if board[r][c] is None:
                    used = set()
                    for i in range(9):
                        if board[r][i]: used.add(board[r][i])
                        if board[i][c]: used.add(board[i][c])
                    br, bc = 3*(r//3), 3*(c//3)
                    for i in range(3):
                        for j in range(3):
                            if board[br+i][bc+j]:
                                used.add(board[br+i][bc+j])
                    notes[r][c] = set(range(1,10)) - used
                else:
                    notes[r][c].clear()

    def fill_obvious():
        """
        Coloca automáticamente números que sólo tienen una posible ubicación en su grupo.

        Returns:
            bool: True si se colocó algún número.
        """
        placed = False
        groups = (
            [[(r, c) for c in range(9)] for r in range(9)] +
            [[(r, c) for r in range(9)] for c in range(9)] +
            [[(br+i, bc+j) for i in range(3) for j in range(3)]
             for br in (0,3,6) for bc in (0,3,6)]
        )
        for group in groups:
            cnt = {n: [] for n in range(1,10)}
            for r, c in group:
                if board[r][c] is None:
                    for n in notes[r][c]:
                        cnt[n].append((r,c))
            for n, positions in cnt.items():
                if len(positions) == 1:
                    pr, pc = positions[0]
                    board[pr][pc] = n
                    placed = True
        return placed

    def eliminate_notes():
        """
        Elimina candidatos de notas según los números ya colocados.

        Returns:
            bool: True si se modificaron notas.
        """
        changed = False
        for r in range(9):
            for c in range(9):
                if board[r][c]:
                    n = board[r][c]
                    for i in range(9):
                        changed |= (n in notes[r][i] and (notes[r][i].discard(n) or True))
                        changed |= (n in notes[i][c] and (notes[i][c].discard(n) or True))
                    br, bc = 3*(r//3), 3*(c//3)
                    for i in range(3):
                        for j in range(3):
                            changed |= (n in notes[br+i][bc+j] and (notes[br+i][bc+j].discard(n) or True))
        return changed

    def backtrack():
        """Aplica backtracking utilizando MRV (mínimos valores restantes)."""
        empties = [(r,c) for r in range(9) for c in range(9) if board[r][c] is None]
        if not empties:
            return True
        r, c = min(empties, key=lambda rc: len(notes[rc[0]][rc[1]]))
        opts = list(notes[r][c])
        for n in opts:
            if all(board[r][j] != n for j in range(9)) and all(board[i][c] != n for i in range(9)):
                br, bc = 3*(r//3), 3*(c//3)
                if all(board[br+i][bc+j] != n for i in range(3) for j in range(3)):
                    board[r][c] = n
                    saved = [row.copy() for row in notes]
                    eliminate_notes()
                    if backtrack():
                        return True
                    board[r][c] = None
                    notes[:] = [row.copy() for row in saved]
        return False

    # Ciclo de deducción lógica
    init_notes()
    while True:
        if fill_obvious():
            init_notes()
            continue
        if eliminate_notes():
            init_notes()
            continue
        break

    # Fallback final: backtracking MRV
    backtrack()


# Benchmark
results = {d: {'backtrack': [], 'with_notes': []} for d in DIFFICULTY_REVEALED}

for diff_name, revealed in DIFFICULTY_REVEALED.items():
    for _ in range(100):
        puzzle = generate_puzzle(revealed)

        b1 = copy.deepcopy(puzzle)
        t0 = time.perf_counter()
        solver_backtrack(b1)
        results[diff_name]['backtrack'].append(time.perf_counter() - t0)

        b2 = copy.deepcopy(puzzle)
        t1 = time.perf_counter()
        solver_hybrid(b2)
        results[diff_name]['with_notes'].append(time.perf_counter() - t1)

# Mostrar promedios de tiempo
for diff_name in DIFFICULTY_REVEALED:
    bt_avg = sum(results[diff_name]['backtrack']) / 100
    hn_avg = sum(results[diff_name]['with_notes']) / 100
    print(f"{diff_name}: Backtrack = {bt_avg:.4f}s, Con Notas = {hn_avg:.4f}s")
