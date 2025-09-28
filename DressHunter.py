from phBot import *
import os
import sqlite3
from time import time
from threading import Timer
import struct
import QtBind
import json

pName = 'Dress Hunter'
pVersion = '0.5'
gui = QtBind.init(__name__, pName)

name=None
gold=0
limitValue = 0
unit = 0
freeSlot = 0
goldSpent = 0
dropPot = False
mode = None
stop = False

goldLabel = QtBind.createLabel(gui, "Gold:                                         ", 10, 15)
freeSlo = QtBind.createLabel(gui, "Free Slot:                                         ", 160, 15)
limitLabel = QtBind.createLabel(gui, "Gold Limit:                                                                                  ", 10, 35)
goldSpnt = QtBind.createLabel(gui, "Gold Spent: 0                                                                                 ", 550, 13) # -------

cbDropPotion = QtBind.createCheckBox(gui, 'drop10xPot', "Drop Pot", 420, 13)

clear = QtBind.createButton(gui, 'clearLimit', 'Clear Limit', 212,70)
limit1 = QtBind.createButton(gui, 'btnAdd_1_limit', '1xAdd', 212,93)
limit10 = QtBind.createButton(gui, 'btnAdd_10_limit', '10xAdd', 212,116)
limit100 = QtBind.createButton(gui, 'btnAdd_100_limit', '100xAdd', 212,139)
maxLimit = QtBind.createButton(gui, 'btnAdd_max_limit', 'Max Limit', 212,162)


QtBind.createButton(gui, 'start', 'Start', 10,250)
QtBind.createButton(gui, 'stop_script', 'Stop', 85,250)

check = QtBind.createButton(gui, 'check', 'Check', 10,285)
QtBind.createButton(gui, 'openBox', 'Open Box', 85,285)
toGain = QtBind.createLabel(gui, 'To Gain: ', 75, 55)
avhieve = QtBind.createLabel(gui, 'Avhieve: ', 350, 55)

moonBox = QtBind.createList(gui, 10, 70, 200, 170)# What needs to be won > Kazanilmasi gerekenler
eAwards = QtBind.createList(gui, 288, 70, 200, 170)# Earned Awards > Kazanilan itemler

# Klasör ve dosya yolları
configDir = os.path.join(get_config_dir(), "DressHunter")
configFile = os.path.join(configDir, "configFile.json")


# Fonksiyonlar
def btnAdd_1_limit():
    update_Limit(1)

def btnAdd_10_limit():
    update_Limit(10)

def btnAdd_100_limit():
    update_Limit(100)
    
def btnAdd_max_limit():
    global gold,limitValue,unit
    unit = 0
    limitValue = 0
    maxLimit = int(gold/20000000)
    update_Limit(maxLimit)

def update_Limit(multiplier):
    global limitValue, unit
    increment = multiplier * 20_000_000
    limitValue += increment
    unit += multiplier
    
    if gold <= limitValue:
        log('o kadar gold yok')
        return
    # Nokta ile formatlı gösterim
    formatted = f"{limitValue:,}".replace(",", ".")
    QtBind.setText(gui, limitLabel, f"Gold Limit: {formatted}")

def clearLimit():
    global limitValue, unit
    limitValue = 0
    unit = 0
    formatted = f"{limitValue:,}".replace(",", ".")
    QtBind.setText(gui, limitLabel, f"Gold Limit: {formatted}")

def update_gold_label():
    gold = get_character_data()['gold']
    formatted = f"{gold:,}".replace(",", ".")
    QtBind.setText(gui, goldLabel, f"Gold: {formatted}")


if not os.path.exists(configDir):
    os.makedirs(configDir)

def userName():
    global name, gold
    data = get_character_data()
    name = data['name']
    gold = data['gold']
    return name


def inventory():
    global freeSlot
    freeSlot = 0
    invData = get_inventory()
    
    if not invData or 'items' not in invData:
        return
    
    inv = invData['items']
    if len(inv) < 1:
        return
    
    
    for slot, item in enumerate(inv): 
        if not item and slot > 16:
            freeSlot +=1
    QtBind.setText(gui, freeSlo, f"Free Slot: {freeSlot}")



rb1 = QtBind.createCheckBox(gui, 'radio_clicked1', "One by one   - ", 235, 13)
rb2 = QtBind.createCheckBox(gui, 'radio_clicked2', "Multiple", 333, 13)
radio_map = {1: rb1, 2: rb2}
def radio_clicked1(checked): radio_select(1)
def radio_clicked2(checked): radio_select(2)

def radio_select(index):
    global mode
    inventory()
    for rb in radio_map.values():
        QtBind.setChecked(gui, rb, False)

    if index in radio_map:
        mode = index
        QtBind.setChecked(gui, radio_map[index], True)
        if index < 2:
            log('The boxes will be taken and opened one by one.')
        else:
            log('The boxes will be collected and opened all together.')
