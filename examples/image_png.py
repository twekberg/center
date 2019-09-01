#!/usr/bin/env python
"""
Display a png file and report the mouse position on a mouse click.
"""

import tkinter as tk

margin_x = 20
margin_y = 20

root = tk.Tk()      
canvas = tk.Canvas(root, width = 600, height = 400)      
canvas.pack()      
img = tk.PhotoImage(file="ball.png")      
canvas.create_image(margin_x, margin_y, anchor=tk.NW, image=img)      

def callback(event):  
    x = event.x - margin_x
    y = event.y - margin_y
    if x >= 0 and y >= 0:
        print("clicked at: ", x, y)

canvas.bind("<Button-1>", callback)

tk.mainloop()
