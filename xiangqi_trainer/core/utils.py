import re
from typing import Optional, Tuple, List, Dict, Any
from .board import Board
from .pieces import (
    Piece, PieceColor, PieceType,
    King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
)
from .move import Move
from .rules import generate_moves, is_check, is_checkmate


PIECE_CHAR_MAP = {
    'K': (PieceColor.RED, PieceType.KING),
    'A': (PieceColor.RED, PieceType.ADVISOR),
    'B': (PieceColor.RED, PieceType.ELEPHANT),
    'N': (PieceColor.RED, PieceType.HORSE),
    'R': (PieceColor.RED, PieceType.CHARIOT),
    'C': (PieceColor.RED, PieceType.CANNON),
    'P': (PieceColor.RED, PieceType.PAWN),
    'k': (PieceColor.BLACK, PieceType.KING),
    'a': (PieceColor.BLACK, PieceType.ADVISOR),
    'b': (PieceColor.BLACK, PieceType.ELEPHANT),
    'n': (PieceColor.BLACK, PieceType.HORSE),
    'r': (PieceColor.BLACK, PieceType.CHARIOT),
    'c': (PieceColor.BLACK, PieceType.CANNON),
    'p': (PieceColor.BLACK, PieceType.PAWN),
}


CHAR_PIECE_MAP = {
    (PieceColor.RED, PieceType.KING): 'K',
    (PieceColor.RED, PieceType.ADVISOR): 'A',
    (PieceColor.RED, PieceType.ELEPHANT): 'B',
    (PieceColor.RED, PieceType.HORSE): 'N',
    (PieceColor.RED, PieceType.CHARIOT): 'R',
    (PieceColor.RED, PieceType.CANNON): 'C',
    (PieceColor.RED, PieceType.PAWN): 'P',
    (PieceColor.BLACK, PieceType.KING): 'k',
    (PieceColor.BLACK, PieceType.ADVISOR): 'a',
    (PieceColor.BLACK, PieceType.ELEPHANT): 'b',
    (PieceColor.BLACK, PieceType.HORSE): 'n',
    (PieceColor.BLACK, PieceType.CHARIOT): 'r',
    (PieceColor.BLACK, PieceType.CANNON): 'c',
    (PieceColor.BLACK, PieceType.PAWN): 'p',
}


def char_to_piece(char: str) -> Optional[Piece]:
    if not char or char not in PIECE_CHAR_MAP:
        return None
    color, ptype = PIECE_CHAR_MAP[char]
    if ptype == PieceType.KING:
        return King(color)
    elif ptype == PieceType.ADVISOR:
        return Advisor(color)
    elif ptype == PieceType.ELEPHANT:
        return Elephant(color)
    elif ptype == PieceType.HORSE:
        return Horse(color)
    elif ptype == PieceType.CHARIOT:
        return Chariot(color)
    elif ptype == PieceType.CANNON:
        return Cannon(color)
    elif ptype == PieceType.PAWN:
        return Pawn(color)
    return None


def piece_to_char(piece: Piece) -> str:
    return CHAR_PIECE_MAP.get((piece.color, piece.type), '')


def board_from_grid(grid) -> Board:
    board = Board()
    for y in range(Board.HEIGHT):
        for x in range(Board.WIDTH):
            char = grid[y][x] if y < len(grid) and x < len(grid[y]) else ''
            piece = char_to_piece(char)
            board.set_piece(x, Board.HEIGHT - 1 - y, piece)
    return board


def board_to_grid(board: Board):
    grid = [['' for _ in range(Board.WIDTH)] for _ in range(Board.HEIGHT)]
    for y in range(Board.HEIGHT):
        for x in range(Board.WIDTH):
            piece = board.get_piece(x, Board.HEIGHT - 1 - y)
            if piece:
                grid[y][x] = piece_to_char(piece)
    return grid


