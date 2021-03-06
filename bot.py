import telebot
from telebot import types
import json
import os
# import os.path as path

# activated = true

# Abrir cosas

with open("./bot.token", "r") as token:
  bot = telebot.TeleBot(token.readline().strip()) # Strip elimina mierda que se pueda colar en el token 


with open('./data/admins.json', 'r') as adminData:
    admins = json.load(adminData)


    
adictos_a_croissants = "./data/subscribers.json"
# historico = "./data/historico.json"



global lista_compra # Lista en texto para admin
lista_compra = []


global adictos_en_lista_compra # Lista para notificación
adictos_en_lista_compra = []


# User tracking
global adictos_en_tramite
adictos_en_tramite = {} 


global adictos_no_contestados
adictos_no_contestados = []



def isAdmin_fromPrivate(message):
    if message.chat.type == 'private':
        userID = message.from_user.id
        if str(userID) in admins:
            return True
        return False


def notificarAdictos():
  with open(adictos_a_croissants, "r+") as subscribersRaw:
      subscribers_list = json.load(subscribersRaw)
  [replyToQuestion(adict) for adict in subscribers_list]  
  return

def notificarAdictosCompra():
  [avisar_final(adict) for adict in adictos_no_contestados]  
  [mensaje_compra(adict) for adict in adictos_en_lista_compra]  
  return


def replyToQuestion(adict):
  adictos_no_contestados.append(adict)
  markup = types.ReplyKeyboardMarkup()
  markup.one_time_keyboard = True
  markup.row('¡SÍ!')
  markup.row('¡NO, PESADA!')
  adictos_en_tramite[adict] = 1 # El adicto ha progresado al nivel 1
  bot.send_message(adict, "¿Croissant?", reply_markup=markup)

def mensaje_compra(adict):
  bot.send_message(adict, "Los Croissants van de camino ;)")

def avisar_final(adict):
  bot.send_message(adict, "Demasiado tarde, la compra ha acabado.")
  


### cosas de comandos
      
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # import ipdb; ipdb.set_trace()
  bot.send_message(message.chat.id, "¡Hola *" + message.from_user.first_name + "*!\nTe doy la bienvenida al mejor bot de la historia: Le Croissant. Disfruta la experiencia\n/help", parse_mode="Markdown")

  
# Lista de comandos      
@bot.message_handler(commands=['help'])
def send_help(message):
  bot.send_message(message.chat.id, "Hola!\n Los comandos que puedes usar son:\n/help\n/subscribe\n/horario\n/unsubscribe")
  
@bot.message_handler(commands=['subscribe'])
def send_subscr(message):
  if not os.path.isfile(adictos_a_croissants):
    with open(adictos_a_croissants, "w") as subscribers:
      subscribers.write(json.dumps([str(message.from_user.id)]))
      subscribers.close()
      bot.send_message(message.chat.id, "Has sido añadido a la lista de suscriptores a noticias sobre croissants. ¡Enhorabuena!")
  else:
    with open(adictos_a_croissants, "r+") as subscribersRaw:
      subscribers_list = json.load(subscribersRaw)
      if str(message.from_user.id) in subscribers_list:
        bot.send_message(message.chat.id, "Pero si ya estás en la lista, Caesa!!!!")
        print (message.from_user.id)
        subscribersRaw.close()
      else:
        subscribers_list.append(str(message.chat.id))
        bot.send_message(message.chat.id, "Has sido añadido a la lista de suscriptores a noticias sobre croissants. ¡Enhorabuena!")
        os.remove(adictos_a_croissants)
        with open(adictos_a_croissants, "w") as subscribers:
          subscribers.write(json.dumps(subscribers_list))
        subscribers.close()      
       

# Esto aun no sirve de nada pero me gusta el nombre
@bot.message_handler(commands=['croissantDay'])
def send_msssg(message):
    bot.send_message(message.chat.id, "Día de Croissants")


# Horario de la panadería
@bot.message_handler(commands=['horario'])
def horarios(message):
    bot.send_message(message.chat.id, "Horario de la Panadería:\nLunes - Viernes: 07:30 - 21:30\nSábados: 09:00 - 16:00\nDomingos y festivos: 09:00 - 21:00")

  
