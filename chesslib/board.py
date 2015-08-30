from itertools import groupby
from copy import deepcopy
import Tkinter as tk
import re

import pieces

class ChessError(Exception): pass
class InvalidCoord(ChessError): pass
class InvalidColor(ChessError): pass
class InvalidMove(ChessError): pass
class Check(ChessError): pass
class CheckMate(ChessError): pass
class Draw(ChessError): pass
class NotYourTurn(ChessError): pass

FEN_STARTING = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
RANK_REGEX = re.compile(r"^[A-Z][1-8]$")

chosen_piece = ''

# This would be better if put in its own file, but I'm not sure how to make it see the gloabl chosen_piece variable.
class PieceChooser:
    def __init__(self, parent, color):
        top = self.top = tk.Toplevel(parent)
        self.myLabel = tk.Label(top, text='Choose a Piece')
        self.myLabel.pack()
        self.color = color
        if self.color == 'black':
            self.Q = tk.PhotoImage(file='/home/melvyn/Simple-Python-Chess/img/blackQ.gif')
            self.N = tk.PhotoImage(file='/home/melvyn/Simple-Python-Chess/img/blackN.gif')
            self.B = tk.PhotoImage(file='/home/melvyn/Simple-Python-Chess/img/blackB.gif')
            self.R = tk.PhotoImage(file='/home/melvyn/Simple-Python-Chess/img/blackR.gif')
        else:
            self.Q = tk.PhotoImage(file='/home/melvyn/Simple-Python-Chess/img/whiteQ.gif')
            self.N = tk.PhotoImage(file='/home/melvyn/Simple-Python-Chess/img/whiteN.gif')
            self.B = tk.PhotoImage(file='/home/melvyn/Simple-Python-Chess/img/whiteB.gif')
            self.R = tk.PhotoImage(file='/home/melvyn/Simple-Python-Chess/img/whiteR.gif')
        self.myButton = tk.Button(top,  compound=tk.TOP, width=100, height=100, image=self.Q, text="optional text", bg='green', command=self.chooseQ)
        self.myButton.pack()

        self.myButton = tk.Button(top,  compound=tk.TOP, width=100, height=100, image=self.B, text="optional text", bg='green', command=self.chooseB)
        self.myButton.pack()

        self.myButton = tk.Button(top,  compound=tk.TOP, width=100, height=100, image=self.N, text="optional text", bg='green', command=self.chooseN)
        self.myButton.pack()

        self.myButton = tk.Button(top,  compound=tk.TOP, width=100, height=100, image=self.R, text="optional text", bg='green', command=self.chooseR)
        self.myButton.pack()

    def chooseQ(self):
        global chosen_piece
        if self.color == 'black':
            chosen_piece = 'q'
        else:
            chosen_piece = 'Q'
        self.top.destroy()

    def chooseN(self):
        global chosen_piece
        if self.color == 'black':
            chosen_piece = 'n'
        else:
            chosen_piece = 'N'
        self.top.destroy()

    def chooseR(self):
        global chosen_piece
        if self.color == 'black':
            chosen_piece = 'r'
        else:
            chosen_piece = 'R'
        self.top.destroy()
    
    def chooseB(self):
        global chosen_piece
        if self.color == 'black':
            chosen_piece = 'b'
        else:
            chosen_piece = 'B'
        self.top.destroy()
            
def choose_piece(root, color):
    inputDialog = PieceChooser(root, color)
    root.wait_window(inputDialog.top)


