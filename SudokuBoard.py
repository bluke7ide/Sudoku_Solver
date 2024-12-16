import numpy as np
class SudokuCell:
    def __init__(self, row, col):
        # Inicializar la celda
        self.coords = [row, col]
        self.posible = [1,2,3,4,5,6,7,8,9]
        
class SudokuBoard:
    def __init__(self):
        # Inicializar el tablero vacío
        self.board = [[0]*9 for _ in range(9)]
        self.cells = [[0]*9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                self.cells[i][j] = SudokuCell(i,j)

    def add_number(self, row, col, number):
        # Agregar un número al tablero
        if 0 <= row < 9 and 0 <= col < 9 and 1 <= number <= 9:
            self.board[row][col] = number
        else:
            raise ValueError("Posición o número inválido")
            
    def verificarPosibles(self, row, col):
        marcados = []
        columna = [r[col] for r in self.board]
        fila = self.board[row]
        coords = [3*(row%3), 3*(col%3)]
        square = [[0]*9]
        lim = [3*(row%3+1), 3*(col%3+1)]
        con = 0
        for i in range(coords[1], lim[1]):
            for j in range(coords[2], lim[2]):
                square[con] = self.board[i][j]
                con += 1
        dados = columna + fila + square
        dados = np.unique(dados)
        dados.remove(0)
        self.cells[coords[1]][coords[2]].posible = marcados
        


