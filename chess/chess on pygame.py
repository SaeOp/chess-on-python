import copy
import pygame as p
import sys

inputs = [
    "5 2",
    "5 4",
    "5 7",
    "5 5",
    "6 2",
    "6 4",
    "4 8",
    "8 4",
]


def load_images(cell_cize):
    images = {}
    figures = ["wP","bP","wN","bN","wB","bB","wR","bR","wQ","bQ","wK","bK"]
    for fig in figures:
        images[fig] = p.transform.smoothscale(p.image.load(f"images/{fig}.png"), (cell_cize, cell_cize))
    return images

class BOARD:
    figures = []
    checked = None
    checkmated = None
    slatemated = None
    
    def __init__(self):
        for i in range(1,9):
            self.figures.append(PAWN([i,2], "Белая пешка", "white"))
            self.figures.append(PAWN([i,7], "Чёрная пешка", "black"))
        for i in [1,8]:
            self.figures.append(ROOK([i,1], "Белая ладья", "white"))
            self.figures.append(ROOK([i,8], "Чёрная ладья", "black"))
        for i in [2,7]:
            self.figures.append(KNIGHT([i,1], "Белый конь", "white"))
            self.figures.append(KNIGHT([i,8], "Чёрный конь", "black"))
        for i in [3,6]:
            self.figures.append(BISHOP([i,1], "Белый слон", "white"))
            self.figures.append(BISHOP([i,8], "Чёрный слон", "black"))
        self.figures.append(QUEEN([4,1], "Белый ферзь", "white"))
        self.figures.append(QUEEN([4,8], "Чёрный ферзь", "black"))
        self.figures.append(KING([5,1], "Белый король", "white"))
        self.figures.append(KING([5,8], "Чёрный король", "black"))

    def describe(self):
        for i in self.figures:
            i.describe()

    # выводит доску 
    def get_board(self):
        board = [[""]*8 for _ in range(8)]
        for i in self.figures:
            pos = i.pos
            board[7 - (pos[1] - 1)][pos[0] - 1] = i.sign
            
        return board
            
    # возвращает цвет фигуры, стоящей на заданной клетке
    def pos_check(self, need_pos):
        for fig in self.figures:
            if fig.pos == need_pos:
                return fig.color
                
    # получение фигуры по ее позиции
    def get_figure(self, need_pos):
        for fig in self.figures:
            if fig.pos == need_pos:
                return fig
            
    # пермещает фигуру из одной точки в другую
    def admin_move(self, old_pos, new_pos):
        if self.get_figure(new_pos) != None:
            self.figures.remove(self.get_figure(new_pos))
        self.get_figure(old_pos).move(new_pos)

    # на вход цвет фигур, для которого расщитываются поля покрытия
    def hit_grid(self, color):
        moves = set()
        for fig in self.figures:
            if fig.color == color:
                if isinstance(fig, KING):
                    for move in fig.theory_moves(self):
                        moves.add(tuple(move))
                else:
                    for move in fig.avaible_moves(self):
                        moves.add(tuple(move))
        moves = [list(move) for move in list(moves)]
        return moves
    
    # на вход цвет короля для которого проверяется шах
    def is_checked(self, color):
        king = next(fig for fig in self.figures if isinstance(fig, KING) and fig.color == color)
        enemy_color = "white" if king.color == "black" else "black"
        ht = self.hit_grid(enemy_color)
        if king.pos in ht:
             self.checked = color
        else:
            self.checked = None
            
    def is_checkmated(self, color):
        moves = []
        for fig in self.figures:
            if fig.color == color:
                for move in fig.legal_moves(self):
                    moves.append(move)
        if len(moves) == 0 and self.checked != None:
            self.checkmated = color
        elif len(moves) == 0:
            self.slatemated = color
        
    def where_is_king(self, color):
        return next(fig for fig in self.figures if isinstance(fig, KING) and fig.color == color).pos
    
class FIGURE:
    def __init__(self, pos, fig_type, color):
        self.pos = pos
        self.color = color
        self.fig_type = fig_type
        self.posx = pos[0]
        self.posy = pos[1]

    def move(self, next_pos):
        self.pos = next_pos
        self.posx = next_pos[0]
        self.posy = next_pos[1]

    def describe(self):
        print(self.color, self.pos, self.fig_type)

    # проверяет ходы на возможность их совершения(связки)
    def legal_moves(self, board):
        legal = []
        for move in self.avaible_moves(board):
            virtual_board = copy.deepcopy(board)
            virtual_figures = [fig.clone() for fig in board.figures]
            virtual_board.figures = virtual_figures
            virtual_self = virtual_board.get_figure(self.pos)
            if virtual_board.get_figure(move) != None:
                virtual_board.figures.remove(virtual_board.get_figure(move))
            virtual_board.admin_move(virtual_self.pos, move)
            if self.color == "white":
                enemy_color = "black"
            else:
                enemy_color = "white"
            king = next(fig for fig in virtual_board.figures if isinstance(fig, KING) and fig.color == self.color)
            virtual_board.is_checked(self.color)
            if king.pos not in virtual_board.hit_grid(enemy_color) and virtual_board.checked == None:
                legal.append(move)
        return legal
    
    def clone(self):
        return type(self)(self.pos.copy(), self.fig_type, self.color)

