# -*- coding: utf-8 -*-
"""
Entry point of the application

@author: rlewandkow
"""

import tkinter as tk
from main_window import App

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    

if __name__ == '__main__':
    main()