def load_json():
    """JSON varsa oku, yoksa boş dict döndür"""
    if os.path.exists(configFile):
        try:
            with open(configFile, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(data):
    with open(configFile, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_current_list():
    global goldSpent, dropPot
    data = load_json()
    uname = userName()
    itemWon = QtBind.getItems(gui, eAwards)

    data[uname] = {
        "wonDress": itemWon,
        "goldSpent": goldSpent,
        "dropPotion": dropPot
    }
    save_json(data)

def load_saved_list():
    global goldSpentm, dropPot, goldSpent
    data = load_json()
    uname = userName()
    update_gold_label()
    inventory()
    
    if uname in data:
        char_data = data[uname]
        if "wonDress" in char_data:
            for item in char_data["wonDress"]:
                QtBind.append(gui, eAwards, item)
        
        if "goldSpent" in char_data:
            goldSpent = char_data.get("goldSpent", 0)
            QtBind.setText(gui, goldSpnt, f"Gold Spent: {goldSpent:,}".replace(",", "."))
        
        if "dropPotion" in char_data:
            dropPot = char_data.get("dropPotion", False)
            
            QtBind.setChecked(gui, cbDropPotion, dropPot)
        
def set_gold(value):
    global goldSpent
    goldSpent = value
    data = load_json()
    uname = userName()
    if uname in data:
        data[uname]["goldSpent"] = goldSpent
        save_json(data)
        update_gold_label()
        QtBind.setText(gui, goldSpnt, f"Gold Spent: {goldSpent:,}".replace(",", "."))

def dressWon(name):
    QtBind.append(gui, eAwards, name)
    save_current_list()
    log(f'BINGO >>> {name}')
    


def drop10xPot(checked):
    global dropPot
    if checked:
        dropPot = True
        log('MP & HP Recovery Potion (X-Large) will be dropped.')
    else:
        dropPot = False
        log('Drop Pot Disabled') 
        
    save_current_list()
    
    data = load_json()
    uname = userName()
    if uname in data:
        data[uname]["dropPotion"] = dropPot
        save_json(data)
        

items = [
    "Hussar Hat (M)",
    "Hussar Dress (M)",
    "Hussar Accessory (M)",
    "Hussar Hat (F)",
    "Hussar Dress (F)",
    "Hussar Accessory (F)",
    "Ninja Hat 2025 (M)",
    "Ninja Dress 2025 (M)",
    "Ninja Accessory 2025 (M)",
    "Ninja Hat 2025 (F)",
    "Ninja Dress 2025 (F)",
    "Ninja Accessory 2025 (F)",
    "Ottoman Emperor Hat (M)",
    "Ottoman Emperor Dress (M)",
    "Ottoman Emperor Accessory (M)",
    "Ottoman Emperor Hat (F)",
    "Ottoman Emperor Dress (F)",
    "Ottoman Emperor Accessory (F)",
    "Samurai Hat 2025 (M)",
    "Samurai Dress 2025 (M)",
    "Samurai Sword Accessory 2025 (M)",
    "Samurai Cloak Accessory 2025 (M)",
    "Samurai Hat 2025 (F)",
    "Samurai Dress 2025 (F)",
    "Samurai Sword Accessory 2025 (F)",
    "Samurai Cloak Accessory 2025 (F)",
    "Shaolin Monk Hat (M)",
    "Shaolin Monk Dress (M)",
    "Shaolin Monk Accessory (M)",
    "Shaolin Monk Hat (F)",
    "Shaolin Monk Dress (F)",
    "Shaolin Monk Accessory (F)",
    "HP Recovery Potion (X-Large)",
    "MP Recovery Potion (X-Large)"
]

for x in items:
    QtBind.append(gui, moonBox, x)

def check():
    userName()
    update_gold_label()
    log('Checked')

def npcGetId(npcName):
    npcs = get_npcs() or {}
    for uid, npc in npcs.items():
        if npc.get("name") == npcName:
            return uid
    return None

def start():
    global stop
    stop = False
    log('Good luck, Amigo! ☘')
    moonBoxBuy()



def moonBoxBuy():
    global unit, mode
    if not mode:
        log("You have to choose a mode > One by one OR Multiple")
        return

    npc_names = ['Grocery Trader Yeosun', 'Grocery Trader Saha']
    packet = None
    for npc in npc_names:
        uids = npcGetId(npc)
        if uids is None:
            continue

        packet = struct.pack('<I', uids)
    item = b'\x08\x01\x08\x01\x00' + packet
    
    Timer(0.5, lambda: inject_joymax(0x7045, packet, False)).start()
    Timer(1.0, lambda: inject_joymax(0x7046, packet + b'\x01', False)).start()

    if mode == 1:
        def oneBox():
            global unit, stop, freeSlot
            if stop or freeSlot < 3:
                log('Stopped!')
                Timer(1.0, lambda: inject_joymax(0x704B, packet, False)).start()
                Timer(1.5, lambda: inject_joymax(0x704B, packet, False)).start()
                return
            if unit > 0:
                unit -= 1
                freeSlot -= 1
                Timer(1.0, lambda: inject_joymax(0x7034, item, False)).start()
                Timer(1.5, openBox).start()
                Timer(2.0, oneBox).start()
            else:
                log("Purchase Completed.")
                Timer(1.0, lambda: inject_joymax(0x704B, packet, False)).start()
                Timer(1.5, lambda: inject_joymax(0x704B, packet, False)).start()
                return
        oneBox() 
        
    elif mode == 2:
        def multiBox():
            global unit, stop, freeSlot
            if stop or freeSlot < 3:
                log('Stopped!')
                Timer(1.0, lambda: inject_joymax(0x704B, packet, False)).start()
                Timer(1.5, lambda: inject_joymax(0x704B, packet, False)).start()
                return
            if unit > 0:
                unit -= 1
                freeSlot -= 1
                Timer(1.0, lambda: inject_joymax(0x7034, item, False)).start()
                Timer(1.5, multiBox).start()
            else:
                log("Purchase Completed.")
                Timer(1.0, lambda: inject_joymax(0x704B, packet, False)).start()
                Timer(1.5, lambda: inject_joymax(0x704B, packet, False)).start()
                Timer(2.0, openBox).start()
                return
            # open box function0x704B
        multiBox()  

    
def slotMoonBox(itemId=None):
    inv = get_inventory().get('items', [])
    for slot, item in enumerate(inv):
        if not isinstance(item, dict):  # item dict değilse atla
            continue

        # Önce Moonlight Box kontrolü
        if slot > 16 and item.get('name') == "Moonlight Box":
            return slot

        # Sonra itemId kontrolü
        if itemId is not None and itemId == item.get('model'):
            name = item.get('name')
            dressWon(name)

    return None

def openBox():
    global dropPot
    slotmoon = slotMoonBox()
    if slotmoon is None:
        log("Moonlight Box is over.")
        Timer(1.5,sort_inventory).start()
        return
    if stop:
        log('Stopped')
        Timer(1.5,sort_inventory).start()
        return
        
    item = b'\x08' + bytes([slotmoon])
    
    Timer(1.0, lambda i=item: inject_joymax(0x7680, i, False)).start()
    Timer(1.5, openBox).start() 
    if dropPot:
        Timer(1.7, log_target_items).start()

def stop_script():
    global stop
    stop = True
    clearLimit()

def clear_all():
    uname = userName()
    data = load_json()

    QtBind.setText(gui, goldLabel, "Gold: 0")
    
    QtBind.setText(gui, goldSpnt, "Gold Spent: 0")

    QtBind.setText(gui, freeSlo, "Free Slot: 0")

    QtBind.setText(gui, limitLabel, "Gold Limit: 0")

    QtBind.setChecked(gui, cbDropPotion, False)

    if uname in data:
        del data[uname]
        save_json(data)

    log("All data have been cleared!")

btnClearAll = QtBind.createButton(gui, 'clear_all', 'Clear All', 610, 267)

def count_item(item_name):
    inventory = get_inventory()
    total = 0
    if inventory:
        for item in inventory['items']:
            if item and item['name'] == item_name:
                total += item['quantity']
    log(f"{item_name} total: {total} units")

    return total

target_items = [
    "HP Recovery Potion (X-Large)",
    "MP Recovery Potion (X-Large)"

]
item_queue = []
item_index = 0

def process_item_queue():
    global item_queue, item_index, dropPot

    if item_index >= len(item_queue):
        item_index = 0
        item_queue = []
        log('Dropped Complated')

    slot, name, quantity = item_queue[item_index]
    log(f"Slot {slot}: {name} x{quantity}")
    p = b'\x07' + bytes([slot])
    inject_joymax(0x7034, p, False)

    item_index += 1
    Timer(1.0, process_item_queue).start() 

def log_target_items():
    global item_queue, item_index
    inventory = get_inventory()
    if not inventory:
        log("Inventory empty.")
        return

    item_queue = []
    item_index = 0

    for slot, item in enumerate(inventory['items']):
        if item and any(item['name'] in t for t in target_items):
            item_queue.append((slot, item['name'], item['quantity']))

    if item_queue:
        process_item_queue()

def handle_joymax(opcode, data):
    global goldSpent

    if opcode == 0xB034 and data[1] == 8:
        log(str(data))
        goldSpent += 20000000
        set_gold(goldSpent)
        QtBind.setText(gui, goldSpnt, f"Gold Spent: {goldSpent:,}".replace(",", "."))

    if opcode == 0x3040:
        itemId = int.from_bytes(data[2:4], byteorder='little')
        if itemId > 15:
            slotMoonBox(itemId)

    return True
    
load_saved_list()

QtBind.createLabel(gui, f'🐱‍👤 By EzKime v.{pVersion}', 610, 297)
log(f'Plugin: {pName} Versiyon {pVersion} Yüklendi')
