import re
import requests
import json
import os
from bs4 import BeautifulSoup
import codecs
from request import WeekScheduleDirectRoute

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
            tos.append(re.sub('<[^<]+?>', '', l.next))
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

    def MapDirectRoutesToJson(self, force_ = True):
        if force_ is False:
            return
        r = requests.get(URL)
        file = open(MAP_CODE, "w")
        file.write(r.text)
        file.close()
        self.Read(force=force_)

    def CreateFolderFromTos(self, f, specific_from = None):
        data = {}
        with open(f, encoding='utf-8') as json_file:
            data = json.load(json_file)

        if specific_from:
            try:
                tos = data.get(specific_from)
                #test zone
                week = WeekScheduleDirectRoute(specific_from, 'Conte')
                week.Exec(verbose = True)
                t = ''
                #todo, organise jsons in directories and aoso on like specified sur mon cahier
                #
            except Exception as e:
                print(e)



def main():
    pipe = FromToPipeline()
    pipe.MapDirectRoutesToJson( not os.path.isfile(JSON_FILE))
    pipe.CreateFolderFromTos(JSON_FILE, 'Golfito')


if __name__ == '__main__':
    main()


