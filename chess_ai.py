import chess


# ============================================================
# PIECE VALUES
# ============================================================

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100
}

# Total starting value of capturable pieces (8*1 + 2*3 + 2*3 + 2*5 + 1*9 = 39)
STARTING_MATERIAL = 39


# ============================================================
# CALCULATE INDIVIDUAL PLAYER SCORES
# ============================================================

def get_player_scores(board):

    white_material = 0
    black_material = 0

    # 1. Material (excluding King so starting material is 39 instead of 139)
    for piece_type, value in PIECE_VALUES.items():
        if piece_type == chess.KING:
            continue

        white_material += len(board.pieces(piece_type, chess.WHITE)) * value
        black_material += len(board.pieces(piece_type, chess.BLACK)) * value

    # Points earned by capturing opponent's pieces
    white_captured_points = STARTING_MATERIAL - black_material
    black_captured_points = STARTING_MATERIAL - white_material

    # 2. Center Control Bonus
    white_center = 0
    black_center = 0
    center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]

    for square in center_squares:
        piece = board.piece_at(square)
        if piece is not None:
            if piece.color == chess.WHITE:
                white_center += 0.2
            else:
                black_center += 0.2

    # 3. Mobility Bonus
    current_turn = board.turn

    board.turn = chess.WHITE
    white_mobility = board.legal_moves.count() * 0.01

    board.turn = chess.BLACK
    black_mobility = board.legal_moves.count() * 0.01

    board.turn = current_turn

    # Total evaluation score for each player
    white_total_score = white_material + white_center + white_mobility
    black_total_score = black_material + black_center + black_mobility

    return {
        "white_points": white_captured_points,
        "black_points": black_captured_points,
        "white_eval": round(white_total_score, 2),
        "black_eval": round(black_total_score, 2)
    }


def print_scoreboard(board):
    scores = get_player_scores(board)
    net_eval = round(scores["white_eval"] - scores["black_eval"], 2)

    if net_eval > 0:
        status = f"You are ahead by +{net_eval}"
    elif net_eval < 0:
        status = f"AI is ahead by {net_eval}"
    else:
        status = "Game is tied (0.0)"

    print()
    print("------------------------------------")
    print("             SCOREBOARD             ")
    print("------------------------------------")
    print(f"You (WHITE) | Captured Score: {scores['white_points']} pts | Eval Score: {scores['white_eval']}")
    print(f"AI  (BLACK) | Captured Score: {scores['black_points']} pts | Eval Score: {scores['black_eval']}")
    print(f"Status      | {status}")
    print("------------------------------------")


# ============================================================
# BOARD EVALUATION
# Positive  -> White is better
# Negative  -> Black is better
# ============================================================

def evaluate_board(board):

    # Checkmate
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -9999      # Black wins
        else:
            return 9999       # White wins

    # Draw
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    scores = get_player_scores(board)
    return scores["white_eval"] - scores["black_eval"]


# ============================================================
# MINIMAX + ALPHA-BETA PRUNING
# ============================================================

def minimax(board, depth, alpha, beta, maximizing_player):

    # Stop searching
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    # --------------------------------------------------------
    # WHITE = MAXIMIZING PLAYER
    # --------------------------------------------------------
    if maximizing_player:

        best_score = float('-inf')

        for move in board.legal_moves:

            board.push(move)

            score = minimax(
                board,
                depth - 1,
                alpha,
                beta,
                False
            )

            board.pop()

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if beta <= alpha:
                break

        return best_score

    # --------------------------------------------------------
    # BLACK = MINIMIZING PLAYER
    # --------------------------------------------------------
    else:

        best_score = float('inf')

        for move in board.legal_moves:

            board.push(move)

            score = minimax(
                board,
                depth - 1,
                alpha,
                beta,
                True
            )

            board.pop()

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            if beta <= alpha:
                break

        return best_score


# ============================================================
# FIND BEST MOVE FOR AI
# AI = BLACK = MINIMIZING PLAYER
# ============================================================

def find_best_move(board, depth):

    best_move = None
    best_score = float('inf')

    for move in board.legal_moves:

        is_capture = board.is_capture(move)
        moving_piece = board.piece_at(move.from_square)
        move_penalty = 0

        # Discourage unnecessary rook/queen movement during the opening
        if board.fullmove_number <= 10:
            if moving_piece is not None:
                if moving_piece.piece_type == chess.ROOK:
                    move_penalty = 0.15
                elif moving_piece.piece_type == chess.QUEEN:
                    move_penalty = 0.05

        board.push(move)

        score = minimax(
            board,
            depth - 1,
            float('-inf'),
            float('inf'),
            True
        )

        board.pop()

        score += move_penalty

        if is_capture:
            score -= 0.1

        if score < best_score:
            best_score = score
            best_move = move

    return best_move, best_score


# ============================================================
# PLAY GAME
# ============================================================

def play_game():

    board = chess.Board()

    print()
    print("====================================")
    print("       AI CHESS USING MINIMAX")
    print("       + ALPHA-BETA PRUNING")
    print("====================================")

    print()
    print("You are WHITE.")
    print("AI is BLACK.")

    print()
    print("Enter moves using UCI format.")
    print("Example: e2e4")
    print("Type 'quit' to exit.")

    print()
    print(board)
    print_scoreboard(board)

    # --------------------------------------------------------
    # GAME LOOP
    # --------------------------------------------------------

    while not board.is_game_over():

        # ====================================================
        # HUMAN TURN
        # ====================================================

        if board.turn == chess.WHITE:

            print()
            print("Your turn.")

            move_input = input("Your move: ").strip()

            # Quit
            if move_input.lower() == "quit":
                print()
                print("Game ended.")
                print_scoreboard(board)
                return

            try:
                move = chess.Move.from_uci(move_input)

                if move in board.legal_moves:
                    board.push(move)

                    print()
                    print("Board after your move:")
                    print(board)
                    print_scoreboard(board)

                else:
                    print()
                    print("Illegal move.")
                    print("Please try again.")

            except ValueError:
                print()
                print("Invalid move format.")
                print("Use format like e2e4.")

        # ====================================================
        # AI TURN
        # ====================================================

        else:

            print()
            print("AI is thinking...")

            best_move, best_score = find_best_move(
                board,
                depth=2
            )

            if best_move is None:
                print("AI could not find a move.")
                break

            board.push(best_move)

            print()
            print("AI move:", best_move)
            print("AI evaluation:", round(best_score, 2))

            print()
            print("Board after AI move:")
            print(board)
            print_scoreboard(board)

    # ========================================================
    # GAME RESULT
    # ========================================================

    print()
    print("====================================")
    print("              GAME OVER")
    print("====================================")

    print_scoreboard(board)

    if board.is_checkmate():
        if board.turn == chess.WHITE:
            print("AI WINS!")
        else:
            print("YOU WIN!")

    elif board.is_stalemate():
        print("DRAW - STALEMATE")

    elif board.is_insufficient_material():
        print("DRAW - INSUFFICIENT MATERIAL")

    else:
        print("DRAW")


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    play_game()