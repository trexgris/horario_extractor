import os
from graph import Graph
import json
import math


def get_stops_file_name(frm, to):
    return 'from_'+frm+'_to_'+to+'_stops.json'

def comp_min(t1):
    return time_to_mins(t1.get('time_dep'))
    

def time_to_mins(time_str):
    return int(time_str[:-3]) * 60 + int(time_str[-2:])

class Date:
    week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    def __init__(self, day = None, time_str = None):
        self.day = day
        self.time_m = time_to_mins(time_str)            

class Trip:
    def __init__(self, country_path_file):
        default_date = Date('monday', '01:30')
        self.__build_graph(country_path_file, default_date)

    def __get_faster_transition(self, stops_ids, compared_to_date):
        now = compared_to_date.time_m
        now_day_idx = Date.week_list.index(compared_to_date.day)
        mn = math.inf
        wait_duration = 0  
        #bloody buggy function
        # DO NO TREAT 2 different bus stops as part of ONE SAME ENTITY !!!
        # #instead 2 stops in 1 city should be treated as 2 different nodes !!!
        # #TO FIX IN V2 
        for stop_id, content in stops_ids.items():
            schedule = content.get('schedule')
            for next_day_id, next_day_schedule in schedule.items():
                next_day_idx = Date.week_list.index(next_day_id)
                for time in next_day_schedule:
                    if next_day_idx < now_day_idx:
                        # DIRTY
                        wait_duration = (len(Date.week_list) - now_day_idx + next_day_idx) * time_to_mins('24:00') + time_to_mins(time.get('time_dep')) - now
                    elif next_day_idx > now_day_idx:
                        wait_duration = (next_day_idx - now_day_idx) * time_to_mins('24:00') + time_to_mins(time.get('time_dep')) - now 
                    elif next_day_idx == now_day_idx:
                        if  time_to_mins(time.get('time_dep')) > now:
                            wait_duration = time_to_mins(time.get('time_dep')) - now
                        else:
                            wait_duration = time_to_mins('24:00') * len(Date.week_list) + time_to_mins(time.get('time_dep')) - now
                    if wait_duration <= mn:
                        mn = wait_duration
                        #save min detail

                        




            av_times_for_day = schedule.get(compared_to_date.day)
            #next(av_times_for_day, key = lambda x:  comp_min(x))
            next(av_times_for_day, )




    def __build_graph(self, country_path_file, dep_date):
        graph = Graph()        
        nodes = [ f.path for f in os.scandir(country_path_file) if f.is_dir() ]
        #review departure city too
        for node in nodes:
            direct_connections = [ f.name for f in os.scandir(node) if f.is_dir() ]
            node_name = node.rsplit('/', 1)[-1]
            graph.add_node(node_name)
            for direct_connection in direct_connections:
                p = node + '/' + direct_connection
                json_name = '/' + get_stops_file_name(node_name, direct_connection)
                with open(p+json_name) as json_file:
                    stops_ids = json.load(json_file)
                    if len(stops_ids) >0:
                        faster_transition = self.__get_faster_transition(stops_ids, dep_date)
                    #get next date, iterate on it

    def build_graph2(self, country_path_file):
        graph = Graph()        


if __name__ == "__main__":
    trip = Trip('../costa_rica/')
pass