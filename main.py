import pygame, sys, json, random

pygame.init()

#Initializing pygame
width = 1000
height = 640
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Two Zero Four Eight')

colors = json.load(open('colors.json', 'r'))

rows = cols = 4

res = 160
offset = 3

def generate_board(rows, cols):
    board = [[0 for j in range(cols)] for i in range(rows)]

    #Add random values in the beginning
    i = 0
    while i < 2:
        x = random.randrange(cols)
        y = random.randrange(rows)
        if board[y][x] == 0:
            board[y][x] = random.choice((2, 4))
            i += 1

    return board

def render_board(surface, board):
    #Font
    font = pygame.font.SysFont('comicsans', res//2)

    for i in range(rows):
        for j in range(cols):
            #Rendering background
            pygame.draw.rect(screen, (22, 19, 35), (j*res+offset, i*res+offset, res-offset*2, res-offset*2), border_radius=4)

            #Rendering colored box with number
            if board[i][j] > 0:
                try:
                    color = colors.get(str(board[i][j]))
                except:
                    color = colors.get("2")

                pygame.draw.rect(surface, color, (j*res+offset, i*res+offset, res-offset*2, res-offset*2), border_radius=4)

                #Rendering the number
                label = font.render(str(board[i][j]), 1, (22, 19, 35))
                surface.blit(label, (j*res+res//2-label.get_width()//2, i*res+res//2-label.get_height()//2))

def left(board, sound_effect=None):
    new_board = []
    total_score = 0
    for i in range(rows):
        #Sliding all numbers in the row
        row = slide(board[i], -1)

        #Combining all of them (if they are the same and adjacent to each other)
        row, scr = combine(row, sound_effect)
        total_score += scr

        #Sliding again (gives effect of two blocks becoming one)
        row = slide(row, -1)
        new_board.append(row)
    return new_board, total_score

def right(board, sound_effect=None):
    new_board = []
    total_score = 0
    for i in range(rows):
        #Sliding all numbers in the row
        row = slide(board[i], 1)

        #Combining all of them (if they are the same and adjacent to each other)
        row, scr = combine(row, sound_effect)
        total_score += scr

        #Sliding again (gives effect of two blocks becoming one)
        row = slide(row, 1)
        new_board.append(row)
    return new_board, total_score

def up(board, sound_effect=None):
    #Rotates board and runs left movement for the board
    board = rotate(board,-1)
    board, total_score = left(board, sound_effect)

    #Rotates it in the other direction to bring it back to normal
    board = rotate(board, 1)
    return board, total_score

def down(board, sound_effect=None):
    #Rotates board and runs right movement for the board
    board = rotate(board,-1)
    board, total_score = right(board, sound_effect)

    #Rotates it in the other direction to bring it back to normal
    board = rotate(board, 1)
    return board, total_score

def slide(row, dir):
    new_row = [n for n in row if n != 0]
    zeros = [0 for n in range(cols-len(new_row))]

    #Adding the zeros according to the direction
    if dir == -1:
        new_row += zeros
    if dir == 1:
        new_row = zeros+new_row

    return new_row

def combine(row, sound_effect):
    new_row = row.copy()
    scr = 0
    for i in range(rows-1, 0, -1):
        #Combines the numbers that are adjacent and equal
        if new_row[i] == new_row[i-1] and new_row[i] != 0:
            #Plays the combining sound effect
            if sound_effect:
                sound_effect.play()
            new_row[i] += new_row[i-1]
            scr += new_row[i]
            new_row[i-1] = 0

    return new_row, scr

def rotate(board, direction):
    #Rotates the 2d list
    new_board = []

    rows_range = range(rows-1, -1, -1)
    cols_range = range(cols)

    if direction == 1:
        rows_range = range(rows)
        cols_range = range(cols-1, -1, -1)

    for i in rows_range:
        row = []
        for j in cols_range:
            row.append(board[j][i])
        new_board.append(row)

    return new_board

def add_new(board, new_board):
    #Adds a number in any random free spot
    b = new_board.copy()
    if board != new_board:
        while True:
            x = random.randrange(cols)
            y = random.randrange(rows)
            if b[y][x] == 0:
                b[y][x] = random.choice((2, 4))
                break
    return b

def check(board):
    #Runs all the functions to see if there can be moves made yet
    for func in ['up', 'down', 'right', 'left']:
        function = globals()[func]
        b,score = function(board)

        if b != board:
            return False

    #If no moves left, then game over
    return True

def render_scores(score, highscore):
    #Renders the current score and highscore
    font = pygame.font.SysFont('arial', 30)

    highscore_label = font.render('Highscore: '+str(highscore), 1, (254, 254, 215))
    score_label = font.render('Score: '+str(score), 1, (254, 254, 215))

    screen.blit(highscore_label, (res*cols+10, 10))
    screen.blit(score_label, (res*cols+10, 12+highscore_label.get_height()))

def update_highscore(score, highscore):
    #If score is greater than the highscore, highscore is set to the current score and updating the highscore json file
    if highscore < score:
        highscore = score
        highscore_json = json.dumps(highscore)
        highscore_file = open('highscore.json', 'w')
        highscore_file.write(highscore_json)
        highscore_file.close()
    return highscore

def main():
    #The starting board generates
    board = generate_board(rows, cols)
    game_over = False
    score = 0
    #Highscore loaded from the highscore json file
    highscore = json.load(open('highscore.json', 'r'))
    #Sound effect when two blocks combine
    sound_effect = pygame.mixer.Sound('combining_sound_effect.wav')
    sound_effect.set_volume(0.5)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            #Updates the board according to the key pressed
            if event.type == pygame.KEYDOWN:
                old_board = board.copy()
                scr = 0
                if event.key == pygame.K_LEFT:
                    board, scr = left(board, sound_effect)
                    board = add_new(old_board, board)
                if event.key == pygame.K_RIGHT:
                    board, scr = right(board, sound_effect)
                    board = add_new(old_board, board)
                if event.key == pygame.K_UP:
                    board, scr = up(board, sound_effect)
                    board = add_new(old_board, board)
                if event.key == pygame.K_DOWN:
                    board, scr = down(board, sound_effect)
                    board = add_new(old_board, board)

                #Updates the score according to the numbers combined in total
                score += scr

        screen.fill((50, 52, 65))

        #Rendering the board and scores
        render_board(screen, board)
        render_scores(score, highscore)

        #Updates the score and highscore
        highscore = update_highscore(score, highscore)

        #Update the pygame display
        pygame.display.update()

        #Checks if the game is over
        game_over = check(board)

def lost_screen():
    #Renders 'You lost!' for 1 second
    n = 0
    while n < 1000:
        font = pygame.font.SysFont('arial', 60)
        screen.fill((22, 19, 35))
        label = font.render('You Lost!', 1, (254, 254, 215))
        screen.blit(label, (width/2-label.get_width()/2, height/2-label.get_height()/2))
        pygame.display.update()
        n += 1

def main_menu():
    font = pygame.font.SysFont('arial', 60)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            #Runs the game when any key is pressed
            if event.type == pygame.KEYDOWN:
                main()

                #If the main function is over, that means the game is over, so show the lost screen
                lost_screen()

        #Renders 'Press any key to play...'
        screen.fill((22, 19, 35))
        label = font.render('Press any key to play...', 1, (254, 254, 215))
        screen.blit(label, (width/2-label.get_width()/2, height/2-label.get_height()/2))

        #Updates the screen
        pygame.display.update()

#Runs the main menu
main_menu()
