import tkinter as tk
from tkinter import messagebox

class SudokuGUI:
    def __init__(self, root, board):
        self.root = root
        self.board = board
        self.entries = [[None]*9 for _ in range(9)]
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack()

        for i in range(9):
            for j in range(9):
                entry = tk.Entry(frame, width=2, font=('Arial', 18), justify='center', bd=1, relief='solid')

                # Añadir borde más grueso en las líneas divisorias de los subcuadrantes
                if i in {0, 3, 6}:
                    entry.grid(row=i, column=j, padx=(2, 0), pady=(2, 0))
                else:
                    entry.grid(row=i, column=j, padx=(0, 0), pady=(0, 0))

                if j in {2, 5, 8}:
                    entry.grid(padx=(0, 2), pady=(0, 0))

                self.entries[i][j] = entry

        btn_submit = tk.Button(self.root, text="Submit", command=self.submit_board)
        btn_submit.pack(pady=10)

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
