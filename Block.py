import pygame
from pygame.math import Vector2


class Block(object):
    def __init__(self, game):
        self.game = game
        #ustawienie poczatkowej pozycji
        self.pos = Vector2()
        self.pos.x = 0
        self.pos.y = -190
        #ustawienie zmiennej wysokości bloczka potrzebnej do zminy pozyci przy animacji po usunięciu rzędu bloczków
        self.animation = 760
        #ustawienie gamy kolorów
        self.effect = -1
        try:
            self.color = pygame.image.load('Image/Colors/' + self.game.colors[self.game.buff[0]] + '.png')
        except Exception as e:
            self.game.error(e)

    #funkcja ustawia dane do poruszania bloczkiem przy animacji
    def set_animation(self, on_off = 0):
        #kasuje ustawienie animacji na dany rząd
        if on_off == -1:
            self.animation = 760
            return
        #zapisuje swoją współrzędną y ( ustawia dane do poruszania bloczkiem przy animacji )
        self.animation = self.get_position().y

    #funkcja zwraca aktywność przy animacji jako początkowa współrzędną y
    def get_animation(self):
        return self.animation

    #funkcja przesuwa bloczek o jedno miejsce w prawo
    def move_right(self):
        #przesuwa bloczek o jedną kratkę w prawo
        self.pos += (38, 0)
        if self.pos.x > 380:
            return 0
        return 1

    #funkcja przesuwa bloczke o jedno miejsce w lewo
    def move_left(self):
        #przesuwa bloczke o jedną kratkę w lewo
        self.pos += (-38, 0)
        if self.pos.x < 38:
            return 0
        return 1

    #funkcja przesuwa bloczek o jedno miejsce w dół
    def move_down(self):
        #obniża bloczek o jedną pozycję w dół
        self.pos += (0, 38)
        #sprawdzenie kolizji z innymi bloczkami
        for block in self.game.blocks[:len(self.game.blocks) - 4]:
            for active in self.game.blocks[len(self.game.blocks)-4:]:
                if block.get_position() == active.get_position() + (0, 38):
                    return 0
        #sprawdzenie czy bloczek jest na końcu planszy
        if self.pos.y >= 722:
            return 0
        return 1

    #funkcja ustawia pozycję bloczka
    def set_position(self, x, y):
        #ustawia pozycję bloczka
        self.pos.x = x
        self.pos.y = y

    #funkcja zwraca pozycję bloczka
    def get_position(self):
        return self.pos

    #funkcja rysuje bloczek na ekranie
    def draw(self):
        try:
            #wyświetlanie bloczka
            self.game.window.blit(self.color, self.pos)
            #wyświetlanie animacji wybuchu
            if self.effect >= 0:
                self.game.window.blit(pygame.image.load('Image/Explosion/' + str(self.effect) + '.png'), self.pos)
        except Exception as e:
            self.game.error(e)
