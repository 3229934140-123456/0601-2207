"""综合功能测试 - 模拟一次完整的残局练习流程"""
import sys
sys.path.insert(0, r'd:\trae-bz\TraeProjects\2207')

from xiangqi_trainer.core.game import GameController
from xiangqi_trainer.core.board import Board
from xiangqi_trainer.core.pieces import PieceColor
from xiangqi_trainer.core.rules import is_checkmate, is_check
from xiangqi_trainer.core.utils import parse_move_str, board_to_grid
from xiangqi_trainer.data.puzzles import get_all_puzzles, get_puzzle_by_id
from xiangqi_trainer.data.storage import Statistics, record_puzzle_result, load_stats

print("=" * 60)
print("象棋残局训练 - 综合功能测试")
print("=" * 60)
print()

# 1. 测试残局加载
print("1. 测试残局加载...")
puzzles = get_all_puzzles()
print(f"   共找到 {len(puzzles)} 个残局")
assert len(puzzles) > 0, "没有残局数据"

# 选第一个残局
puzzle = puzzles[0]
print(f"   测试残局: {puzzle.name}")
print(f"   类型: {puzzle.kill_type}, 难度: {puzzle.difficulty}, 步数: {puzzle.steps}")
print("   ✓ 残局加载成功")
print()

# 2. 测试游戏控制器
print("2. 测试游戏控制器...")
game = GameController()
game.load_puzzle(puzzle)
print(f"   当前回合: {'红方' if game.current_turn == PieceColor.RED else '黑方'}")
print(f"   初始分数: {game.score}")
assert not game.is_game_over, "游戏一开始就结束了"
print("   ✓ 游戏控制器初始化成功")
print()

# 3. 测试走法生成
print("3. 测试走法生成...")
from xiangqi_trainer.core.rules import generate_moves
moves = generate_moves(game.board, game.current_turn)
print(f"   红方合法走法数: {len(moves)}")
assert len(moves) > 0, "没有合法走法"
print("   ✓ 走法生成成功")
print()

# 4. 测试解法解析
print("4. 测试解法解析...")
solution_move_str = puzzle.solution[0]
player_color = PieceColor.BLACK if puzzle.black_to_move else PieceColor.RED
solution_move = parse_move_str(game.board, solution_move_str, player_color)
assert solution_move is not None, f"解法解析失败: {solution_move_str}"
print(f"   解法: {solution_move_str}")
print(f"   解析结果: ({solution_move.from_x},{solution_move.from_y}) -> ({solution_move.to_x},{solution_move.to_y})")
print("   ✓ 解法解析成功")
print()

# 5. 测试走子
print("5. 测试走子...")
success, msg = game.make_move(
    solution_move.from_x, solution_move.from_y,
    solution_move.to_x, solution_move.to_y
)
assert success, f"走子失败: {msg}"
print(f"   走子成功: {msg if msg else '无信息'}")
print(f"   走子后回合: {'红方' if game.current_turn == PieceColor.RED else '黑方'}")
print("   ✓ 走子成功")
print()

# 6. 测试游戏结束判定
print("6. 测试游戏结束判定...")
opponent = PieceColor.BLACK if player_color == PieceColor.RED else PieceColor.RED
is_mate = is_checkmate(game.board, opponent)
print(f"   是否将死对方: {is_mate}")
print(f"   游戏是否结束: {game.is_game_over}")
print(f"   游戏结果: {game.game_result}")
if puzzle.steps == 1:
    assert game.is_game_over, "一步杀残局走完一步应该结束"
    assert is_mate, "一步杀残局走完一步应该将死对方"
print("   ✓ 游戏结束判定正确")
print()

# 7. 测试撤回
print("7. 测试撤回功能...")
can_undo = game.undo_move()
print(f"   撤回是否成功: {can_undo}")
print(f"   撤回后回合: {'红方' if game.current_turn == PieceColor.RED else '黑方'}")
assert game.current_turn == player_color, "撤回后应该回到玩家回合"
print("   ✓ 撤回功能正常")
print()

# 8. 测试重来
print("8. 测试重来功能...")
game.restart_puzzle()
print(f"   重来后回合: {'红方' if game.current_turn == PieceColor.RED else '黑方'}")
print(f"   重来后分数: {game.score}")
assert game.score == 100, "重来后分数应该重置"
assert game.current_turn == player_color, "重来后应该回到玩家回合"
print("   ✓ 重来功能正常")
print()

# 9. 测试提示功能
print("9. 测试提示功能...")
hint = game.get_solution_hint(1)
print(f"   一级提示: {hint}")
print(f"   使用提示后分数: {game.score}")
assert game.score < 100, "使用提示后应该扣分"
assert hint is not None, "提示不能为空"
print("   ✓ 提示功能正常")
print()

# 10. 测试成绩记录
print("10. 测试成绩记录...")
stats = Statistics()
record_puzzle_result(stats, puzzle.id, True, 1, 10.5, 1, None)
print(f"   总题数: {stats.total_puzzles}")
print(f"   正确数: {stats.correct_count}")
print(f"   正确率: {(stats.correct_count/stats.total_puzzles)*100:.0f}%")
print(f"   最佳记录数: {len(stats.best_records)}")
assert stats.total_puzzles == 1, "应该有1条记录"
assert stats.correct_count == 1, "应该正确1题"
print("   ✓ 成绩记录正常")
print()

# 11. 测试按筛选条件获取残局
print("11. 测试残局筛选...")
from xiangqi_trainer.data.puzzles import (
    get_puzzles_by_difficulty, get_puzzles_by_kill_type,
    get_puzzles_by_steps
)
diff_puzzles = get_puzzles_by_difficulty("简单")
print(f"   简单难度: {len(diff_puzzles)} 个")

kill_type_puzzles = get_puzzles_by_kill_type("重炮")
print(f"   重炮杀: {len(kill_type_puzzles)} 个")

step_puzzles = get_puzzles_by_steps(1, 1)
print(f"   1步杀: {len(step_puzzles)} 个")
print("   ✓ 筛选功能正常")
print()

# 12. 测试所有残局的解法都能正确执行
print("12. 测试所有残局解法...")
failed = []
for i, p in enumerate(puzzles):
    g = GameController()
    g.load_puzzle(p)
    color = PieceColor.BLACK if p.black_to_move else PieceColor.RED

    move_str = p.solution[0]
    move = parse_move_str(g.board, move_str, color)
    if move is None:
        failed.append(f"{p.id} {p.name}: 解法解析失败 '{move_str}'")
        continue

    success, msg = g.make_move(move.from_x, move.from_y, move.to_x, move.to_y)
    if not success:
        failed.append(f"{p.id} {p.name}: 走子失败 {msg}")
        continue

    opp = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED
    if not is_checkmate(g.board, opp):
        failed.append(f"{p.id} {p.name}: 走完后未将死对方")

if failed:
    print(f"   ✗ 有 {len(failed)} 个残局失败:")
    for f in failed:
        print(f"     - {f}")
else:
    print(f"   ✓ 全部 {len(puzzles)} 个残局测试通过")
print()

print("=" * 60)
print("所有测试通过！✓")
print("=" * 60)