def parse_move_str(board: Board, move_str: str, color: PieceColor) -> Optional[Move]:
    """
    解析简谱走法字符串，如 'N7+9'、'C5=7'、'P4+1'
    红方用大写字母，黑方用小写字母
    """
    if len(move_str) < 3:
        return None

    piece_char = move_str[0]
    target_info = move_str[1:]

    piece_type = None
    if piece_char.upper() == 'K':
        piece_type = PieceType.KING
    elif piece_char.upper() == 'A':
        piece_type = PieceType.ADVISOR
    elif piece_char.upper() == 'B':
        piece_type = PieceType.ELEPHANT
    elif piece_char.upper() == 'N':
        piece_type = PieceType.HORSE
    elif piece_char.upper() == 'R':
        piece_type = PieceType.CHARIOT
    elif piece_char.upper() == 'C':
        piece_type = PieceType.CANNON
    elif piece_char.upper() == 'P':
        piece_type = PieceType.PAWN

    if piece_type is None:
        return None

    move_type = None
    if '+' in target_info:
        move_type = 'forward'
        parts = target_info.split('+')
    elif '-' in target_info:
        move_type = 'backward'
        parts = target_info.split('-')
    elif '=' in target_info:
        move_type = 'sideways'
        parts = target_info.split('=')
    else:
        return None

    if len(parts) != 2:
        return None

    try:
        from_col_num = int(parts[0])
        from_col = 9 - from_col_num
        target = parts[1]
    except ValueError:
        return None

    all_moves = generate_moves(board, color)
    candidates = []
    for m in all_moves:
        if m.piece.type != piece_type:
            continue
        if m.from_x != from_col:
            continue

        if move_type == 'sideways':
            try:
                to_col_num = int(target)
                to_col = 9 - to_col_num
                if m.to_x == to_col and m.from_y == m.to_y:
                    candidates.append(m)
            except ValueError:
                pass
        elif move_type in ('forward', 'backward'):
            if m.from_y == m.to_y:
                continue
            is_forward = (m.to_y > m.from_y) if color == PieceColor.RED else (m.to_y < m.from_y)
            if (move_type == 'forward' and is_forward) or (move_type == 'backward' and not is_forward):
                diagonal_pieces = {PieceType.HORSE, PieceType.ADVISOR, PieceType.ELEPHANT}
                if piece_type in diagonal_pieces:
                    try:
                        to_col_num = int(target)
                        to_col = 9 - to_col_num
                        if m.to_x == to_col:
                            candidates.append(m)
                    except ValueError:
                        pass
                else:
                    distance = abs(m.to_y - m.from_y)
                    try:
                        target_dist = int(target)
                        if distance == target_dist:
                            candidates.append(m)
                    except ValueError:
                        pass

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        return candidates[0]

    return None


def find_solution_move(board: Board, solution_steps, color: PieceColor) -> Optional[Move]:
    """从解法步骤中找到当前局面的对应走法"""
    for step in solution_steps:
        move = parse_move_str(board, step, color)
        if move:
            return move
    return None


CHINESE_NUMBERS = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
ARABIC_TO_CHINESE = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九'}
CHINESE_PIECE_NAMES = {
    '帅': ('K', PieceColor.RED), '车': ('R', PieceColor.RED), '马': ('N', PieceColor.RED),
    '相': ('B', PieceColor.RED), '象': ('B', PieceColor.RED), '仕': ('A', PieceColor.RED),
    '士': ('A', PieceColor.RED), '兵': ('P', PieceColor.RED), '炮': ('C', PieceColor.RED),
    '将': ('k', PieceColor.BLACK), '俥': ('r', PieceColor.BLACK), '車': ('r', PieceColor.BLACK),
    '傌': ('n', PieceColor.BLACK), '馬': ('n', PieceColor.BLACK), '象': ('b', PieceColor.BLACK),
    '相': ('b', PieceColor.BLACK), '士': ('a', PieceColor.BLACK), '仕': ('a', PieceColor.BLACK),
    '卒': ('p', PieceColor.BLACK), '砲': ('c', PieceColor.BLACK), '炮': ('c', PieceColor.BLACK),
}


