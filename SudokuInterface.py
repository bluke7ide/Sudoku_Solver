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
        self.cell_size = 80
        super().__init__(master, width=self.cell_size, height=self.cell_size,
                         bg=AZUL_CLARO, highlightthickness=0)
        self.row, self.col = row, col
        self.number = None
        self.notes = set()
        self.selected = False
        self.bind("<Button-1>", self.select_cell)

    def update_display(self):
        self.delete("all")
        s, lw, thw = self.cell_size, 1, 3

        # líneas internas
        self.create_line(0, 0, s, 0, width=lw, fill=GRIS_CLARO)
        self.create_line(0, s, s, s, width=lw, fill=GRIS_CLARO)
        self.create_line(0, 0, 0, s, width=lw, fill=GRIS_CLARO)
        self.create_line(s, 0, s, s, width=lw, fill=GRIS_CLARO)

        # líneas gruesas 3×3
        if self.row % 3 == 0:
            self.create_line(0, 0, s, 0, width=thw, fill=NEGRO)
        if self.row % 3 == 2:
            self.create_line(0, s, s, s, width=thw, fill=NEGRO)
        if self.col % 3 == 0:
            self.create_line(0, 0, 0, s, width=thw, fill=NEGRO)
        if self.col % 3 == 2:
            self.create_line(s, 0, s, s, width=thw, fill=NEGRO)

        # número o notas
        if self.number is not None:
            fs = max(int(s * 0.3), 8)
            self.create_text(s/2, s/2, text=str(self.number),
                             font=("Arial", fs), fill=AZUL_OSCURO)
        else:
            nfs = max(int(s * 0.1), 6)
            for val in self.notes:
                rr, cc = divmod(val-1, 3)
                x = s*0.25 + cc*(s*0.25)
                y = s*0.25 + rr*(s*0.25)
                self.create_text(x, y, text=str(val),
                                 font=("Arial", nfs), fill=AZUL_OSCURO)

        # selección
        if self.selected:
            m = s * 0.025
            self.create_rectangle(m, m, s-m, s-m, outline="blue", width=3)

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
        self.geometry("600x750")

        # tablero
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

        # selección + teclado
        self.selected_cell = None
        self.bind_all('<Key>', self.key_input)
        self.bind_all('<Up>',    lambda e: self.move_selection(-1, 0))
        self.bind_all('<Down>',  lambda e: self.move_selection(1, 0))
        self.bind_all('<Left>',  lambda e: self.move_selection(0, -1))
        self.bind_all('<Right>', lambda e: self.move_selection(0, 1))

        # controles número/nota
        self.control_frame = tk.Frame(self, bg=AZUL_MEDIO)
        self.control_frame.pack()
        self.mode = "number"
        self.mode_button = tk.Button(
            self.control_frame, text="Modo: Número", command=self.toggle_mode,
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

        # botones acción
        self.action_frame = tk.Frame(self, bg=AZUL_MEDIO)
        self.action_frame.pack(pady=10)
        for btn in (
            ("Cargar Partida", self.import_from_excel),
            ("Guardar Partida", self.save_to_excel),
            ("Limpiar Tablero", self.confirm_clear_board)
        ):
            b = tk.Button(self.action_frame, text=btn[0], command=btn[1],
                          bg=(AZUL_OSCURO if btn[0]!="Limpiar Tablero" else "red"),
                          fg="white", width=12, height=1)
            b.pack(side="left", padx=5)

        # engranaje y soluciones
        self.solution_toggle = tk.Button(
            self, text="", bg=AZUL_MEDIO, relief="flat",
            command=self.toggle_solution_buttons,
            width=2, height=1, highlightthickness=0, bd=0,
            activebackground=AZUL_OSCURO
        )
        self.solution_toggle.place(relx=1.0, rely=1.0, anchor="se")
        self.solution_frame = tk.Frame(self, bg=AZUL_MEDIO)
        self.solution_visible = False

        # redimensionado
        self.last_cell_size = None
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 300 or h < 350: return
        m_w, m_h = 40, 150
        new_size = int(min((w-m_w)/9, (h-m_h)/9))
        new_size = max(40, min(new_size, 120))
        if new_size != self.last_cell_size:
            self.last_cell_size = new_size
            for row in self.cells:
                for cell in row:
                    cell.resize(new_size)

    def toggle_solution_buttons(self):
        if self.solution_visible:
            for w in self.solution_frame.winfo_children(): w.destroy()
            self.solution_frame.place_forget()
        else:
            tk.Button(self.solution_frame, text="Resolver Sudoku", bg=AZUL_OSCURO,
                      fg="white", command=self.solve_sudoku).pack(pady=5)
            tk.Button(self.solution_frame, text="Paso a paso", bg=AZUL_OSCURO,
                      fg="white", command=self.solve_step_by_step).pack(pady=5)
            self.solution_frame.place(relx=0, rely=1, anchor="sw", x=10, y=-10)
        self.solution_visible = not self.solution_visible

    def clear_selected_cell(self):
        if self.selected_cell: self.selected_cell.set_number(None)

    def confirm_clear_board(self):
        if messagebox.askyesno("Confirmar", "¿Borrar todo el tablero?"):
            for row in self.cells:
                for cell in row:
                    cell.number = None
                    cell.notes.clear()
                    cell.update_display()

    def set_selected_cell(self, c):
        if self.selected_cell: self.selected_cell.set_selected(False)
        self.selected_cell = c
        self.selected_cell.set_selected(True)
        self.focus_set()

    def move_selection(self, dr, dc):
        if not self.selected_cell: return
        r, c = self.selected_cell.row, self.selected_cell.col
        nr, nc = r + dr, c + dc
        if 0 <= nr < 9 and 0 <= nc < 9:
            self.set_selected_cell(self.cells[nr][nc])

    def toggle_mode(self):
        self.mode = "note" if self.mode=="number" else "number"
        self.mode_button.config(text=f"Modo: {'Nota' if self.mode=='note' else 'Número'}")

    def enter_input(self, num):
        if not self.selected_cell: return
        if self.mode=="number": self.selected_cell.set_number(num)
        else: self.selected_cell.toggle_note(num)

    def key_input(self, event):
        if event.keysym in ('BackSpace','Delete'): self.clear_selected_cell()
        elif event.char in '123456789': self.enter_input(int(event.char))

    def get_grid_as_matrix(self):
        return [[cell.number or 0 for cell in row] for row in self.cells]

    def solve_sudoku(self): pass
    def solve_step_by_step(self): pass

    def import_from_excel(self):
        path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path:
            return
        try:
            nums = pd.read_excel(path, header=None, sheet_name=0)
            xls = pd.ExcelFile(path)
            has_notes = len(xls.sheet_names) > 1
            notes = pd.read_excel(path, header=None, sheet_name=1) if has_notes else None
    
            for i in range(9):
                for j in range(9):
                    cell = self.cells[i][j]
    
                    # Cargar número
                    v = nums.iat[i, j] if i < nums.shape[0] and j < nums.shape[1] else None
                    num = None
                    try:
                        if pd.notna(v):
                            num_candidate = int(float(str(v).strip()))
                            if 1 <= num_candidate <= 9:
                                num = num_candidate
                    except Exception:
                        pass
                    cell.number = num
                    cell.notes.clear()
    
                    # Cargar notas solo si no hay número
                    if has_notes and cell.number is None:
                        try:
                            raw_note = notes.iat[i, j] if i < notes.shape[0] and j < notes.shape[1] else None
                            if pd.notna(raw_note):
                                txt = str(raw_note)
                                for part in txt.split(","):
                                    if part.strip().isdigit():
                                        val = int(part.strip())
                                        if 1 <= val <= 9:
                                            cell.notes.add(val)
                        except Exception:
                            pass
    
                    cell.update_display()
        except Exception as e:
            messagebox.showerror("Error", "No se pudo cargar:\n" + str(e))



    def save_to_excel(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files","*.xlsx *.xls")])
        if not path: return
        try:
            df_nums = pd.DataFrame(self.get_grid_as_matrix())
            df_notes = pd.DataFrame([
                [",".join(str(n) for n in cell.notes) for cell in row]
                for row in self.cells
            ])
            with pd.ExcelWriter(path) as writer:
                df_nums.to_excel(writer, sheet_name="Numbers", index=False, header=False)
                df_notes.to_excel(writer, sheet_name="Notes", index=False, header=False)
            messagebox.showinfo("Guardado","Partida y notas guardadas.")
        except Exception as e:
            messagebox.showerror("Error","No se pudo guardar:\n"+str(e))


if __name__ == "__main__":
    app = SudokuGUI()
    app.mainloop()
