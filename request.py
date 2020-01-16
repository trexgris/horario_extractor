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
        self.__from = fromClass
        self.__to = toClass
        data = {}
        data['fromClass'] = fromClass
        data['toClass'] = toClass
        data['viaClass'] = ''
        data['jDate'] = '12/22/2019' #starting point #sunday, midnight, will basically pull whole week from monday
        data['jTime'] = '00:01'  
        data['addtime'] = '0'
        data['lang'] = 'en'
        data['b2'] = 'Search connection'


        data = {k: str(v).encode("ISO-8859-1") for k,v in data.items()}


        self.__fullschedule = {}
        self.__lastbody = {}
        self.__headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
}

        
        self.__data = data
        self.__week_dates = {'12/23': 'monday',
         '12/24':'tuesday', #tuesday
         '12/25':'wednesday', #wednesday
         '12/26':'thursday', #thursday
         '12/27':'friday', #friday
         '12/28':'saturday', #saturday
         '12/29':'sunday'
         } #sunday


    def FormatFullSchedule(self,From='', To='', discard_non_direct = False, force=False):
        ret = defaultdict(list)
        for key, val in self.__fullschedule.items():
            if len(key) != 2:
                raise Exception('request.py - FormatFullSchedule(): Tuple isnt of size 2')
            if discard_non_direct is True:
                if val.get('from') != From or val.get('to') != To:
                    continue #bug
            day = key[0]
            #get lon lat
            from_link = val.get('from_link')
            to_link = val.get('to_link')
            from_coords = re.findall("\d+\.\d+", from_link) #dirty regex
            to_coords = re.findall("\d+\.\d+", to_link) #dirty regex

            if len(from_coords) != 0: #dirty hack
                from_lon = from_coords[0]
                from_lat = from_coords[1]
                val['from_lon'] = from_lon
                val['from_lat'] = from_lat
            if len(to_coords) != 0: #dirty hack
                to_lon = to_coords[0]
                to_lat = to_coords[1]
                val['to_lon'] = to_lon
                val['to_lat'] = to_lat
            ret[day].append(val)
            #todo: production refactor
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
                if match_day == 'tuesday' and val.get('time_dep') == '05:00':
                    t = True
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

        r = requests.post(URL, headers = self.__headers, data=self.__data)


        file = open(RESP, "w")
        file.write(r.text)
        file.close()

        delete_TO = 1
        wait_until = datetime.now() + timedelta(minutes=55)
        break_loop = False
        lastlen = 0
        cntretry = 0

#to avoid timeout -> process only day?
        while True:
            if wait_until < datetime.now():
                break
            time.sleep(1.5)
            resp = ResponseToJson(RESP)
            if resp.PastLastDate(29, verbose):
                ret = resp.ProcessBody()
                self.PopulateSchedule(ret, verbose = verbose)
                break
            ret_later = resp.GetLaterPost()
            if ret_later is None or ret_later.get('fromClass') is None:
            #    except 'RET_LATER IS NONE' #BUG
                return
            if len(ret_later) == 0:
                ret_later = self.UpdatePostDataWithLastDate(resp) #test golfito - buenos aires
            ret_later = {k: str(v).encode("ISO-8859-1") for k,v in ret_later.items()}
            r = requests.post(URL, headers=self.__headers,data=ret_later)
            file = open(RESP, "w")
            file.write(r.text)
            file.close()

            ret = resp.ProcessBody()
            #tmp hack
            if lastlen == len(ret):
                if cntretry == 0:
                    cntretry = 1
                else:
                    cntretry = 0
                    break
            else:
                cntretry = 0
            lastlen = len(ret)


            self.PopulateSchedule(ret, verbose = verbose) #can be moved to if ret later == 0

    def UpdatePostDataWithLastDate(self, resp):
        ret = resp.UpdateData(From=self.__from, To=self.__to, idx=-2)
        ret_later = {}


        ret_later['fromClass'] = ret.get('from')
        ret_later['toClass'] = ret.get('to')
        ret_later['viaClass'] = ''

        #format date
        format_date = ret.get('date_dep')[4:] + '/2019'
        ret_later['addtime'] = '0'
        ret_later['lang'] = 'en'
        ret_later['jDate'] = format_date
        ret_later['jTime'] = ret.get('time_dep')  
        ret_later['b2'] = 'Search connection'
        return ret_later


def main():
  #  week = WeekScheduleDirectRoute('Golfito', 'Conte')
  #  week.Exec()


    data = {}
    data['fromClass'] = 'Golfito'
    data['toClass'] = 'Ca%F1on+del+Guarco'
    data['viaClass'] = '+'
    data['jDate'] = '01%2F12%2F2020' #starting point #sunday, midnight, will basically pull whole week from monday
    data['jTime'] = '13%3A59'  
    data['addtime'] = '0'
    data['lang'] = 'en'
    data['b2'] = 'Search+connection'
    r = requests.post(URL, data=data)
    file = open(RESP, "w")
    file.write(r.text)
    file.close()



  

if __name__ == '__main__':
    main()

