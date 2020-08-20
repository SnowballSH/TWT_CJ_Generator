# GUI using pygame

# Imports
import json

import pygame
# import os
from pygame.locals import *

import compiler

pygame.font.init()

# Variables

FPS = 120

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

GREY = (198, 214, 198)

SEA_GREEN = (0, 255, 197)

BLOCK_FONT = pygame.font.SysFont("lemon", 20)
OPTION_FONT = pygame.font.SysFont("lemon", 20)


class Block:
    def __init__(self, x, y, w, h, colour, name, func=None, textdraw=True):
        # defining variables
        self.color = colour
        self.x = x
        self.y = y
        self.orig_w = w
        self.w = w
        self.h = h
        self.name = name
        self.func = func
        self.textdraw = textdraw

        # renders the name and calls class TextInput
        self.text = BLOCK_FONT.render(name, True, BLACK)
        self.text_input = TextInput(self.x + self.w - 85, self.y + self.h - 45, 80, 40)

    def draw(self, win, x, y):
        # draws the block and the text box if you define textdraw as true
        pygame.draw.rect(win, self.color, (x, y, self.w, self.h))
        if self.textdraw:
            self.text_input.render()
            self.text_input.draw(win, self.x + self.w - 85, self.y + self.h - 45)
        win.blit(self.text, (self.x + 4, self.y + 4))

    def moving(self, win, x, y):
        # draws when everything is being moved
        pygame.draw.rect(win, self.color, (x, y, self.w, self.h))
        self.text_input.moving(win, x + self.w - 85, y + self.h - 45)
        win.blit(self.text, (x + 4, y + 4))

    def clicked(self, pos):
        # makes checking for clicking easier
        x, y = pos
        if self.x < x < self.x + self.w and self.y < y < self.y + self.h:
            return True
        return False

    def __lt__(self, other):
        return self.y < other.y


