import requests as req
import unidecode
import sys
import json

from termcolor import colored
from bs4 import BeautifulSoup as bs


COLOR = True
MESSAGE = True


URL = 'https://www.tibiawiki.com.br/wiki/Lista_de_Criaturas'
BASE_URL = 'https://www.tibiawiki.com.br'


DICT_VALUES = {
  'Trivial': 'Harmless',
  'Fácil': 'Easy',
  'Mediana': 'Medium',
  'Difícil': 'Hard',
  'Desafiador': 'Challenging'
}


LOOT_DICT_VALUES = {
  'Incomum': 'Uncommon',
  'Comum': 'Common',
  'Semi-Raro': 'Semi-Rare',
  'Raro': 'Rare',
  'Muito Raro': 'Very Rare',
  'Durante Eventos': 'During Events',
}


def monster_own_page(complement):
  global LOOT_DICT_VALUES, COLOR, MESSAGE

  if MESSAGE:
    if COLOR:
      print(f'{colored("Extracting information from creature", on_color="on_green", attrs=["bold"])} => {colored(complement.replace("/wiki/", "").replace("_", " "), color="green", attrs=["bold"])}')
    else:
      print(f'Extracting information from creature => {complement.replace("/wiki/", "").replace("_", " ")}')

  page = req.get(BASE_URL + complement)

  soup = bs(page.content, 'html.parser')

  table = soup.find('table', {'class': 'infobox-main'})

  table_all_tr = table.find_all('tr')

  behavior = {}
  loot = {}
  local_existence = []
  habilities = {}

  for tr in table_all_tr:
    td = tr.find('td')

    try:
      if td.text.strip() == 'Habilidades:':

        td_parent_divs = td.parent.find_all('div')

        if MESSAGE:
          if COLOR:
            print(f"\t{colored('Extracting habilidades:', attrs=['bold'], on_color='on_yellow')}")
          else:
            print(f'\tExtracting habilidades:')

        if len(td_parent_divs) == 0:
          formated = unidecode.unidecode(td.parent.text.strip().replace('\n', '')).replace('Habilidades:', '').split(',')
          habilities = {'list': [f.strip() for f in formated]}

        if MESSAGE:
          for hab in formated:
            if COLOR:
              print(f"\t\t{colored(hab, color='yellow', attrs=['bold'])}")
            else:
              print(f"\t\t{hab}")

        else:
          __ = []
          for _ in td_parent_divs:
            hab_arr = _.text.strip().replace(';', ',').split(':')
            formated = unidecode.unidecode(hab_arr[1].strip().replace('\n', '')).split(',')
            formated = [ f.strip() for f in formated]
            __.append({unidecode.unidecode(hab_arr[0]): formated})

          habilities['object'] = __

          if MESSAGE:
            for obj in habilities['object']:
              for k, v in obj.items():
                if COLOR:
                  print(f"\t\t{colored(k, color='yellow', attrs=['bold'])} => ")
                else:
                  print(f'\t\t{k} =>')
                for i in v:
                  if COLOR:
                    print(f"\t\t\t{colored(i, color='grey', attrs=['bold'])}")
                  else:
                    print(f'\t\t\t{i}')
    except:
      if MESSAGE:
        print(f'failed to get habilities from {complement.replace("/wiki/", "")}')

    try:
      if td.text.strip() == 'Localização:':
        for _ in td.parent.find_all('a'):
          local_existence.append(_.text.strip())

        if MESSAGE:
          if COLOR:
            print(f'\t{colored("Extracting localização:", on_color="on_red", attrs=["bold"])}')
          else:
            print(f'\tExtracting localização:')

        if MESSAGE:
          for loc in local_existence:
            if COLOR:
              print(f"\t\t{colored(loc, color='red', attrs=['bold'])}")
            else:
              print(f'\t\t{loc}')
    except:
      if MESSAGE:
        print(f'failed to get local existence from {complement.replace("/wiki/", "")}')

    try:
      if td.text.strip() == 'Loot:':

        try:
          table_tr = td.parent.find('table').find('tbody').find_all('tr')
          loot_arr = []
          for _ in range(0, len(table_tr), 2):
            loot_arr.append({LOOT_DICT_VALUES[table_tr[_].text[:-1]] : table_tr[_ - 1].text.strip().replace('*', '')})

          loot['object'] = loot_arr

          if MESSAGE:
            if COLOR:
              print(f"\t{colored('Extracting loot:', on_color='on_blue', attrs=['bold'])}")
            else:
              print(f"\tExtracting loot:")

          if MESSAGE:
            for obj in loot['object']:
              for k, v in obj.items():
                if COLOR:
                  print(f"\t\t{colored(k, 'blue', attrs=['bold'])} => {colored(v, 'cyan', attrs=['bold'])}")
                else:
                  print(f"\t\tExtracting loot: {k} => {v}")
        except:
          if MESSAGE:
            if COLOR:
              print(f"\t{colored('Extracting loot:', on_color='on_blue', attrs=['bold'])}")
            else:
              print(f"\tExtracting loot:")

          loot['list'] = unidecode.unidecode(td.parent.text.strip().replace('\n', ' ').replace('\u00a0', '').replace('Loot:  ', ''))

          if MESSAGE:
            for i in loot['list'].split(','):
              if COLOR:
                print(f"\t\t{colored(i.strip(), 'cyan', attrs=['bold'])}")
              else:
                print(f"\t\t{i}")

    except:
      if MESSAGE:
        print(f'failed to get loot from {complement.replace("/wiki/", "")}')

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
      
      if MESSAGE:
        print(f"\t{colored('Extracting behavior: ', on_color='on_magenta', attrs=['bold'])}")

      if MESSAGE:
        for k, v in behavior.items():
          if COLOR:
            print(f"\t\t{colored(k, 'magenta', attrs=['bold'])} => {colored(v, 'white', attrs=['bold'])}")
          else:
            print(f'\tExtracting behavior: {k} => {v}')

  return behavior, loot, local_existence, habilities


def parse_tr(tr):
  global DICT_VALUES
  row = []
  c = 0

  behavior = {}
  loot = {}

  for td in tr.find_all('td'):
    if c == 0:
      a = td.find('a', href=True)['href']
      behavior, loot, existence, habilities = monster_own_page(a)

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
        row.append('---')
    
    if c == 5:
      try:
        _ = DICT_VALUES[td.find('img', alt=True)['alt'].strip()]
        row.append(_)
      except:
        row.append('---')
    
    c += 1

  row.append(behavior)
  row.append(loot)
  row.append(existence)
  row.append(habilities)

  return row


if __name__ == '__main__':

  if '--nocolor' in sys.argv:
    COLOR = False
  if '--nomsg' in sys.argv:
    MESSAGE = False

  page = req.get(URL)

  soup = bs(page.content, 'html.parser')

  table_by_id = soup.find_all(id='tabelaDPL')

  data = []

  default = {}

  for tab in table_by_id:
    table_header = tab.find_all('th')

    table_header = [ _ for _ in table_header if _.text.strip() != 'Loot' ]

    for _ in tab.find_all('small'):
      _.clear()

    table_tr = tab.find_all('tr')

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
    default['Local'] = ''
    default['Habilities'] = ''

    for tr in table_tr[1:]:
      data.append(dict(zip(default, list(parse_tr(tr)))))

  with open('creatures_list.json', 'w') as file:
    json.dump(data, file, indent=4)