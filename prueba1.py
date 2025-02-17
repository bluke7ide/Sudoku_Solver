class Sudoku:
    def __init__(self):
        # Inicializar el tablero vacío
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.possible =[[[i for i in range(1, 10)] for _ in range(9)] for _ in range(9)]

    def add_number(self, row, col, num):
        # Agregar un número al tablero
        if 0 <= row < 9 and 0 <= col < 9 and 1 <= num <= 9:
            self.board[row][col] = num
            self.eliminarNumPos(row, col, num)

        else:
            raise ValueError("Posición o número inválido")
            
    def verificarPosibles(self, row, col):
        # if self.board[row][col] != 0 | len(self.possible[:][row][col]) == 1:
        #     self.possible[:][row][col] = self.board[row][col]
        #     return
        if self.board[row][col] != 0:
            self.possible[row][col] = [self.board[row][col]]
            return
        columna = [r[col] for r in self.board]
        fila = self.board[row]
        coords = [3*(row//3), 3*(col//3)]
        lim = [3*(row//3+1), 3*(col//3+1)]
        square = [0 for _ in range(9)]
        con = 0
        for i in range(coords[0], lim[0]):
            for j in range(coords[1], lim[1]):
                square[con] = self.board[i][j]
                con += 1
        dados = columna + fila + square
        sincero = [x for x in dados if x != 0]
        unicos = list(set(sincero))
        base = [i for i in range(1, 10)]
        self.possible[row][col] = [x for x in base if x not in unicos]
            
    def eliminarNumPos(self, row, col, num):
        def eliminar(lista, n):
            lista = [x for x in lista if x != n]
            return lista
        coords = [3*(row//3), 3*(col//3)]
        lim = [3*(row//3+1), 3*(col//3+1)]
        for i in range(coords[0], lim[0]):
            for j in range(coords[1], lim[1]):
                self.possible[i][j] = eliminar(self.possible[i][j], num)
        for i in range(9):
            self.possible[row][i] = eliminar(self.possible[row][i], num)
            self.possible[i][col] = eliminar(self.possible[i][col], num)
        self.possible[row][col] = [num]
            
    def verificarTodo(self):
        for i in range(9):
            for j in range(9):
                self.verificarPosibles(i, j)
                
    def rondaMarcado(self):
        change = False
        for i in range(9):
            for j in range(9):
                if (len(self.possible[i][j]) == 1) & (self.board[i][j] == 0):
                    change = True
                    self.board[i][j] = self.possible[i][j][0]
                    self.eliminarNumPos(i, j, self.possible[i][j][0])
        return change
    
    def clearEasy(self):
        cond = True
        while cond:
            cond = self.rondaMarcado()
            
        


a = Sudoku()