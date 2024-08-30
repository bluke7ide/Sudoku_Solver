from SudokuBoard import SudokuBoard
from SudokuGUI import SudokuGUI
import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Sudoku")
    board = SudokuBoard()
    SudokuGUI(root, board)
    root.mainloop()

if __name__ == "__main__":
    main()
