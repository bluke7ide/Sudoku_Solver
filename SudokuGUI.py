import tkinter as tk
from tkinter import messagebox

class SudokuGUI:
    def __init__(self, root, board):
        self.root = root
        self.board = board
        self.entries = [[None]*9 for _ in range(9)]
        self.create_widgets()

    def create_widgets(self):
        canvas = tk.Canvas(self.root, width=450, height=450, bg="white")
        canvas.pack()

        # Dibujar las líneas divisorias del tablero
        self.draw_board(canvas)

        # Crear las entradas de texto
        for i in range(9):
            for j in range(9):
                entry = tk.Entry(self.root, width=1, font=('Arial', 18), justify='center', bd=1, relief='solid')
                entry_window = canvas.create_window(50 * j + 25, 50 * i + 25, window=entry, width=49, height=49)
                self.entries[i][j] = entry

        
        self.root.title("Sudoku")
        menu = tk.Menu(self.root)
        self.root.config(menu = menu)

        file = tk.Menu(menu)
        menu.add_cascade(label = 'File', menu = file)
        file.add_command(label = 'Submit', command = self.submit_board)

    def draw_board(self, canvas):
        cell_size = 50

        for i in range(9):
            width = 5 if i % 3 == 0 else 1
            color = "blue" if i % 3 == 0 else "gray"
            # Líneas horizontales
            canvas.create_line(0, i * cell_size, 450, i * cell_size, fill=color, width=width)
            # Líneas verticales
            canvas.create_line(i * cell_size, 0, i * cell_size, 450, fill=color, width=width)

    def submit_board(self):
        for i in range(9):
            for j in range(9):
                try:
                    value = int(self.entries[i][j].get())
                    self.board.add_number(i, j, value)
                except ValueError:
                    continue  # Ignorar celdas vacías o valores no numéricos
        
        if self.board.is_valid():
            messagebox.showinfo("Sudoku", "¡Tablero válido!")
        else:
            messagebox.showerror("Sudoku", "Tablero inválido. Revisa tus números.")
            