# This is the only class that should be in this file.
class Board(dict):
    '''
       Board

       A simple chessboard class

       TODO:

        * PGN export
        * En passant
        * Castling
        * Promoting pawns
        * Fifty-move rule
    '''

    axis_y = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
    axis_x = tuple(range(1,9)) # (1,2,3,...8)

    captured_pieces = { 'white': [], 'black': [] }
    player_turn = None
    castling = '-'
    en_passant = '-'
    halfmove_clock = 0
    fullmove_number = 1
    history = []

    def __init__(self, fen = None):
        if fen is None: self.load(FEN_STARTING)
        else: self.load(fen)

    def __getitem__(self, coord):
        if isinstance(coord, str):
            coord = coord.upper()
            if not re.match(RANK_REGEX, coord.upper()): raise KeyError
        elif isinstance(coord, tuple):
            coord = self.letter_notation(coord)
        try:
            return super(Board, self).__getitem__(coord)
        except KeyError:
            return None

    def save_to_file(self): pass

    def is_in_check_after_move(self, p1, p2, parent):
        # Create a temporary board
        tmp = deepcopy(self)
        tmp._do_move(p1,p2,parent)
        return tmp.is_in_check(self[p1].color)

    def move(self, p1, p2, parent):
        p1, p2 = p1.upper(), p2.upper()
        piece = self[p1]
        dest  = self[p2]

        if self.player_turn != piece.color:
            raise NotYourTurn("Not " + piece.color + "'s turn!")

        enemy = self.get_enemy(piece.color)
        possible_moves = piece.possible_moves(p1)
        # 0. Check if p2 is in the possible moves
        if p2 not in possible_moves:
            raise InvalidMove

        # If enemy has any moves look for check
        if self.all_possible_moves(enemy):
            if self.is_in_check_after_move(p1,p2, parent):
                raise Check

        if not possible_moves and self.is_in_check(piece.color):
            print 'Checkmate!'
            raise CheckMate
        elif not possible_moves:
            print 'Stalemate!'
            raise Draw
        else:
            choose = 'choose piece'
            self._do_move(p1, p2, parent, choose)
            self._finish_move(piece, dest, p1,p2)

    def get_enemy(self, color):
        if color == "white": return "black"
        else: return "white"

    def _do_move(self, p1, p2, parent, choose = 'dont choose'):
        '''
            Move a piece without validation
        '''
        piece = self[p1]
        dest  = self[p2]
        del self[p1]
        if piece.color == 'white' and self.on_boundary(p2) and piece.abbreviation.lower() == 'p' and choose == 'choose piece':
            choose_piece(parent, piece.color)
            self[p2] = pieces.piece(chosen_piece)
            self[p2].place(self)    
        elif piece.color == 'black' and self.on_boundary(p2) and piece.abbreviation.lower() == 'p' and choose == 'choose piece':
            choose_piece(parent, piece.color)
            self[p2] = pieces.piece(chosen_piece)
            self[p2].place(self)
        else:
            self[p2] = piece


    def on_boundary(self, p2):
        ''' This function is used for pawn promotion. '''
        bd = re.compile(r'^[A-H][1|8]$')
        if bd.match(p2):
            return True
        else:
            return False

    def _finish_move(self, piece, dest, p1, p2):
        '''
            Set next player turn, count moves, log moves, etc.
        '''
        enemy = self.get_enemy(piece.color)
        if piece.color == 'black':
            self.fullmove_number += 1
        self.halfmove_clock +=1
        self.player_turn = enemy
        abbr = piece.abbreviation
        if abbr == 'P':
            # Pawn has no letter
            abbr = ''
            # Pawn resets halfmove_clock
            self.halfmove_clock = 0
        if dest is None:
            # No capturing
            movetext = abbr +  p2.lower()
        else:
            # Capturing
            movetext = abbr + 'x' + p2.lower()
            # Capturing resets halfmove_clock
            self.halfmove_clock = 0

        self.history.append(movetext)


    def all_possible_moves(self, color):
        '''
            Return a list of `color`'s possible moves.
            Does not check for check.
        '''
        if(color not in ("black", "white")): raise InvalidColor
        result = []
        for coord in self.keys():
            if (self[coord] is not None) and self[coord].color == color:
                moves = self[coord].possible_moves(coord)
                if moves: result += moves
        return result

    def occupied(self, color):
        '''
            Return a list of coordinates occupied by `color`
        '''
        result = []
        if(color not in ("black", "white")): raise InvalidColor

        for coord in self:
            if self[coord].color == color:
                result.append(coord)
        return result

    def is_king(self, piece):
        return isinstance(piece, pieces.King)


    def get_king_position(self, color):
        for pos in self.keys():
            if self.is_king(self[pos]) and self[pos].color == color:
                return pos

    def get_king(self, color):
        if(color not in ("black", "white")): raise InvalidColor
        return self[self.get_king_position(color)]

    def is_in_check(self, color):
        if(color not in ("black", "white")): raise InvalidColor
        king = self.get_king(color)
        enemy = self.get_enemy(color)
        return king in map(self.__getitem__, self.all_possible_moves(enemy))

    def letter_notation(self,coord):
        if not self.is_in_bounds(coord): return
        try:
            return self.axis_y[coord[1]] + str(self.axis_x[coord[0]])
        except IndexError:
            raise InvalidCoord

    def number_notation(self, coord):
        return int(coord[1])-1, self.axis_y.index(coord[0])

    def is_in_bounds(self, coord):
        if coord[1] < 0 or coord[1] > 7 or\
           coord[0] < 0 or coord[0] > 7:
            return False
        else: return True

    def load(self, fen):
        '''
            Import state from FEN notation
        '''
        self.clear()
        # Split data
        fen = fen.split(' ')
        # Expand blanks
        def expand(match): return ' ' * int(match.group(0))

        fen[0] = re.compile(r'\d').sub(expand, fen[0])

        for x, row in enumerate(fen[0].split('/')):
            for y, letter in enumerate(row):
                if letter == ' ': continue
                coord = self.letter_notation((7-x,y))
                self[coord] = pieces.piece(letter)
                self[coord].place(self)

        if fen[1] == 'w': self.player_turn = 'white'
        else: self.player_turn = 'black'

        self.castling = fen[2]
        self.en_passant = fen[3]
        self.halfmove_clock = int(fen[4])
        self.fullmove_number = int(fen[5])

    def export(self):
        '''
            Export state to FEN notation
        '''
        def join(k, g):
            if k == ' ': return str(len(g))
            else: return "".join(g)

        def replace_spaces(row):
            # replace spaces with their count
            result = [join(k, list(g)) for k,g in groupby(row)]
            return "".join(result)


        result = ''
        for number in self.axis_x[::-1]:
            for letter in self.axis_y:
                piece = self[letter+str(number)]
                if piece is not None:
                    result += piece.abbreviation
                else: result += ' '
            result += '/'

        result = result[:-1] # remove trailing "/"
        result = replace_spaces(result)
        result += " " + (" ".join([self.player_turn[0],
                         self.castling,
                         self.en_passant,
                         str(self.halfmove_clock),
                         str(self.fullmove_number)]))
        return result
