import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

AZUL_CLARO = "#e0f0ff"
AZUL_MEDIO = "#99ccff"
AZUL_OSCURO = "#336699"
NEGRO = "black"
GRIS_CLARO = "#cccccc"

class SudokuCell(tk.Canvas):
    def __init__(self, master, row, col):
        super().__init__(master, width=80, height=80, bg=AZUL_CLARO, highlightthickness=0)
        self.row, self.col = row, col
        self.number = None
        self.notes = set()
        self.mode = "number"
        self.selected = False
        self.bind("<Button-1>", self.select_cell)

    def set_mode(self, mode):
        self.mode = mode

    def update_display(self):
        self.delete("all")
        self.create_line(0, 0, 80, 0, width=1, fill=GRIS_CLARO)
        self.create_line(0, 80, 80, 80, width=1, fill=GRIS_CLARO)
        self.create_line(0, 0, 0, 80, width=1, fill=GRIS_CLARO)
        self.create_line(80, 0, 80, 80, width=1, fill=GRIS_CLARO)

        if self.row % 3 == 0:
            self.create_line(0, 0, 80, 0, width=3, fill=NEGRO)
        if self.row % 3 == 2:
            self.create_line(0, 80, 80, 80, width=3, fill=NEGRO)
        if self.col % 3 == 0:
            self.create_line(0, 0, 0, 80, width=3, fill=NEGRO)
        if self.col % 3 == 2:
            self.create_line(80, 0, 80, 80, width=3, fill=NEGRO)

        if self.number is not None:
            self.create_text(40, 40, text=str(self.number), font=("Arial", 24), fill=AZUL_OSCURO)
        else:
            for val in range(1, 10):
                if val in self.notes:
                    row = (val - 1) // 3
                    col = (val - 1) % 3
                    x = 20 + col * 20
                    y = 20 + row * 20
                    self.create_text(x, y, text=str(val), font=("Arial", 8), fill=AZUL_OSCURO)

        if self.selected:
            self.create_rectangle(2, 2, 78, 78, outline="blue", width=3)

    def select_cell(self, event=None):
        self.master.master.set_selected_cell(self)

    def set_number(self, num):
        self.number = num
        self.notes.clear()
        self.update_display()

    def toggle_note(self, num):
        if num in self.notes:
            self.notes.remove(num)
        else:
            self.notes.add(num)
        self.update_display()

    def set_selected(self, selected):
        self.selected = selected
        self.update_display()

class SudokuGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku")
        self.configure(bg=AZUL_MEDIO)
        self.geometry("800x900")

        self.grid_frame = tk.Frame(self, bg=AZUL_MEDIO)
        self.grid_frame.pack(pady=20)

        self.cells = [[SudokuCell(self.grid_frame, r, c) for c in range(9)] for r in range(9)]
        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                cell.grid(row=r, column=c)
                cell.update_display()

        self.selected_cell = None
        self.bind_all('<Key>', self.key_input)
        self.bind_all('<Up>', lambda e: self.move_selection(-1, 0))
        self.bind_all('<Down>', lambda e: self.move_selection(1, 0))
        self.bind_all('<Left>', lambda e: self.move_selection(0, -1))
        self.bind_all('<Right>', lambda e: self.move_selection(0, 1))

        self.control_frame = tk.Frame(self, bg=AZUL_MEDIO)
        self.control_frame.pack()

        self.mode = "number"
        self.mode_button = tk.Button(
            self.control_frame, text="Modo: Número",
            command=self.toggle_mode, bg=AZUL_OSCURO, fg="white"
        )
        self.mode_button.pack(side="left", padx=10, pady=10)

        for i in range(1, 10):
            btn = tk.Button(
                self.control_frame, text=str(i), width=4, height=2,
                command=lambda n=i: self.enter_input(n), bg=AZUL_OSCURO, fg="white"
            )
            btn.pack(side="left", padx=2)

        self.action_frame = tk.Frame(self, bg=AZUL_MEDIO)
        self.action_frame.pack(pady=10)

        self.solve_button = tk.Button(
            self.action_frame, text="Resolver Sudoku",
            bg=AZUL_OSCURO, fg="white", command=self.solve_sudoku
        )
        self.solve_button.pack(side="left", padx=10)

        self.step_button = tk.Button(
            self.action_frame, text="Paso a paso",
            bg=AZUL_OSCURO, fg="white", command=self.solve_step_by_step
        )
        self.step_button.pack(side="left", padx=10)

        self.import_button = tk.Button(
            self.action_frame, text="Importar Excel",
            bg=AZUL_OSCURO, fg="white", command=self.import_from_excel
        )
        self.import_button.pack(side="left", padx=10)

        self.clear_button = tk.Button(
            self.action_frame, text="Limpiar Tablero",
            bg="red", fg="white", command=self.confirm_clear_board
        )
        self.clear_button.pack(side="left", padx=10)

    def confirm_clear_board(self):
        confirm = messagebox.askyesno("Confirmar", "¿Seguro que deseas borrar todo el tablero?")
        if confirm:
            for row in self.cells:
                for cell in row:
                    cell.set_number(None)

    def set_selected_cell(self, cell):
        if self.selected_cell:
            self.selected_cell.set_selected(False)
        self.selected_cell = cell
        self.selected_cell.set_selected(True)
        self.focus_set()

    def move_selection(self, dr, dc):
        if self.selected_cell:
            r, c = self.selected_cell.row, self.selected_cell.col
            nr, nc = (r + dr) % 9, (c + dc) % 9
            self.set_selected_cell(self.cells[nr][nc])

    def toggle_mode(self):
        self.mode = "note" if self.mode == "number" else "number"
        self.mode_button.config(
            text=f"Modo: {'Nota' if self.mode == 'note' else 'Número'}"
        )

    def enter_input(self, num):
        if self.selected_cell:
            if self.mode == "number":
                self.selected_cell.set_number(num)
            else:
                self.selected_cell.toggle_note(num)

    def key_input(self, event):
        if event.keysym in ('BackSpace', 'Delete'):
            if self.selected_cell:
                self.selected_cell.set_number(None)
        elif event.char in '123456789':
            if self.selected_cell:
                if self.mode == "number":
                    self.selected_cell.set_number(int(event.char))
                else:
                    self.selected_cell.toggle_note(int(event.char))

    def get_grid_as_matrix(self):
        return [[cell.number if cell.number is not None else 0 for cell in row] for row in self.cells]

    def solve_sudoku(self):
        pass  # <-- AQUÍ VA TU SOLVER COMPLETO

    def solve_step_by_step(self):
        pass  # <-- AQUÍ VA TU SOLVER PASO A PASO

    def import_from_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path:
            return
        try:
            df = pd.read_excel(path, header=None)
            if df.shape != (9, 9):
                raise ValueError("El archivo debe ser de 9x9.")
            for i in range(9):
                for j in range(9):
                    val = df.iat[i, j]
                    if pd.notna(val) and isinstance(val, (int, float)) and 1 <= int(val) <= 9:
                        self.cells[i][j].set_number(int(val))
                    else:
                        self.cells[i][j].set_number(None)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

if __name__ == "__main__":
    app = SudokuGUI()
    app.mainloop()
