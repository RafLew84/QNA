# -*- coding: utf-8 -*-
"""
Entry point of the application

@author: rlewandkow
"""

import tkinter as tk
import config
from main_window import App



def main():
    config.setup_logging()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    

if __name__ == '__main__':
    main()