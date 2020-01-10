import re
import requests
import json
import os
import os.path
from bs4 import BeautifulSoup
import codecs
from request import WeekScheduleDirectRoute
import types

URL = 'http://horariodebuses.com/EN/cr/overview.php?lang=en'
MAP_CODE = 'map.html'
JSON_FILE  = 'COSTA_RICA_DIRECT_ROUTES.json'

class FromToPipeline:
    def __init__(self):
        pass

    def Process(self, elem):
        tos = []
        soup = BeautifulSoup(elem)
        From = soup.find('b').text
        tmp = soup.find_all('a')
        for l in tmp:
            tos.append(re.sub('<[^<]+?>', '', str(l.next)))
        return (From, tos)

    def Read(self, force):
        #and casts to json
        if os.path.isfile(JSON_FILE) and force is False:
            return
        json_file = {}
        with open(MAP_CODE) as open_file:
            data = open_file.read()
            m = re.findall('bindPopup\("(.*?)",{', data, re.DOTALL)
            for el in m:
                ret = self.Process(el)
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

    def MakeRawFromRequest(self, From, To, force=False):
        p = str(From)+'/'+str(To)
        if not os.path.isdir(p):
            os.makedirs(p)
        json_name = 'from_'+From +'_to_'+To+'.json'
        if not os.path.isfile(p+'/'+json_name) or not force: #force = redo
            week = WeekScheduleDirectRoute(From, To)
            week.Exec(verbose=True)
            to_write = week.FormatFullSchedule() #or here to file?
            to_write['from'] = From
            to_write['to'] = To

            with open(p+'/'+json_name, 'w', encoding='utf-8') as fp:
                json.dump(to_write, fp, sort_keys=True, ensure_ascii=False)
            return to_write


    def ConvertRawToStops(self, raw, force=False):
        try:
            if not isinstance(raw, dict):
                return
            week_map = {
                'Mo':'monday',
                'Tu':'tuesday',
                'We':'wednesday',
                'Th':'thursday',
                'Fr':'friday',
                'Sa':'saturday',
                'Su':'sunday'
            }
            From = raw.get('from')
            To = raw.get('to')
            p = str(From)+'/'+str(To)
            stops_name = 'from_'+From+'_to_'+To+'_stops.json'
            stops = {}
            del raw['from']
            del raw['to']
            if not os.path.isfile(p+'/'+stops_name) or force: #force = redo
                for key, time in raw.items():
                    for val in time:
                        day = key
                        from_lon = float(val.get('from_lon'))
                        from_lat = float(val.get('from_lat'))
                        key_from = from_lon + from_lat


                        detail_for_day = {} #dep time dep arr day arr remarks
                        detail_for_day['time_dep'] = val.get('time_dep')
                        detail_for_day['time_arr'] = val.get('time_arr')
                        detail_for_day['remarks'] = val.get('remarks')
                        detail_for_day['date_arr'] = week_map.get(val.get('date_arr')[:2])

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

    def GenerateNode(self, From):
        Map = {}
        exists = os.path.isfile(JSON_FILE)
        self.MapDirectRoutesToJson(not exists)
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            Map = json.load(f)

        Tos = Map.get(From)
        for To in Tos:
            raw = self.MakeRawFromRequest(From, To)
            stops = self.ConvertRawToStops(raw)



def main():
    pipe = FromToPipeline()
   
    pipe.GenerateNode('Golfito')

   # pipe.MakeRawFromRequest('Golfito', 'Conte')
   # with open('./Golfito/Conte/from_Golfito_to_Conte.json', 'r') as f:
   #     raw = json.load(f)
   # pipe.ConvertRawToStops(raw, True)

   # pipe.CreateFolderFromTos(JSON_FILE, 'Golfito')


if __name__ == '__main__':
    main()


