import os
import json
import re 
import base64
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from bs4.element import Tag


#should process 1 query
class ResponseToJson:
    def __init__(self, response_html):
        f = open(response_html, 'r').read()
        self.__soup = BeautifulSoup(f, features="html.parser")
        self.__json = {} 
        self.__later_keys = ["fromClass","toClass","jDate","jTime","SearchForw","jRoute",
        "tivek","gua","addtime","lastdatum","firstdatum","goback","vorher","nachher","nc","lang","viaClass"]           

    def GetLaterPost(self):
        ret = {}
        forms = self.__soup.find_all('form')
        for form in forms:
            input_ = form.find('input', {'name':'addtime'})
            if input_ is not None:
                val = input_.get('value')
                if val == '1':
                    for key in self.__later_keys:
                        ret[key] = form.find('input', {'name': key}).get('value')
        return ret


        
    def ProcessHead(self):
        table = self.__soup.find_all('table', class_="table table-striped table-bordered table-list table-responsive table table-condensed")
        for thead in table:
            thead = self.__soup.findAll('thead')
            for t in thead:
                #first one for keys is enough
                tr = t.find("tr" , recursive=False)
                for th in tr.findAll('th'):
                    if isinstance(th, Tag):
                        self.__json[th.text] = []

    def ProcessSubFromTo(self, trtag):
        ret = {}
        #build json dict
        #direct route
        try:
            #lets consider that the format stays the same, same order
            tds = trtag.findAll('td')
            # ui idx 1. 2. ... 23.
           # ret['ui_idx'] = re.findall("\d+", tds[0].text)[0]

            #From To (direct route)
            from_to = tds[1].get_text(separator='|br|', strip=True).split('|br|')
            if len(from_to) == 2:
                ret['from'] = from_to[0]
                ret['to'] = from_to[1]
        
            ftl = tds[2].findAll('a', href = True)
            if len(ftl) == 2:
                ret['from_link'] = ftl[0]['href']
                ret['to_link'] = ftl[1]['href'] 

            date_dep_arr = tds[3].get_text(separator='|br|', strip=True).split('|br|')
            if len(date_dep_arr) == 1:
                ret['date_dep'] = date_dep_arr[0]
                ret['date_arr'] = date_dep_arr[0]
            elif len(date_dep_arr) == 2:
                ret['date_dep'] = date_dep_arr[0]
                ret['date_arr'] = date_dep_arr[1]
            
            time_dep_arr = tds[5].get_text(separator='|br|', strip=True).split('|br|')
            if len(time_dep_arr) ==2:                
                ret['time_dep'] = time_dep_arr[0]
                ret['time_arr'] = time_dep_arr[1]
            
            trans_info = tds[6].find('a', href = True)
            if trans_info is not None:
                ret['trans_link'] = trans_info['href']
            trans_tel = tds[6].get_text(separator='|br|', strip=True).split('|br|')            
            if trans_tel is not None:
                if len(trans_tel) > 0:
                    ret['trans_name'] = trans_tel[0]
                if len(trans_tel) > 1:
                    ret['trans_tel'] = trans_tel[1]

            ret['remarks'] = tds[7].text
            return ret
        except:
            return {}
    
    def ProcessBody(self):
        ret = {}
        table = self.__soup.find_all('table', class_="table table-striped table-bordered table-list table-responsive table table-condensed")
        for tbody in table:
            tbody = self.__soup.find('tbody')
            for tr in tbody.findAll('tr'):
                tmp = self.ProcessSubFromTo(tr) #read last date here
                if tmp:
                    st = json.dumps(list(tmp.values())).encode('utf-8')
                    lst = base64.b64encode(st)
                    ret[lst] = tmp
        return ret

    def MinusIdx(self, arg):
        return 

    def UpdateData(self, From, To, idx =-2):
        ret = {}
        table = self.__soup.find_all('table', class_="table table-striped table-bordered table-list table-responsive table table-condensed")
        for tbody in table:
            tbody = self.__soup.find('tbody') 
            last = tbody.find_all('tr')[idx] #should be last date ... as the last component is a clickable
            ret = self.ProcessSubFromTo(last) #should be one only
            if ret.get('from') != From or ret.get('to') != To:
                return self.UpdateData(From, To, idx=idx-2)
            return ret
        return ret
            



    def PastLastDate(self, compare_to_this_date, verbose_date = False):
        table = self.__soup.find_all('table', class_="table table-striped table-bordered table-list table-responsive table table-condensed")
        for tbody in table: #should we test against index text?
            tbody = self.__soup.find('tbody') #HERE TODO 
            last = tbody.find_all('tr')[-2] #should be last date ... as the last component is a clickable
            tmp = self.ProcessSubFromTo(last)
            date = tmp.get('date_dep')
            if verbose_date:
                print('Doing ' + str(date))
            date_ = re.search(r'\d{2}/\d{2}', date).group(0)
            d = int(date_.rsplit("/", 1)[-1])
            if d > compare_to_this_date:
                return True
            return False


def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    html_response = 'resp.html'
    pipe = ResponseToJson(html_response)
#    ret = pipe.ReadLastDate()

if __name__ == '__main__':
    main()