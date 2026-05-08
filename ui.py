from pieces import Color, Position, Piece, PieceType
from board import GameState, setup_initial_board
from moves import Move, get_all_moves, is_in_check, is_checkmate, is_stalemate


WHITE_PIECES = {
    PieceType.KING: '♔',
    PieceType.QUEEN: '♕',
    PieceType.ROOK: '♖',
    PieceType.BISHOP: '♗',
    PieceType.KNIGHT: '♘',
    PieceType.PAWN: '♙'
}

BLACK_PIECES = {
    PieceType.KING: '♚',
    PieceType.QUEEN: '♛',
    PieceType.ROOK: '♜',
    PieceType.BISHOP: '♝',
    PieceType.KNIGHT: '♞',
    PieceType.PAWN: '♟'
}


def get_piece_symbol(piece: Piece) -> str:
    if piece.color == Color.WHITE:
        return WHITE_PIECES[piece.piece_type]
    return BLACK_PIECES[piece.piece_type]


def display_board(game: GameState):
    board_grid = game.board

    print("  a b c d e f g h")
    for rank in range(7, -1, -1):
        print(f"{rank + 1} ", end="")
        for file in range(8):
            piece = board_grid[rank][file]
            if piece:
                print(f"{get_piece_symbol(piece)} ", end="")
            else:
                print(". ", end="")
        print(f"{rank + 1}")
    print("  a b c d e f g h")


def parse_position(pos_str: str) -> Position:
    if len(pos_str) != 2:
        return None
    file_char = pos_str[0]
    rank_char = pos_str[1]
    if file_char not in 'abcdefgh' or rank_char not in '12345678':
        return None
    return Position.from_algebraic(pos_str)


def parse_move(move_str: str) -> tuple[Position, Position]:
    move_str = move_str.strip()
    if len(move_str) != 4:
        return None, None
    from_pos = parse_position(move_str[:2])
    to_pos = parse_position(move_str[2:])
    return from_pos, to_pos


def get_player_move(game: GameState) -> tuple[Position, Position]:
    while True:
        turn_color = "White" if game.get_active_color() == Color.WHITE else "Black"
        move_str = input(f"{turn_color} to move: ").strip()
        if move_str.lower() == "quit":
            return None
        from_pos, to_pos = parse_move(move_str)
        if from_pos is None or to_pos is None:
            print("Invalid format. Use algebraic notation (e.g., e2e4)")
            continue
        return from_pos, to_pos


def format_move(from_pos: Position, to_pos: Position) -> str:
    return f"{from_pos.to_algebraic()}{to_pos.to_algebraic()}"


def apply_move(game: GameState, move: Move) -> None:
    piece = game.get_piece(move.from_pos)
    game.set_piece(move.from_pos, None)
    
    if move.en_passant:
        captured_pos = Position.from_algebraic(f"{move.to_pos.file}{move.from_pos.rank}")
        game.set_piece(captured_pos, None)
    
    if move.castling:
        rank = move.from_pos.rank
        if move.castling == "kingside":
            rook_from = Position.from_algebraic(f"h{rank}")
            rook_to = Position.from_algebraic(f"f{rank}")
        else:
            rook_from = Position.from_algebraic(f"a{rank}")
            rook_to = Position.from_algebraic(f"d{rank}")
        rook = game.get_piece(rook_from)
        game.set_piece(rook_from, None)
        game.set_piece(rook_to, rook)
    
    piece.has_moved = True
    game.set_piece(move.to_pos, piece)
    
    game.white_to_move = not game.white_to_move
    game.move_history.append(move.to_algebraic())


def play_game():
    game = setup_initial_board()
    
    while True:
        display_board(game)
        
        turn_color = "White" if game.get_active_color() == Color.WHITE else "Black"
        valid_moves = get_all_moves(game)
        
        if len(valid_moves) == 0:
            if is_in_check(game, game.get_active_color()):
                print(f"Checkmate! {turn_color} is in checkmate.")
                winner = "Black" if game.get_active_color() == Color.WHITE else "White"
                print(f"{winner} wins!")
                break
            else:
                print("Stalemate! The game is a draw.")
                break
        
        if is_in_check(game, game.get_active_color()):
            print(f"{turn_color} is in check!")
        
        from_pos = None
        to_pos = None
        
        while True:
            move_str = input(f"{turn_color} to move: ").strip()
            if move_str.lower() == "quit":
                print("Game terminated.")
                return
            
            if len(move_str) != 4:
                print("Invalid format. Use algebraic notation (e.g., e2e4)")
                continue
            
            from_pos = parse_position(move_str[:2])
            to_pos = parse_position(move_str[2:])
            
            if from_pos is None or to_pos is None:
                print("Invalid position format. Use algebraic notation (e.g., e2e4)")
                continue
            
            move = Move(from_pos, to_pos, game.get_piece(from_pos))
            valid = False
            for vm in valid_moves:
                if vm.from_pos == from_pos and vm.to_pos == to_pos:
                    valid = True
                    break
            
            if not valid:
                print("Invalid move. Try again.")
                continue
            
            break
        
        apply_move(game, move)
        
        if is_checkmate(game, game.get_active_color()):
            display_board(game)
            winner = "Black" if game.get_active_color() == Color.WHITE else "White"
            print(f"Checkmate! {winner} wins!")
            break
        
        if is_stalemate(game, game.get_active_color()):
            display_board(game)
            print("Stalemate! The game is a draw.")
            break
        
        if is_in_check(game, game.get_active_color()):
            print(f"{turn_color} is in check!")
