"""
Created on Mon Nov 27 03:01:23 2017

@author: Libo
"""

import requests
from bs4 import BeautifulSoup
import time 

unit_code_url = 'https://irmaservices.nps.gov/v2/rest/unit/park?format=json'
units = [((u['UnitName'], u['UnitDesignationCode']), u['UnitCode']) for u in requests.get(unit_code_url).json() if u['UnitDesignationCode'] is not None]
base_url = "https://irma.nps.gov/Stats/SSRSReports/Park%20Specific%20Reports/Annual%20Park%20Recreation%20Visitation%20(1904%20-%20Last%20Calendar%20Year)?Park="
result = {}
with requests.session() as s:
    s.headers['user-agent'] = 'Mozilla/5.0'

    for u in units:
        page = s.get(base_url + u[1])
        soup = BeautifulSoup(page.content, 'html.parser')
        year = soup.find('td', string='Year')
        if year is None:
            continue
        data = year.find_parent('table').find_all('tr', recursive=False)[2:-1]
        visitation = [[r.string for r in d.find_all('div')] for d in data]
        visitation = [(int(v[0]), int(v[1].replace(',', ''))) for v in visitation]
        for v in visitation:
            if v[0] in result:
                result[v[0]][u[0]] = v[1]
            else:
                result[v[0]] = {u[0]: v[1]}
        time.sleep(5)

s = set()

for r in result.values():
    for d in r:
        s.add(d[0])
            
rc = {k:dict(v) for (k,v) in  result.items()}
for r in rc.keys():
    for p in s:
        if p not in rc[r]:
            rc[r][p] = ''
        else:
            rc[r][p] = str(rc[r][p])

with open('a.csv', 'w') as f:
    st = ',' + ','.join(sorted([l[0] for l in s]))
    f.write(st + '\n')
    st = ',' + ','.join(sorted([l[1] for l in s]))
    f.write(st + '\n')
    for k, v in rc.items():
        st = str(k) + ',' + ','.join(v.values())
        f.write(st + '\n')        
        
