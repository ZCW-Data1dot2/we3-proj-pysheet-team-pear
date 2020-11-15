#!/usr/bin/env python
import tkinter as tk
import math
import re
from collections import ChainMap

Nrows = 5
Ncols = 5

cellre = re.compile(r'\b[A-Z][0-9]\b')


def cellname(col, row):
    # returns a string translates col 0, row 0 to 'A1'
    # uses ascii to find letter equivalent to number
    return chr(ord('A') + col) + str(row + 1)


class Cell():
    def __init__(self, row, col, siblings, parent):
        #make instance variables from arguments
        self.row = row
        self.col = col
        self.name = cellname(col, row)
        self.siblings = siblings
        self.parent = parent

        self.value = 0
        self.formula = str(self.value)

        #make set of dependencies and requirements
        self.dependencies = set()
        self.requirements = set()

        # be happy you get this machinery for free.
        self.var = tk.StringVar()
        entry = self.widget = tk.Entry(parent,
                                       textvariable=self.var,
                                       justify='right')
        entry.bind('<FocusIn>', self.edit)
        entry.bind('<FocusOut>', self.update)
        entry.bind('<Return>', self.update)
        entry.bind('<Up>', self.move(-1, 0))
        entry.bind('<Down>', self.move(+1, 0))
        entry.bind('<Left>', self.move(0, -1))
        entry.bind('<Right>', self.move(0, 1))

        # set this cell's var to cell's value
        # and you're done.
        self.var.set(self.value)

    def move(self, rowadvance, coladvance):
        targetrow = (self.row + rowadvance) % Nrows
        targetcol = (self.col + coladvance) % Ncols

        def focus(event):
            targetwidget = self.siblings[cellname(targetrow, targetcol)].widget
            targetwidget.focus()

        return focus

    def calculate(self):
        # find all the cells mentioned in the formula.
        #  put them all into a tmp set currentreqs
        currentreqs = set(cellre.findall(self.formula))
        # Add this cell to the new requirement's dependents
        # removing all the reqs that we might no longer need
        for each in currentreqs - self.requirements:
            self.siblings[each].dependencies.add(self.name)
        # Add remove this cell from dependents no longer referenced
        for each in self.requirements - currentreqs:
            self.siblings[each].dependencies.remove(self.name)
        #
        # Look up the values of our required cells
        # reqvalues = a comprehension of r,
        reqvalues = {self.siblings[r].value for r in currentreqs}
        # Build an environment with these values and basic math functions

        environment = ChainMap(math.__dict__, reqvalues)
        # Note that eval is DANGEROUS and should not be used in production
        self.value = eval(self.formula, {}, environment)

        # save currentreqs in self.reqs
        self.requirements = currentreqs
        # set this cell's var to cell's value
        self.var.set(self.value)

    def propagate(self):
        for each in self.depenencies:
            self.siblings[each].calculate()
            self.siblings[each].propogate()

    def edit(self,event):
        #"clicking" on the cell, displays formula instead of value for editing
        self.var.set(self.formula)
        self.widget.select_range(0, tk.END)

    def update(self, event):
        
        # get the value of this cell and put it in formula
        # calculate all dependencies
        # propogate to all dependecnies
        self.formula = str(self.var.get())
        self.calculate()
        self.propagate()
        # If this was after pressing Return, keep showing the formula
        if hasattr(event, 'keysym') and event.keysym == "Return":
            self.var.set(self.formula)

    def save(self, filename):
        pass

    def load(self, filename):
        pass


class SpreadSheet(tk.Frame):
    def __init__(self, rows=5, cols=5, master=None):
        super().__init__(master)
        self.rows = rows
        self.cols = cols
        self.cells = {}

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # Frame for all the cells
        self.cellframe = tk.Frame(self)
        self.cellframe.pack(side='top')

        # Column labels
        blank = tk.Label(self.cellframe)
        blank.grid(row=0, column=0)
        for j in range(self.cols):
            label = tk.Label(self.cellframe, text=chr(ord('A') + j))
            label.grid(row=0, column=j + 1)

        # Fill in the rows
        for i in range(self.rows):
            rowlabel = tk.Label(self.cellframe, text=str(i + 1))
            rowlabel.grid(row=1 + i, column=0)
            for j in range(self.cols):
                cell = Cell(i, j, self.cells, self.cellframe)
                self.cells[cell.name] = cell
                cell.widget.grid(row=1 + i, column=1 + j)


root = tk.Tk()
app = SpreadSheet(Nrows, Ncols, master=root)
app.mainloop()
