import tkinter as tk
from tkinter import *
from tkinter import ttk
import json
import requests
from functools import partial
from direct_from_to_pipeline import FromToPipeline
import os
class MainUi(Tk):
    overviews_path = './overviews_links/overviews.json'
    def __init__(self):
        Tk.__init__(self)
        self.__create_engine()
        self.__create_widgets()
    def __create_engine(self):
        self.__ftpipe = FromToPipeline()
    def __on_country_selected(self, name, overviews, nodes_box_ptr):
        self.__ftpipe.generate_nodes_map(overviews[name], name)
        nodes = self.__ftpipe.get_nodes_map(name)
        nodes_box_ptr.delete(0, END)
        nodes_box_ptr.insert(END, *nodes.keys())
    def __generate_map_on_country_selected(self, name, overwrite = False):
        self.__ftpipe.generate_map(name, overwrite)
    def __create_widgets(self):
        tab_parent = ttk.Notebook(self)
        # tabs
        tab_c_roadmap = ttk.Frame(tab_parent)
        tab_map_algo = ttk.Frame(tab_parent)

        # country selection  + cities
        nodes_box = tk.Listbox( tab_c_roadmap)
        nodes_scrollbar = tk.Scrollbar(tab_c_roadmap)
        nodes_box.config(yscrollcommand = nodes_scrollbar.set) 
        nodes_scrollbar.config(command = nodes_box.yview)
        overviews = {}
        with open(MainUi.overviews_path, 'r', encoding='utf-8') as f:
            overviews = json.load(f)
        c_list_var = StringVar(self)
        c_list_var.trace('w', lambda *args:  self.__on_country_selected(c_list_var.get(), overviews, nodes_box))
        country_dd = tk.OptionMenu(tab_c_roadmap, c_list_var, *overviews.keys())
        generate_map_button = tk.Button(tab_c_roadmap, text='Generate Map', command=lambda: self.__generate_map_on_country_selected(name=c_list_var.get(), overwrite=True))

        country_dd.grid(row=0, column=0, padx=15, pady=15)
        nodes_box.grid(row=1, column=0, padx=15, pady=15)
        generate_map_button.grid(row=2, column = 0, padx=15, pady=15)

        nodes_scrollbar.grid(row=1, column=1, padx=15, pady=15, rowspan=1, sticky=N+S+W)
        tab_parent.add(tab_c_roadmap, text='Country roadmap generation')
        tab_parent.add(tab_map_algo, text='Path Algo')
        tab_parent.pack(expand=1, fill='both')    

if __name__ == "__main__":
    os.chdir('../')
    ui = MainUi()
    ui.geometry('500x500')
    ui.mainloop()
