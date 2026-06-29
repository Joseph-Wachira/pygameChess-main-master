import pygame
import os
import time
import sys

# Dynamically find the path whether running as script or bundled .exe
if getattr(sys, 'frozen', False):
    base_asset_dir = os.path.join(sys._MEIPASS, 'assets')
else:
    base_asset_dir = os.path.join(os.path.dirname(__file__), 'assets')

pygame.init()
WIDTH = 1000
HEIGHT = 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Two player Chess')
font = pygame.font.Font('freesansbold.ttf', 20)
big_font = pygame.font.Font('freesansbold.ttf', 50)
timer = pygame.time.Clock()
fps = 60

# ------------------------- Board state -------------------------
white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn','pawn','pawn','pawn','pawn','pawn','pawn','pawn']
white_location = [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),
                  (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1)]
black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn','pawn','pawn','pawn','pawn','pawn','pawn','pawn']
black_location = [(0,7),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7),(7,7),
                  (0,6),(1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6)]

captured_pieces_white = []
captured_pieces_black = []
turn_step = 0
selection = 100
valid_moves = []
white_castle_ks = True
white_castle_qs = True
black_castle_ks = True
black_castle_qs = True
en_passant_target = None
promotion_pawn_pos = None

# ------------------------- Image loading -------------------------
def load_image(path, default_size=(80,80)):
    try:
        img = pygame.image.load(path)
        return pygame.transform.scale(img, default_size)
    except:
        return None

# Absolute path to your specific assets directory using a raw string
base_asset_dir = r"C:\Users\joewa\OneDrive\Desktop\repo\pygameChess-main-master\pygameChess-main-master\assets"

# Dynamically handle whether the images are directly in assets or a subfolder named 'images'
if os.path.exists(os.path.join(base_asset_dir, 'images')):
    image_dir = os.path.join(base_asset_dir, 'images')
else:
    image_dir = base_asset_dir

piece_names = ['queen', 'king', 'rook', 'bishop', 'knight', 'pawn']
image_cache = {}
for color in ['white', 'black']:
    for piece in piece_names:
        # Check standard variations of image filenames
        for sep in ['_', ' ', '-']:
            fname = f"{color}{sep}{piece}.png"
            path = os.path.join(image_dir, fname)
            img = load_image(path)
            if img is not None:
                image_cache[(color, piece)] = img
                break
        if (color, piece) not in image_cache:
            fname = f"{color}_{piece}.png".lower()
            path = os.path.join(image_dir, fname)
            img = load_image(path)
            if img is not None:
                image_cache[(color, piece)] = img

small_cache = {}
for key, img in image_cache.items():
    small_cache[key] = pygame.transform.scale(img, (45,45))

def get_piece_image(color, piece, small=False):
    cache = small_cache if small else image_cache
    return cache.get((color, piece), None)

# ------------------------- Drawing functions -------------------------
def draw_board():
    for i in range(32):
        column = i % 4
        row = i // 4
        if row % 2 == 0:
            x = 600 - (column * 200)
        else:
            x = 700 - (column * 200)
        pygame.draw.rect(screen, 'light grey', [x, row * 100, 100, 100])
    pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
    pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
    pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
    status_text = [
        'white: select a piece to move!',
        'white: select a destination!',
        'black: select a piece to move!',
        'black: select a destination!'
    ]
    screen.blit(big_font.render(status_text[turn_step], True, 'black'), (20, 820))
    for j in range(9):
        pygame.draw.line(screen, 'black', (0, 100 * j), (800, 100 * j), 2)
        pygame.draw.line(screen, 'black', (100 * j, 0), (100 * j, 800), 2)