# Ya se verá si se implementa esto algún día, por ahora supongo que nadie querrá salir de la lista nunca.    
@bot.message_handler(commands=['unsubscribe'])
def send_goodbye(message):
    bot.send_message(message.chat.id, "Los croissants no te echarán de menos\n\n(de todas maneras esta función no está implementada..ups)")


# Cuando un admin va a ir a la Panadería, esto notifica a todos los suscriptores.
@bot.message_handler(commands=['croissant'])
def croissant_notif(message):
    if isAdmin_fromPrivate(message):
      bot.reply_to(message,
                   "Lanzando ofrecimiento de dulce felicidad en forma de Croissant Supremo...")
      
      notificarAdictos()
    else:
      bot.reply_to(message, "No intentes suplantar al proveedor de Croissants")

      
@bot.message_handler(commands=['compra'])
def compra_notif(message):
  if isAdmin_fromPrivate(message):
    notificarAdictosCompra()
    bot.reply_to(message, "Avisando de compra.... \nRecomendado /reset")
  else:
    bot.reply_to(message, "No intentes suplantar al proveedor de Croissants")

      
@bot.message_handler(commands=['reset'])
def compra_notif(message):
  if isAdmin_fromPrivate(message):
    
    adictos_en_tramite = {}
    lista_compra = []
    adictos_en_lista_compra = []
    adictos_no_contestados = []
    bot.reply_to(message, "Reiniciando listas......")
  else:
    bot.reply_to(message, "No intentes suplantar al proveedor de Croissants")

  

##### RESPUESTA NIVEL 1
@bot.message_handler(func=lambda message: str(message.from_user.id) in adictos_en_tramite.keys() and adictos_en_tramite[str(message.from_user.id)] == 1)
# @bot.message_handler(func=lambda message: adictos_en_tramite[message.from_user.id] == 1)
def respuesta_niv1(message):
  respuesta = message.text
  adictL1 = str(message.from_user.id)
  adictos_no_contestados.remove(adictL1)
  if (respuesta == '¡SÍ!'):
    markup2 = types.ReplyKeyboardMarkup()
    markup2.one_time_keyboard = True
    markup2.row('1')
    markup2.row('2')
    markup2.row('MUCHOS MÁS')
    adictos_en_tramite[adictL1] = 2 # El adicto ha progresado al nivel 2
    bot.send_message(adictL1, "¿Cuántos?", reply_markup=markup2)
  else:
    adictos_en_tramite.pop(adictL1)
    bot.send_message(adictL1, ":(")
  

@bot.message_handler(func=lambda message: str(message.from_user.id) in adictos_en_tramite.keys() and adictos_en_tramite[str(message.from_user.id)] == 2)
# @bot.message_handler(func=lambda message: adictos_en_tramite[message.from_user.id] == 1)
def respuesta_niv2(message):
  respuesta = message.text
  adictL2 = str(message.from_user.id)
  if (respuesta == '1'):
    adictos_en_lista_compra.append(adictL2)
    lista_compra.append(str(message.from_user.first_name) + " 1")
    bot.send_message(6419832, "Lista de la compra\n:" + '\n'.join(lista_compra))
    bot.send_message(adictL2, "¡Apuntado!")
  elif (respuesta == '2'):
    adictos_en_lista_compra.append(adictL2)
    lista_compra.append(str(message.from_user.first_name) + " 2")
    bot.send_message(6419832, "Lista de la compra:\n" + '\n'.join(lista_compra))
    bot.send_message(adictL2, "¡Apuntado!")
  elif (respuesta == 'MUCHOS MÁS'):
    adictos_en_lista_compra.append(adictL2)
    lista_compra.append(str(message.from_user.first_name) + " 2")
    bot.send_message(6419832, "Lista de la compra:\n" + '\n'.join(lista_compra))
    bot.send_message(adictL2, "Mejor ponte en contacto con @palome directamente")
  adictos_en_tramite.pop(adictL2)

                
# users_tracked.pop(uid)      


### AVISAR COMPRADO


print("Running....")
bot.polling()
