"""生成验证过的残局数据"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves, is_checkmate, is_check
from xiangqi_trainer.core.pieces import PieceColor, PieceType, King, Advisor, Elephant, Horse, Chariot, Cannon, Pawn
from xiangqi_trainer.core.utils import parse_move_str, board_to_grid
import json


def is_valid_puzzle(board: Board, color: PieceColor = PieceColor.RED):
    """检查残局是否合法（红先，双方都没被将军）"""
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


def find_chongpao_puzzles():
    """找重炮杀残局"""
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
                        notation = get_notation(board, mates[0], PieceColor.RED)
                        parsed = parse_move_str(board, notation, PieceColor.RED)
                        if parsed:
                            count += 1
                            # 选几个有代表性的
                            if len(results) < 5 or c1x in [0, 2, 4] or c2x in [0, 2]:
                                results.append({
                                    'name': f'重炮杀{count}',
                                    'type': '重炮',
                                    'c1x': c1x, 'c1y': c1y,
                                    'c2x': c2x, 'c2y': c2y,
                                    'solution': notation,
                                    'difficulty': '简单'
                                })

    return results


def find_shuangche_puzzles():
    """找双车错杀残局"""
    results = []
    count = 0

    for r1x in range(9):
        for r1y in range(3, 8):
            for r2x in range(9):
                for r2y in range(3, 8):
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
                        notation = get_notation(board, mates[0], PieceColor.RED)
                        parsed = parse_move_str(board, notation, PieceColor.RED)
                        if parsed:
                            count += 1
                            if len(results) < 5:
                                results.append({
                                    'name': f'双车错{count}',
                                    'type': '双车错',
                                    'r1x': r1x, 'r1y': r1y,
                                    'r2x': r2x, 'r2y': r2y,
                                    'solution': notation,
                                    'difficulty': '简单'
                                })

    return results


def find_mabing_puzzles():
    """找马兵配合杀法（简单版，只有一个士）"""
    results = []
    count = 0

    # 将在九宫顶
    kx, ky = 4, 9

    # 士的位置
    for ax in [3, 4, 5]:
        for ay in [7, 8, 9]:
            if ax == kx and ay == ky:
                continue

            # 马的位置
            for nx in range(9):
                for ny in range(3, 9):
                    # 兵的位置（过河兵才有杀伤力）
                    for px in range(9):
                        for py in range(5, 9):
                            if nx == px and ny == py:
                                continue
                            if nx == kx and ny == ky:
                                continue
                            if px == kx and py == ky:
                                continue
                            if px == ax and py == ay:
                                continue
                            if nx == ax and ny == ay:
                                continue

                            board = Board()
                            for x in range(9):
                                for y in range(10):
                                    board.set_piece(x, y, None)

                            board.set_piece(kx, ky, King(PieceColor.BLACK))
                            board.set_piece(ax, ay, Advisor(PieceColor.BLACK))
                            board.set_piece(4, 0, King(PieceColor.RED))
                            board.set_piece(nx, ny, Horse(PieceColor.RED))
                            board.set_piece(px, py, Pawn(PieceColor.RED))

                            valid, mates = is_valid_puzzle(board)
                            if valid:
                                notation = get_notation(board, mates[0], PieceColor.RED)
                                parsed = parse_move_str(board, notation, PieceColor.RED)
                                if parsed:
                                    count += 1
                                    if len(results) < 3:
                                        results.append({
                                            'name': f'马兵杀{count}',
                                            'type': '马兵',
                                            'kx': kx, 'ky': ky,
                                            'ax': ax, 'ay': ay,
                                            'nx': nx, 'ny': ny,
                                            'px': px, 'py': py,
                                            'solution': notation,
                                            'difficulty': '简单'
                                        })

    return results


def main():
    print("搜索一步杀残局...")
    print()

    # 重炮杀
    print("搜索重炮杀...")
    chongpao = find_chongpao_puzzles()
    print(f"找到 {len(chongpao)} 个代表性重炮杀残局")
    for p in chongpao[:3]:
        print(f"  {p['name']}: {p['solution']}")

    print()

    # 双车错
    print("搜索双车错...")
    shuangche = find_shuangche_puzzles()
    print(f"找到 {len(shuangche)} 个代表性双车错残局")
    for p in shuangche[:3]:
        print(f"  {p['name']}: {p['solution']}")

    print()

    # 马兵
    print("搜索马兵杀...")
    mabing = find_mabing_puzzles()
    print(f"找到 {len(mabing)} 个代表性马兵杀残局")
    for p in mabing[:3]:
        print(f"  {p['name']}: {p['solution']}")

    print()

    # 输出为JSON格式，方便后续使用
    all_puzzles = chongpao + shuangche + mabing
    print(f"共找到 {len(all_puzzles)} 个残局")

    # 保存到文件
    with open('puzzle_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_puzzles, f, ensure_ascii=False, indent=2)
    print("已保存到 puzzle_data.json")


if __name__ == '__main__':
    main()