def draw_piece_shape(col, row, color, piece):
    x = col * 100 + 50
    y = row * 100 + 50
    if color == 'white':
        main_color = (255, 255, 255)
        accent = (0, 0, 0)
    else:
        main_color = (0, 0, 0)
        accent = (200, 200, 200)
    if piece == 'pawn':
        pygame.draw.circle(screen, main_color, (x, y - 10), 15)
        pygame.draw.circle(screen, accent, (x, y - 10), 15, 2)
        pygame.draw.rect(screen, main_color, (x - 10, y - 5, 20, 20))
        pygame.draw.rect(screen, accent, (x - 10, y - 5, 20, 20), 2)
    elif piece == 'rook':
        pygame.draw.rect(screen, main_color, (x - 20, y - 20, 40, 40))
        pygame.draw.rect(screen, accent, (x - 20, y - 20, 40, 40), 2)
        pygame.draw.rect(screen, main_color, (x - 15, y - 30, 10, 10))
        pygame.draw.rect(screen, main_color, (x + 5, y - 30, 10, 10))
        pygame.draw.rect(screen, accent, (x - 15, y - 30, 10, 10), 2)
        pygame.draw.rect(screen, accent, (x + 5, y - 30, 10, 10), 2)
    elif piece == 'knight':
        pygame.draw.polygon(screen, main_color, [(x - 15, y + 15), (x - 15, y - 10), (x, y - 25), (x + 15, y - 10), (x + 15, y + 15)])
        pygame.draw.polygon(screen, accent, [(x - 15, y + 15), (x - 15, y - 10), (x, y - 25), (x + 15, y - 10), (x + 15, y + 15)], 2)
        pygame.draw.circle(screen, main_color, (x + 5, y - 10), 8)
        pygame.draw.circle(screen, accent, (x + 5, y - 10), 8, 2)
    elif piece == 'bishop':
        pygame.draw.polygon(screen, main_color, [(x, y - 25), (x - 15, y + 15), (x + 15, y + 15)])
        pygame.draw.polygon(screen, accent, [(x, y - 25), (x - 15, y + 15), (x + 15, y + 15)], 2)
        pygame.draw.circle(screen, main_color, (x, y - 25), 8)
        pygame.draw.circle(screen, accent, (x, y - 25), 8, 2)
    elif piece == 'queen':
        pygame.draw.circle(screen, main_color, (x, y - 15), 20)
        pygame.draw.circle(screen, accent, (x, y - 15), 20, 2)
        for dx in [-20, -10, 10, 20]:
            pygame.draw.circle(screen, main_color, (x + dx, y - 15), 6)
            pygame.draw.circle(screen, accent, (x + dx, y - 15), 6, 2)
        pygame.draw.polygon(screen, main_color, [(x - 20, y + 5), (x + 20, y + 5), (x, y + 25)])
        pygame.draw.polygon(screen, accent, [(x - 20, y + 5), (x + 20, y + 5), (x, y + 25)], 2)
    elif piece == 'king':
        pygame.draw.circle(screen, main_color, (x, y - 15), 22)
        pygame.draw.circle(screen, accent, (x, y - 15), 22, 2)
        pygame.draw.line(screen, main_color, (x - 25, y - 15), (x + 25, y - 15), 4)
        pygame.draw.line(screen, accent, (x - 25, y - 15), (x + 25, y - 15), 4)
        pygame.draw.line(screen, main_color, (x, y - 35), (x, y + 5), 4)
        pygame.draw.line(screen, accent, (x, y - 35), (x, y + 5), 4)
        pygame.draw.polygon(screen, main_color, [(x - 20, y + 5), (x + 20, y + 5), (x, y + 25)])
        pygame.draw.polygon(screen, accent, [(x - 20, y + 5), (x + 20, y + 5), (x, y + 25)], 2)

def draw_piece(col, row, color, piece):
    img = get_piece_image(color, piece, small=False)
    if img is not None:
        screen.blit(img, (col * 100 + 10, row * 100 + 10))
    else:
        draw_piece_shape(col, row, color, piece)

def draw_all_pieces():
    for i, (col, row) in enumerate(white_location):
        draw_piece(col, row, 'white', white_pieces[i])
    for i, (col, row) in enumerate(black_location):
        draw_piece(col, row, 'black', black_pieces[i])

def draw_valid_moves():
    for (col, row) in valid_moves:
        pygame.draw.circle(screen, (0, 255, 0), (col * 100 + 50, row * 100 + 50), 20, 3)

def draw_captured():
    for i, piece in enumerate(captured_pieces_white):
        draw_piece(8, i, 'black', piece)
    for i, piece in enumerate(captured_pieces_black):
        draw_piece(9, i, 'white', piece)

