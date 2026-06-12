"""走法解析调试脚本"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.rules import generate_moves
from xiangqi_trainer.core.pieces import PieceColor, PieceType
from xiangqi_trainer.core.utils import parse_move_str


def debug_parse_move():
    """调试走法解析"""
    board = Board()
    print("初始局面（标准开局）:")
    for y in range(Board.HEIGHT - 1, -1, -1):
        row = f"{y+1:2d} "
        for x in range(Board.WIDTH):
            piece = board.get_piece(x, y)
            if piece:
                row += piece.chinese_name
            else:
                row += "·"
        print(row)
    print()

    # 打印红方所有合法走法
    moves = generate_moves(board, PieceColor.RED)
    print(f"红方合法走法共 {len(moves)} 个")
    
    # 按棋子类型分组
    by_type = {}
    for m in moves:
        ptype = m.piece.type
        if ptype not in by_type:
            by_type[ptype] = []
        by_type[ptype].append(m)
    
    for ptype, type_moves in by_type.items():
        print(f"\n{ptype.value}: {len(type_moves)} 个走法")
        # 按起始列分组
        by_col = {}
        for m in type_moves:
            col = 9 - m.from_x
            if col not in by_col:
                by_col[col] = []
            by_col[col].append(m)
        
        for col in sorted(by_col.keys()):
            col_moves = by_col[col]
            print(f"  第{col}列(x={9-col}): {len(col_moves)} 个走法")
            for m in col_moves[:3]:
                direction = ""
                if m.from_y == m.to_y:
                    direction = "平"
                elif m.to_y > m.from_y:
                    direction = "进"
                else:
                    direction = "退"
                
                if ptype in (PieceType.HORSE, PieceType.ADVISOR, PieceType.ELEPHANT):
                    target_col = 9 - m.to_x
                    target_str = f"到第{target_col}列"
                else:
                    dist = abs(m.to_y - m.from_y)
                    target_str = f"{dist}步"
                
                print(f"    ({m.from_x},{m.from_y}) -> ({m.to_x},{m.to_y}) {direction}{target_str}")

    # 测试解析几个常见走法
    test_moves = [
        ('P2+1', '红兵七进一'),
        ('P7+1', '红兵三进一'),
        ('N2+3', '红马八进七'),
        ('R1=2', '红车九平八'),
        ('C2=5', '红炮八平五'),
    ]

    print("\n\n测试走法解析:")
    for move_str, desc in test_moves:
        move = parse_move_str(board, move_str, PieceColor.RED)
        status = "✓" if move else "✗"
        print(f"  {status} {move_str} ({desc}): ", end="")
        if move:
            print(f"({move.from_x},{move.from_y}) -> ({move.to_x},{move.to_y})")
        else:
            print("解析失败")


if __name__ == '__main__':
    debug_parse_move()
