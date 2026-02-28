import pygame, sys, random, time
pygame.init()

# ----- Window -----
WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Abandoned Mine")
clock = pygame.time.Clock()

# ----- Assets -----
background = pygame.transform.scale(pygame.image.load("mine_bg.jpg").convert(), (WIDTH, HEIGHT))
player_img = pygame.transform.scale(pygame.image.load("miner.png").convert_alpha(), (100, 100))
diamond_img = pygame.transform.scale(pygame.image.load("diamond.png").convert_alpha(), (32, 32))
emerald_img = pygame.transform.scale(pygame.image.load("emerald.png").convert_alpha(), (32, 32))
ruby_img = pygame.transform.scale(pygame.image.load("ruby.png").convert_alpha(), (32, 32))

# Pickaxe icons
iron_img = pygame.Surface((32, 32)); iron_img.fill((180,180,180))
diamond_pick_img = pygame.Surface((32, 32)); diamond_pick_img.fill((0,255,255))
gold_pick_img = pygame.Surface((32, 32)); gold_pick_img.fill((255,215,0))

# ----- Player -----
player = {"x":WIDTH//2, "y":HEIGHT//2, "speed":5, "rect":pygame.Rect(WIDTH//2, HEIGHT//2, 100, 100)}
swing_timer = 0

# ----- Pickaxes -----
pickaxes = {
    "wood":{"damage":1, "price":0, "icon":None},
    "iron":{"damage":3, "price":50, "icon":iron_img},
    "diamond":{"damage":15, "price":200, "icon":diamond_pick_img},
    "gold":{"damage":30, "price":500, "icon":gold_pick_img}
}
current_pickaxe = "wood"

# ----- Unlocks -----
ore_unlocked = {"emerald":False,"ruby":False,"mutations":False}
mutation_colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255)]

# ----- Ores -----
ores = []
def spawn_ore():
    rnd = random.random()
    if ore_unlocked["ruby"] and rnd < 0.1:
        val = 150
        if ore_unlocked["mutations"]: val = int(val*random.uniform(1.2,2.0))
        return {"type":"ruby","hp":25,"max":25,"value":val,"img":ruby_img,"rect":pygame.Rect(0,0,32,32),"mutated_color":None}
    if ore_unlocked["emerald"] and rnd < 0.3:
        val = 50
        if ore_unlocked["mutations"]: val = int(val*random.uniform(1.2,2.0))
        return {"type":"emerald","hp":15,"max":15,"value":val,"img":emerald_img,"rect":pygame.Rect(0,0,32,32),"mutated_color":None}
    val = 10
    if ore_unlocked["mutations"]: val = int(val*random.uniform(1.2,2.0))
    return {"type":"diamond","hp":3,"max":3,"value":val,"img":diamond_img,"rect":pygame.Rect(0,0,32,32),"mutated_color":None}

for _ in range(8):
    o = spawn_ore()
    o["x"]=random.randint(60, WIDTH-60)
    o["y"]=random.randint(80, HEIGHT-60)
    o["rect"].x = o["x"]
    o["rect"].y = o["y"]
    ores.append(o)

# ----- Economy -----
inventory = {"diamond":0,"emerald":0,"ruby":0}
money = 0

# ----- UI -----
font = pygame.font.SysFont("trebuchetms",20)
bold_font = pygame.font.SysFont("arialblack",28)
small_font = pygame.font.SysFont("trebuchetms",16)
TEXT = (220,200,160)
BUTTON_BG = (200,180,120)
BUTTON_ACTIVE = (180,150,0)
menu_open = False
menu_width = 280
menu_x = WIDTH
toggle_btn = pygame.Rect(WIDTH-40,10,30,30)
shop_scroll = 0

# ----- Buttons -----
button_list=[
    {"text":"Buy Iron Pickaxe $50","action":"buy_iron","icon":iron_img,"unlocked":True,"purchased":False},
    {"text":"Unlock Emerald $100","action":"unlock_emerald","icon":emerald_img,"unlocked":True,"purchased":False},
    {"text":"Buy Diamond Pickaxe $200","action":"buy_diamond","icon":diamond_pick_img,"unlocked":False,"purchased":False},
    {"text":"Unlock Ruby $300","action":"unlock_ruby","icon":ruby_img,"unlocked":False,"purchased":False},
    {"text":"Buy Gold Pickaxe $500","action":"buy_gold","icon":gold_pick_img,"unlocked":False,"purchased":False},
    {"text":"Buy Mutations $1000","action":"mutations","icon":None,"unlocked":False,"purchased":False},
]
sell_button_data = {"text":"Sell Inventory","action":"sell","clicked_time":0}