def draw_promotion_popup():
    if promotion_pawn_pos is None:
        return
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 128))
    screen.blit(s, (0, 0))
    pieces = ['queen', 'rook', 'bishop', 'knight']
    x_start = 300
    y_start = 350
    for i, p in enumerate(pieces):
        x = x_start + i * 100
        pygame.draw.rect(screen, 'white', (x, y_start, 80, 80), border_radius=10)
        pygame.draw.rect(screen, 'black', (x, y_start, 80, 80), 3, border_radius=10)
        draw_piece((x + 40) // 100, (y_start + 40) // 100, 'white', p)
        label = font.render(p.capitalize(), True, 'black')
        screen.blit(label, (x + 10, y_start + 85))
    global promotion_buttons
    promotion_buttons = [(x_start + i * 100, y_start, 80, 80) for i in range(4)]

# ------------------------- Chess logic -------------------------
def get_piece_at(col, row):
    for i, (c, r) in enumerate(white_location):
        if c == col and r == row:
            return ('white', i)
    for i, (c, r) in enumerate(black_location):
        if c == col and r == row:
            return ('black', i)
    return None

def is_in_check(color):
    king_pos = None
    if color == 'white':
        for i, p in enumerate(white_pieces):
            if p == 'king':
                king_pos = white_location[i]
                break
    else:
        for i, p in enumerate(black_pieces):
            if p == 'king':
                king_pos = black_location[i]
                break
    if king_pos is None:
        return False
    opponent = 'black' if color == 'white' else 'white'
    attacks = get_all_attacks(opponent)
    return king_pos in attacks

def get_all_attacks(color):
    attacks = set()
    if color == 'white':
        pieces = white_pieces
        locations = white_location
    else:
        pieces = black_pieces
        locations = black_location
    for i, (col, row) in enumerate(locations):
        piece = pieces[i]
        moves = get_raw_moves(col, row, piece, color, check_castling=False)
        for (c, r) in moves:
            attacks.add((c, r))
    return attacks

def get_raw_moves(col, row, piece, color, check_castling=True):
    moves = []
    enemy = 'black' if color == 'white' else 'white'
    if piece == 'pawn':
        direction = 1 if color == 'white' else -1
        start_row = 1 if color == 'white' else 6
        new_row = row + direction
        if 0 <= new_row <= 7:
            if get_piece_at(col, new_row) is None:
                moves.append((col, new_row))
                if row == start_row:
                    new_row2 = row + 2 * direction
                    if 0 <= new_row2 <= 7 and get_piece_at(col, new_row2) is None:
                        moves.append((col, new_row2))
        for dc in [-1, 1]:
            new_col = col + dc
            new_row = row + direction
            if 0 <= new_col <= 7 and 0 <= new_row <= 7:
                target = get_piece_at(new_col, new_row)
                if target is not None and target[0] == enemy:
                    moves.append((new_col, new_row))
                if en_passant_target is not None and en_passant_target == (new_col, new_row):
                    moves.append((new_col, new_row))
    elif piece == 'knight':
        jumps = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
        for dc, dr in jumps:
            new_col, new_row = col+dc, row+dr
            if 0 <= new_col <= 7 and 0 <= new_row <= 7:
                target = get_piece_at(new_col, new_row)
                if target is None or target[0] != color:
                    moves.append((new_col, new_row))
    elif piece == 'bishop':
        directions = [(1,1),(1,-1),(-1,1),(-1,-1)]
        for dc, dr in directions:
            for step in range(1, 8):
                new_col = col + dc * step
                new_row = row + dr * step
                if not (0 <= new_col <= 7 and 0 <= new_row <= 7):
                    break
                target = get_piece_at(new_col, new_row)
                if target is None:
                    moves.append((new_col, new_row))
                else:
                    if target[0] != color:
                        moves.append((new_col, new_row))
                    break
    elif piece == 'rook':
        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        for dc, dr in directions:
            for step in range(1, 8):
                new_col = col + dc * step
                new_row = row + dr * step
                if not (0 <= new_col <= 7 and 0 <= new_row <= 7):
                    break
                target = get_piece_at(new_col, new_row)
                if target is None:
                    moves.append((new_col, new_row))
                else:
                    if target[0] != color:
                        moves.append((new_col, new_row))
                    break
    elif piece == 'queen':
        directions = [(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]
        for dc, dr in directions:
            for step in range(1, 8):
                new_col = col + dc * step
                new_row = row + dr * step
                if not (0 <= new_col <= 7 and 0 <= new_row <= 7):
                    break
                target = get_piece_at(new_col, new_row)
                if target is None:
                    moves.append((new_col, new_row))
                else:
                    if target[0] != color:
                        moves.append((new_col, new_row))
                    break
    elif piece == 'king':
        directions = [(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]
        for dc, dr in directions:
            new_col, new_row = col+dc, row+dr
            if 0 <= new_col <= 7 and 0 <= new_row <= 7:
                target = get_piece_at(new_col, new_row)
                if target is None or target[0] != color:
                    moves.append((new_col, new_row))
        # Castling
        if check_castling:
            if color == 'white':
                if white_castle_ks and row == 0 and col == 4:
                    if not is_in_check('white') and \
                       (5,0) not in get_all_attacks('black') and \
                       (6,0) not in get_all_attacks('black') and \
                       get_piece_at(5,0) is None and get_piece_at(6,0) is None:
                        moves.append((6,0))
                if white_castle_qs and row == 0 and col == 4:
                    if not is_in_check('white') and \
                       (3,0) not in get_all_attacks('black') and \
                       (2,0) not in get_all_attacks('black') and \
                       get_piece_at(3,0) is None and get_piece_at(2,0) is None and get_piece_at(1,0) is None:
                        moves.append((2,0))
            else:
                if black_castle_ks and row == 7 and col == 4:
                    if not is_in_check('black') and \
                       (5,7) not in get_all_attacks('white') and \
                       (6,7) not in get_all_attacks('white') and \
                       get_piece_at(5,7) is None and get_piece_at(6,7) is None:
                        moves.append((6,7))
                if black_castle_qs and row == 7 and col == 4:
                    if not is_in_check('black') and \
                       (3,7) not in get_all_attacks('white') and \
                       (2,7) not in get_all_attacks('white') and \
                       get_piece_at(3,7) is None and get_piece_at(2,7) is None and get_piece_at(1,7) is None:
                        moves.append((2,7))
    return moves

def generate_legal_moves(color):
    legal = {}
    pieces = white_pieces if color == 'white' else black_pieces
    locations = white_location if color == 'white' else black_location
    for i, (col, row) in enumerate(locations):
        piece = pieces[i]
        raw = get_raw_moves(col, row, piece, color, check_castling=True)
        valid = []
        for (end_col, end_row) in raw:
            captured = None
            captured_index = None
            captured_piece_name = None
            en_passant_capture = False
            ep_idx = None
            
            target = get_piece_at(end_col, end_row)
            if target is not None:
                captured = target
                captured_index = target[1]
                captured_piece_name = black_pieces[captured_index] if color == 'white' else white_pieces[captured_index]
                
            if piece == 'pawn' and en_passant_target is not None and (end_col, end_row) == en_passant_target:
                en_passant_capture = True
            old_location = (col, row)
            
            # Simulate move
            if color == 'white':
                white_location[i] = (end_col, end_row)
                if captured is not None and captured[0] == 'black':
                    black_location.pop(captured_index)
                    black_pieces.pop(captured_index)
                if en_passant_capture:
                    for idx, (c, r) in enumerate(black_location):
                        if c == end_col and r == row:
                            ep_idx = idx
                            black_location.pop(idx)
                            black_pieces.pop(idx)
                            break
                if piece == 'king' and abs(end_col - col) == 2:
                    if end_col == 6:
                        for idx, (c, r) in enumerate(white_location):
                            if c == 7 and r == row and white_pieces[idx] == 'rook':
                                white_location[idx] = (5, row)
                                break
                    elif end_col == 2:
                        for idx, (c, r) in enumerate(white_location):
                            if c == 0 and r == row and white_pieces[idx] == 'rook':
                                white_location[idx] = (3, row)
                                break
            else:
                black_location[i] = (end_col, end_row)
                if captured is not None and captured[0] == 'white':
                    white_location.pop(captured_index)
                    white_pieces.pop(captured_index)
                if en_passant_capture:
                    for idx, (c, r) in enumerate(white_location):
                        if c == end_col and r == row:
                            ep_idx = idx
                            white_location.pop(idx)
                            white_pieces.pop(idx)
                            break
                if piece == 'king' and abs(end_col - col) == 2:
                    if end_col == 6:
                        for idx, (c, r) in enumerate(black_location):
                            if c == 7 and r == row and black_pieces[idx] == 'rook':
                                black_location[idx] = (5, row)
                                break
                    elif end_col == 2:
                        for idx, (c, r) in enumerate(black_location):
                            if c == 0 and r == row and black_pieces[idx] == 'rook':
                                black_location[idx] = (3, row)
                                break
            
            in_check = is_in_check(color)
            
            # Undo move
            if color == 'white':
                white_location[i] = old_location
                if captured is not None and captured[0] == 'black':
                    black_location.insert(captured_index, (end_col, end_row))
                    black_pieces.insert(captured_index, captured_piece_name)
                if en_passant_capture and ep_idx is not None:
                    black_location.insert(ep_idx, (end_col, row))
                    black_pieces.insert(ep_idx, 'pawn')
                if piece == 'king' and abs(end_col - col) == 2:
                    if end_col == 6:
                        for idx, (c, r) in enumerate(white_location):
                            if c == 5 and r == row and white_pieces[idx] == 'rook':
                                white_location[idx] = (7, row)
                                break
                    elif end_col == 2:
                        for idx, (c, r) in enumerate(white_location):
                            if c == 3 and r == row and white_pieces[idx] == 'rook':
                                white_location[idx] = (0, row)
                                break
            else:
                black_location[i] = old_location
                if captured is not None and captured[0] == 'white':
                    white_location.insert(captured_index, (end_col, end_row))
                    white_pieces.insert(captured_index, captured_piece_name)
                if en_passant_capture and ep_idx is not None:
                    white_location.insert(ep_idx, (end_col, row))
                    white_pieces.insert(ep_idx, 'pawn')
                if piece == 'king' and abs(end_col - col) == 2:
                    if end_col == 6:
                        for idx, (c, r) in enumerate(black_location):
                            if c == 5 and r == row and black_pieces[idx] == 'rook':
                                black_location[idx] = (7, row)
                                break
                    elif end_col == 2:
                        for idx, (c, r) in enumerate(black_location):
                            if c == 3 and r == row and black_pieces[idx] == 'rook':
                                black_location[idx] = (0, row)
                                break
            if not in_check:
                valid.append((end_col, end_row))
        if valid:
            legal[(col, row)] = valid
    return legal

def execute_move(start, end):
    global en_passant_target, white_castle_ks, white_castle_qs, black_castle_ks, black_castle_qs
    global promotion_pawn_pos
    start_col, start_row = start
    end_col, end_row = end
    color = None
    idx = None
    for i, (c, r) in enumerate(white_location):
        if c == start_col and r == start_row:
            color = 'white'
            idx = i
            break
    if color is None:
        for i, (c, r) in enumerate(black_location):
            if c == start_col and r == start_row:
                color = 'black'
                idx = i
                break
    if color is None:
        return False
    piece = white_pieces[idx] if color == 'white' else black_pieces[idx]

    # Handle capture
    target = get_piece_at(end_col, end_row)
    captured_name = None
    if target is not None:
        captured_name = white_pieces[target[1]] if target[0] == 'white' else black_pieces[target[1]]
        if target[0] == 'white':
            captured_pieces_black.append(captured_name)
            white_location.pop(target[1])
            white_pieces.pop(target[1])
        else:
            captured_pieces_white.append(captured_name)
            black_location.pop(target[1])
            black_pieces.pop(target[1])

    # En passant capture
    if piece == 'pawn' and en_passant_target is not None and (end_col, end_row) == en_passant_target:
        if color == 'white':
            for i, (c, r) in enumerate(black_location):
                if c == end_col and r == start_row:
                    captured_pieces_white.append('pawn')
                    black_location.pop(i)
                    black_pieces.pop(i)
                    break
        else:
            for i, (c, r) in enumerate(white_location):
                if c == end_col and r == start_row:
                    captured_pieces_black.append('pawn')
                    white_location.pop(i)
                    white_pieces.pop(i)
                    break

    # Move the piece (re-fetch current index safely)
    if color == 'white':
        idx = white_location.index((start_col, start_row))
        white_location[idx] = (end_col, end_row)
    else:
        idx = black_location.index((start_col, start_row))
        black_location[idx] = (end_col, end_row)

    # Update en passant target
    en_passant_target = None
    if piece == 'pawn' and abs(end_row - start_row) == 2:
        if color == 'white':
            en_passant_target = (start_col, start_row + 1)
        else:
            en_passant_target = (start_col, start_row - 1)

    # Castling
    if piece == 'king' and abs(end_col - start_col) == 2:
        if color == 'white':
            if end_col == 6:
                for i, (c, r) in enumerate(white_location):
                    if c == 7 and r == start_row and white_pieces[i] == 'rook':
                        white_location[i] = (5, start_row)
                        break
            elif end_col == 2:
                for i, (c, r) in enumerate(white_location):
                    if c == 0 and r == start_row and white_pieces[i] == 'rook':
                        white_location[i] = (3, start_row)
                        break
            white_castle_ks = False
            white_castle_qs = False
        else:
            if end_col == 6:
                for i, (c, r) in enumerate(black_location):
                    if c == 7 and r == start_row and black_pieces[i] == 'rook':
                        black_location[i] = (5, start_row)
                        break
            elif end_col == 2:
                for i, (c, r) in enumerate(black_location):
                    if c == 0 and r == start_row and black_pieces[i] == 'rook':
                        black_location[i] = (3, start_row)
                        break
            black_castle_ks = False
            black_castle_qs = False

    # Update castling rights
    if piece == 'king':
        if color == 'white':
            white_castle_ks = False
            white_castle_qs = False
        else:
            black_castle_ks = False
            black_castle_qs = False
    if piece == 'rook':
        if color == 'white':
            if start_col == 0 and start_row == 0:
                white_castle_qs = False
            elif start_col == 7 and start_row == 0:
                white_castle_ks = False
        else:
            if start_col == 0 and start_row == 7:
                black_castle_qs = False
            elif start_col == 7 and start_row == 7:
                black_castle_ks = False

    # Promotion
    if piece == 'pawn' and (end_row == 0 or end_row == 7):
        promotion_pawn_pos = (end_col, end_row)

    return True

def check_game_over(color):
    moves = generate_legal_moves(color)
    if not moves:
        if is_in_check(color):
            return 'checkmate'
        else:
            return 'stalemate'
    return None

# ------------------------- Main loop -------------------------
run = True
promotion_buttons = []
while run:
    timer.tick(fps)
    screen.fill('dark grey')
    draw_board()
    draw_all_pieces()
    draw_valid_moves()
    draw_captured()
    if promotion_pawn_pos is not None:
        draw_promotion_popup()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()
            if promotion_pawn_pos is not None:
                for i, rect in enumerate(promotion_buttons):
                    rect_x, rect_y, w, h = rect
                    if rect_x <= x <= rect_x + w and rect_y <= y <= rect_y + h:
                        pieces = ['queen', 'rook', 'bishop', 'knight']
                        chosen = pieces[i]
                        col, row = promotion_pawn_pos
                        found = False
                        for idx, (c, r) in enumerate(white_location):
                            if c == col and r == row and white_pieces[idx] == 'pawn':
                                white_pieces[idx] = chosen
                                found = True
                                break
                        if not found:
                            for idx, (c, r) in enumerate(black_location):
                                if c == col and r == row and black_pieces[idx] == 'pawn':
                                    black_pieces[idx] = chosen
                                    break
                        promotion_pawn_pos = None
                        if turn_step == 0 or turn_step == 1:
                            turn_step = 2
                        else:
                            turn_step = 0
                        break
                continue
            col = x // 100
            row = y // 100
            if col < 0 or col > 7 or row < 0 or row > 7:
                continue
            if turn_step == 0 or turn_step == 1:
                color = 'white'
            else:
                color = 'black'
            if selection == 100:
                piece_info = get_piece_at(col, row)
                if piece_info is not None and piece_info[0] == color:
                    selection = piece_info[1]
                    moves_dict = generate_legal_moves(color)
                    start = (col, row)
                    if start in moves_dict:
                        valid_moves = moves_dict[start]
                    else:
                        valid_moves = []
                    if turn_step == 0:
                        turn_step = 1
                    else:
                        turn_step = 3
            else:
                if color == 'white':
                    start_col, start_row = white_location[selection]
                else:
                    start_col, start_row = black_location[selection]
                if (col, row) in valid_moves:
                    success = execute_move((start_col, start_row), (col, row))
                    if success:
                        selection = 100
                        valid_moves = []
                        if promotion_pawn_pos is None:
                            if turn_step == 1:
                                turn_step = 2
                            elif turn_step == 3:
                                turn_step = 0
                        pygame.display.flip()
                        pygame.time.delay(200)
                    else:
                        selection = 100
                        valid_moves = []
                        if turn_step == 1:
                            turn_step = 0
                        else:
                            turn_step = 2
                else:
                    selection = 100
                    valid_moves = []
                    if turn_step == 1:
                        turn_step = 0
                    else:
                        turn_step = 2

            if promotion_pawn_pos is None:
                current_color = 'white' if (turn_step == 0 or turn_step == 1) else 'black'
                result = check_game_over(current_color)
                if result == 'checkmate':
                    print("Checkmate! " + ("White" if current_color == 'black' else "Black") + " wins!")
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    run = False
                elif result == 'stalemate':
                    print("Stalemate! It's a draw.")
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    run = False

    pygame.display.flip()

pygame.quit()