class KING(FIGURE):
    def __init__(self, pos, fig_type, color):
        super(KING, self).__init__(pos, fig_type, color)
        if color == "white":
            self.sign = "wK"
        else:
            self.sign = "bK"

    def avaible_moves(self, board):
        sus_moves = []
        moves = []
        flag = ['white', 'black']
        if self.color == "black":
            flag.reverse()
        combinations = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
        for it in combinations:
            x = self.posx
            y = self.posy
            x += it[0]
            y += it[1]
            if not ((1 <= x <= 8) and (1 <= y <= 8)):
                continue
            elif board.pos_check([x,y]) == flag[0]:
                continue
            elif board.pos_check([x,y]) == flag[1]:
                sus_moves.append([x,y])
                continue
            else:
                sus_moves.append([x,y])
        hitted = board.hit_grid(flag[1])
        for move in sus_moves:
            if move not in hitted:
                moves.append(move)
                
        return moves
        
    # зона вокруг короля
    def theory_moves(self, board):
        moves = []
        flag = ['white', 'black']
        if self.color == "black":
            flag.reverse()
        combinations = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
        for it in combinations:
            x = self.posx
            y = self.posy
            x += it[0]
            y += it[1]
            if not ((1 <= x <= 8) and (1 <= y <= 8)):
                continue
            elif board.pos_check([x,y]) == flag[0]:
                continue
            elif board.pos_check([x,y]) == flag[1]:
                moves.append([x,y])
                continue
            else:
                moves.append([x,y])

        return moves
            
class QUEEN(FIGURE):
    def __init__(self, pos, fig_type, color):
        super(QUEEN, self).__init__(pos, fig_type, color)
        if color == "white":
            self.sign = "wQ"
        else:
            self.sign = "bQ"

    def avaible_moves(self, board):
        moves = []
        flag = ['white', 'black']
        if self.color == "black":
            flag.reverse()
        combinations = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
        for it in combinations:
            x = self.posx
            y = self.posy
            while True:
                x += it[0]
                y += it[1]
                if not ((1 <= x <= 8) and (1 <= y <= 8)):
                    break
                elif board.pos_check([x,y]) == flag[0]:
                    break
                elif board.pos_check([x,y]) == flag[1]:
                    moves.append([x,y])
                    break
                else:
                    moves.append([x,y])
        #print(moves)
        return moves


class ROOK(FIGURE):
    def __init__(self, pos, fig_type, color):
        super(ROOK, self).__init__(pos, fig_type, color)
        if color == "white":
            self.sign = "wR"
        else:
            self.sign = "bR"

    def avaible_moves(self, board):
        moves = []
        flag = ['white', 'black']
        if self.color == "black":
            flag.reverse()
        combinations = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        for it in combinations:
            x = self.posx
            y = self.posy
            while True:
                x += it[0]
                y += it[1]
                if not ((1 <= x <= 8) and (1 <= y <= 8)):
                    break
                elif board.pos_check([x,y]) == flag[0]:
                    break
                elif board.pos_check([x,y]) == flag[1]:
                    moves.append([x,y])
                    break
                else:
                    moves.append([x,y])
        return moves


class BISHOP(FIGURE):
    def __init__(self, pos, fig_type, color):
        super(BISHOP, self).__init__(pos, fig_type, color)
        if color == "white":
            self.sign = "wB"
        else:
            self.sign = "bB"

    def avaible_moves(self, board):
        moves = []
        flag = ['white', 'black']
        if self.color == "black":
            flag.reverse()
        combinations = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
        for it in combinations:
            x = self.posx
            y = self.posy
            while True:
                x += it[0]
                y += it[1]
                if not ((1 <= x <= 8) and (1 <= y <= 8)):
                    break
                elif board.pos_check([x,y]) == flag[0]:
                    break
                elif board.pos_check([x,y]) == flag[1]:
                    moves.append([x,y])
                    break
                else:
                    moves.append([x,y])
        return moves
    

