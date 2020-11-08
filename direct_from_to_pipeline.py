import re
import requests
import json
import os
import os.path
from glob import glob
from bs4 import BeautifulSoup
import codecs
from request import WeekScheduleDirectRoute
import types

URL = 'https://horariodebuses.com/EN/cr/overview.php?lang=en'
MAP_CODE = 'map.html'
LIST_STOPS = "list_stops_cr.html"
JSON_FILE  = 'COSTA_RICA_DIRECT_ROUTES.json'

def get_stops_file_name(frm, to):
    return 'from_'+frm+'_to_'+to+'_stops.json'
def __process( elem):
    tos = []
    soup = BeautifulSoup(elem, features="html.parser")
    From = soup.find('b').text
    tmp = soup.find_all('a')
    for l in tmp:
        tos.append(re.sub('<[^<]+?>', '', str(l.next)))
    return (From, tos)

class FromToPipeline:
    country_nodes_path = './country_nodes_map/' 
    country_maps_path = './country_maps'
    week_map = {    'Mo':'monday',
                    'Tu':'tuesday',
                    'We':'wednesday',
                    'Th':'thursday',
                    'Fr':'friday',
                    'Sa':'saturday',
                    'Su':'sunday'
            }



    def __init__(self):
        if not os.path.exists(FromToPipeline.country_nodes_path):
            os.mkdir(FromToPipeline.country_nodes_path)        

    def generate_nodes_map(self, url, out_file_name, overwrite = False):
        fpath = FromToPipeline.country_nodes_path+'/'+out_file_name+'.json'
        json_map = {}
        if overwrite or not os.path.exists(fpath):
                r = requests.get(url)
                content = r.text
                ROI = re.findall('L.marker\(\[.*?}\);', content, re.DOTALL)
                for roi in ROI:
                    map = {}
                    GPS = re.findall('[-+]?\d*\.\d+', roi, re.DOTALL)
                    FROM = re.findall('(?<=<b>)(.*)(?=<\/b>)', roi, re.DOTALL)
                    TOS = re.findall('(?<=toClass=)(.*?)(?=\\\\">)', roi, re.DOTALL)
                    map['destinations'] = TOS
                    map['lat'] = GPS[0]
                    map['lon'] = GPS[1]
                    json_map[FROM[0]] = map
        pog = {}
        pog['destinations'] = list(json_map.keys())
        pog['lat'] = '9.928069'
        pog['lon'] = '-84.090725'
        json_map['San José'] = pog        
        with open(fpath, 'w+', encoding='utf-8') as fp:
            json.dump(json_map, fp, sort_keys=True, ensure_ascii=False)

    def get_nodes_map(self, name):
        data = {}
        j =str(FromToPipeline.country_nodes_path)+'/'+str(name)+'.json'
        with open(j,'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data

    def __process(self, elem):
        tos = []
        soup = BeautifulSoup(elem, features="html.parser")
        From = soup.find('b').text
        tmp = soup.find_all('a')
        for l in tmp:
            tos.append(re.sub('<[^<]+?>', '', str(l.next)))
        return (From, tos)

    def __generate_node(self, fmpath, From, tos, from_lat, from_lon, verbose = False):
        #WIP
        for to in tos:
            print('FROM ' + From)
            print('TO ' + to)
            if From == 'Bagaces':
                t = True
            path = fmpath + '/' + From + '/' + to
            if not os.path.exists(path):
                os.makedirs(path)
            json_name = 'from_'+From+'_to_'+to+'.json'
            if os.path.exists(path+'/'+json_name): #overwrite option 
                continue
            week = WeekScheduleDirectRoute(From, to)
            week.Exec(verbose=True) 
            raw = week.FormatFullSchedule(From=From, To=to,discard_non_direct=True) #or here to file?
            raw['from'] = From
            raw['to'] = to
            with open(path+'/'+json_name, 'w+', encoding='utf-8') as fp:
                json.dump(raw, fp, sort_keys=True, ensure_ascii=False)            
            self.__convert_raw_to_stops_format(raw, from_lat, from_lon, path )

    def __convert_raw_to_stops_format(self, raw, from_lat_arg, from_lon_arg, path):       
        From = raw.get('from')
        To = raw.get('to')
        #path = FromToPipeline.country_maps_path + '/'+ str(From)+ '/' + str(To)
        stops_name = 'from_'+From+'_to_'+To+'_stops.json'
        stops = {}
        del raw['from']
        del raw['to']
        for key, time in raw.items():
            for val in time:
                from_lon = 0.0
                from_lat = 0.0
                if val.get('from_lon') is not None:
                    from_lon = float(val.get('from_lon'))
                else:
                    from_lon = float(from_lon_arg)
                if val.get('from_lat') is not None:
                    from_lat = float(val.get('from_lat'))
                else:
                    from_lat = float(from_lat_arg)
                key_from = from_lon + from_lat
                #NEED A CHECK FOR ALL THE VALS IDEALLY
                detail_for_day = {} #dep time dep arr day arr remarks #TODO: IMPROVEMENT LOOP OVER KEYS
                if val.get('time_dep') is not None:
                    detail_for_day['time_dep'] = val.get('time_dep')
                if val.get('time_arr') is not None:
                    detail_for_day['time_arr'] = val.get('time_arr')
                if val.get('remarks') is not None:
                    detail_for_day['remarks'] = val.get('remarks')
                if val.get('date_arr') is not None:
                    detail_for_day['date_arr'] = FromToPipeline.week_map.get(val.get('date_arr')[:2])
                if 'trans_name' in val:
                    detail_for_day['trans_name'] = val.get('trans_name')
                if 'trans_tel' in val:
                    detail_for_day['trans_tel'] = val.get('trans_tel')
                if 'trans_link' in val:
                    detail_for_day['trans_link'] = val.get('trans_link')
                if 'to_lat' in val:
                    detail_for_day['to_lat'] = val.get('to_lat')
                if 'to_lon' in val:
                    detail_for_day['to_lon'] = val.get('to_lon')
                if key_from not in stops:
                    tmp = {}
                    tmp['lon'] = from_lon
                    tmp['lat'] = from_lat
                    schedule = {}
                    schedule[key] = []
                    tmp['schedule'] = schedule
                    stops[key_from] = tmp
                if key not in stops[key_from]['schedule']: #check if theres a list or not
                    stops[key_from]['schedule'][key] = []
                stops[key_from]['schedule'][key].append(detail_for_day)
        with open(path+'/'+stops_name, 'w+', encoding='utf-8') as fp:
            json.dump(stops, fp, sort_keys=True, ensure_ascii=False)
    

    def ConvertRawToStops(self, raw, force=False):
            try:
                if not isinstance(raw, dict):
                    return     
                From = raw.get('from')
                To = raw.get('to')
                p = './cr/' + str(From)+'/'+str(To)
                stops_name = 'from_'+From+'_to_'+To+'_stops.json'
                stops = {}
                del raw['from']
                del raw['to']
                if not os.path.isfile(p+'/'+stops_name) or force: #force = redo
                    for key, time in raw.items():
                        for val in time:
                            day = key
                            from_lon = 0.0
                            from_lat = 0.0
                            if val.get('from_lon') is not None:
                                from_lon = float(val.get('from_lon'))
                            if val.get('from_lat') is not None:
                                from_lat = float(val.get('from_lat'))
                            key_from = from_lon + from_lat
                            #NEED A CHECK FOR ALL THE VALS IDEALLY


                            detail_for_day = {} #dep time dep arr day arr remarks #TODO: IMPROVEMENT LOOP OVER KEYS
                            if val.get('time_dep') is not None:
                                detail_for_day['time_dep'] = val.get('time_dep')
                            if val.get('time_arr') is not None:
                                detail_for_day['time_arr'] = val.get('time_arr')
                            if val.get('remarks') is not None:
                                detail_for_day['remarks'] = val.get('remarks')
                            if val.get('date_arr') is not None:
                                detail_for_day['date_arr'] = FromToPipeline.week_map.get(val.get('date_arr')[:2])
                            if 'trans_name' in val:
                                detail_for_day['trans_name'] = val.get('trans_name')
                            if 'trans_tel' in val:
                                detail_for_day['trans_tel'] = val.get('trans_tel')
                            if 'trans_link' in val:
                                detail_for_day['trans_link'] = val.get('trans_link')
                            if 'to_lat' in val:
                                detail_for_day['to_lat'] = val.get('to_lat')
                            if 'to_lon' in val:
                                detail_for_day['to_lon'] = val.get('to_lon')

    #                        detail_for_day

                            if key_from not in stops:
                                tmp = {}
                                tmp['lon'] = from_lon
                                tmp['lat'] = from_lat
                                schedule = {}
                                schedule[key] = []
                                tmp['schedule'] = schedule
                                stops[key_from] = tmp
                            if key not in stops[key_from]['schedule']: #check if theres a list or not
                                stops[key_from]['schedule'][key] = []
                            stops[key_from]['schedule'][key].append(detail_for_day)

                    with open(p+'/'+stops_name, 'w', encoding='utf-8') as fp:
                        json.dump(stops, fp, sort_keys=True, ensure_ascii=False)
                    return stops
            except Exception as e:
                print(e)

    def MakeRawFromRequest(self, From, To, force=False):
        p ='./cr/'+ str(From)+'/'+str(To) #Path built from From/To
        if not os.path.isdir(p): #if path doesnt exist, we make it
            os.makedirs(p)
        json_name = 'from_'+From +'_to_'+To+'.json' #raw request json name, not optimised by stops
        tot = p+'/'+json_name
        if not os.path.isfile(tot) or force: #force = redo #if doesnt exist or redo enabled, we create it
            week = WeekScheduleDirectRoute(From, To) #will build the structure holdhing all the data regarding the from to request
            week.Exec(verbose=True) 
            to_write = week.FormatFullSchedule(From=From, To=To,discard_non_direct=True) #or here to file?
            to_write['from'] = From
            to_write['to'] = To
            with open(p+'/'+json_name, 'w', encoding='utf-8') as fp:
                json.dump(to_write, fp, sort_keys=True, ensure_ascii=False)
            return to_write
        else:
            with open(p+'/'+json_name, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                return data

    def GenerateMap(self):
        Map = {}
        exists = os.path.isfile(JSON_FILE)
        self.MapDirectRoutesToJson(not exists)
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            Map = json.load(f)
        for k, v in Map.items():
            self.GenerateNode(k, v)

    def generate_map(self, name, overwrite = False):
        fmpath = str(FromToPipeline.country_maps_path) + '/' + str(name)
        if overwrite:# or not os.path.exists(fmpath):
            nodes = self.get_nodes_map(name)
            for k, v in nodes.items():
                list = v.get('destinations')
                from_lat = v.get('lat')
                from_lon = v.get('lon')
                if k == 'Bagaces':
                    tt = True
                self.__generate_node(fmpath, k, list, from_lat, from_lon)
    #refactor
    def Read(self, force):
        #and casts to json
        if os.path.isfile(JSON_FILE) and force is False:
            return
        json_file = {}
        with open(MAP_CODE) as open_file:
            data = open_file.read()
            m = re.findall('bindPopup\("(.*?)",{', data, re.DOTALL)
            for el in m:
                ret = self.__process(el)
                if len(ret) == 2 :
                    json_file[ret[0]] = ret[1]

        with open(JSON_FILE, 'w', encoding='utf-8') as fp:
            json.dump(json_file, fp, sort_keys=True, ensure_ascii=False)


    def MapDirectRoutesToJson(self, force = False): 
        if force is False:
            return
        r = requests.get(URL)
        file = open(MAP_CODE, "w")
        file.write(r.text)
        file.close()
        self.Read(force=force)

    def CreateFoldersFromTo(self, f, specific_from = None):
        #not finished #edit : ?
        data = {}
        with open(f, encoding='utf-8') as json_file:
            data = json.load(json_file)

        if specific_from:
            try:
                tos = data.get(specific_from)
                week = WeekScheduleDirectRoute(specific_from, 'Conte')
                json_name = 'from_'+specific_from +'_to_'
                week.Exec(verbose = True)
                week.FormatFullSchedule()

            except Exception as e:
                print(e)





    

    def GenerateNode(self, From, Tos):
   #    Map = {}
   #    exists = os.path.isfile(JSON_FILE)
   #    self.MapDirectRoutesToJson(not exists)
   #    with open(JSON_FILE, 'r', encoding='utf-8') as f:
   #        Map = json.load(f)
   #    Tos = Map.get(From)
        for To in Tos:
            print('GENERATING '+From +' TO ' + To)
           
            raw = self.MakeRawFromRequest(From, To)
            stops = self.ConvertRawToStops(raw)



    def BuildDirectConnectionsFor(self, l, s):
        # 1. need to find function from to and build folder with 2 jsons independently from the rest, an exception of some sort
        #self.GenerateNode(s, ['Golfito'])
        self.GenerateNode(s, l)
        
        return

def ConvertRawToStopsFromFile(frm, to ):
    p ='./cr/'+ str(frm)+'/'+str(to) #Path built from From/To
    data = {}
    json_name = 'from_'+frm +'_to_'+to+'.json' #raw request json name, not optimised by stops
    with open(p+'/'+json_name, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    return data 
    
    
    


def main():

    pipe = FromToPipeline()
   # pipe.GenerateMap()

  #  raw = pipe.MakeRawFromRequest('Daniel Oduber', 'Bagaces',force=True)
  #  stops = pipe.ConvertRawToStops(raw, force=True)


  # exception 
   #exc = "San José"
   #list_subfolders_with_paths = []
   #for root, dirs, files in os.walk('./cr/'):
   #    for dir in dirs:
   #        list_subfolders_with_paths.append( dir )
   #    break
   #pipe.BuildDirectConnectionsFor(list_subfolders_with_paths,exc)

   #for city in list_subfolders_with_paths:
   #    print('GENERATING '+city +' TO ' + exc)           
   #    raw = pipe.MakeRawFromRequest(city, exc)
   #    stops = pipe.ConvertRawToStops(raw)



    frm = 'Liberia'
    to = 'Bagaces'
    p ='./cr/'+ str(frm)+'/'+str(to) #Path built from From/To
    data = {}
    json_name = 'from_'+frm +'_to_'+to+'.json' #raw request json name, not optimised by stops
    with open(p+'/'+json_name, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
#    raw = pipe.MakeRawFromRequest('Liberia', 'Bagaces', force =  True)
    stops = pipe.ConvertRawToStops(data, force=True)


def __convert_raw_to_stops_format( raw, from_lat_arg, from_lon_arg, path):       
        From = raw.get('from')
        To = raw.get('to')
        #path = FromToPipeline.country_maps_path + '/'+ str(From)+ '/' + str(To)
        stops_name = 'from_'+From+'_to_'+To+'_stops.json'
        stops = {}
        del raw['from']
        del raw['to']
        for key, time in raw.items():
            for val in time:
                from_lon = 0.0
                from_lat = 0.0
                if val.get('from_lon') is not None:
                    from_lon = float(val.get('from_lon'))
                    if from_lon == 0.0:
                        tt = True
                else:
                    from_lon = from_lon_arg
                    if from_lon == 0.0:
                        tt = True
                if val.get('from_lat') is not None:
                    from_lat = float(val.get('from_lat'))
                else:
                    from_lat = from_lat_arg
                if from_lon == 0.0:
                    tt = True
                key_from = from_lon + from_lat
                #NEED A CHECK FOR ALL THE VALS IDEALLY
                detail_for_day = {} #dep time dep arr day arr remarks #TODO: IMPROVEMENT LOOP OVER KEYS
                if val.get('time_dep') is not None:
                    detail_for_day['time_dep'] = val.get('time_dep')
                if val.get('time_arr') is not None:
                    detail_for_day['time_arr'] = val.get('time_arr')
                if val.get('remarks') is not None:
                    detail_for_day['remarks'] = val.get('remarks')
                if val.get('date_arr') is not None:
                    detail_for_day['date_arr'] = FromToPipeline.week_map.get(val.get('date_arr')[:2])
                if 'trans_name' in val:
                    detail_for_day['trans_name'] = val.get('trans_name')
                if 'trans_tel' in val:
                    detail_for_day['trans_tel'] = val.get('trans_tel')
                if 'trans_link' in val:
                    detail_for_day['trans_link'] = val.get('trans_link')
                if 'to_lat' in val:
                    detail_for_day['to_lat'] = val.get('to_lat')
                if 'to_lon' in val:
                    detail_for_day['to_lon'] = val.get('to_lon')
                if key_from not in stops:
                    tmp = {}
                    tmp['lon'] = from_lon
                    tmp['lat'] = from_lat
                    schedule = {}
                    schedule[key] = []
                    tmp['schedule'] = schedule
                    stops[key_from] = tmp
                if key not in stops[key_from]['schedule']: #check if theres a list or not
                    stops[key_from]['schedule'][key] = []
                stops[key_from]['schedule'][key].append(detail_for_day)
        with open(path+'/'+stops_name, 'w+', encoding='utf-8') as fp:
            json.dump(stops, fp, sort_keys=True, ensure_ascii=False)    




if __name__ == '__main__':
    raw = None
    os.chdir('.')
    print(os.listdir('.'))
    j = '.\\country_maps\\costa_rica\\Buenos Aires\\División'
    with open(j+'\\from_Buenos Aires_to_División.json','r', encoding='utf-8') as json_file:
        raw = json.load(json_file)
    __convert_raw_to_stops_format(raw, '0.0', '0.0', j)

    #main()

#var nid\d = L.marker\(\[.*?}\); #gets nids
#[-+]?\d*\.\d+ #gets gps cooords
#from (?<=<b>)(.*)(?=<\/b>)
#(?<=toClass=)(.*?)(?=\\\\">) #dests


