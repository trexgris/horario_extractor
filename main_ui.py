import tkinter as tk
from tkinter import *
from tkinter import ttk
import json
import requests
from functools import partial
from direct_from_to_pipeline import FromToPipeline



class MainUi(Tk):
    overviews_path = './overviews_links/overviews.json'
    def __init__(self):
        Tk.__init__(self)
        self.__create_engine()
        self.__create_wdigets()
    def __create_engine(self):
        self.__ftpipe = FromToPipeline()
    def __on_country_selected(self, name, overviews, nodes_box_ptr):
        self.__ftpipe.generate_nodes_map(overviews[name], name)
        nodes = self.__ftpipe.get_nodes_map(name)
        nodes_box_ptr.delete(0, END)
        nodes_box_ptr.insert(END, *nodes.keys())
    def __create_wdigets(self):
        tab_parent = ttk.Notebook(self)
        # country data generation 
        tab_c_roadmap = ttk.Frame(tab_parent)
        # country selection  + cities
        nodes_box = tk.Listbox( tab_c_roadmap)
        nodes_scrollbar = tk.Scrollbar(tab_c_roadmap)
        nodes_box.config(yscrollcommand = nodes_scrollbar.set) 
        nodes_scrollbar.config(command = nodes_box.yview)
        overviews = {}
        with open(MainUi.overviews_path, 'r', encoding='utf-8') as f:
            overviews = json.load(f)
        __c_list_var = StringVar(self)
        __c_list_var.trace('w', lambda *args:  self.__on_country_selected(__c_list_var.get(), overviews, nodes_box))
        country_dd = tk.OptionMenu(tab_c_roadmap, __c_list_var, *overviews.keys())
        country_dd.grid(row=0, column=0, padx=15, pady=15)
        nodes_box.grid(row=1, column=0, padx=15, pady=15)
        nodes_scrollbar.grid(row=1, column=1, padx=0, pady=15)


        tab_parent.add(tab_c_roadmap, text='Country roadmap generation')
        tab_parent.pack(expand=1, fill='both')


        




if __name__ == "__main__":
    ui = MainUi()
    ui.geometry('500x500')
    ui.mainloop()
