# main.py
import os
import sys
from game import Game

# Fix working directory for PyInstaller builds
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

if __name__ == '__main__':
    game = Game()
    game.run()