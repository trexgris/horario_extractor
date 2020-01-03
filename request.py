import requests
import json
import datetime
from bs4 import BeautifulSoup
from response_to_json import ResponseToJson
import re
import time
import os
from collections import defaultdict
from datetime import timedelta
from datetime import datetime, date

RESP  = "resp.html"
URL = 'http://horariodebuses.com/EN/cr/index.php'
SCHEDULE_FILE = 'golfito_conte_week_schedule.json'
#should be used for direct routes
class WeekScheduleDirectRoute:
    def __init__(self, fromClass, toClass):
        data = {}
        data['fromClass'] = fromClass
        data['toClass'] = toClass
        data['viaClass'] = ''
        data['jDate'] = '12/22/2019' #starting point #sunday, midnight, will basically pull whole week from monday
        data['jTime'] = '00:01'  
        data['addtime'] = '0'
        data['lang'] = 'en'
        data['b2'] = 'Search connection'


        self.__fullschedule = {}
        
        self.__data = data
        self.__week_dates = {'12/23': 'monday',
         '12/24':'tuesday', #tuesday
         '12/25':'wednesday', #wednesday
         '12/26':'thursday', #thursday
         '12/27':'friday', #friday
         '12/28':'saturday', #saturday
         '12/29':'sunday'
         } #sunday


    def FormatFullSchedule(self,force=False):
        #not finished
        if os.path.isfile(SCHEDULE_FILE) and force is False:
            with open(SCHEDULE_FILE, encoding='utf-8') as json_file:
                data = json.load(json_file)
                return data

        ret = defaultdict(list)
        for key, val in self.__fullschedule.items():
            if len(key) != 2:
                raise Exception('request.py - FormatFullSchedule(): Tuple isnt of size 2')
            day = key[0]
            #get lon lat
            from_link = val.get('from_link')
            to_link = val.get('to_link')
            from_coords = re.findall("\d+\.\d+", from_link) #dirty regex
            to_coords = re.findall("\d+\.\d+", to_link) #dirty regex

            if len(from_coords) != 0: #dirty hack
                val['from_lon'] = from_coords[0]
                val['from_lat'] = from_coords[1]
            if len(to_coords) != 0: #dirty hack
                val['to_lon'] = to_coords[0]
                val['too_lat'] = to_coords[1]
            ret[day].append(val)
            #todo: production refactor
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as fp:
            json.dump(ret, fp, sort_keys=True, ensure_ascii=False)
        return ret

        
    def DateOfNextWeek(self, s):
        d = int(s.rsplit("/", 1)[-1])

        sunday = int(29)
        if d > sunday:
            return True
        return False

    def PopulateSchedule(self, body_dict, verbose = False):
        ret = {}
        if len(body_dict) == 0:
            return True
        for key, val in body_dict.items():
            try:
                #monday to monday
                date = re.search(r'\d{2}/\d{2}', val.get('date_dep')).group(0)
                if self.DateOfNextWeek(date):
                    return True    
                match_day = self.__week_dates.get(date)
                if match_day is None:    
                    continue                
                self.__fullschedule[(match_day, key)] = val
                if verbose is True:
                    print('Doing ' + match_day)
            except Exception  as e:
                print(e)
                continue
        return False
    
    def Exec(self, verbose = False):
        if verbose is True:
            print('Verbose enabled')
        r = requests.post(URL, data=self.__data)
        file = open(RESP, "w")
        file.write(r.text)
        file.close()

        delete_TO = 1
        wait_until = datetime.now() + timedelta(minutes=30)
        break_loop = False

#to avoid timeout -> process only day?
        while True:
            if wait_until < datetime.now():
                break    
            time.sleep(3)
            resp = ResponseToJson(RESP)
            if resp.PastLastDate(29, verbose):
                ret = resp.ProcessBody()
                self.PopulateSchedule(ret, verbose = verbose)
                break
            ret_later = resp.GetLaterPost()
            if ret_later is None:
                break
            r = requests.post(URL, data=ret_later)
            file = open(RESP, "w")
            file.write(r.text)
            file.close()
def main():
  #  week = WeekScheduleDirectRoute('Golfito', 'Conte')
  #  week.Exec()
   
    test = defaultdict(list)

    test['a'].append('a')
    test['a'].append('b')
    test['a'].append('c')


    st = 'http://horariodebuses.com/cr/busstop.php?city=Golfito&lang=en&ruta=bu,f&comp=&tele=&cweb=&ort=Bus%20Terminal&lon=-83.1650984287262&lat=8.63732820166971'
    rest = re.findall("\d+\.\d+",st)
    n=str.split("?long=?&lat=");


    tt =''

  

if __name__ == '__main__':
    main()

