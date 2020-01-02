import re
import requests
from bs4 import BeautifulSoup

URL = 'http://horariodebuses.com/EN/cr/overview.php?lang=en'
MAP_CODE = 'map.html'
class FromToPipeline:
    def __init__(self):
        pass

    def Process(self, elem):
        ll = []
        soup = BeautifulSoup(elem)
        From = soup.find('b').text
     #   if From == 'Golfito':
     #       b = True
        tmp = soup.find_all('a')
        for l in tmp:
            to = re.sub('<[^<]+?>', '', l.next)


    def Read(self):
        with open(MAP_CODE) as open_file:
            data = open_file.read()
            m = re.findall('bindPopup\("(.*?)",{', data, re.DOTALL)
            for el in m:
                self.Process(el)


    def Exec(self):
        r = requests.get(URL)
        file = open(MAP_CODE, "w")
        file.write(r.text)
        file.close()
        self.Read()


    

def main():
    pipe = FromToPipeline()
    pipe.Exec()
    #text1 = 'var nid17 = L.marker([23.003394491348782, -82.38608837127686], {icon: TransIcon1, itle:"marker_16"}).addTo(map).bindPopup("<b>Boyeros</b><br>Direct connections to:<br />- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Alquizar\">Alquizar<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Artemisa\">Artemisa<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Güira de Melena\">Güira de Melena<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Herradura\">Herradura<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=La Habana\">La Habana<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=La Salud\">La Salud<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Los Palacios\">Los Palacios<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Pinar del Río\">Pinar del Río<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Puerta de Golpe\">Puerta de Golpe<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Rincón\">Rincón<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=San Antonio de los Baños\">San Antonio de los Baños<\/a>",{maxWidth: 600, maxHeight: 200}); '

    #text = 'var nid16 = L.marker([23.003394491348782, -82.38608837127686], {icon: TransIcon1, itle:"marker_16"}).addTo(map).bindPopup("<b>Boyeros</b><br>Direct connections to:<br />- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Alquizar\">Alquizar<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Artemisa\">Artemisa<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Güira de Melena\">Güira de Melena<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Herradura\">Herradura<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=La Habana\">La Habana<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=La Salud\">La Salud<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Los Palacios\">Los Palacios<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Pinar del Río\">Pinar del Río<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Puerta de Golpe\">Puerta de Golpe<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=Rincón\">Rincón<\/a><br>- <a href=\"http://horariodebuses.com/EN/cu/index.php?fromClass=Boyeros&amp;toClass=San Antonio de los Baños\">San Antonio de los Baños<\/a>",{maxWidth: 600, maxHeight: 200}); '
    #fin = text1 + text
    #m = re.findall('bindPopup\("(.*?)",{', fin, re.DOTALL)
    #print(m)

if __name__ == '__main__':
    main()


