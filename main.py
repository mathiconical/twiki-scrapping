import requests as req
import unidecode
import sys
import json
import time
from psutil import cpu_count
from multiprocessing.dummy import Pool as ThreadPool

from termcolor import colored
from bs4 import BeautifulSoup as bs


COLOR = False
MESSAGE = True
MAX_THREAD = (cpu_count() // cpu_count(logical=False)) * cpu_count()
THREAD = MAX_THREAD // 2

URL = 'https://www.tibiawiki.com.br/wiki/Lista_de_Criaturas'
BASE_URL = 'https://www.tibiawiki.com.br'


def monster_own_page(complement):

  if MESSAGE:
    if COLOR:
      print(f'{colored("Extracting information from creature", on_color="on_green", attrs=["bold"])} => {colored(complement.replace("/wiki/", "").replace("_", " "), color="green", attrs=["bold"])}')
    else:
      print(f'Extracting information from creature => {complement.replace("/wiki/", "").replace("_", " ")}')

  page = req.get(BASE_URL + complement)

  soup = bs(page.content, 'html.parser')

  table = soup.find('table', {'class': 'infobox-main'})

  table_all_tr = table.find_all('tr')

  behavior = {
    'RunWithLowLife': False,
    'CanBlockRespawn': False,
    'Melee': False,
    'RunWithLowLife': False,
    'MeleeAndRange': False,
    'Range': False,
    'JustRun': False,
  }

  loot = {
    'canOpenCorpse': False,
    'dropLoots': False,
    'drop': []
  }

  for tr in table_all_tr:
    td = tr.find('td')

    try:
      if td.text.strip() == 'Loot:':

        try:
          table_tr = td.parent.find('table').find('tbody').find_all('tr')
          _loot = []
          timiras_phrase = False
          for _ in range(0, len(table_tr), 2):
            __ = unidecode.unidecode(table_tr[_ - 1].text.strip().replace('*', '').replace('\u00a0', '').replace('.', ''))

            if 'Não pode ser aberto' in __ or 'Nao pode ser aberto' in __:
              loot['canOpenCorpse'] = False
              loot['dropLoots'] = False
            elif 'Nenhum.' in __:
              loot['canOpenCorpse'] = True
              loot['dropLoots'] = False
            elif 'Nada.' in __:
              loot['canOpenCorpse'] = True
              loot['dropLoots'] = False
            elif 'loot cai' in __ or 'loot dropa' in __:
              loot['canOpenCorpse'] = True
              loot['dropLoots'] = False
            else:
              loot['canOpenCorpse'] = True
              loot['dropLoots'] = True

            if '(loot unico por personagem, sempre cai na primeira vez que matar o boss)' in __:
              timiras_phrase = True

            _loot = [
              *[
                k.strip()
                .replace('(loot unico por personagem', '')
                .replace('sempre cai na primeira vez que matar o boss)', '')
              for k in __.split(',')], *_loot ]
            
          if timiras_phrase:
            _loot.pop(_loot.index('Naga Basin') + 1)

          loot['drop'] = _loot

          if MESSAGE:
            if COLOR:
              print(f"\t{colored('Extracting loot:', on_color='on_blue', attrs=['bold'])}")
            else:
              print(f"\tExtracting loot:")

          if MESSAGE:
            for item in loot:
              if COLOR:
                print(f"\t\t{colored(item, 'cyan', attrs=['bold'])}", end=', ')
              else:
                print(f"\t\tExtracting loot: {item}", end=', ')
        except:
          if MESSAGE:
            if COLOR:
              print(f"\t{colored('Extracting loot:', on_color='on_blue', attrs=['bold'])}")
            else:
              print(f"\tExtracting loot:")

          _ = unidecode.unidecode(td.parent.text.strip().replace('\n', ' ').replace('\u00a0', '').replace('Loot:  ', '').replace('*', ''))

          if 'Não pode ser aberto' in _ or 'Nao pode ser aberto' in _:
            loot['canOpenCorpse'] = False
            loot['dropLoots'] = False
          elif 'Nenhum.' in _:
            loot['canOpenCorpse'] = True
            loot['dropLoots'] = False
          elif 'Nada.' in _:
            loot['canOpenCorpse'] = True
            loot['dropLoots'] = False
          elif 'loot cai' in _ or 'loot dropa' in _:
            loot['canOpenCorpse'] = True
            loot['dropLoots'] = False
          else:
            loot['canOpenCorpse'] = True
            loot['dropLoots'] = True
          
          loot['drop'] = [f.strip().replace('.', '').replace('(raro)', '').replace('(semi-raro)', '').replace('(muito raro)', '') for f in _.split(',')]

          if MESSAGE:
            for item in loot.split(','):
              if COLOR:
                print(f"\t\t{colored(item.strip(), 'cyan', attrs=['bold'])}")
              else:
                print(f"\t\t{item}")

    except:
      if MESSAGE:
        print(f'failed to get loot from {complement.replace("/wiki/", "")}')

    if td.text.strip() == 'Comportamento:':
      _ = td.parent.text.strip().replace('\n', '')

      if 'Foge com a vida baixa' in _:
        behavior['RunWithLowLife'] = True

      if 'Não é possível bloquear o respawn dessa criatura' in _:
        behavior['CanBlockRespawn'] = False

      if 'Combate corpo a corpo' in _:
        behavior['Melee'] = True

      if 'É possível bloquear o respawn dessa criatura' in _:
        behavior['CanBlockRespawn'] = True

      if 'Luta até a morte' in _:
        behavior['RunWithLowLife'] = True

      if 'Combate corpo a corpo e à distância' in _:
        behavior['MeleeAndRange'] = True

      if 'Combate à distância' in _ or 'corpo a corpo e à distância' in _:
        behavior['Range'] = True

      if 'Eles sempre irão correr e não atacam' in _:
        behavior['JustRun'] = True
      
      if MESSAGE:
        if COLOR:
          print(f"\t{colored('Extracting behavior: ', on_color='on_magenta', attrs=['bold'])}")
        else:
          print(f"\tExtracting behavior:")

      if MESSAGE:
        for k, v in behavior.items():
          if COLOR:
            print(f"\t\t{colored(k, 'magenta', attrs=['bold'])} => {colored(v, 'white', attrs=['bold'])}")
          else:
            print(f'\tExtracting behavior: {k} => {v}')

  return behavior, loot


def parse_tr(tr):
  row = []
  c = 0

  behavior = {}
  loot = {}

  permited = [0, 2, 3]

  for td in tr.find_all('td'):
    if c in permited:
      if c == 0:
        a = td.find('a', href=True)['href']
        behavior, loot = monster_own_page(a)

      _ = td.text.strip().replace('\n', ' ').replace('\u2010', '').replace('\u221e', '')

      if _ in ['--', '0', '?']:
        _ = None

      row.append(_)

    c += 1

  row.append(behavior)
  row.append(loot)

  return row


if __name__ == '__main__':

  print('Consider type --help to see more details about this program.')
  time.sleep(2)

  try:
    if '--color' in sys.argv:
      COLOR = True
    if '--nomsg' in sys.argv:
      MESSAGE = False
    if '--help' in sys.argv:
      print('--color      => turn color mode on (only windows console)')
      print('--nomsg      => turn off messages.')
      print('--thread X   => where X is the number of threads.')
      print(f'                NOTE: Your maximum thread is {MAX_THREAD}')
      print(f'                NOTE: Your DEFAULT thread is {THREAD}')
    if '--thread' in sys.argv:
      try:
        THREAD = int(sys.argv[sys.argv.index('--thread') + 1])
        if THREAD > MAX_THREAD:
          print(f'Your machine maximum thread is {MAX_THREAD}, setting your input of {THREAD} to {MAX_THREAD}.')
          THREAD = MAX_THREAD
        if THREAD <= 0:
          print(f'Setting your input of {THREAD} to default {MAX_THREAD // 2}.')
          THREAD = MAX_THREAD // 2
      except:
        raise ValueError(f'Error on get number of thread on arg \'--thread X\' where \'X\' need to be a int.')
  except ValueError as err:
    print(repr(err.args[0]))
    print('--color     => turn color mode on (only windows console)')
    print('--nomsg     => turn off messages.')
    print('--thread X  => where X is the number of threads to thread the requests (DEFAULT is 4)')
    print('               NOTE: exist more than 1.500 creatures in the game, this thread will be slower if thread is 1.')
    exit()

  print('PROGRAM WILL RUN WITH PARAMS')
  print(f'color   : {COLOR}')
  print(f'message : {MESSAGE}')
  print(f'threads : {THREAD}')

  time.sleep(4)

  page = req.get(URL)

  soup = bs(page.content, 'html.parser')

  table_by_id = soup.find_all(id='tabelaDPL')

  data = []

  default = {
    'Criatura': '',
    'HP': '',
    'EXP': '',
    'Behavior': '',
    'Loot': ''
  }

  temp_table_tr = []

  for tab in table_by_id:
    table_header = tab.find_all('th')

    table_header = [ _ for _ in table_header if _.text.strip() != 'Loot' ]

    for _ in tab.find_all('small'):
      _.clear()
  
    table_tr = tab.find_all('tr')

    temp_table_tr.append(table_tr)

  all_table_tr = temp_table_tr[0] + temp_table_tr[1] + temp_table_tr[2] + temp_table_tr[3]

  all_table_tr = all_table_tr[:]

  pool = ThreadPool(THREAD)

  res = pool.map(parse_tr, all_table_tr)
  pool.close()
  pool.join()
  
  res = [k for k in res]
  res = res[1:]

  data = [dict(zip(default, k)) for k in res]

  with open('creatures_list.json', 'w') as file:
    json.dump(data, file, indent=4)