def parse_chinese_move(board: Board, move_str: str, color: PieceColor) -> Optional[Move]:
    """
    解析中文象棋记谱，如 炮二平五、马8进7
    红方用中文数字（一二三四五六七八九）
    黑方用阿拉伯数字（123456789）
    """
    move_str = move_str.strip()
    if len(move_str) < 4:
        return None

    piece_char = move_str[0]
    action_char = move_str[2]

    if action_char not in ('平', '进', '退'):
        return None

    if piece_char not in CHINESE_PIECE_NAMES:
        return None

    letter, parsed_color = CHINESE_PIECE_NAMES[piece_char]

    from_str = move_str[1]
    to_str = move_str[3]

    if color == PieceColor.RED:
        if from_str not in CHINESE_NUMBERS:
            return None
        from_num = CHINESE_NUMBERS[from_str]
        if to_str in CHINESE_NUMBERS:
            to_num = CHINESE_NUMBERS[to_str]
        elif to_str.isdigit():
            to_num = int(to_str)
        else:
            return None
    else:
        if not from_str.isdigit():
            return None
        from_num = int(from_str)
        if to_str.isdigit():
            to_num = int(to_str)
        elif to_str in CHINESE_NUMBERS:
            to_num = CHINESE_NUMBERS[to_str]
        else:
            return None

    if action_char == '平':
        simple = f'{letter.upper() if color == PieceColor.RED else letter.lower()}{from_num}={to_num}'
    elif action_char == '进':
        simple = f'{letter.upper() if color == PieceColor.RED else letter.lower()}{from_num}+{to_num}'
    else:
        simple = f'{letter.upper() if color == PieceColor.RED else letter.lower()}{from_num}-{to_num}'

    return parse_move_str(board, simple, color)


