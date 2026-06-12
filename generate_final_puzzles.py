"""高效搜索各种类型的一步杀残局，并生成puzzles.py"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, PieceType, King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
from xiangqi_trainer.core.utils import parse_move_str


def is_valid_puzzle(board: Board, color: PieceColor = PieceColor.RED):
    """检查残局是否合法"""
    if is_check(board, color):
        return False, []

    opponent = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED
    if is_check(board, opponent):
        return False, []

    if is_checkmate(board, opponent):
        return False, []

    moves = generate_moves(board, color)
    mate_moves = []
    for m in moves:
        new_board = board.clone()
        new_board.move_piece(m.from_x, m.from_y, m.to_x, m.to_y)
        if is_checkmate(new_board, opponent):
            mate_moves.append(m)

    return len(mate_moves) > 0, mate_moves


def get_notation(board, move, color):
    """生成记谱"""
    piece = board.get_piece(move.from_x, move.from_y)
    col = 9 - move.from_x

    type_map = {
        PieceType.KING: 'K',
        PieceType.ADVISOR: 'A',
        PieceType.ELEPHANT: 'B',
        PieceType.HORSE: 'N',
        PieceType.CHARIOT: 'R',
        PieceType.CANNON: 'C',
        PieceType.PAWN: 'P',
    }
    piece_char = type_map.get(piece.type, '?')

    if move.from_y == move.to_y:
        direction = '='
        target = 9 - move.to_x
    elif move.to_y > move.from_y:
        direction = '+'
        diagonal = {PieceType.HORSE, PieceType.ADVISOR, PieceType.ELEPHANT}
        if piece.type in diagonal:
            target = 9 - move.to_x
        else:
            target = abs(move.to_y - move.from_y)
    else:
        direction = '-'
        diagonal = {PieceType.HORSE, PieceType.ADVISOR, PieceType.ELEPHANT}
        if piece.type in diagonal:
            target = 9 - move.to_x
        else:
            target = abs(move.to_y - move.from_y)

    return f"{piece_char}{col}{direction}{target}"


def grid_from_board(board):
    """从board生成grid格式"""
    grid = [['' for _ in range(9)] for _ in range(10)]
    char_map = {
        PieceType.KING: ('k', 'K'),
        PieceType.ADVISOR: ('a', 'A'),
        PieceType.ELEPHANT: ('b', 'B'),
        PieceType.HORSE: ('n', 'N'),
        PieceType.CHARIOT: ('r', 'R'),
        PieceType.CANNON: ('c', 'C'),
        PieceType.PAWN: ('p', 'P'),
    }
    for y in range(10):
        for x in range(9):
            piece = board.get_piece(x, y)
            if piece:
                black_char, red_char = char_map[piece.type]
                grid_y = 9 - y
                grid[grid_y][x] = red_char if piece.color == PieceColor.RED else black_char
    return grid


def create_empty_board_obj():
    board = Board()
    for x in range(9):
        for y in range(10):
            board.set_piece(x, y, None)
    board.set_piece(4, 0, King(PieceColor.RED))
    return board


def add_black_defense(board, kx, ky, advisors, elephants):
    """添加黑方防守子力"""
    board.set_piece(kx, ky, King(PieceColor.BLACK))
    if 'a1' in advisors:
        board.set_piece(3, 9, Advisor(PieceColor.BLACK))
    if 'a2' in advisors:
        board.set_piece(5, 9, Advisor(PieceColor.BLACK))
    if 'a3' in advisors:
        board.set_piece(4, 8, Advisor(PieceColor.BLACK))
    if 'e1' in elephants:
        board.set_piece(2, 7, Elephant(PieceColor.BLACK))
    if 'e2' in elephants:
        board.set_piece(6, 7, Elephant(PieceColor.BLACK))


def search_puzzle_type(attack_pieces, defense_configs, name, kill_type, difficulty, max_count=10):
    """搜索特定类型的残局
    attack_pieces: 攻击方子力类型列表，如 ['C', 'C']
    """
    results = []

    # 防守方布局
    defense_layouts = []
    for kx in range(3, 6):
        for ky in range(7, 10):
            for advisors in [['a1', 'a2'], ['a1', 'a3'], ['a2', 'a3'], ['a1'], ['a2']]:
                for elephants in [[], ['e1'], ['e2'], ['e1', 'e2']]:
                    defense_layouts.append((kx, ky, advisors, elephants))

    print(f"  防守布局数: {len(defense_layouts)}")

    # 攻击方位置范围
    pos_ranges = []
    for pt in attack_pieces:
        if pt in ['R', 'C']:
            pos_ranges.append((range(9), range(1, 8)))
        elif pt == 'N':
            pos_ranges.append((range(9), range(3, 9)))
        elif pt == 'P':
            pos_ranges.append((range(9), range(5, 9)))
        else:
            pos_ranges.append((range(9), range(1, 9)))

    # 生成所有攻击方位置组合
    from itertools import product

    all_positions = []
    for i, pt in enumerate(attack_pieces):
        xs, ys = pos_ranges[i]
        positions = [(x, y) for x in xs for y in ys]
        all_positions.append(positions)

    count = 0
    total = len(defense_layouts)
    for idx, (kx, ky, advisors, elephants) in enumerate(defense_layouts):
        if len(results) >= max_count:
            break

        for combo in product(*all_positions):
            if len(results) >= max_count:
                break

            # 检查位置是否重叠
            positions = list(combo)
            valid_pos = True
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    if positions[i] == positions[j]:
                        valid_pos = False
                        break
                if not valid_pos:
                    break

            if not valid_pos:
                continue

            # 检查是否和防守子力重叠
            for (px, py) in positions:
                if px == kx and py == ky:
                    valid_pos = False
                    break
                if 'a1' in advisors and px == 3 and py == 9:
                    valid_pos = False
                    break
                if 'a2' in advisors and px == 5 and py == 9:
                    valid_pos = False
                    break
                if 'a3' in advisors and px == 4 and py == 8:
                    valid_pos = False
                    break
                if 'e1' in elephants and px == 2 and py == 7:
                    valid_pos = False
                    break
                if 'e2' in elephants and px == 6 and py == 7:
                    valid_pos = False
                    break

            if not valid_pos:
                continue

            # 创建棋盘
            board = create_empty_board_obj()
            add_black_defense(board, kx, ky, advisors, elephants)

            type_map = {
                'R': Chariot,
                'N': Horse,
                'C': Cannon,
                'P': Pawn,
            }
            for i, pt in enumerate(attack_pieces):
                x, y = positions[i]
                board.set_piece(x, y, type_map[pt](PieceColor.RED))

            # 检查
            valid, mates = is_valid_puzzle(board)
            if valid:
                # 验证记谱
                notation = get_notation(board, mates[0], PieceColor.RED)
                parsed = parse_move_str(board, notation, PieceColor.RED)
                if parsed:
                    results.append({
                        'name': f'{name}{len(results)+1}',
                        'type': kill_type,
                        'difficulty': difficulty,
                        'board': board.clone(),
                        'solution': [notation],
                        'mate_move': mates[0],
                    })
                    if len(results) >= max_count:
                        break

    return results


def generate_puzzles_file(all_puzzles, output_path):
    """生成puzzles.py文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('from dataclasses import dataclass, field\n')
        f.write('from typing import List, Optional\n\n\n')

        f.write('def create_empty_board() -> List[List[str]]:\n')
        f.write('    return [["" for _ in range(9)] for _ in range(10)]\n\n\n')

        f.write('@dataclass\n')
        f.write('class Puzzle:\n')
        f.write('    id: str\n')
        f.write('    name: str\n')
        f.write('    description: str\n')
        f.write('    difficulty: str\n')
        f.write('    kill_type: str\n')
        f.write('    steps: int\n')
        f.write('    initial_board: List[List[str]]\n')
        f.write('    solution: List[str]\n')
        f.write('    black_to_move: bool = False\n\n\n')

        for i, puzzle in enumerate(all_puzzles):
            puzzle_id = f'puzzle_{i+1:03d}'
            grid = grid_from_board(puzzle['board'])

            f.write(f'def {puzzle_id}() -> Puzzle:\n')
            f.write(f'    board = [\n')
            for row in grid:
                row_str = "', '".join(c if c else '' for c in row)
                f.write(f"        ['{row_str}'],\n")
            f.write(f'    ]\n')
            f.write(f"    return Puzzle(\n")
            f.write(f"        id='{puzzle_id}',\n")
            f.write(f"        name='{puzzle['name']}',\n")
            f.write(f"        description='{puzzle['name']}残局练习。',\n")
            f.write(f"        difficulty='{puzzle['difficulty']}',\n")
            f.write(f"        kill_type='{puzzle['type']}',\n")
            f.write(f"        steps={len(puzzle['solution'])},\n")
            f.write(f"        initial_board=board,\n")
            sol_str = "', '".join(puzzle['solution'])
            f.write(f"        solution=['{sol_str}'],\n")
            f.write(f"        black_to_move=False\n")
            f.write(f"    )\n\n\n")

        f.write('def get_all_puzzles() -> List[Puzzle]:\n')
        f.write('    puzzle_generators = [\n')
        for i in range(len(all_puzzles)):
            f.write(f'        puzzle_{i+1:03d},\n')
        f.write('    ]\n')
        f.write('    return [gen() for gen in puzzle_generators]\n\n\n')

        f.write('def get_puzzle_by_id(puzzle_id: str) -> Optional[Puzzle]:\n')
        f.write('    for puzzle in get_all_puzzles():\n')
        f.write('        if puzzle.id == puzzle_id:\n')
        f.write('            return puzzle\n')
        f.write('    return None\n\n\n')

        f.write('def get_puzzles_by_difficulty(difficulty: str) -> List[Puzzle]:\n')
        f.write('    return [p for p in get_all_puzzles() if p.difficulty == difficulty]\n\n\n')

        f.write('def get_puzzles_by_kill_type(kill_type: str) -> List[Puzzle]:\n')
        f.write('    return [p for p in get_all_puzzles() if p.kill_type == kill_type]\n\n\n')

        f.write('def get_puzzles_by_steps(min_steps: int = 1, max_steps: int = 7) -> List[Puzzle]:\n')
        f.write('    return [p for p in get_all_puzzles() if min_steps <= p.steps <= max_steps]\n\n\n')

        f.write("DIFFICULTIES = ['简单', '中等', '困难']\n")
        f.write("KILL_TYPES = ['马后炮', '重炮', '铁门栓', '海底捞月', '双车错', '马兵', '炮兵', '车兵', '双马']\n")


