import requests # https://docs.python-requests.org/en/v2.0.0/
from bs4 import BeautifulSoup as bs # https://tedboy.github.io/bs4_doc/
import re
import pandas as pd
import time

###########
# Functions
###########

# Recibes URL on BS parsed html 
def parse_url_to_bs_html(url):
  """
  Input -> string: url
  Output -> Beutiful Soap HTML Parsed object
  """
  return bs(requests.get(url).text, "html.parser")

# Recibes a Query and makes URL for it  
def generate_link(query):
  """
  Input -> string: Query
  Output -> string: mercado libre URL for that query
  """ 
  query_splited= query.split()
  query_html="%19".join(query_splited)
  query_line="-".join(query_splited)
  url="https://listado.mercadolibre.com.ar/"+query_line+"#D[A:"+query_html+"]"
  return url

#######################
# Printing each element of a query link
#######################

def finder(url,number,query):
  # Gets starting time
  current_time = time.localtime()
  date, hour = [str(current_time.tm_mday) + "/" + str(current_time.tm_mon) + "/" + str(current_time.tm_year), str(current_time.tm_hour) + ":" + str(current_time.tm_min)] 

  # Incrementator for page counter
  current_page_number = number+1

  # Parses the utl
  html = parse_url_to_bs_html(url)

  # List of items in the current page
  items_on_page = html.find_all("li", attrs = {"class":"ui-search-layout__item"})

  for x in items_on_page:
    # Gets product page URL
    product_url = x.find("a", attrs = {"class":"ui-search-link"})["href"]

    # Request to product page
    product_page = parse_url_to_bs_html(product_url)

    # Name
    title = product_page.find("h1",attrs = {"class":"ui-pdp-title"}).text
    print("\n" + title)

    # Price
    price = x.find("span", attrs = {"class":"andes-money-amount__fraction"}).text.replace(".", "")
    print("Precio: $", price)

    # URL printing
    print("Product URL: ",product_url)

    # Try to product ID, when it fails, is bc is not on the page. we still not founding how to scrap it in another way
    try:
      product_id = product_page.find("span", attrs = {"class":"ui-pdp-color--BLACK ui-pdp-family--SEMIBOLD"}).text
    except:
      product_id = "No Disponible"
    print("Product ID: ", product_id)

    # Try to get vendor's name, when it fails is because it is not on the page (rare) or it did't loaded well, so it retries ten times/until it gets the value.
    try:
      product_vendor_name = re.sub("\?brandId=\d*$","", product_page.find("a", attrs = {"target":"_blank","class":"ui-pdp-media__action ui-box-component__action"})["href"][35:])
      print("Vender Name: ", product_vendor_name)
    except:
      for _ in range(10):
        product_page = parse_url_to_bs_html(product_url)
        try:
          product_vendor_name = re.sub("\?brandId=\d*$","", product_page.find("a",attrs={"target":"_blank","class":"ui-pdp-media__action ui-box-component__action"})["href"][35:])
          print("Vender Name: ", product_vendor_name)
          break
        except:
          product_vendor_name = "error"
          print("We got problems getting vendors name :/")

    # After getting all the data, it appends it to the list of items for the dataframe
    list_of_items.append([title, price, product_url, product_id, product_vendor_name, date, hour])

    # Just because it looks cool...
    print("-"*9)

  # This finds the next page url on the page, so it can continue scrapping
  siguiente = html.find("a",attrs={"title":"Siguiente"})

  # If it founds the next page, recurses into it
  try:
    finder(siguiente["href"],current_page_number,query)
  # If it fails, is because there is not next page, so starts function ending...
  except:
    # Prints the amount of visited pages
    print("Numero de paginas visitadas",current_page_number)

    print("\nAgregando datos al dataframe...")

    # Crates dataframe and add items.
    data_frame=pd.DataFrame(list_of_items,columns=["Nombre","Precio","URL","ID","Vendedor","Fecha","Hora"])

    # Warning beacuse ID getter can fail (see up there on ID getting part for more info), so we ask if they want to keep the empty IDs
    print("\nPuede que existan articulos donde el ID no este disponible, por lo que puede resultarle inutil en el futuro si requiere esta informacion, desea ignorarlos??")
    response=input("SI/no [Por defecto si] ")

    # Menu for choosing keeping data or not
    while True:
      if len(response)==0 or response[0].lower() == "s":
        print("Seran ignorados")
        data_frame = data_frame.loc[data_frame["ID"] != "No Disponible"].reset_index(drop=True)
        break
      elif response[0].lower() == "n":
        print("Seran incluidos")
        break
      else:
        print("Respuesta erronea, reintentar")

    # Creation of the csv
    name = query.replace(" ","_")+"_"+str(current_time.tm_mday) +"-"+ str(current_time.tm_mon) +"-"+ str(current_time.tm_year)+"_"+str(current_time.tm_hour) +":"+ str(current_time.tm_min)
    data_frame.to_csv(name+".csv")

    # Closing message that apears when it succed
    print(f"\nDataframe guardado con exito con el nombre {name}")

