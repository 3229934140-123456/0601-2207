"""自动搜索并生成所有类型的一步杀残局，输出到puzzles.py"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, PieceType, King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
from xiangqi_trainer.core.utils import parse_move_str, board_from_grid
import json


def is_valid_puzzle(board: Board, color: PieceColor = PieceColor.RED):
    """检查残局是否合法（红先，双方都没被将军，且有杀着）"""
    # 走棋方不能被将军
    if is_check(board, color):
        return False, []

    # 对方也不能被将军（否则应该对方走）
    opponent = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED
    if is_check(board, opponent):
        return False, []

    # 不能已经是杀局
    if is_checkmate(board, opponent):
        return False, []

    # 找出所有杀着
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


def create_board_base(defenders, attackers, color=PieceColor.RED):
    """创建基础棋盘"""
    board = Board()
    for x in range(9):
        for y in range(10):
            board.set_piece(x, y, None)

    # 放置双方的帅/将
    if color == PieceColor.RED:
        board.set_piece(4, 0, King(PieceColor.RED))
    else:
        board.set_piece(4, 9, King(PieceColor.BLACK))

    # 放置防守方子力
    opponent = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED
    opp_king_y = 9 if color == PieceColor.RED else 0
    if opponent == PieceColor.BLACK:
        board.set_piece(4, opp_king_y, King(PieceColor.BLACK))
    else:
        board.set_piece(4, opp_king_y, King(PieceColor.RED))

    # 放置防守方的士
    # （不，我们只放防守方的子）
    for p_type, positions in defenders.items():
        for (x, y) in positions:
            piece_class = {
                'a': Advisor, 'b': Elephant, 'n': Horse,
                'r': Chariot, 'c': Cannon, 'p': Pawn,
            }.get(p_type, None)
            if piece_class:
                board.set_piece(x, y, piece_class(opponent))

    # 放置攻方的子
    for p_type, positions in attackers.items():
        for (x, y) in positions:
            piece_class = {
                'K': King, 'A': Advisor, 'B': Elephant, 'N': Horse,
                'R': Chariot, 'C': Cannon, 'P': Pawn,
            }.get(p_type, None)
            if piece_class:
                board.set_piece(x, y, piece_class(color))

    return board


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
                grid_y = 9 - y  # 转换坐标系
                grid[grid_y][x] = red_char if piece.color == PieceColor.RED else black_char
    return grid


def search_chongpao():
    """搜索重炮杀残局"""
    results = []
    count = 0

    for c1x in range(9):
        for c1y in range(3, 7):
            for c2x in range(9):
                for c2y in range(1, c1y - 1):
                    if c1x == c2x and c1y == c2y:
                        continue

                    board = Board()
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)
                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(c1x, c1y, Cannon(PieceColor.RED))
                    board.set_piece(c2x, c2y, Cannon(PieceColor.RED))

                    valid, mates = is_valid_puzzle(board)
                    if valid:
                        for mate in mates:
                            notation = get_notation(board, mate, PieceColor.RED)
                            parsed = parse_move_str(board, notation, PieceColor.RED)
                            if parsed:
                                count += 1
                                results.append({
                                    'name': f'重炮杀{count}',
                                    'type': '重炮',
                                    'difficulty': '简单',
                                    'board': board.clone(),
                                    'solution': [notation],
                                    'mate_move': mate,
                                })
                                break  # 每个局面只取一个杀法
    return results


def search_shuangche():
    """搜索双车错残局"""
    results = []
    count = 0

    for r1x in range(9):
        for r1y in range(2, 8):
            for r2x in range(9):
                for r2y in range(2, 8):
                    if r1x == r2x and r1y == r2y:
                        continue

                    board = Board()
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)
                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(r1x, r1y, Chariot(PieceColor.RED))
                    board.set_piece(r2x, r2y, Chariot(PieceColor.RED))

                    valid, mates = is_valid_puzzle(board)
                    if valid:
                        for mate in mates:
                            notation = get_notation(board, mate, PieceColor.RED)
                            parsed = parse_move_str(board, notation, PieceColor.RED)
                            if parsed:
                                count += 1
                                results.append({
                                    'name': f'双车错{count}',
                                    'type': '双车错',
                                    'difficulty': '简单',
                                    'board': board.clone(),
                                    'solution': [notation],
                                    'mate_move': mate,
                                })
                                break
    return results


def search_tiemenshuan():
    """搜索铁门栓残局（车+炮）"""
    results = []
    count = 0

    for rx in range(9):
        for ry in range(3, 8):
            for cx in range(9):
                for cy in range(2, ry):
                    if rx == cx and ry == cy:
                        continue

                    board = Board()
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)
                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(rx, ry, Chariot(PieceColor.RED))
                    board.set_piece(cx, cy, Cannon(PieceColor.RED))

                    valid, mates = is_valid_puzzle(board)
                    if valid:
                        for mate in mates:
                            notation = get_notation(board, mate, PieceColor.RED)
                            parsed = parse_move_str(board, notation, PieceColor.RED)
                            if parsed:
                                count += 1
                                results.append({
                                    'name': f'铁门栓{count}',
                                    'type': '铁门栓',
                                    'difficulty': '简单',
                                    'board': board.clone(),
                                    'solution': [notation],
                                    'mate_move': mate,
                                })
                                break
    return results


def search_mahoupao():
    """搜索马后炮残局"""
    results = []
    count = 0

    for nx in range(9):
        for ny in range(3, 9):
            for cx in range(9):
                for cy in range(1, ny):
                    if nx == cx and ny == cy:
                        continue

                    board = Board()
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)
                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(nx, ny, Horse(PieceColor.RED))
                    board.set_piece(cx, cy, Cannon(PieceColor.RED))

                    valid, mates = is_valid_puzzle(board)
                    if valid:
                        for mate in mates:
                            notation = get_notation(board, mate, PieceColor.RED)
                            parsed = parse_move_str(board, notation, PieceColor.RED)
                            if parsed:
                                count += 1
                                results.append({
                                    'name': f'马后炮{count}',
                                    'type': '马后炮',
                                    'difficulty': '中等',
                                    'board': board.clone(),
                                    'solution': [notation],
                                    'mate_move': mate,
                                })
                                break
    return results


def search_mabing():
    """搜索马兵杀残局"""
    results = []
    count = 0

    for nx in range(9):
        for ny in range(4, 9):
            for px in range(9):
                for py in range(5, 9):
                    if nx == px and ny == py:
                        continue

                    board = Board()
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)
                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(nx, ny, Horse(PieceColor.RED))
                    board.set_piece(px, py, Pawn(PieceColor.RED))

                    valid, mates = is_valid_puzzle(board)
                    if valid:
                        for mate in mates:
                            notation = get_notation(board, mate, PieceColor.RED)
                            parsed = parse_move_str(board, notation, PieceColor.RED)
                            if parsed:
                                count += 1
                                results.append({
                                    'name': f'马兵杀{count}',
                                    'type': '马兵',
                                    'difficulty': '简单',
                                    'board': board.clone(),
                                    'solution': [notation],
                                    'mate_move': mate,
                                })
                                break
    return results


def search_paobing():
    """搜索炮兵杀残局"""
    results = []
    count = 0

    for cx in range(9):
        for cy in range(2, 7):
            for px in range(9):
                for py in range(4, 9):
                    if cx == px and cy == py:
                        continue

                    board = Board()
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)
                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(cx, cy, Cannon(PieceColor.RED))
                    board.set_piece(px, py, Pawn(PieceColor.RED))

                    valid, mates = is_valid_puzzle(board)
                    if valid:
                        for mate in mates:
                            notation = get_notation(board, mate, PieceColor.RED)
                            parsed = parse_move_str(board, notation, PieceColor.RED)
                            if parsed:
                                count += 1
                                results.append({
                                    'name': f'炮兵杀{count}',
                                    'type': '炮兵',
                                    'difficulty': '简单',
                                    'board': board.clone(),
                                    'solution': [notation],
                                    'mate_move': mate,
                                })
                                break
    return results


def search_chebing():
    """搜索车兵杀残局"""
    results = []
    count = 0

    for rx in range(9):
        for ry in range(3, 8):
            for px in range(9):
                for py in range(5, 9):
                    if rx == px and ry == py:
                        continue

                    board = Board()
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)
                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(rx, ry, Chariot(PieceColor.RED))
                    board.set_piece(px, py, Pawn(PieceColor.RED))

                    valid, mates = is_valid_puzzle(board)
                    if valid:
                        for mate in mates:
                            notation = get_notation(board, mate, PieceColor.RED)
                            parsed = parse_move_str(board, notation, PieceColor.RED)
                            if parsed:
                                count += 1
                                results.append({
                                    'name': f'车兵杀{count}',
                                    'type': '车兵',
                                    'difficulty': '中等',
                                    'board': board.clone(),
                                    'solution': [notation],
                                    'mate_move': mate,
                                })
                                break
    return results


def search_shuangma():
    """搜索双马杀残局"""
    results = []
    count = 0

    for n1x in range(9):
        for n1y in range(4, 9):
            for n2x in range(9):
                for n2y in range(4, 9):
                    if n1x == n2x and n1y == n2y:
                        continue

                    board = Board()
                    for x in range(9):
                        for y in range(10):
                            board.set_piece(x, y, None)
                    board.set_piece(4, 9, King(PieceColor.BLACK))
                    board.set_piece(3, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(5, 9, Advisor(PieceColor.BLACK))
                    board.set_piece(4, 0, King(PieceColor.RED))
                    board.set_piece(n1x, n1y, Horse(PieceColor.RED))
                    board.set_piece(n2x, n2y, Horse(PieceColor.RED))

                    valid, mates = is_valid_puzzle(board)
                    if valid:
                        for mate in mates:
                            notation = get_notation(board, mate, PieceColor.RED)
                            parsed = parse_move_str(board, notation, PieceColor.RED)
                            if parsed:
                                count += 1
                                results.append({
                                    'name': f'双马杀{count}',
                                    'type': '双马',
                                    'difficulty': '中等',
                                    'board': board.clone(),
                                    'solution': [notation],
                                    'mate_move': mate,
                                })
                                break
    return results


def generate_puzzles_file(all_puzzles, output_path):
    """生成puzzles.py文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('from dataclasses import dataclass, field\n')
        f.write('from typing import List, Optional\n\n\n')
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