# ----- Popups -----
popups = []

# ----- Functions -----
def move_player():
    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_d]-keys[pygame.K_a])*player["speed"]
    dy = (keys[pygame.K_s]-keys[pygame.K_w])*player["speed"]
    player["rect"].x += dx
    for ore in ores:
        if player["rect"].colliderect(ore["rect"]):
            if dx>0: player["rect"].right=ore["rect"].left
            if dx<0: player["rect"].left=ore["rect"].right
    player["rect"].y += dy
    for ore in ores:
        if player["rect"].colliderect(ore["rect"]):
            if dy>0: player["rect"].bottom=ore["rect"].top
            if dy<0: player["rect"].top=ore["rect"].bottom
    player["x"] = player["rect"].x
    player["y"] = player["rect"].y

def mine_ore():
    global swing_timer
    swing_timer=10
    dmg = pickaxes[current_pickaxe]["damage"]
    mouse = pygame.mouse.get_pos()
    for ore in ores[:]:
        if ore["rect"].collidepoint(mouse):
            ore["hp"] -= dmg
            if ore["hp"]<=0:
                inventory[ore["type"]] += 1
                popups.append({"x":ore["x"],"y":ore["y"],"text":f"+{ore['value']}", "time":time.time()})
                ores.remove(ore)
                new = spawn_ore()
                new["x"] = random.randint(60, WIDTH-60)
                new["y"] = random.randint(80, HEIGHT-60)
                new["rect"].x = new["x"]
                new["rect"].y = new["y"]
                if ore_unlocked["mutations"]: new["mutated_color"]=random.choice(mutation_colors)
                ores.append(new)
            break

def handle_menu_click(pos):
    global money, current_pickaxe, ore_unlocked
    for b in button_list+[sell_button_data]:
        if "rect" in b and b["rect"].collidepoint(pos):
            action = b["action"]
            if action=="buy_iron" and money>=50 and not b["purchased"]:
                money-=50; current_pickaxe="iron"; b["purchased"]=True
            elif action=="unlock_emerald" and money>=100 and not b["purchased"]:
                money-=100; ore_unlocked["emerald"]=True; b["purchased"]=True
            elif action=="buy_diamond" and money>=200 and not b["purchased"]:
                money-=200; current_pickaxe="diamond"; b["purchased"]=True
            elif action=="unlock_ruby" and money>=300 and not b["purchased"]:
                money-=300; ore_unlocked["ruby"]=True; b["purchased"]=True
            elif action=="buy_gold" and money>=500 and not b["purchased"]:
                money-=500; current_pickaxe="gold"; b["purchased"]=True
            elif action=="mutations" and money>=1000 and not b["purchased"]:
                money-=1000; ore_unlocked["mutations"]=True; b["purchased"]=True
                for o in ores: o["mutated_color"]=random.choice(mutation_colors)
            elif action=="sell":
                total=inventory["diamond"]*10+inventory["emerald"]*50+inventory["ruby"]*150
                money+=total
                for k in inventory: inventory[k]=0
                sell_button_data["clicked_time"]=time.time()
    # Unlock dependent shop items
    for b in button_list:
        if b["action"]=="buy_diamond" and ore_unlocked["emerald"] and any(bt["action"]=="buy_iron" and bt["purchased"] for bt in button_list):
            b["unlocked"]=True
        if b["action"]=="unlock_ruby" and current_pickaxe=="diamond":
            b["unlocked"]=True
        if b["action"]=="buy_gold" and ore_unlocked["ruby"] and any(bt["action"]=="buy_diamond" and bt["purchased"] for bt in button_list):
            b["unlocked"]=True
        if b["action"]=="mutations": b["unlocked"]=True

