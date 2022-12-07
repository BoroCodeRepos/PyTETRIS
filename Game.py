import pygame
import sys
import time
from random import randint
from pygame.math import Vector2
from tkinter import messagebox
from Block import Block


class Game:
    def __init__(self):
        #inicjalizacja okna
        pygame.init()
        pygame.mixer.init()
        self.effect = 0
        pygame.display.set_caption('TETRIS')
        pygame.display.set_mode((722, 798))
        self.window = pygame.display.get_surface()
        try:
            self.background = pygame.image.load('Image/background.jpeg')
            self.sound = pygame.mixer.Sound('Music/tetris_1.wav')
            self.sound.play(-1)
        except Exception as e:
            self.error(e)

        #inicjalizacja bloczków do pierwszego ruchu
        self.rotate = 0
        self.figure = [[(0, 2, 4, 6), (2, 4, 6, 7), (3, 5, 6, 7), (2, 4, 5, 6), (4, 5, 6, 7), (3, 4, 5, 6), (2, 4, 5, 7)],
                       [(0, 2, 4, 6), (2, 4, 6, 7), (3, 5, 6, 7), (2, 4, 5, 6), (2, 3, 4, 5), (3, 4, 5, 6), (2, 4, 5, 7)],
                       [(7, 5, 3, 1), (0, 2, 4, 5), (1, 3, 4, 5), (0, 2, 3, 4), (0, 1, 2, 3), (1, 2, 3, 4), (0, 2, 3, 5)],
                       [(7, 5, 3, 1), (0, 2, 4, 5), (1, 3, 4, 5), (0, 2, 3, 4), (2, 3, 4, 5), (1, 2, 3, 4), (0, 2, 3, 5)]]

        self.blocks_position = [[  (-38, -76), (0, -76),  (-38, -38), (0, -38), (-38, 0), (0, 0),     (-38, 38), (0, 38)],
                                [  (-76, 38),  (-76, 0),  (-38, 38),  (-38, 0), (0, 38),  (0, 0),     (38, 38),  (38, 0)    ],
                                [  (0, 38),    (-38, 38), (0, 0),     (-38, 0), (0, -38), (-38, -38), (0, -76),  (-38, -76) ],
                                [  (38, 0),    (38, 38),  (0, 0),     (0, 38),  (-38, 0), (-38, 38),  (-76, 0),  (-76, 38)  ]]

        # 0 - pionowy
        # 1 - L                               pionowo       lewo         w dół        prawo
        # 2 - odwrócone L           rotacja      0            1            2            3
        # 3 - trójkątny                         0 1                       7 6
        # 4 - kwadrat                           2 3        1 3 5 7        5 4        6 4 2 0
        # 5 - zygzak ,'                         4 5        0 2 4 6        3 2        7 5 3 1
        # 6 - zygzak ',                         6 7                       1 0



        self.colors = ['dark_blue', 'blue', 'green', 'yellow', 'orange', 'red', 'pink']
        self.buff = [randint(0, 6)]     #losowanie pierwszej figury
        self.lottery(5)                 #losowanie 5 kolejnych figur
        self.blocks = [Block(self),
                       Block(self),
                       Block(self),
                       Block(self)]
        self.figure_position_first = Vector2()
        self.figure_position_first.x = 228
        self.figure_position_first.y = -76
        self.figure_position = self.figure_position_first
        self.set_position(self.figure_position.x, self.figure_position.y)

        #inicjalizacja ilości klatek na sekunde
        self.time_to_reaction = 0.7
        self.fps = 30.0

        #inicjalizacja zegara gry
        self.time_ = time.time()
        self.clk = pygame.time.Clock()
        self.time_to_game_over = 0
        self.delay = 0
        self.timer = 0

        #inicjalizacja gry
        try:
            #próba otwarcia pliku
            self.file = open('Settings/tetris.txt', 'r+')
        except:
            #niepowodzenie - tworzenie pliku
            self.file = open('Settings/tetris.txt', 'w')
            self.file.write('0')
            self.file.close()
            self.file = open('Settings/tetris.txt', 'r+')

        try:
            #próba odczytania liczby
            self.best_score = int(self.file.readline().strip())
        except:
            #niepowodzenie
            self.best_score = 0

        self.file.close()
        self.file = open('Settings/tetris.txt', 'w')
        self.volume = 1.0
        self.collision = False
        self.next_round = False
        self.level_up = False
        self.GAME_OVER = False
        self.create_new_figure = False
        self.erase_list = list()
        self.animation_ = False
        self.stacked_rows = 0
        self.image = 0
        self.level = 0
        self.time = 0
        self.font = pygame.font.Font('Font/atomic.ttf', 50)

        #inicjalizacja startu gry
        self.start = True
        self.start_pos = Vector2()
        self.start_pos.x = 234
        self.start_pos.y = 100

    def __del__(self):
        #zapisuje najlepszy wynik do pliku textowego
        try:
            self.file.write(str(self.best_score))
            self.file.close()
        except Exception as e:
            self.error(e)

    #funkcja uaktualnia stan gry
    def update(self):
        #opóźnienie związane ze stałą ilością klatek na sekunde
        self.delay += self.clk.tick() / 1000.0
        self.time = time.time() - self.time_
        #obsługa zdarzeń
        self.event_test()

        #zachowanie stałej ilości klatek na sekunde
        if self.delay >= 1 / self.fps:
            self.timer += self.delay
            self.delay = 0.0

            #ruch figury po odpowiednim czasie
            if self.timer >= self.time_to_reaction and not self.start:
                self.timer = 0
                if not self.animation_ and not self.GAME_OVER:
                    self.move_blocks_down()
            if self.animation_:
                self.animation()
            self.draw()

    #funkcja tworzy grę na ekranie
    def draw(self):
        #renderowanie powierzchni
        self.window.blit(self.background, (0, 0))

        # renderowanie sterowania
        self.text('A - ROTATE LEFT', 18, 570, 625)
        self.text('D/UP-ROTATE RIGHT', 18, 570, 645)
        self.text('SPACE - MOVE DOWN', 18, 570, 665)
        self.text('LEFT - MOVE LEFT', 18, 570, 685)
        self.text('RIGHT-MOVE RIGHT', 18, 570, 705)
        self.text('DOWN - MOVE DOWN', 18, 570, 725)
        self.text('ONE STEP', 18, 570, 745)

        #obliczanie czasu gry
        minutes = int(self.time / 60)
        seconds = int(self.time % 60)

        if not self.start:
            # konwercja i renderowanie skilla gracza
            if self.level > 999999:
                self.best_score = 999999
                self.level = 999999
            if self.level > self.best_score:
                self.best_score = self.level
            self.text(str(self.level), 32, 570, 175)

            #konwercja i renderowanie czasu gry
            string = 0
            if minutes < 10:
                string = '0'
            string = string + str(minutes) + ':'
            if seconds < 10:
                string += '0'
            string += str(seconds)
            self.text(string, 32, 570, 98)

            #obsługa najlepszego wyniku
            self.text('best score:', 18, 570, 513)
            self.text(str(self.best_score), 32, 570, 551)

            #wyświetlanie bloczków
            for block in self.blocks:
                block.draw()

            #wyświetlanie bufora bloczków
            i = 1
            for figure in self.buff[1:5]:
                try:
                    picture = pygame.image.load('Image/Figures/' + str(figure) + '.png')
                    tXY = picture.get_rect()
                    tab = [(532, 304), (608, 304), (532, 380), (608, 380)]
                    tXY.center = tab[i - 1]
                    self.window.blit(picture, tXY)
                    i += 1
                except Exception as e:
                    self.error(e)

            #obsługa napisu level up
            if self.level_up:
                self.text('LEVEL UP', 54, self.start_pos.x, self.start_pos.y + 250)

            #wyświetlanie napisu końca gry i odliczanie do ponownej gry
            if self.GAME_OVER:
                #zciszanie muzyki
                if self.volume >= 0.1:
                    self.volume -= 0.1
                    self.sound.set_volume(self.volume)

                #po zciszeniu głos game over
                if int(self.volume * 10) == 0:
                    try:
                        self.sound.stop()
                        self.sound = pygame.mixer.Sound('Music/Effect/game_over.wav')
                        self.sound.play(0)
                        self.volume = -1

                    except Exception as e:
                        self.error(e)

                for block in self.blocks:
                    block.effect = self.image
                    if self.image > 4:
                        try:
                            block.color = pygame.image.load('Image/Explosion/16.png')
                        except Exception as e:
                            self.error(e)

                self.image += 1
                if self.image > 16:
                    self.image = 16
                num = int(7 - (time.time() - self.time_to_game_over))

                if num < 1:
                    #powrót do normalnego trybu gry
                    self.end()
                    return

                #wyświetlanie tekstu związanego z końcem gry
                self.text('GAME OVER', 50, self.start_pos.x, self.start_pos.y)
                self.text('NEXT GAME:', 50, self.start_pos.x, self.start_pos.y + 200)
                self.text(str(num - 1), 50, self.start_pos.x, self.start_pos.y + 300)

        #wyświetlanie napisaów na początku gry
        if self.start:
            if 5 - seconds < 0:
                self.end()
                return

            self.text('Welcome to', 50, self.start_pos.x, self.start_pos.y)
            self.text('TETRIS!!!', 50, self.start_pos.x, self.start_pos.y + 100)
            self.text('START:', 50, self.start_pos.x, self.start_pos.y + 300)
            self.text(str(5 - seconds), 50, self.start_pos.x, self.start_pos.y + 400)

        # renderowanie zmian
        pygame.display.update()

    #funkcja sprawdza zdarzenia klawiszy
    def event_test(self):
        #obsługa zdarzeń
        for event in pygame.event.get():
            #wyłączene gry
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or event.type == pygame.QUIT:
                sys.exit(0)

            #obsługa przerwania odliczania czasu startu gry przez naduszenie dowolnego klawisza
            if self.start or self.GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    self.end()
                return

            #opuszczenie figury o jeden stopień
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.timer = 0
                self.move_blocks_down()

            #obracanie figury w lewo
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                self.rotate += 1
                if self.rotate == 4:
                    self.rotate = 0
                self.set_position(self.figure_position.x, self.figure_position.y)

                if not self.rotate_test():
                    #nie przeszło testu, figury nie można obrócić
                    self.rotate -= 1
                    if self.rotate == 0:
                        self.rotate = 3
                    self.set_position(self.figure_position.x, self.figure_position.y)

                for figure in self.blocks[len(self.blocks) - 4:]:
                    for block in self.blocks[: len(self.blocks) - 4]:
                        if block.get_position() == figure.get_position() + (0, 38):
                            self.collision = True
                            break


            #obracanie figury w prawo
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_d or event.key == pygame.K_UP):
                self.rotate -= 1
                if self.rotate == -1:
                    self.rotate = 3
                self.set_position(self.figure_position.x, self.figure_position.y)

                if not self.rotate_test():
                    #nie przeszło testu, figury nie można obrócić
                    self.rotate += 1
                    if self.rotate == 4:
                        self.rotate = 0
                    self.set_position(self.figure_position.x, self.figure_position.y)

                #sprawdzenie kolizji z innymi bloczkami
                for figure in self.blocks[len(self.blocks) - 4:]:
                    for block in self.blocks[: len(self.blocks) - 4]:
                        if block.get_position() == figure.get_position() + (0, 38):
                            self.collision = True
                            break

            #całkowite opuszczenie figury
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.animation_:
                while self.move_blocks_down() == 1:
                    pass
                #self.move_blocks_down()
                self.timer = 0

            #ruch figurą w lewo
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT and not self.animation_:
                self.move_blocks_left()

            #ruch figura w prawo
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT and not self.animation_:
                self.move_blocks_right()

    #funkcja ustawia figurę pod wskazaną współrzędną
    def set_position(self, x, y):
        self.figure_position.x = x
        self.figure_position.y = y
        i = 1
        for block in self.figure[self.rotate][self.buff[0]]:
            self.blocks[len(self.blocks) - i].set_position(x + int(self.blocks_position[self.rotate][block][0]), y + int(self.blocks_position[self.rotate][block][1]))
            i += 1

    #funkcja obniża o jeden stopień figurę sprawdzając warunki ruchu
    def move_blocks_down(self):
        skip = False            #pomija opadanie figury
        #sprawdza czy po czasie nie ma przesunięć, jeśli są to pozwala przejść niżej figurze
        if self.next_round:
            new = False
            for figure in self.blocks[len(self.blocks) - 4 :]:
                if figure.get_position().y == 722:
                    new = True
                    skip = True

                for block in self.blocks[: len(self.blocks) - 4]:
                    if block.get_position() == figure.get_position() + (0, 38):
                        new = True
                        skip = True

            if not new:
                self.create_new_figure = False
                self.next_round = False

        #przesuwa bloczki o jeden stopień w dół
        if not self.collision and not skip:
            self.create_new_figure = False
            self.figure_position += (0, 38)
            for block in self.blocks[len(self.blocks) - 4:]:
                if block.move_down() == 0:
                    self.create_new_figure = True
        else:
            self.create_new_figure = True
            self.collision = False

        #tworzy nową figurę
        if self.create_new_figure:
            #pomija jeden cykl na ruch figurą
            if not self.next_round:
                self.next_round = True
                return 0
            #sprawdenie czy bloczki nie wyszły poza górną granice - game over
            if self.end_test() == 0:
                #tworzenie nowej figury
                #przesuwanie buffora z figurami
                for i in range(1, 6, 1):
                    self.buff[i - 1] = self.buff[i]
                #losowanie nowej niepowtarzającej sie figury
                self.lottery(1)
                #tworzenie nowych bloków do gry
                for i in range(0, 4, 1):
                    self.blocks.append(Block(self))
                #inicjalizacja nowej figury
                self.rotate = 0
                self.level += 1
                self.next_round = False
                self.set_position(228, -76)
                self.line_test()
                return 0
            else:
                self.GAME_OVER = True
                self.time_to_game_over = time.time()
                return -1
        return 1

    #funkcja przesuwa figurę o jeden stopień w lewo
    def move_blocks_left(self):
        self.figure_position += (-38, 0)
        collision = False
        len_ = len(self.blocks)
        for block in self.blocks[len_ - 4:]:
            if block.move_left() == 0:
                collision = True
         #sprawdzenie czy bloczki nie nakładają sie na siebie
        for block in self.blocks[:len_ - 4]:
            for active in self.blocks[len_ - 4:]:
                if block.get_position() == active.get_position():
                    collision = True
        #jak nastąpiłą kolizja to cofnij
        if collision:
            self.move_blocks_right()
            return False
        #wykrycie kolizji po przesunięciu bloczka
        len_ = len(self.blocks)
        for active in self.blocks[len_ - 4:]:
            for block in self.blocks[: len_ - 4]:
                if block.get_position() == active.get_position() + (0, 38):
                    self.collision = True
        return True

    #funkcja przesuwa figurę o jeden stopień w prawo
    def move_blocks_right(self):
        self.figure_position += (38, 0)
        collision = False
        len_ = len(self.blocks)
        for block in self.blocks[len_ - 4:]:
            if block.move_right() == 0:
                collision = True
         #sprawdzenie czy bloczki nie nakładają sie na siebie
        for block in self.blocks[:len_ - 4]:
            for active in self.blocks[len_ - 4:]:
                if block.get_position() == active.get_position():
                    collision = True
        #jak nastąpila kolizja to cofnij
        if collision:
            self.move_blocks_left()
            return False
        len_ = len(self.blocks)
        for active in self.blocks[len_ - 4:]:
            for block in self.blocks[: len_ - 4]:
                if block.get_position() == active.get_position() + (0, 38):
                    self.collision = True
        return True

    #funkcja sprawdza warunki rotacji
    def rotate_test(self):
        #zwraca true jeśli pozycję figury udało się ustalić, jeśli nie zwraca false
        fail = False
        idx = 0
        collision = False
        old_pos = self.figure_position

        #jeżeli znaleziono błąd pozycji to przesuń figurę do odpowiedniej pozycji
        while self.figure_out_map():
             #zmiana pozycji figury
             for figure in self.blocks[len(self.blocks) - 4 :]:
                x = figure.get_position().x
                y = figure.get_position().y
                #dzielenie ekranu na pół, sprawdzenie czy figura powinna być przesunieta w prawo czy w lewo
                if x < 228:
                    x += 38
                else:
                    x -= 38
                figure.set_position(x, y)

        #jeżeli zmieniono pozycje figury i pokrywa się ona z pozostałymi bloczkami
        for figure in self.blocks[len(self.blocks) - 4 :]:
            for block in self.blocks[: len(self.blocks) - 4]:
                if figure.get_position() == block.get_position():
                    fail = True
                    self.set_position(old_pos.x, old_pos.y)

        #bloczki sie pokrywają - próba przesunięia bloczków
        if fail:
            for i in range(0, 2, 1):
                #przesunięcie bloczków
                self.set_position(old_pos.x - 38, old_pos.y)

                #sprawdzenie czy bloczki się nie pokrywają
                for figure in self.blocks[len(self.blocks) - 4 :]:
                    for block in self.blocks[: len(self.blocks) - 4]:
                        if figure.get_position() == block.get_position():
                            collision = True

                #bloczki sie nie pokrywaja - znaleziono pozycję
                if not collision and not self.figure_out_map():
                    return True
                collision = False
                idx += 1


            #w lewo stronę nie znaleziono pozycji, próba z prawej strony
            for i in range(0, 1, 1):
                # przesunięcie bloczków
                self.set_position(old_pos.x + 38, old_pos.y)

                # sprawdzenie czy bloczki się nie pokrywaj
                for figure in self.blocks[len(self.blocks) - 4:]:
                    for block in self.blocks[: len(self.blocks) - 4]:
                        if figure.get_position() == block.get_position():
                            collision = True

                # bloczki sie nie pokrywaja - znaleziono pozycję
                if not collision and not self.figure_out_map():
                    return True
                collision = False
                idx -= 1
            #nie udało sie naleźć pozycji - nie można obrócić figury
            self.figure_position = old_pos + (38 * idx, 0)
            return False

        # wsystko przebiegło poprawnie, znaleziono pozycje figury
        return True

    #funkcja sprawdza ułożenie bloczków w wierszu
    def line_test(self):
        for y in range(0, 760, 38):
            n = 0
            for block in self.blocks[: len(self.blocks) - 4]:
                if block.get_position().y == y:
                    n += 1
                    if n == 10:

                        self.animation_ = True
                        self.erase_list.append(y)
                        self.stacked_rows += 1
                        try:
                            if self.stacked_rows == 10:
                                self.sound.stop()
                                self.sound = pygame.mixer.Sound('Music/tetris_2.wav')
                                self.sound.play(-1)
                            if self.stacked_rows == 20:
                                self.sound.stop()
                                self.sound = pygame.mixer.Sound('Music/tetris_3.wav')
                                self.sound.play(-1)
                        except Exception as e:
                            self.error(e)
                        if self.stacked_rows % 10 == 0:
                            self.level_up = True
                            self.time_to_reaction -= 0.1
                            if self.time_to_reaction < 0.1:
                                self.time_to_reaction = 0.1
        self.level += (100 * len(self.erase_list))
        if len(self.erase_list) > 0:
            len_ = len(self.erase_list)
            path = 'Music/Effect/'
            try:
                if len_ == 1:
                    path += 'perfect.wav'
                if len_ == 2:
                    path += 'double_kill.wav'
                if len_ == 3:
                    path += 'triple_kill.wav'
                if len_ > 3:
                    path += 'monster_kill.wav'
                self.effect = pygame.mixer.Sound(path)
                self.effect.play(0)
            except Exception as e:
                self.error(e)
        #bloczki ustawione do animacji
        for y in self.erase_list:
            for block in self.blocks[: len(self.blocks) - 4]:
                if block.get_position().y < y:
                    block.set_animation()

    #funkcja sprawdza czy ułożone bloczki nie wyszły poza obszar rysowania - game over
    def end_test(self):
        #sprawdzenie czy figura nie wyszła poza obszar rysowania
        #jesli wyszła - zwraca True
        #w przeciwnym wypadku False
        for block in self.blocks[len(self.blocks) - 4:]:
            if block.get_position().y <= 0:
                return True
        return False

    #funkcja dokonuje animacji bloczków przy ich usunięciu
    def animation(self):
        #procedura animacji w grze
        if self.image < 16:
            for erase in self.erase_list:
                for block in self.blocks[: len(self.blocks) - 4]:
                    if block.get_position().y == erase:
                        block.effect = self.image
                        if self.image > 4:
                            try:
                                block.color = pygame.image.load('Image/Explosion/16.png')
                            except Exception as e:
                                self.error(e)

        if self.image == 16:
            for erase in self.erase_list:
                for block in self.blocks[: len(self.blocks) - 4]:
                    if block.get_position().y == erase:
                        self.blocks.remove(block)

        if self.image > 16:
            for block in self.blocks[: len(self.blocks) - 4]:
                for y in self.erase_list:
                    if block.get_animation() < y:
                        pos = block.get_position()
                        block.set_position(pos.x, pos.y + 2)

        #koniec animacji
        if self.image == 35:
            self.image = -1
            self.animation_ = False
            self.level_up = False
            self.erase_list.clear()
            for block in self.blocks:
                block.set_animation(-1)

        self.image += 1

    #funkcja losuje wskazają ilość niepowtarzających sie bloczków w buforze
    def lottery(self, amount):
        repeating = False
        idx = 0
        while idx < amount:
            value = randint(0, 6)

            for b in self.buff:
                if value == b:
                    repeating = True
            if not repeating:
                if amount == 1:
                    self.buff[5] = value
                else:
                    self.buff.append(value)
                idx += 1
            else:
                repeating = False

    #funkcja wyświetla text na ekranie pod wskazaną współrzędną
    def text(self, text, size, x, y):
        #wyświetlanie tekstu na ekranie
        try:
            self.font = pygame.font.Font('Font/atomic.ttf', size)
            text_ = self.font.render(text, True, (255, 0, 0))
            tXY = text_.get_rect()
            tXY.center = (x, y)
            self.window.blit(text_, tXY)

        except Exception as e:
            self.error(e)

    #funkcja sprawdza czy bloczki znajdują sie w polu gry
    def figure_out_map(self):
        #zwraca true jeśli figura znajduje sie poza obszarem mmapy
        #w przeciwnym wypadku False
        for figure in self.blocks[len(self.blocks) - 4 :]:
            if figure.get_position().x < 38 or figure.get_position().x < 0 or figure.get_position().x > 380:
                return True
        return False

    #funkcja kasuje odliczanie czasu startu lub końca gry i ustawia dane początkowe
    def end(self):
        #procedura kończąca start lub koniec gry
        if self.start:
            self.start = False
            self.time_ = time.time()
            self.timer = 0
            return

        if self.GAME_OVER:
            self.image = 0
            self.volume = 1.0
            self.blocks.clear()
            self.GAME_OVER = False
            # losowanie nowego bufora figur
            self.buff = [randint(0, 6)]
            self.lottery(5)
            #losowanie nowego zestawu figur
            self.blocks = [Block(self),
                           Block(self),
                           Block(self),
                           Block(self)]
            self.set_position(228, -76)
            self.time_ = time.time()
            self.timer = 0
            self.level = 0
            self.stacked_rows = 0
            self.sound.stop()
            try:
                self.sound = pygame.mixer.Sound('Music/tetris_1.wav')
                self.sound.play(-1)
            except Exception as e:
                self.error(e)

    #funkcja informuje o błędzie gry
    @staticmethod
    def error(message):
        messagebox.showerror('ERROR!', message)
        sys.exit(0)
