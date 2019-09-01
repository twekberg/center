#!/usr/bin/env python

import tkinter as tk
root = tk.Tk()      
canvas = tk.Canvas(root, width = 300, height = 500)      
canvas.pack()      
img = tk.PhotoImage(file="ball.gif")      
canvas.create_image(20,20, anchor=tk.NW, image=img)      
tk.mainloop()
