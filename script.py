# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 03:01:23 2017

@author: Libo
"""

from bs4 import BeautifulSoup
import requests
import asyncio
from aiohttp import ClientSession

async def fetch(u, url, session, result):
    retries_count = 0
    retries = 3
    while retries_count < retries:
        try:
            name = u['UnitName'], u['UnitDesignationCode']
            async with session.get(url) as response:
                page =  await response.text()
        except Exception as err:
            retries_count += 1
            message = "Query for {1} resulted in exception {0}. {2} of {3} retries attempted".format(type(err), name, retries_count, retries)
    
            print(message)
    
            await asyncio.sleep(5)
        else:        
            print(name)
            
            soup = BeautifulSoup(page, 'html.parser')
            year = soup.find('td', string='Year')
            if year is None:
                return
            table_data = year.find_parent('table').find_all('tr', recursive=False)[2:-1]
            visitation = [[r.string for r in d.find_all('div')] for d in table_data]
            visitation = [(int(v[0]), int(v[1].replace(',', ''))) for v in visitation]
            for v in visitation:
                if v[0] in result:
                    result[v[0]][name] = v[1]
                else:
                    result[v[0]] = {name: v[1]}
            return

async def run(url, units, result):
    tasks = []

    async with ClientSession(headers={'User-Agent': 'Mozilla/5.0'}) as session:
        for u in units:
            task = asyncio.ensure_future(fetch(u, url.format(u['UnitCode']), session, result))
            tasks.append(task)
            await asyncio.sleep(0.1)

        return await asyncio.gather(*tasks)



unit_code_url = 'https://irmaservices.nps.gov/v2/rest/unit/park?format=json'
base_url = "https://irma.nps.gov/Stats/SSRSReports/Park%20Specific%20Reports/Annual%20Park%20Recreation%20Visitation%20(1904%20-%20Last%20Calendar%20Year)?Park={0}"

units = [u for u in requests.get(unit_code_url).json() if u['UnitDesignationCode'] is not None]

result = {}
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(base_url, units, result))
loop.run_until_complete(future)
loop.run_until_complete(asyncio.sleep(0))
loop.close()

s = set()

for r in result.values():
    for k, v in r.items():
        s.add(k)

s = sorted(s)
            
for r in result.keys():
    for p in s:
        if p not in result[r]:
            result[r][p] = ''
        else:
            result[r][p] = str(result[r][p])

with open('result.csv', 'w') as f:
    st = ',' + ','.join(['"' + l[0] + '"' for l in s])
    f.write(st + '\n')
    st = ',' + ','.join(['"' + l[1] + '"' for l in s])
    f.write(st + '\n')
    for k, v in sorted(result.items()):
        values = [v for k,v in sorted(v.items())]
        st = str(k) + ',' + ','.join(['"' + str(l) + '"' for l in values])
        f.write(st + '\n')        
        