def draw_ui(menu_x):
    mouse = pygame.mouse.get_pos()
    money_text = bold_font.render(f"${money}",True,(255,255,0))
    screen.blit(money_text,(20,15))
    screen.blit(font.render(f"Pickaxe: {current_pickaxe}",True,TEXT),(20,50))
    pygame.draw.rect(screen,(60,50,30),(10,200,140,160))
    pygame.draw.rect(screen,(255,255,255),(10,200,140,160),2)
    screen.blit(small_font.render("INVENTORY",True,(255,255,255)),(30,205))
    screen.blit(diamond_img,(20,235)); screen.blit(small_font.render(f"x{inventory['diamond']}",True,(255,255,255)),(60,240))
    screen.blit(emerald_img,(20,265)); screen.blit(small_font.render(f"x{inventory['emerald']}",True,(255,255,255)),(60,270))
    if ore_unlocked["ruby"]: screen.blit(ruby_img,(20,295)); screen.blit(small_font.render(f"x{inventory['ruby']}",True,(255,255,255)),(60,300))
    pygame.draw.rect(screen,(180,140,90),toggle_btn); screen.blit(small_font.render("≡",True,(0,0,0)),(toggle_btn.x+8,toggle_btn.y+4))
    pygame.draw.rect(screen,(80,60,40),(menu_x,50,280,460))
    screen.blit(font.render("SHOP",True,(0,0,0)),(menu_x+100,55))
    scroll_area = pygame.Surface((240,300)); scroll_area.fill((60,50,30))
    for i,b in enumerate(button_list):
        if b["unlocked"] and not b["purchased"]:
            rect = pygame.Rect(0,i*60-shop_scroll,240,50)
            if rect.bottom>=0 and rect.top<=300:
                btn_font = small_font
                text_width, _ = btn_font.size(b["text"])

                # ---- SAFE FONT SHRINK (FIXED) ----
                font_size = 16  # start size

                while text_width > rect.width - 60 and font_size > 8:
                    font_size -= 1
                    btn_font = pygame.font.SysFont(None, font_size)  # <-- SAFE
                    text_width, _ = btn_font.size(b["text"])
                pygame.draw.rect(scroll_area,BUTTON_BG,rect)
                scroll_area.blit(btn_font.render(b["text"],True,(0,0,0)),(rect.x+60,rect.y+15))
                if b["icon"]: scroll_area.blit(b["icon"],(rect.x+10,rect.y+10))
            b["rect"]=pygame.Rect(menu_x+20+rect.x,60+rect.y,rect.width,rect.height)
    screen.blit(scroll_area,(menu_x+20,60))
    sell_rect=pygame.Rect(menu_x+20,400,240,50)
    if time.time()-sell_button_data["clicked_time"]<0.1: pygame.draw.rect(screen,BUTTON_ACTIVE,sell_rect)
    else: pygame.draw.rect(screen,BUTTON_BG,sell_rect)
    screen.blit(small_font.render(sell_button_data["text"],True,(0,0,0)),(sell_rect.x+60,sell_rect.y+15))
    sell_button_data["rect"]=sell_rect
    # ore hover values
    for ore in ores:
        if ore["rect"].collidepoint(mouse):
            val_text=small_font.render(f"Value: {ore['value']}",True,(255,255,0))
            pygame.draw.rect(screen,(0,0,0),(mouse[0],mouse[1]-20,val_text.get_width()+4,val_text.get_height()+4))
            screen.blit(val_text,(mouse[0]+2,mouse[1]-18))
    # popups
    for popup in popups[:]:
        elapsed = time.time()-popup["time"]
        if elapsed>1: popups.remove(popup)
        else:
            alpha = int(255*(1-elapsed))
            temp_surf = small_font.render(popup["text"],True,(255,255,0))
            temp_surf.set_alpha(alpha)
            screen.blit(temp_surf,(popup["x"],popup["y"]-elapsed*30))

# ----- Main Loop -----
while True:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type==pygame.QUIT: pygame.quit(); sys.exit()
        if e.type==pygame.MOUSEBUTTONDOWN:
            if e.button==1:
                if toggle_btn.collidepoint(e.pos): menu_open = not menu_open
                handle_menu_click(e.pos)
                mine_ore()
            if e.button==4: shop_scroll = max(shop_scroll-20,0)
            if e.button==5: shop_scroll += 20
    # smooth shop
    target_x = WIDTH-280 if menu_open else WIDTH
    menu_x += (target_x - menu_x)/5
    move_player()
    screen.blit(background,(0,0))
    for ore in ores:
        img=ore["img"].copy()
        if ore_unlocked["mutations"] and ore.get("mutated_color"): img.fill(ore["mutated_color"])
        screen.blit(img,(ore["x"],ore["y"]))
        hp_text=pygame.font.SysFont("trebuchetms",16).render(str(ore["hp"]),True,(255,255,255))
        screen.blit(hp_text,(ore["x"],ore["y"]-15))
    draw_img = player_img
    if swing_timer>0: draw_img=pygame.transform.rotate(player_img,15); swing_timer-=1
    screen.blit(draw_img,(player["x"],player["y"]))
    draw_ui(menu_x)
    pygame.display.flip()
    