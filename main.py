import pygame, random, sys, time
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ---------------- Load Images ----------------
def load_img(path, size=None):
    img = pygame.image.load(BASE_DIR / path).convert_alpha()
    if size: img = pygame.transform.scale(img, size)
    return img

async def main():
    pygame.init()

    # ---------------- Window ----------------
    WIDTH, HEIGHT = 1000, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Miner Dungeon RPG - Raids")
    clock = pygame.time.Clock()

    # ---------------- Fonts ----------------
    font = pygame.font.SysFont(None, 26)
    big_font = pygame.font.SysFont(None, 36)

    background = load_img("background.png", (WIDTH, HEIGHT))
    miner_img = load_img("miner.png", (120, 120))
    bat_img = load_img("bat.png", (100, 100))
    diamond_img = load_img("diamond.png", (50, 50))
    emerald_img = load_img("emerald.png", (50, 50))
    ruby_img = load_img("ruby.png", (55, 55))
    sapphire_img = load_img("sapphire.png", (60, 60))
    gem_boss_img = load_img("ruby.png", (120, 120))

    # ---------------- Player ----------------
    player = pygame.Rect(100, 300, 120, 120)
    player_health = 100
    player_max_health = 100
    player_flash = 0
    money = 0
    dead = False

    # ---------------- Pickaxes ----------------
    pickaxes = {
        "Iron": {"cost": 100, "one_shot": ["diamond"]},
        "Diamond": {"cost": 300, "one_shot": ["diamond","emerald"]},
        "Gold": {"cost": 600, "one_shot": ["diamond","emerald","ruby"]},
        "Sapphire": {"cost": 1000, "one_shot": ["diamond","emerald","ruby","sapphire"]}
    }
    current_pickaxe = None
    purchased_pickaxes = set()

    # ---------------- Swords ----------------
    swords = {
        "Wood": {"cost": 50, "damage": 1},
        "Iron": {"cost": 150, "damage": 3},
        "Diamond": {"cost": 400, "damage": 6},
        "Gold": {"cost": 800, "damage": 10},
        "Sapphire": {"cost": 1000, "damage": 2000}
    }
    current_sword = "Wood"
    purchased_swords = {"Wood"}

    # ---------------- Ores ----------------
    ores = []
    spawn_timer = 0
    emerald_unlocked = False
    ruby_unlocked = False
    sapphire_unlocked = False
    inventory = {"diamond":0,"emerald":0,"ruby":0,"sapphire":0}

    def spawn_ore():
        possible = ["diamond"]
        if emerald_unlocked: possible.append("emerald")
        if ruby_unlocked: possible.append("ruby")
        if sapphire_unlocked: possible.append("sapphire")
        ore_type = random.choice(possible)
        if ore_type == "diamond": hp = 3; value = 10; img = diamond_img
        elif ore_type == "emerald": hp = 10; value = 45; img = emerald_img
        elif ore_type == "ruby": hp = 200; value = 500; img = ruby_img
        else: hp = 2000; value = 5000; img = sapphire_img
        rect = pygame.Rect(random.randint(200, 900), random.randint(50, 500), img.get_width(), img.get_height())
        ores.append({"type": ore_type, "rect": rect, "hp": hp, "max_hp": hp, "value": value, "img": img, "flash":0})

    for _ in range(8): spawn_ore()

    # ---------------- Bats & Raids ----------------
    bats = []
    raid_number = 1
    bats_per_raid = 3
    gem_boss_alive = False
    prepping = False
    prep_start_time = 0
    prep_duration = 30

    def spawn_bat(is_boss=False):
        if is_boss:
            rect = pygame.Rect(random.randint(300, 700), random.randint(50, 400), 120, 120)
            hp = 500
            bats.append({"rect": rect, "hp": hp, "flash": 0, "boss":True})
        else:
            rect = pygame.Rect(random.randint(300, 900), random.randint(50, 500), 100, 100)
            hp = 5 + raid_number*2
            bats.append({"rect": rect, "hp": hp, "flash": 0, "boss":False})

    for _ in range(bats_per_raid): spawn_bat()

    # ---------------- Shop ----------------
    shop_open = False
    shop_width = 280
    shop_x = WIDTH
    buy_flash = {}
    toggle_btn = pygame.Rect(WIDTH-50, 10, 40, 40)
    shop_scroll = 0

    # ---------------- Restart Button ----------------
    restart_btn = pygame.Rect(WIDTH-150, 50, 130, 40)

    # ---------------- Restart Function ----------------
    def restart_game():
        nonlocal player_health, player_flash, money, current_pickaxe, current_sword
        nonlocal purchased_pickaxes, purchased_swords, emerald_unlocked, ruby_unlocked, sapphire_unlocked
        nonlocal inventory, spawn_timer, raid_number, bats_per_raid, gem_boss_alive
        nonlocal prepping, prep_start_time, dead
        dead = False

        # Player
        player.x, player.y = 100, 300
        player_health = player_max_health
        player_flash = 0
        money = 0

        # Inventory & Pickaxes/Swords
        current_pickaxe = None
        current_sword = "Wood"
        purchased_pickaxes = set()
        purchased_swords = {"Wood"}

        # Unlocks
        emerald_unlocked = False
        ruby_unlocked = False
        sapphire_unlocked = False

        # Ores
        ores.clear()
        for _ in range(8): spawn_ore()
        spawn_timer = 0
        inventory = {"diamond":0,"emerald":0,"ruby":0,"sapphire":0}

        # Bats & Raids
        bats.clear()
        raid_number = 1
        bats_per_raid = 3
        gem_boss_alive = False
        prepping = False
        prep_start_time = 0

    # ---------------- Main Loop ----------------
    running = True
    while running:
        clock.tick(60)
        mx,my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running=False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Toggle Shop
                if toggle_btn.collidepoint(mx,my): shop_open = not shop_open

                # Scroll
                if shop_open:
                    if event.button == 4: shop_scroll = max(shop_scroll-20,0)
                    if event.button == 5: shop_scroll += 20

                # Hit ores
                for ore in ores:
                    if ore["rect"].collidepoint(mx,my):
                        if current_pickaxe and ore["type"] in pickaxes.get(current_pickaxe,{}).get("one_shot",[]):
                            ore["hp"] = 0
                        else:
                            ore["hp"] -= 1
                        ore["flash"]=5
                        if ore["hp"] <= 0:
                            inventory[ore["type"]] += 1
                            ores.remove(ore)
                            spawn_ore()
                        break

                # Hit bats
                for bat in bats:
                    if bat["rect"].collidepoint(mx,my):
                        bat["hp"] -= swords[current_sword]["damage"]
                        bat["flash"]=10
                        if bat["hp"] <= 0:
                            reward = 15 + swords[current_sword]["damage"]
                            if bat.get("boss"): reward = 1000
                            money += reward
                            if bat.get("boss"): gem_boss_alive = False
                            bats.remove(bat)
                        break

                # Shop buttons
                if shop_open and shop_x < WIDTH:
                    content_y = 120 - shop_scroll
                    # Pickaxes
                    for name in pickaxes:
                        if name in purchased_pickaxes: continue
                        btn = pygame.Rect(shop_x+20, content_y, 240, 35)
                        if btn.collidepoint(mx,my) and money >= pickaxes[name]["cost"]:
                            money -= pickaxes[name]["cost"]
                            current_pickaxe = name
                            purchased_pickaxes.add(name)
                            buy_flash[name]=6
                        content_y += 45
                    # Swords
                    for name in swords:
                        if name in purchased_swords: continue
                        btn = pygame.Rect(shop_x+20, content_y, 240, 35)
                        if btn.collidepoint(mx,my) and money >= swords[name]["cost"]:
                            money -= swords[name]["cost"]
                            current_sword = name
                            purchased_swords.add(name)
                            buy_flash[name+"_sword"]=6
                        content_y += 45
                    # Unlock emerald
                    if not emerald_unlocked:
                        btn = pygame.Rect(shop_x+20, content_y, 240, 35)
                        if btn.collidepoint(mx,my) and money >= 100:
                            money -= 100; emerald_unlocked=True; buy_flash["emerald"]=6
                        content_y += 45
                    # Unlock ruby
                    if not ruby_unlocked:
                        btn = pygame.Rect(shop_x+20, content_y, 240, 35)
                        if btn.collidepoint(mx,my) and money >= 250:
                            money -= 250; ruby_unlocked=True; buy_flash["ruby"]=6
                        content_y += 45
                    # Unlock sapphire
                    if not sapphire_unlocked:
                        btn = pygame.Rect(shop_x+20, content_y, 240, 35)
                        if btn.collidepoint(mx,my) and money >= 1000:
                            money -= 1000; sapphire_unlocked=True; buy_flash["sapphire"]=6
                        content_y += 45

                    # Sell Inventory
                    sell_btn = pygame.Rect(shop_x+20, HEIGHT-70, 240, 50)
                    if sell_btn.collidepoint(mx,my):
                        total = inventory["diamond"]*10 + inventory["emerald"]*45 + inventory["ruby"]*500 + inventory["sapphire"]*5000
                        money += total
                        for k in inventory: inventory[k]=0
                        buy_flash["sell"]=6

                # Restart Button
                if restart_btn.collidepoint(mx,my):
                    restart_game()

        # ---------------- Random Spawns ----------------
        spawn_timer +=1
        if spawn_timer > 180:
            spawn_ore(); spawn_timer=0

        # ---------------- Shop Animation ----------------
        target_x = WIDTH-shop_width if shop_open else WIDTH
        shop_x += (target_x - shop_x)/5

        # ---------------- Move Bats ----------------
        for bat in bats:
            if bat["rect"].x < player.x: bat["rect"].x += 1
            if bat["rect"].x > player.x: bat["rect"].x -= 1
            if bat["rect"].y < player.y: bat["rect"].y += 1
            if bat["rect"].y > player.y: bat["rect"].y -= 1
            if bat["rect"].colliderect(player):
                player_health -= 0.2
                player_flash = 5

        # ---------------- Raids ----------------
        if not bats and not prepping:
            prepping = True
            prep_start_time = time.time()

        # ---------------- Draw Background ----------------
        screen.blit(background,(0,0))

        # ---------------- Draw Raid Info ----------------
        if prepping:
            prep_remaining = max(0, int(prep_duration - (time.time() - prep_start_time)))
            raid_text = big_font.render(f"Raid {raid_number} starting in {prep_remaining}s", True, (255,255,0))
            screen.blit(raid_text, (WIDTH//2 - raid_text.get_width()//2, 10))
            if prep_remaining <= 0:
                prepping=False
                if raid_number % 15 == 0 and not gem_boss_alive:
                    spawn_bat(is_boss=True)
                    gem_boss_alive=True
                else:
                    for _ in range(3 + raid_number):
                        spawn_bat()
                raid_number += 1
        else:
            raid_text = big_font.render(f"Raid {raid_number}", True, (255,255,0))
            screen.blit(raid_text, (WIDTH//2 - raid_text.get_width()//2, 10))

        # ---------------- Draw Ores ----------------
        for ore in ores:
            img = ore["img"].copy()
            if ore["flash"]>0:
                img.fill((255,0,0), special_flags=pygame.BLEND_MULT)
                ore["flash"] -= 1
            screen.blit(img, ore["rect"].topleft)
            hp_text = font.render(str(ore["hp"]), True, (255,255,255))
            screen.blit(hp_text, (ore["rect"].x+10, ore["rect"].y-20))

        # ---------------- Draw Bats ----------------
        for bat in bats:
            img = gem_boss_img if bat.get("boss") else bat_img
            if bat["flash"]>0:
                red = img.copy()
                red.fill((255,0,0), special_flags=pygame.BLEND_MULT)
                screen.blit(red, bat["rect"].topleft)
                bat["flash"] -= 1
            else:
                screen.blit(img, bat["rect"].topleft)
            max_hp = 500 if bat.get("boss") else 5 + raid_number*2
            pygame.draw.rect(screen,(255,0,0),(bat["rect"].x, bat["rect"].y-10, bat["rect"].width,5))
            pygame.draw.rect(screen,(0,255,0),(bat["rect"].x, bat["rect"].y-10, bat["rect"].width*(bat["hp"]/max_hp),5))

        # ---------------- Draw Player ----------------
        if player_flash>0:
            red = miner_img.copy()
            red.fill((255,0,0), special_flags=pygame.BLEND_MULT)
            screen.blit(red, player.topleft)
            player_flash -=1
        else:
            screen.blit(miner_img, player.topleft)
        pygame.draw.rect(screen,(255,0,0),(player.x, player.y-15, player.width,10))
        pygame.draw.rect(screen,(0,255,0),(player.x, player.y-15, player.width*(player_health/player_max_health),10))

        # ---------------- Draw Money ----------------
        money_text = big_font.render(f"Money: ${int(money)}", True, (255,255,0))
        screen.blit(money_text, (20,50))

        # ---------------- Draw Restart Button ----------------
        pygame.draw.rect(screen, (180,50,50), restart_btn)
        pygame.draw.rect(screen, (0,0,0), restart_btn,3)
        screen.blit(font.render("RESTART", True, (255,255,255)), (restart_btn.x+20, restart_btn.y+10))

        # ---------------- Draw Shop ----------------
        pygame.draw.rect(screen,(100,70,40),(shop_x,0,shop_width,HEIGHT))
        title = big_font.render("SHOP", True,(255,255,255))
        screen.blit(title,(shop_x+90,40))
        pygame.draw.rect(screen,(150,120,80),toggle_btn)
        pygame.draw.rect(screen,(50,25,0),toggle_btn,3)
        screen.blit(font.render("≡",True,(0,0,0)),(toggle_btn.x+10,toggle_btn.y+5))

        # Shop items scroll
        content_y = 120 - shop_scroll
        for name in pickaxes:
            if name not in purchased_pickaxes:
                btn = pygame.Rect(shop_x+20, content_y, 240, 35)
                color=(130,100,60)
                if name in buy_flash: color=(90,70,50)
                pygame.draw.rect(screen,color,btn)
                pygame.draw.rect(screen,(50,25,0),btn,3)
                screen.blit(font.render(f"{name} Pickaxe (${pickaxes[name]['cost']})",True,(255,255,255)),(btn.x+10,btn.y+5))
                content_y += 45
        for name in swords:
            if name not in purchased_swords:
                btn = pygame.Rect(shop_x+20, content_y, 240, 35)
                color=(80,80,120)
                if name+"_sword" in buy_flash: color=(50,50,90)
                pygame.draw.rect(screen,color,btn)
                pygame.draw.rect(screen,(50,25,0),btn,3)
                screen.blit(font.render(f"{name} Sword (${swords[name]['cost']})",True,(255,255,255)),(btn.x+10,btn.y+5))
                content_y += 45
        # Emerald / Ruby / Sapphire unlock buttons
        if not emerald_unlocked:
            btn = pygame.Rect(shop_x+20, content_y, 240, 35)
            color = (50,150,50)
            if "emerald" in buy_flash: color=(30,100,30)
            pygame.draw.rect(screen,color,btn)
            pygame.draw.rect(screen,(50,25,0),btn,3)
            screen.blit(font.render("Unlock Emerald ($100)", True, (255,255,255)), (btn.x+10, btn.y+5))
            content_y += 45
        if not ruby_unlocked:
            btn = pygame.Rect(shop_x+20, content_y, 240, 35)
            color = (150,50,50)
            if "ruby" in buy_flash: color=(100,30,30)
            pygame.draw.rect(screen,color,btn)
            pygame.draw.rect(screen,(50,25,0),btn,3)
            screen.blit(font.render("Unlock Ruby ($250)", True, (255,255,255)), (btn.x+10, btn.y+5))
            content_y += 45
        if not sapphire_unlocked:
            btn = pygame.Rect(shop_x+20, content_y, 240, 35)
            color = (50,50,200)
            if "sapphire" in buy_flash: color=(30,30,120)
            pygame.draw.rect(screen,color,btn)
            pygame.draw.rect(screen,(50,25,0),btn,3)
            screen.blit(font.render("Unlock Sapphire ($1000)", True, (255,255,255)), (btn.x+10, btn.y+5))
            content_y += 45

        # Sell button
        sell_btn = pygame.Rect(shop_x+20, HEIGHT-70, 240, 50)
        color = (200,180,120)
        if "sell" in buy_flash: color = (180,150,0)
        pygame.draw.rect(screen, color, sell_btn)
        pygame.draw.rect(screen,(50,25,0),sell_btn,3)
        screen.blit(font.render("SELL INVENTORY", True, (0,0,0)), (sell_btn.x+40, sell_btn.y+10))

        # Reduce buy flash timers
        for key in list(buy_flash.keys()):
            buy_flash[key]-=1
            if buy_flash[key]<=0: del buy_flash[key]

        if player_health <= 0:
            dead = True

        if dead:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))  # semi-transparent black
            screen.blit(overlay, (0,0))
            game_over_text = big_font.render("YOU DIED", True, (255,0,0))
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))

        pygame.display.flip()
        await asyncio.sleep(0)  # yield control to the browser event loop (required for pygbag/Pyodide)

asyncio.run(main())