def main():
    print("开始搜索一步杀残局...")
    print()

    puzzle_types = [
        (['C', 'C'], '重炮杀', '重炮', '简单', 8),
        (['R', 'R'], '双车错', '双车错', '简单', 8),
        (['R', 'C'], '铁门栓', '铁门栓', '简单', 5),
        (['N', 'C'], '马后炮', '马后炮', '中等', 8),
        (['N', 'N'], '双马杀', '双马', '中等', 5),
        (['N', 'P'], '马兵杀', '马兵', '简单', 5),
        (['C', 'P'], '炮兵杀', '炮兵', '简单', 5),
        (['R', 'P'], '车兵杀', '车兵', '中等', 5),
    ]

    all_puzzles = []

    for attack_pieces, name, kill_type, diff, count in puzzle_types:
        print(f"搜索{name}...", end=' ', flush=True)
        puzzles = search_puzzle_type(attack_pieces, None, name, kill_type, diff, max_count=count)
        print(f"找到 {len(puzzles)} 个")
        all_puzzles.extend(puzzles)

    print()
    print(f"总计: {len(all_puzzles)} 个残局")

    # 按类型排序
    type_order = ['重炮', '双车错', '铁门栓', '马后炮', '双马', '马兵', '炮兵', '车兵']
    all_puzzles.sort(key=lambda p: type_order.index(p['type']) if p['type'] in type_order else 99)

    # 生成puzzles.py
    output_path = r'd:\trae-bz\TraeProjects\2207\xiangqi_trainer\data\puzzles.py'
    generate_puzzles_file(all_puzzles, output_path)
    print(f"\n已生成 {output_path}")

    # 打印概览
    print("\n残局概览:")
    for p in all_puzzles:
        print(f"  {p['name']}: {p['solution'][0]}")


if __name__ == '__main__':
    main()