def select_puzzles(puzzles, max_per_type=5):
    """从每种类型中选择最多N个有代表性的残局"""
    by_type = {}
    for p in puzzles:
        t = p['type']
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(p)

    selected = []
    for t, ps in by_type.items():
        # 选择一些有代表性的（间隔选取）
        if len(ps) <= max_per_type:
            selected.extend(ps)
        else:
            step = len(ps) // max_per_type
            for i in range(max_per_type):
                idx = min(i * step, len(ps) - 1)
                selected.append(ps[idx])

    return selected


def main():
    print("开始搜索一步杀残局...")
    print()

    all_puzzles = []

    # 重炮杀
    print("搜索重炮杀...", end='', flush=True)
    chongpao = search_chongpao()
    print(f" 找到 {len(chongpao)} 个")

    # 双车错
    print("搜索双车错...", end='', flush=True)
    shuangche = search_shuangche()
    print(f" 找到 {len(shuangche)} 个")

    # 铁门栓
    print("搜索铁门栓...", end='', flush=True)
    tiemenshuan = search_tiemenshuan()
    print(f" 找到 {len(tiemenshuan)} 个")

    # 马后炮
    print("搜索马后炮...", end='', flush=True)
    mahoupao = search_mahoupao()
    print(f" 找到 {len(mahoupao)} 个")

    # 马兵
    print("搜索马兵杀...", end='', flush=True)
    mabing = search_mabing()
    print(f" 找到 {len(mabing)} 个")

    # 炮兵
    print("搜索炮兵杀...", end='', flush=True)
    paobing = search_paobing()
    print(f" 找到 {len(paobing)} 个")

    # 车兵
    print("搜索车兵杀...", end='', flush=True)
    chebing = search_chebing()
    print(f" 找到 {len(chebing)} 个")

    # 双马
    print("搜索双马杀...", end='', flush=True)
    shuangma = search_shuangma()
    print(f" 找到 {len(shuangma)} 个")

    all_puzzles = chongpao + shuangche + tiemenshuan + mahoupao + mabing + paobing + chebing + shuangma

    print()
    print(f"总计: {len(all_puzzles)} 个残局")

    # 选择部分有代表性的
    selected = select_puzzles(all_puzzles, max_per_type=5)
    print(f"筛选后: {len(selected)} 个残局")

    # 按类型排序
    type_order = ['重炮', '双车错', '铁门栓', '马后炮', '马兵', '炮兵', '车兵', '双马']
    selected.sort(key=lambda p: type_order.index(p['type']) if p['type'] in type_order else 99)

    # 生成puzzles.py
    output_path = r'd:\trae-bz\TraeProjects\2207\xiangqi_trainer\data\puzzles.py'
    generate_puzzles_file(selected, output_path)
    print(f"\n已生成 {output_path}")


if __name__ == '__main__':
    main()
