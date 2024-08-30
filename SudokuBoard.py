class SudokuBoard:
    def __init__(self):
        # Inicializar el tablero vacío
        self.board = [[0]*9 for _ in range(9)]

    def add_number(self, row, col, number):
        # Agregar un número al tablero
        if 0 <= row < 9 and 0 <= col < 9 and 1 <= number <= 9:
            self.board[row][col] = number
        else:
            raise ValueError("Posición o número inválido")

    def is_valid(self):
        # Verificar si el tablero es válido
        def is_valid_group(group):
            group = [num for num in group if num != 0]
            return len(group) == len(set(group))
        
        # Verificar filas y columnas
        for i in range(9):
            if not is_valid_group(self.board[i]) or not is_valid_group([self.board[j][i] for j in range(9)]):
                return False

        # Verificar subcuadrículas de 3x3
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                block = [self.board[r][c] for r in range(i, i+3) for c in range(j, j+3)]
                if not is_valid_group(block):
                    return False
        
        return True





