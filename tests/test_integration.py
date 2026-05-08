from pieces import Color, Position, Piece, PieceType
from board import GameState
from moves import Move, get_all_moves, is_in_check, is_checkmate, is_stalemate


def test_position_from_algebraic():
    pos = Position.from_algebraic("e4")
    assert pos.file == 4
    assert pos.rank == 3


def test_position_to_algebraic():
    pos = Position(4, 3)
    assert pos.to_algebraic() == "e4"


def test_position_offset():
    pos = Position(4, 3)
    new_pos = pos.offset(1, -1)
    assert new_pos.file == 5
    assert new_pos.rank == 2


def test_piece_initialization():
    piece = Piece(PieceType.QUEEN, Color.WHITE)
    assert piece.piece_type == PieceType.QUEEN
    assert piece.color == Color.WHITE


def test_game_state_initialization():
    game = GameState()
    assert game.white_to_move is True
    from board import setup_initial_board
    game_with_pieces = setup_initial_board()
    assert game_with_pieces.board[0][0] is not None


def test_move_generation():
    game = GameState()
    moves = get_all_moves(game)
    assert len(moves) > 0


def test_in_check():
    game = GameState()
    game.set_piece(Position.from_algebraic("f7"), None)
    game.set_piece(Position.from_algebraic("d1"), Piece(PieceType.QUEEN, Color.BLACK))
    assert is_in_check(game, Color.WHITE) is True


def test_checkmate():
    game = GameState()
    game.set_piece(Position.from_algebraic("e7"), None)
    game.set_piece(Position.from_algebraic("e8"), None)
    game.set_piece(Position.from_algebraic("d1"), Piece(PieceType.QUEEN, Color.BLACK))
    game.set_piece(Position.from_algebraic("f1"), Piece(PieceType.BISHOP, Color.BLACK))
    assert is_checkmate(game, Color.WHITE) is True


def test_stalemate():
    # Create a position where black king has no legal moves but is not in check
    # Black king on e8, white king on e6, white rook on h8, white pawn on h7
    game = GameState()
    game.white_to_move = False
    for rank in range(8):
        for file_char in "abcdefgh":
            pos = Position.from_algebraic(f"{file_char}{rank+1}")
            game.set_piece(pos, None)
    game.set_piece(Position.from_algebraic("e6"), Piece(PieceType.KING, Color.WHITE))
    game.set_piece(Position.from_algebraic("e8"), Piece(PieceType.KING, Color.BLACK))
    game.set_piece(Position.from_algebraic("h8"), Piece(PieceType.ROOK, Color.WHITE))
    game.set_piece(Position.from_algebraic("h7"), Piece(PieceType.PAWN, Color.WHITE))
    assert is_stalemate(game, Color.BLACK) is True