def create_initial_board() -> Board:
    """创建标准初始棋盘"""
    board = Board()
    initial = [
        ['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r'],
        ['', '', '', '', '', '', '', '', ''],
        ['', 'c', '', '', '', '', '', 'c', ''],
        ['p', '', 'p', '', 'p', '', 'p', '', 'p'],
        ['', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', ''],
        ['P', '', 'P', '', 'P', '', 'P', '', 'P'],
        ['', 'C', '', '', '', '', '', 'C', ''],
        ['', '', '', '', '', '', '', '', ''],
        ['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R'],
    ]
    return board_from_grid(initial)


class PgnParseResult:
    def __init__(self):
        self.success = False
        self.error_message = ""
        self.initial_board: Optional[Board] = None
        self.moves: List[Move] = []
        self.move_strings: List[str] = []
        self.name = ""
        self.is_puzzle = False
        self.puzzle_solution: List[str] = []
        self.final_board: Optional[Board] = None
        self.first_move_color = PieceColor.RED
        self.final_color = PieceColor.RED


def parse_pgn_text(content: str) -> PgnParseResult:
    """
    解析棋谱文本文件内容
    支持格式：
    1. 纯走法列表：每行一个走法，如 炮二平五、马8进7、R2+5
    2. FEN风格初始局面：[Board "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w"]
    3. 带标签：[Name "残局名称"]、[Puzzle "1"]
    """
    result = PgnParseResult()
    result.initial_board = create_initial_board()

    lines = content.replace('\r\n', '\n').replace('\r', '\n').split('\n')

    move_lines: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        tag_match = re.match(r'^\[(.*?)\s+"(.*?)"\s*\]$', line)
        if tag_match:
            tag_name = tag_match.group(1).strip().lower()
            tag_value = tag_match.group(2).strip()
            if tag_name == 'name':
                result.name = tag_value
            elif tag_name == 'puzzle':
                result.is_puzzle = tag_value.lower() in ('1', 'true', 'yes', '是')
            elif tag_name == 'board' or tag_name == 'fen':
                board, color, err = _parse_fen_board(tag_value)
                if board is None:
                    result.error_message = f"解析初始局面失败：{err}"
                    return result
                result.initial_board = board
                if color is not None:
                    result.first_move_color = color
            continue

        if line.startswith('#') or line.startswith(';'):
            continue

        move_lines.append(line)

    all_move_tokens: List[str] = []
    for line in move_lines:
        line = re.sub(r'\d+\.', '', line)
        line = re.sub(r'[，,。;；]', ' ', line)
        tokens = line.split()
        all_move_tokens.extend(tokens)

    if not all_move_tokens:
        result.error_message = "文件中没有找到任何走法记录"
        return result

    board = result.initial_board.clone()
    current_color = result.first_move_color
    moves_count = 0

    for token in all_move_tokens:
        move = None

        if re.match(r'^[KABRNCPkabrncp][0-9][+\-=][0-9]', token):
            move = parse_move_str(board, token, current_color)
        else:
            try:
                move = parse_chinese_move(board, token, current_color)
            except Exception:
                move = None

        if move is None:
            result.error_message = (
                f"第{moves_count + 1}步走法「{token}」解析失败：\n"
                f"可能原因：\n"
                f"1. 走法格式错误（应为：炮二平五 / 马8进7 / R2+5 等）\n"
                f"2. 当前局面中该位置没有对应棋子\n"
                f"3. 该棋子没有符合记谱的合法走法\n"
                f"4. 轮次错误（当前应为{'红方' if current_color == PieceColor.RED else '黑方'}走）"
            )
            return result

        valid_moves = generate_moves(board, current_color)
        is_valid = False
        for vm in valid_moves:
            if (vm.from_x == move.from_x and vm.from_y == move.from_y
                    and vm.to_x == move.to_x and vm.to_y == move.to_y):
                is_valid = True
                break

        if not is_valid:
            result.error_message = (
                f"第{moves_count + 1}步走法「{token}」不合法：\n"
                f"该走法违反象棋规则"
            )
            return result

        result.moves.append(move)
        result.move_strings.append(token)
        if result.is_puzzle and current_color == PieceColor.RED:
            result.puzzle_solution.append(move.to_chinese())

        board.move_piece(move.from_x, move.from_y, move.to_x, move.to_y)
        moves_count += 1
        current_color = PieceColor.BLACK if current_color == PieceColor.RED else PieceColor.RED

    result.success = True
    result.final_board = board
    result.final_color = current_color
    return result


def _parse_fen_board(fen: str) -> Tuple[Optional[Board], Optional[PieceColor], str]:
    """
    解析简化版FEN格式
    格式：用 / 分隔每行，数字表示空位数，字母表示棋子
    例：rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w
    返回：(board, side_to_move, error_message)
    """
    fen = fen.strip()
    side_to_move = None
    if ' ' in fen:
        parts = fen.split(' ')
        board_part = parts[0]
        if len(parts) > 1:
            side_char = parts[1].lower()
            if side_char in ('w', 'r', '红'):
                side_to_move = PieceColor.RED
            elif side_char in ('b', '黑'):
                side_to_move = PieceColor.BLACK
    else:
        board_part = fen

    rows = board_part.split('/')
    if len(rows) != 10:
        return None, None, f"需要10行棋子数据，实际只有{len(rows)}行"

    grid = [['' for _ in range(9)] for _ in range(10)]

    for row_idx, row_str in enumerate(rows):
        col = 0
        for ch in row_str:
            if ch.isdigit():
                count = int(ch)
                if col + count > 9:
                    return None, None, f"第{row_idx + 1}行棋子数量超过9列"
                col += count
            else:
                if col >= 9:
                    return None, None, f"第{row_idx + 1}行棋子数量超过9列"
                if ch not in PIECE_CHAR_MAP:
                    return None, None, f"无法识别的棋子字符：{ch}"
                grid[row_idx][col] = ch
                col += 1
        if col != 9:
            return None, None, f"第{row_idx + 1}行需要9列，实际{col}列"

    return board_from_grid(grid), side_to_move, ""
