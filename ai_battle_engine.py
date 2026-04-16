# ai_battle_engine.py
# ---------------------------------------------------------
# Project: Gomoku AI Coach (15x15)
# Feature: Logic Port (JS to Python) for Offline Simulation
# ---------------------------------------------------------

import random
import logging

logger = logging.getLogger(__name__)

BOARD_SIZE = 15
TOTAL_CELLS = BOARD_SIZE * BOARD_SIZE

class GomokuSimulator:
    """
    负责在服务端模拟五子棋对局，完全复刻前端 index.html 的启发式评分逻辑。
    """
    def __init__(self):
        self.board = [""] * TOTAL_CELLS

    def index_to_coord(self, index):
        col = chr(65 + (index % BOARD_SIZE))
        row = (index // BOARD_SIZE) + 1
        return f"{col}{row}"

    def check_winner(self, board):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                idx = r * BOARD_SIZE + c
                player = board[idx]
                if not player: continue
                for dr, dc in directions:
                    count = 1
                    for step in range(1, 5):
                        nr, nc = r + dr * step, c + dc * step
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                            if board[nr * BOARD_SIZE + nc] == player: count += 1
                            else: break
                        else: break
                    if count >= 5: return player
        if "" not in board: return "tie"
        return None

    def evaluate_cell(self, board, index, player):
        r, c = divmod(index, BOARD_SIZE)
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        total_score = 0
        
        for dr, dc in directions:
            count = 1
            open_ends = 0
            # Check both directions
            for sign in [1, -1]:
                for step in range(1, 5):
                    nr, nc = r + sign * dr * step, c + sign * dc * step
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                        if board[nr * BOARD_SIZE + nc] == player:
                            count += 1
                        elif board[nr * BOARD_SIZE + nc] == "":
                            open_ends += 1
                            break
                        else: break
                    else: break
            
            if count >= 5: return 100000
            if count == 4:
                total_score += 10000 if open_ends == 2 else 1000
            elif count == 3:
                total_score += 500 if open_ends == 2 else 50
            elif count == 2:
                total_score += 50 if open_ends == 2 else 5
            elif count == 1:
                total_score += 5
        return total_score

    def get_best_move(self, board, player):
        opponent = "O" if player == "X" else "X"
        best_score = -1
        best_moves = []
        
        for i in range(TOTAL_CELLS):
            if board[i] == "":
                # 进攻评分 + 稍微加权的防御评分
                score = self.evaluate_cell(board, i, player) + self.evaluate_cell(board, i, opponent) * 1.1
                if score > best_score:
                    best_score = score
                    best_moves = [i]
                elif score == best_score:
                    best_moves.append(i)
        
        return random.choice(best_moves) if best_moves else None

    def run_match(self):
        """执行完整的模拟对局，返回符合前端格式的历史记录。"""
        history = []
        current_player = "X" # 模拟中 X 代表 AI_1, O 代表 AI_2
        step = 1
        
        while True:
            move_idx = self.get_best_move(self.board, current_player)
            if move_idx is None: break
            
            self.board[move_idx] = current_player
            
            # 构建符合前端 recordMove 结构的字典
            history.append({
                "step": step,
                "player": current_player,
                "index": move_idx,
                "evaluation_label": "AI Strategy",
                "comment": f"Automated battle move at {self.index_to_coord(move_idx)}",
                "missed_best_move": ""
            })
            
            winner = self.check_winner(self.board)
            if winner:
                result_str = "Draw" if winner == "tie" else f"AI_{winner} Wins"
                return history, result_str
            
            current_player = "O" if current_player == "X" else "X"
            step += 1