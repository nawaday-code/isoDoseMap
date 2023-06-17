
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import os

class App:
    def __init__(self, root):
        self.entries = []
        for i in range(9):
            row = []
            for j in range(9):
                e = tk.Entry(root, width=5)
                e.grid(row=i, column=j)
                row.append(e)
            self.entries.append(row)

        self.fig = Figure(figsize=(5,5))
        self.ax = self.fig.add_subplot(111)

        self.color_maps = ['jet','viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink', 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper']
        self.methods = ['linear', 'cubic', 'nearest']

        self.control_frame = tk.Frame(root)
        self.control_frame.grid(row=9, column=10, sticky='ns')

        color_map_label = tk.Label(self.control_frame, text="Color map")
        color_map_label.pack()
        self.color_map_var = tk.StringVar()
        self.color_map_var.set(self.color_maps[0])
        self.color_map_om = ttk.Combobox(self.control_frame, textvariable=self.color_map_var, values=self.color_maps, state='readonly')
        self.color_map_om.pack()

        method_label = tk.Label(self.control_frame, text="Interpolation method")
        method_label.pack()
        self.method_var = tk.StringVar()
        self.method_var.set(self.methods[0])
        self.method_om = ttk.Combobox(self.control_frame, textvariable=self.method_var, values=self.methods, state='readonly')
        self.method_om.pack()

        preview_button = tk.Button(self.control_frame, text="Preview Contour", command=self.preview_contour)
        preview_button.pack()

        save_button = tk.Button(self.control_frame, text="Save Preview", command=self.save_preview)
        save_button.pack()

        self.canvas = FigureCanvasTkAgg(self.fig, root)  
        self.canvas.get_tk_widget().grid(row=0, column=10, rowspan=9)

    def get_data_from_entries(self):
        data = []
        for row in self.entries:
            row_data = []
            for e in row:
                val = e.get()
                if val == "":
                    val = "―"
                row_data.append(val)
            data.append(row_data)
        return data

    def preview_contour(self):
        data = self.get_data_from_entries()
        matrix, minN, maxN = self.create_matrix(data)

        self.generate_contour(matrix, minN, maxN)
        self.canvas.draw()

    def save_preview(self):
        filepath = filedialog.asksaveasfilename(defaultextension='.png')
        if not filepath:
            return
        self.fig.savefig(filepath)

    def create_matrix(self, input_data):
        matrix = [[None] * 9 for _ in range(9)]
        minN = np.inf 
        maxN = -np.inf
        for row, input_row in enumerate(input_data):
            for col, value in enumerate(input_row):
                if (row, col) in [(4, 4), (4, 5), (4, 6)]:
                    matrix[8-row][col] = None
                elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
                    matrix[8-row][col] = float(value)
                    if float(value) > maxN:
                        maxN = float(value)
                    if float(value) < minN:
                        minN = float(value)
                elif not isinstance(value, (int, float)):
                    matrix[8-row][col] = 0
        return matrix, minN, maxN

    def generate_contour(self, matrix, minN, maxN):
        self.ax.clear()
        color_map = plt.get_cmap(self.color_map_om.get())
        interplolate_method = self.method_om.get()
        lineNum = 100

        data = np.array(matrix, dtype=np.float64)

        x = np.linspace(0, 8 * 0.5, 9)
        y = np.linspace(0, 8 * 0.5, 9)
        X, Y = np.meshgrid(x, y)

        xy_data = np.vstack([X.ravel(), Y.ravel()]).T
        z_data = data.ravel()

        valid_indices = ~np.isnan(z_data)
        xy_valid = xy_data[valid_indices]
        z_valid = z_data[valid_indices]

        x_grid, y_grid = np.mgrid[0:4:100j, 0:4:100j]
        xy_grid = np.vstack([x_grid.ravel(), y_grid.ravel()]).T
        z_grid = griddata(xy_valid, z_valid, xy_grid, method=interplolate_method).reshape(x_grid.shape)

        center_indices = [(y, x) for y in range(49, 52) for x in range(49, 52)]
        for index in center_indices:
            z_grid[index] = z_valid.max()

        zmin = z_grid.min()
        zmax = z_grid.max()

        self.ax.contourf(x_grid, y_grid, z_grid, cmap=color_map, vmin=zmin, vmax=maxN*1.3, levels=np.linspace(zmin, maxN*1.3, lineNum))
        self.ax.scatter(xy_valid[:, 0], xy_valid[:, 1], c=z_valid, s=50, cmap="viridis", edgecolors="k", alpha=0.5)
        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_title("Interpolated Contour Map (Preview, Measured in μSv/h)")

root = tk.Tk()
app = App(root)
root.mainloop()