class TextInput:
    def __init__(self, x, y, w, h):
        # defines all variables for text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = ""
        self.rendered_text = None
        self.render()

    def render(self):
        # renders the text
        self.rendered_text = []
        textlist = []
        for i in range(len(self.text) // 10 + 1):
            textlist.append("")
        for index, letter in enumerate(self.text):
            lindex = index // 10
            textlist[lindex] = textlist[lindex] + letter

        for text in textlist:
            self.rendered_text.append(OPTION_FONT.render(text, True, BLACK))

    def draw_text(self, win, x, y):
        # draws rendered text
        for index, text in enumerate(self.rendered_text):
            win.blit(text, (x + 4, y + 4 + index * 10))

    def draw(self, win, x, y):
        # draws text box
        self.x, self.y = x, y
        pygame.draw.rect(win, WHITE, (self.x, self.y, self.w, self.h))
        self.draw_text(win, self.x, self.y)

    def moving(self, win, x, y):
        # moves text box around when it doesn't stay there
        pygame.draw.rect(win, WHITE, (x, y, self.w, self.h))
        self.draw_text(win, x, y)

    def clicked(self, pos):
        # makes checking if something is clicked easier
        x, y = pos
        if self.x < x < self.x + self.w and self.y < y < self.y + self.h:
            return True
        return False


# this class saves all of the blocks that are displayed
class Tree:
    def __init__(self):
        # defines the list where all blocks of a certain "tree" are saved
        self.blocks = []
        self.len = len(self.blocks)

    def append(self, block):
        # defining appending
        self.blocks.append(block)
        self.len = len(self.blocks)

    def remove(self, block):
        # defining removing
        self.blocks.remove(block)
        self.len = len(self.blocks)

    def as_dict(self):
        d = {}
        self.blocks = sorted(self.blocks)
        for i, b in enumerate(self.blocks):
            # if b.func == 'input':
            #     b.text_input.text = b.text_input.text.replace("'", r"\'")
            #     d.update({f"{b.func}{i}": {"prompt": f"{b.text_input.text} ", "pos": [b.x, b.y], "size": [b.w, b.h],
            #                                "color": b.color, "name": b.name}})
            # else:
            d.update({f"{b.func}{i}": {"args": {"text": b.text_input.text}, "pos": [b.x, b.y], "size": [b.w, b.h],
                                       "color": b.color, "name": b.name}})

        return d


def main():
    def draw():
        win.fill(GREY)  # creates background colour

        for d_block in code.blocks:  # draws all blocks inside code. MUST STAY HERE BECAUSE OF THE MOVING SYSTEM
            d_block.draw(win, d_block.x, d_block.y)

        # covers any blocks that might have been moved outside code box
        win.fill(GREY, (0, 0, 350, height))
        # pygame.draw.rect(win, GREY, (width * 0.7, 0, width * 0.3, height))

        # draws the basic layout
        pygame.draw.rect(win, BLACK, (350, 0, 10, height))
        # pygame.draw.rect(win, BLACK, (width * 0.7, 0, 10, height))

        # draws all of the blocks you can choose
        for d_block in which_options:
            d_block.draw(win, d_block.x, d_block.y)

        # draws buttons for choosing which options do you want
        for d_block in options.blocks:
            d_block.draw(win, d_block.x, d_block.y)

        # draws the moving block
        for d_block in moving.blocks:
            p_x, p_y = pygame.mouse.get_pos()
            d_block.moving(win, p_x, p_y)

        # draws clear button
        pygame.draw.rect(win, GREEN, (50, height - 55, 200, 50))
        clear = OPTION_FONT.render("Clear or Delete All Blocks", True, BLACK)
        win.blit(clear, (clear.get_width() / 2 - 10, height - 45 + clear.get_height() / 2))

        pygame.display.update()

    # basic setup
    width, height = 1000, 600

    run = True
    clock = pygame.time.Clock()

    win = pygame.display.set_mode((width, height), flags=RESIZABLE)  # or fullscreen if wanted for smaller screens :P
    pygame.display.set_caption("Visual Python - Code Generator")

    # defining all the variables
    bif = Tree()
    bif.append(Block(50, 100, 200, 50, GREEN, "print", "print"))
    bif.append(Block(50, 155, 200, 50, BLUE, "input", "input"))

    ope = Tree()
    ope.append(Block(50, 100, 200, 50, RED, "sum (not functional)", "comment"))
    ope.append(Block(50, 155, 200, 50, RED, "subtract (not functional)", "comment"))
    ope.append(Block(50, 210, 200, 50, RED, "multiply (not functional)", "comment"))
    ope.append(Block(50, 265, 200, 50, RED, "division (not functional)", "comment"))

    var = Tree()
    var.append(Block(50, 100, 200, 50, GREEN, "assign_var (not functional)", "comment"))
    var.append(Block(50, 155, 200, 50, GREEN, "call_var (not functional)", "comment"))

    options = Tree()
    options.append(Block(40, 25, 120, 30, SEA_GREEN, "built-in-func", textdraw=False))
    options.append(Block(180, 25, 120, 30, SEA_GREEN, "operators", textdraw=False))
    options.append(Block(40, 60, 120, 30, SEA_GREEN, "variables", textdraw=False))

    moving = Tree()
    code = Tree()

    try:
        with open("blocks.json", "r") as f:
            data = json.load(f)
        for func, args in data.items():
            func = "".join([i for i in func if i.isalpha()])
            code.append(Block(*args['pos'], *args['size'], args['color'], args['name'], func))
            # if func == 'print':
            #     code.blocks[-1].text_input.text = args["args"][1:-1]
            # if func == 'input':
            #     code.blocks[-1].text_input.text = args["prompt"][1:-1]
            # else:
            code.blocks[-1].text_input.text = args["args"]["text"]
    except Exception:
        with open("blocks.json", "w") as f:
            f.write("{}")

    which_options = bif.blocks
    option = 0

    flying = False
    typing = False

    movecode = False

    xold, yold = pygame.mouse.get_pos()

    flyingblock = None
    typing_block = None

    while run:
        clock.tick(FPS)
        draw()

        # moves code around
        if pygame.mouse.get_pressed()[0] and movecode:
            # checks if you are holding mouse button (movecode is defined in event for loop)
            xnew, ynew = pygame.mouse.get_pos()  # takes current mouse position
            for number in range(len(code.blocks)):  # moves every block that is considered code
                code.blocks[number].x += xold - xnew
                code.blocks[number].y += yold - ynew
        xold, yold = pygame.mouse.get_pos()  # saves current mouse position so you can follow the move of the mouse

        # changes movecode to False everytime that mouse isn't pressed
        if not pygame.mouse.get_pressed()[0]:
            movecode = False

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                win = pygame.display.set_mode((width, height), flags=RESIZABLE)

            # clicking
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # clearing all blocks
                if (50 < x < 250) and (height - 55 < y < height - 5):
                    code = Tree()

                # moving code part
                # if 350 < x < width * 0.7: #checks that mouse click was inside code box
                movecode = True
                for block in code.blocks:  # checks that you didn't click on any of the code blocks
                    if block.clicked(pygame.mouse.get_pos()):
                        movecode = False

                if flying:
                    # while flying is equal to True, everytime when you click it checks that
                    # you clicked inside code box and appends it into code Tree
                    for block in moving.blocks:
                        # if 350 < x < width * 0.7:
                        code.append(Block(x, y, block.w, block.h, block.color, block.name, block.func))
                        code.blocks[-1].text_input.text = block.text_input.text

                    moving = Tree()
                    flying = False

                # after every click sets typing to False and then checks if you clicked on textbox
                typing = False
                for block in code.blocks:
                    if block.text_input.clicked((x, y)):
                        typing = True
                        typing_block = block
                    # checks if you clicked any other part of the block
                    elif block.clicked((x, y)):
                        code.blocks.remove(block)
                        flying = True
                        flyingblock = block

                if not flying:  # checks if any of the available blocks was clicked
                    for block in which_options:
                        if block.clicked((x, y)):
                            flying = True
                            flyingblock = block

                if flying:
                    moving.blocks.append(flyingblock)

                if not typing:
                    for index, block in enumerate(options.blocks):
                        # checks if any of the options buttons was clicked
                        # and changes option accordingly
                        if block.clicked((x, y)):
                            option = index
                            break
                    # variable which_options gets defined for further use of options
                    if option == 0:
                        which_options = bif.blocks
                    elif option == 1:
                        which_options = ope.blocks
                    elif option == 2:
                        which_options = var.blocks

            # writing inside functions
            elif event.type == pygame.KEYDOWN and typing:
                ti = typing_block.text_input
                if event.key == pygame.K_RETURN:  # if enter is pressed writing ends
                    typing = False
                elif event.key == pygame.K_BACKSPACE:  # deleting letters
                    ti.text = ti.text[:-1]
                else:  # every time you time text gets added
                    ti.text += event.unicode

                ti.render()  # renders the output
                ti.draw(win, ti.x, ti.y)  # draws the output

    pygame.quit()

    with open("blocks.json", "w") as j:
        # print(code.as_dict())
        json.dump(code.as_dict(), j, indent=2)
    with open("blocks.json", "r") as j:
        compiler.test_case(json.load(j))


main()
