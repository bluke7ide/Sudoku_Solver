import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

AZUL_CLARO = "#e0f0ff"
AZUL_MEDIO = "#99ccff"
AZUL_OSCURO = "#336699"
AZUL_OSCURO_DESHABILITADO = "#224466"
NEGRO = "black"
GRIS_CLARO = "#cccccc"
ROJO = "red"

class SudokuCell(tk.Canvas):
    def __init__(self, master, row, col):
        self.cell_size = 80
        super().__init__(master, width=self.cell_size, height=self.cell_size,
                         bg=AZUL_CLARO, highlightthickness=0)
        self.row, self.col = row, col
        self.number = None
        self.notes = set()
        self.selected = False
        self.error = False
        self.error_notes = set()
        self.bind("<Button-1>", self.select_cell)

    def update_display(self):
        self.delete("all")
        s, lw, thw = self.cell_size, 1, 3

        self.create_line(0, 0, s, 0, width=lw, fill=GRIS_CLARO)
        self.create_line(0, s, s, s, width=lw, fill=GRIS_CLARO)
        self.create_line(0, 0, 0, s, width=lw, fill=GRIS_CLARO)
        self.create_line(s, 0, s, s, width=lw, fill=GRIS_CLARO)

        if self.row % 3 == 0:
            self.create_line(0, 0, s, 0, width=thw, fill=NEGRO)
        if self.row % 3 == 2:
            self.create_line(0, s, s, s, width=thw, fill=NEGRO)
        if self.col % 3 == 0:
            self.create_line(0, 0, 0, s, width=thw, fill=NEGRO)
        if self.col % 3 == 2:
            self.create_line(s, 0, s, s, width=thw, fill=NEGRO)

        if self.number is not None:
            fs = max(int(s * 0.3), 8)
            color = ROJO if self.error else AZUL_OSCURO
            self.create_text(s/2, s/2, text=str(self.number),
                             font=("Arial", fs), fill=color)
        else:
            nfs = max(int(s * 0.1), 6)
            for val in self.notes:
                rr, cc = divmod(val-1, 3)
                x = s*0.25 + cc*(s*0.25)
                y = s*0.25 + rr*(s*0.25)
                color = ROJO if val in self.error_notes else AZUL_OSCURO
                self.create_text(x, y, text=str(val),
                                 font=("Arial", nfs), fill=color)

        if self.selected:
            m = s * 0.025
            self.create_rectangle(m, m, s-m, s-m, outline="blue", width=3)

        if self.error:
            self.create_rectangle(0, 0, s, s, outline=ROJO, width=3)

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

    def set_selected(self, sel):
        self.selected = sel
        self.update_display()

    def resize(self, new_size):
        self.cell_size = new_size
        self.config(width=new_size, height=new_size)
        self.update_display()


class SudokuGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku")
        self.configure(bg=AZUL_MEDIO)
        self.geometry("600x775")

        self.history = []
        self.error_focus = False

        self.grid_frame = tk.Frame(self, bg=AZUL_MEDIO)
        self.grid_frame.pack(pady=20)
        self.cells = [
            [SudokuCell(self.grid_frame, r, c) for c in range(9)]
            for r in range(9)
        ]
        for r in range(9):
            for c in range(9):
                self.cells[r][c].grid(row=r, column=c)
                self.cells[r][c].update_display()

        self.selected_cell = None
        self.bind_all('<Key>', self.key_input)
        self.bind_all('<Control-z>', self.undo_last_action)
        self.bind_all('<Up>', lambda e: self.move_selection(-1, 0))
        self.bind_all('<Down>', lambda e: self.move_selection(1, 0))
        self.bind_all('<Left>', lambda e: self.move_selection(0, -1))
        self.bind_all('<Right>', lambda e: self.move_selection(0, 1))

        self.control_frame = tk.Frame(self, bg=AZUL_MEDIO)
        self.control_frame.pack()
        self.mode = "number"
        self.mode_button = tk.Button(
            self.control_frame, text="Num", width=5, height=2, 
            command=self.toggle_mode,
            bg=AZUL_OSCURO, fg="white"
        )
        self.mode_button.pack(side="left", padx=10, pady=10)
        for i in range(1, 10):
            btn = tk.Button(
                self.control_frame, text=str(i), width=4, height=2,
                command=lambda n=i: self.enter_input(n),
                bg=AZUL_OSCURO, fg="white"
            )
            btn.pack(side="left", padx=2)
        self.delete_button = tk.Button(
            self.control_frame, text="Borrar", width=5, height=2,
            command=self.clear_selected_cell,
            bg=AZUL_OSCURO, fg="white"
        )
        self.delete_button.pack(side="left", padx=10)
        
        self.undo_button = tk.Button(
            self.control_frame, text="Undo", width=5, height=2,
            command=self.undo_last_action,
            bg=AZUL_OSCURO_DESHABILITADO, fg="white", state="disabled"
        )
        self.undo_button.pack(side="left", padx=10)

        self.action_frame = tk.Frame(self, bg=AZUL_MEDIO)
        self.action_frame.pack(pady=5)

        self.error_button = tk.Button(
            self.action_frame, text="Enfocar Errores", width=14,
            command=self.toggle_error_focus,
            bg=AZUL_OSCURO, fg="white"
        )
        self.error_button.pack(side="left", padx=5)
        
        self.solution_toggle = tk.Button(
            self, text="", bg=AZUL_MEDIO, relief="flat", command=self.toggle_solution_buttons,
            width=2, height=1, highlightthickness=0, bd=0, activebackground=AZUL_OSCURO
        )
        self.solution_toggle.place(relx=1.0, rely=1.0, anchor="se", x=0, y=0)

        self.solution_frame = tk.Frame(self, bg=AZUL_MEDIO)
        self.solution_visible = False


        for (label, cmd, color) in [
            ("Cargar Partida", self.import_from_excel, AZUL_OSCURO),
            ("Guardar Partida", self.save_to_excel, AZUL_OSCURO),
            ("Limpiar Tablero", self.confirm_clear_board, "red"),
        ]:
            b = tk.Button(self.action_frame, text=label, command=cmd,
                          bg=color, fg="white", width=14, height=1)
            b.pack(side="left", padx=5)

        self.last_cell_size = None
        self.bind("<Configure>", self.on_resize)
        self.update_undo_button_state()

    def update_undo_button_state(self):
        if self.history:
            self.undo_button.config(state="normal", bg=AZUL_OSCURO)
        else:
            self.undo_button.config(state="disabled", bg=AZUL_OSCURO_DESHABILITADO)

    def capture_board_state(self):
        return [
            [(cell.number, set(cell.notes)) for cell in row]
            for row in self.cells
        ]

    def restore_board_state(self, state):
        for i in range(9):
            for j in range(9):
                num, notes = state[i][j]
                cell = self.cells[i][j]
                cell.number = num
                cell.notes = set(notes)
                cell.update_display()
        if self.error_focus:
            self.check_conflicts()
        self.update_undo_button_state()

    def undo_last_action(self, event=None):
        if self.history:
            last = self.history.pop()
            self.restore_board_state(last)

    def on_resize(self, event):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 300 or h < 350: return
        m_w, m_h = 40, 150
        new_size = int(min((w - m_w) / 9, (h - m_h) / 9))
        new_size = max(40, min(new_size, 120))
        if new_size != self.last_cell_size:
            self.last_cell_size = new_size
            for row in self.cells:
                for cell in row:
                    cell.resize(new_size)
                    
    def toggle_solution_buttons(self):
        if self.solution_visible:
            for widget in self.solution_frame.winfo_children():
                widget.destroy()
            self.solution_frame.place_forget()
        else:
            self.solve_button = tk.Button(
                self.solution_frame, text="Resolver Sudoku", bg=AZUL_OSCURO, fg="white",
                command=self.solve_sudoku
            )
            self.solve_button.pack(pady=5)

            self.step_button = tk.Button(
                self.solution_frame, text="Paso a paso", bg=AZUL_OSCURO, fg="white",
                command=self.solve_step_by_step
            )
            self.step_button.pack(pady=5)

            self.solution_frame.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)
        self.solution_visible = not self.solution_visible

    def toggle_mode(self):
        self.mode = "note" if self.mode == "number" else "number"
        self.mode_button.config(text=f"{'Nota' if self.mode == 'note' else 'Num'}")
        self.mode_button.config(bg="#33ccff" if self.mode == "note" else AZUL_OSCURO)

    def toggle_error_focus(self):
        self.error_focus = not self.error_focus
        self.error_button.config(bg=ROJO if self.error_focus else AZUL_OSCURO)
        self.check_conflicts()

    def check_conflicts(self):
        for row in self.cells:
            for cell in row:
                cell.error = False
                cell.error_notes.clear()

        def collect(r, c): return self.cells[r][c].number

        for i in range(9):
            self.mark_duplicates([(i, j) for j in range(9)], [collect(i, j) for j in range(9)])
            self.mark_duplicates([(j, i) for j in range(9)], [collect(j, i) for j in range(9)])

        for bi in range(3):
            for bj in range(3):
                block = []
                vals = []
                for i in range(3):
                    for j in range(3):
                        r, c = bi * 3 + i, bj * 3 + j
                        block.append((r, c))
                        vals.append(collect(r, c))
                self.mark_duplicates(block, vals)

        if self.error_focus:
            for r in range(9):
                for c in range(9):
                    cell = self.cells[r][c]
                    if cell.number is None:
                        for note in list(cell.notes):
                            if self.note_violates(r, c, note):
                                cell.error_notes.add(note)

        for row in self.cells:
            for cell in row:
                cell.update_display()

    def mark_duplicates(self, positions, values):
        seen = {}
        for idx, v in enumerate(values):
            if v is None: continue
            if v in seen:
                r1, c1 = positions[seen[v]]
                r2, c2 = positions[idx]
                self.cells[r1][c1].error = True
                self.cells[r2][c2].error = True
            else:
                seen[v] = idx

    def note_violates(self, row, col, value):
        for i in range(9):
            if self.cells[row][i].number == value: return True
            if self.cells[i][col].number == value: return True
        br, bc = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.cells[br + i][bc + j].number == value: return True
        return False

    def clear_selected_cell(self):
        if self.selected_cell:
            self.history.append(self.capture_board_state())
            self.selected_cell.set_number(None)
            if self.error_focus:
                self.check_conflicts()
            self.update_undo_button_state()

    def confirm_clear_board(self):
        if messagebox.askyesno("Confirmar", "¿Borrar todo el tablero?"):
            self.history.clear()
            for row in self.cells:
                for cell in row:
                    cell.number = None
                    cell.notes.clear()
                    cell.update_display()
            if self.error_focus:
                self.check_conflicts()
            self.update_undo_button_state()

    def set_selected_cell(self, cell):
        if self.selected_cell:
            self.selected_cell.set_selected(False)
        self.selected_cell = cell
        self.selected_cell.set_selected(True)
        self.focus_set()

    def move_selection(self, dr, dc):
        if not self.selected_cell: return
        r, c = self.selected_cell.row, self.selected_cell.col
        nr, nc = r + dr, c + dc
        if 0 <= nr < 9 and 0 <= nc < 9:
            self.set_selected_cell(self.cells[nr][nc])

    def enter_input(self, num):
        if not self.selected_cell: return
        self.history.append(self.capture_board_state())
        if self.mode == "number":
            self.selected_cell.set_number(num)
        else:
            self.selected_cell.toggle_note(num)
        if self.error_focus:
            self.check_conflicts()
        self.update_undo_button_state()

    def key_input(self, event):
        if event.keysym in ('BackSpace', 'Delete'):
            self.clear_selected_cell()
        elif event.char == '0':
            self.toggle_mode()
        elif event.char in '123456789':
            self.enter_input(int(event.char))

    def import_from_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path: return
        try:
            self.history.clear()
            nums = pd.read_excel(path, header=None, sheet_name=0)
            xls = pd.ExcelFile(path)
            has_notes = len(xls.sheet_names) > 1
            notes = pd.read_excel(path, header=None, sheet_name=1) if has_notes else None

            for i in range(9):
                for j in range(9):
                    cell = self.cells[i][j]
                    v = nums.iat[i, j] if i < nums.shape[0] and j < nums.shape[1] else None
                    num = None
                    try:
                        if pd.notna(v):
                            cand = int(float(str(v).strip()))
                            if 1 <= cand <= 9: num = cand
                    except: pass
                    cell.number = num
                    cell.notes.clear()

                    if has_notes and cell.number is None:
                        if i < notes.shape[0] and j < notes.shape[1]:
                            raw = notes.iat[i, j]
                            if pd.notna(raw):
                                for part in str(raw).split(","):
                                    if part.strip().isdigit():
                                        val = int(part.strip())
                                        if 1 <= val <= 9:
                                            cell.notes.add(val)
                    cell.update_display()
            if self.error_focus:
                self.check_conflicts()
            self.update_undo_button_state()
        except Exception as e:
            messagebox.showerror("Error", "No se pudo cargar:\n" + str(e))

    def save_to_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path: return
        try:
            df_nums = pd.DataFrame([[cell.number or 0 for cell in row] for row in self.cells])
            df_notes = pd.DataFrame([[",".join(str(n) for n in cell.notes) for cell in row] for row in self.cells])
            with pd.ExcelWriter(path) as w:
                df_nums.to_excel(w, sheet_name="Numbers", index=False, header=False)
                df_notes.to_excel(w, sheet_name="Notes", index=False, header=False)
            messagebox.showinfo("Guardado", "Partida y notas guardadas.")
        except Exception as e:
            messagebox.showerror("Error", "No se pudo guardar:\n" + str(e))
        
    def initialize_notes(self):
        """
        Para cada celda vacía, calcula sus candidatos (notas)
        eliminando los números ya presentes en su fila, columna y bloque 3×3.
        """
        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                if cell.number is None:
                    # Empiezo con todos los números posibles
                    candidates = set(range(1, 10))
                    # Quito los números de la fila
                    candidates -= {self.cells[r][j].number for j in range(9) if self.cells[r][j].number}
                    # Quito los números de la columna
                    candidates -= {self.cells[i][c].number for i in range(9) if self.cells[i][c].number}
                    # Quito los números del bloque 3×3
                    br, bc = 3*(r//3), 3*(c//3)
                    for i in range(3):
                        for j in range(3):
                            n = self.cells[br+i][bc+j].number
                            if n:
                                candidates.discard(n)
                    cell.notes = candidates
                else:
                    cell.notes.clear()
                cell.update_display()
        
    def fill_obvious_numbers(self):
        def buscar_y_colocar(grupos):
            colocado = False
            for grupo in grupos:
                conteo = {n: [] for n in range(1, 10)}
                for r, c in grupo:
                    cell = self.cells[r][c]
                    if cell.number is None:
                        for n in cell.notes:
                            conteo[n].append((r, c))
                for n, posiciones in conteo.items():
                    if len(posiciones) == 1:
                        r, c = posiciones[0]
                        self.history.append(self.capture_board_state())
                        self.cells[r][c].set_number(n)
                        colocado = True
            return colocado
    
        filas    = [[(i, j) for j in range(9)] for i in range(9)]
        columnas = [[(i, j) for i in range(9)] for j in range(9)]
        bloques  = [[(r + i, c + j) for i in range(3) for j in range(3)]
                    for r in (0, 3, 6) for c in (0, 3, 6)]
    
        changes = any(buscar_y_colocar(g) for g in (filas, columnas, bloques))
    
        if changes and self.error_focus:
            self.check_conflicts()
    
        return changes
    
    def eliminate_notes(self):
        changes = False
        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                if cell.number is not None:
                    num = cell.number
                    # Fila y columna
                    for i in range(9):
                        for peer in (self.cells[r][i], self.cells[i][c]):
                            if peer != cell and num in peer.notes:
                                peer.notes.discard(num)
                                changes = True
                    # Cuadro 3x3
                    br, bc = 3 * (r//3), 3 * (c//3)
                    for i in range(3):
                        for j in range(3):
                            peer = self.cells[br+i][bc+j]
                            if peer != cell and num in peer.notes:
                                peer.notes.discard(num)
                                changes = True
        return changes
    
    def solve_sudoku(self):
        self.history.append(self.capture_board_state())
        while True:
            self.initialize_notes()
            changed = self.fill_obvious_numbers() 
            if not changed:
                changed = self.eliminate_notes() 
                if not changed:
                    break
        if not self.is_solved():
            self.backtrack_solve()
            
    def solve_step_by_step(self):
        self.history.append(self.capture_board_state())
        self.initialize_notes()
        state = self.fill_obvious_numbers()
        if not state:
           self.eliminate_notes() 
    
    def get_all_units(self):
        units = []
        for i in range(9):
            units.append([self.cells[i][j] for j in range(9)])  # filas
            units.append([self.cells[j][i] for j in range(9)])  # columnas
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                units.append([
                    self.cells[r][c]
                    for r in range(br, br+3)
                    for c in range(bc, bc+3)
                ])
        return units
    
    def is_solved(self):
        return all(cell.number is not None for row in self.cells for cell in row)
    
    def backtrack_solve(self):
        # 1. Copiamos el estado actual en un tablero local con None para vacíos
        board = [[cell.number for cell in row] for row in self.cells]
    
        # 2. Función que devuelve el conjunto de posibles números para (r,c)
        def possible(b, r, c):
            if b[r][c] is not None:
                return set()
            vals = set(range(1, 10))
            # quitar fila
            vals -= {b[r][j] for j in range(9) if b[r][j] is not None}
            # quitar columna
            vals -= {b[i][c] for i in range(9) if b[i][c] is not None}
            # quitar bloque 3x3
            br, bc = 3*(r//3), 3*(c//3)
            vals -= {
                b[br+i][bc+j]
                for i in range(3) for j in range(3)
                if b[br+i][bc+j] is not None
            }
            return vals
    
        # 3. Recursión con MRV (Minimum Remaining Values)
        def solve():
            # encontrar todas las celdas vacías
            empties = [(r, c) for r in range(9) for c in range(9) if board[r][c] is None]
            if not empties:
                return True  # todo lleno
            
            # elegir la celda con menos candidatos
            r, c = min(empties, key=lambda rc: len(possible(board, rc[0], rc[1])))
            opts = possible(board, r, c)
            if not opts:
                return False  # sin opciones: backtrack
    
            for n in opts:
                board[r][c] = n
                if solve():
                    return True
                board[r][c] = None  # deshacer
    
            return False
    
        # 4. Lanzar el solver
        if solve():
            # reflejar resultado en la GUI
            for r in range(9):
                for c in range(9):
                    # este set_number actualiza la celda y borra notas
                    self.cells[r][c].set_number(board[r][c])
        else:
            messagebox.showinfo("Sudoku", "No se pudo resolver con backtracking optimizado.")



if __name__ == "__main__":
    app = SudokuGUI()
    app.mainloop()