class KNIGHT(FIGURE):
    def __init__(self, pos, fig_type, color):
        super(KNIGHT, self).__init__(pos, fig_type, color)
        self.sign = "wN" if color == "white" else "bN"

    def avaible_moves(self, board):
        moves = []
        combinations = [[2, 1], [-2, 1], [2, -1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]]
        for dx, dy in combinations:
            x = self.posx + dx
            y = self.posy + dy
            if 1 <= x <= 8 and 1 <= y <= 8:
                target_color = board.pos_check([x, y])
                if target_color != self.color:
                    moves.append([x, y])
        return moves


class PAWN(FIGURE):
    def __init__(self, pos, fig_type, color):
        super(PAWN, self).__init__(pos, fig_type, color)
        if color == "white":
            self.sign = "wP"
        else:
            self.sign = "bP"

    def avaible_moves(self, board):
        moves = []
        if self.color == "white":
            flag = "black"
            color_arg = [2, 1]
        else:
            flag = "white"
            color_arg = [7, -1]
        if (board.pos_check([self.posx, self.posy + color_arg[1]]) == None) and (1 <= (self.posy + color_arg[1]) <= 8):
            moves.append([self.posx, self.posy + color_arg[1]])
            
            if (board.pos_check([self.posx, self.posy + color_arg[1] * 2]) == None) and (1 <= (self.posy + color_arg[1] * 2) <= 8)  and self.posy == color_arg[0]:
                moves.append([self.posx, self.posy + color_arg[1] * 2])
                
        if board.pos_check([self.posx + 1, self.posy + color_arg[1]]) == flag:
            moves.append([self.posx + 1, self.posy + color_arg[1]])
        if board.pos_check([self.posx -1, self.posy + color_arg[1]]) == flag:
            moves.append([self.posx - 1, self.posy + color_arg[1]])
        
        return moves

def start_game():
    cell_size = 96
    runnung = True
    images = load_images(cell_size)
    board = BOARD()
    p.init()
    screen = p.display.set_mode((cell_size*8, cell_size*8))
    turn = "white"
    stage = "choosing"
    av_moves =[]
    while runnung:
        user_inp = p.event.get()
        for event in user_inp:
            if event.type == p.QUIT:
                runnung = False    
            if event.type == p.MOUSEBUTTONDOWN:
                x_tap, y_tap = event.pos[0]//cell_size, event.pos[1]//cell_size
                if x_tap<8 and y_tap<8:
                    x, y = x_tap+1, 8-y_tap
                    if stage == "choosing":
                        choosed_figure = board.get_figure([x, y])
                        if choosed_figure != None and choosed_figure.color == turn:
                            av_moves = choosed_figure.legal_moves(board)
                            if len(av_moves) != 0:
                                stage = "make_move"
                    elif stage == "make_move":
                        if [x,y] == choosed_figure.pos:
                            stage = "choosing"
                            av_moves = []
                        elif [x,y] in av_moves:
                            board.admin_move(choosed_figure.pos, [x,y])
                            av_moves = []
                            stage = "choosing"
                            turn = "black" if turn == "white" else "white"
                            board.is_checked(turn)
                            board.is_checkmated(turn)
                        
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    p.draw.rect(screen, (249, 255, 155), (i * cell_size, j * cell_size, (i + 1) * cell_size, (j + 1) * cell_size)) 
                else:
                    p.draw.rect(screen, (18, 179, 59), (i * cell_size, j * cell_size, (i + 1) * cell_size, (j + 1) * cell_size)) 
                    
                if board.get_board()[j][i] != "":
                    screen.blit(images[board.get_board()[j][i]], (i * cell_size, j * cell_size))
            
        for move in av_moves:
            p.draw.circle(screen, "red", ((move[0]) * cell_size - cell_size//2, (8 - move[1]) * cell_size + cell_size//2), cell_size//6, width=5)
        
        if board.checked != None:
            pos = board.where_is_king(board.checked)
            p.draw.rect(screen, "orange", ( (pos[0]-1) * cell_size, (8 - pos[1]) * cell_size, cell_size, cell_size), width=7)

        if board.checkmated != None:
            pos = board.where_is_king(board.checkmated)
            p.draw.rect(screen, "red", ( (pos[0]-1) * cell_size, (8 - pos[1]) * cell_size, cell_size, cell_size), width=7)

        if board.slatemated != None:
            pos = board.where_is_king(board.checkmated)
            p.draw.rect(screen, "gray", ( (pos[0]-1) * cell_size, (8 - pos[1]) * cell_size, cell_size, cell_size), width=7) 
            
        p.display.flip()

    p.quit()
    sys.exit()


start_game()