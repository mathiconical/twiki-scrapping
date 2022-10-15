import requests as req
import sys
import json
from bs4 import BeautifulSoup as bs

URL = 'https://www.tibiawiki.com.br/wiki/Lista_de_Criaturas'
BASE_URL = 'https://www.tibiawiki.com.br'

DICT_VALUES = {
  'Trivial': 'Harmless',
  'Fácil': 'Easy',
  'Mediana': 'Medium',
  'Difícil': 'Hard',
  'Desafiador': 'Challenging'
}

def monster_own_page(complement):
  page = req.get(BASE_URL + complement)

  soup = bs(page.content, 'html.parser')

  table = soup.find('table', {'class': 'infobox-main'})

  table_all_tr = table.find_all('tr')

  behavior = {}

  loot = {}

  for tr in table_all_tr:
    td = tr.find('td')

    try:
      if td.text.strip() == 'Loot:':
        table_tr = td.parent.find('table').find('tbody').find_all('tr')

        for _ in range(0, len(table_tr), 2):
          loot[table_tr[_].text] = table_tr[_ - 1].text.strip().replace('*', '')
    except:
      print(f'failed to get loot from {complement}')

    if td.text.strip() == 'Comportamento:':
      _ = td.parent.text.strip().replace('\n', '')

      if 'Foge com a vida baixa' in _:
        behavior['run with low life'] = True

      if 'Não é possível bloquear o respawn dessa criatura' in _:
        behavior['can block respawn'] = False

      if 'Combate corpo a corpo' in _:
        behavior['fight'] = 'melee'

      if 'É possível bloquear o respawn dessa criatura' in _:
        behavior['can block respawn'] = True

      if 'Luta até a morte' in _:
        behavior['run with low life'] = False

      if 'Combate corpo a corpo e à distância' in _:
        behavior['fight'] = 'melee and range'

      if 'Combate à distância' in _:
        behavior['fight'] = 'range'

      if 'Eles sempre irão correr e não atacam' in _:
        behavior['fight'] = 'just run'

  return behavior, loot

def parse_tr(tr):
  global DICT_VALUES
  row = []
  c = 0

  behavior = {}
  loot = {}

  for td in tr.find_all('td'):
    if c == 0:
      a = td.find('a', href=True)['href']
      behavior, loot = monster_own_page(a)

    _ = td.text.strip().replace('\n', ' ').replace('\u2010', '---').replace('\u221e', '---')

    if _ != '':
      row.append(_)
      c += 1
      continue

    if c == 4:
      try:
        _ = td.text.strip().replace('\n', ' ').replace('\u2010', '---').replace('\u221e', '---')
        row.append(_)
      except:
        print('failed to charms')
        row.append('---')
    
    if c == 5:
      try:
        _ = DICT_VALUES[td.find('img', alt=True)['alt'].strip()]
        row.append(_)
      except:
        print('failed to find img alt')
        row.append('---')
    
    c += 1

  row.append(behavior)
  row.append(loot)

  return row

if __name__ == '__main__':
  page = req.get(URL)

  soup = bs(page.content, 'html.parser')

  table_by_id = soup.find_all(id='tabelaDPL')

  table_header = table_by_id[0].find_all('th')

  table_header = [ _ for _ in table_header if _.text.strip() != 'Loot' ]

  for _ in table_by_id[0].find_all('small'):
    _.clear()

  table_tr = table_by_id[0].find_all('tr')

  data = []

  default = {}

  # create a default dict with header information of the table_header
  for th in table_header:
    _ = th.text.strip().replace('\n', '')

    if _ != '':
      if _ == 'Criatura':
        default['Creature'] = ''
      else:
        default[_] = ''

  default['Charms'] = ''
  default['Difficult'] = ''
  default['Behavior'] = ''
  default['Loot'] = ''

  for tr in table_tr[1:]:
    data.append(dict(zip(default, list(parse_tr(tr)))))

  with open('creatures_list.json', 'w') as file:
    json.dump(data, file, indent=4)