#######################
# Main loop
#######################

print("""

                               _
  /\/\   ___ _ __ ___ __ _  __| | ___
 /    \ / _ \ '__/ __/ _` |/ _` |/ _ \
/ /\/\ \  __/ | | (_| (_| | (_| | (_) |
\/    \/\___|_|  \___\__,_|\__,_|\___/

   __ _ _
  / /(_) |__  _ __ ___   ___ ___  _ __ ___
 / / | | '_ \| '__/ _ \ / __/ _ \| '_ ` _ \
/ /__| | |_) | | |  __/| (_| (_) | | | | | |
\____/_|_.__/|_|  \___(_)___\___/|_| |_| |_|

                                  .......
                       .:^~7??JJJJYYYYYYYYJJJ??7!~:.
                  .^!?JYYJ??7!!!~~~~~~~~~~~~!!77?JJYYJ7~:
              .~?YYJ?7!~^^^^^~~~^^^~~~~~~~~^^^^^^^^~~!?JYY?~.
           .~JGP?!^^^^^~~~^^^^^~!?YYYYYYYYYYJ7!~~^^^^^^^^~7YGY!.
         .75J!?JYYYYJ?7!!!7?JY555?~:.    .:^7JY5YYJJJJJJYYYYJ7J5?:
        !PJ:     .^~!7?JJJ??PBY^   ^7JYYJ!:    .:^~!!!!~^:.    :?P7
      .JP^                !5J:  :75Y7^::~?5Y!.                   ^5Y.
      Y5.                .5P?7?Y5?^       .~J5J^                  .5Y
     !B7:..                :^~^:             .7557.             .:^7B!
     YGYY5YYJ?!^:                               ^J5J^     .^!?JY55YJGY
     YP^~~~!7?JY55J7^!77!:~~~.               .7^  .!5577JY5YJ?7!~~^^PY
     JB!^~~~^^^^~~7YBJ~^J5?7?PY??!.           ~JY!.  ^YB?!~^^^^~~~^7B?
     ^BP~^~~~~~~~~^!GJ::^    ~7^^JG:      .7~   ^J5?~~YP!^~~~~~~~^!GB^
      ?BP7^~~~~~~~~~!JJ5G^ .:    ~GYJ7. .  ^J5!.  ?#YJ7~~~~~~~~^^?GB7
       ?BBY!^^~~~~~~~^^~?5Y5G~..:...:YP.?Y~  ^PPYY5?~^^~~~~~~^~75BB7
        ~PBGY7~^^~~~~~~~^~~~?YY5G!..:YB~:!G5?J5J!~~^~~~~~^^^!?5BB5^
         .7PBBPY?!~^^^~~~~~~^^~~7YYYYJ?YYYJ?7!~^~~~~~^^^~!?5GBB5!.
           .!YGBBGPY?7!~~^^^^^^~^^~~^^^^^^^^^^^^^^~~!7J5PBBBGJ~
              :!JPBBBBGP5YJ?77!!~~~~~~~~~~!!!7??JYPGGBBBG5J~.
                 .:!?YPGBBBBBBBGGGGGPPGGGGGBBBBBBBBG5Y7~:
                      ..^~!7JJY55PPPPPPPP55YYJ?7!^:.
                                    ...

     __ _____
    / //  ___|
   / / \ `--.   ___  _ __   __ _  _ __   _ __    ___  _ __
  / /   `--. \ / __|| '__| / _` || '_ \ | '_ \  / _ \| '__|
 / /   /\__/ /| (__ | |   | (_| || |_) || |_) ||  __/| |
/_/    \____/  \___||_|    \__,_|| .__/ | .__/  \___||_|
                                 | |    | |
                                 |_|    |_|
""")
while True:
  print("""

    1) Buscar
    S) Salir

  """)

  response= input("Opcion elegida: ")
  if response=="1":
    list_of_items = []
    query = input("Inserte busqueda: ")
    finder(generate_link(query),0,query)
    input("ENTER para continuar")
    list_of_items = []

  elif response.lower()=="s":
    break
  else:
    print("Opcion desconocida")