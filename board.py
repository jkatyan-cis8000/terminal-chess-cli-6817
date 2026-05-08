"""Board representation and game state management."""

from typing import Optional

from pieces import Piece, PieceType, Color, Position


class GameState:
    """Holds the current state of the chess game."""
    
    def __init__(self):
        """Initialize game state."""
        # Board: 8x8 grid of Piece objects or None
        self.board: list[list[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        
        # Current turn
        self.white_to_move = True
        
        # Castling rights
        self.white_kingside = True
        self.white_queenside = True
        self.black_kingside = True
        self.black_queenside = True
        
        # En passant target square (where a pawn would move to capture en passant)
        self.en_passant_target: Optional[Position] = None
        
        # Halfmove clock (for 50-move rule)
        self.halfmove_clock = 0
        
        # Fullmove number
        self.fullmove_number = 1
        
        # Move history for debugging/analysis
        self.move_history: list[str] = []
        
        self.setup_initial_position()
    
    def copy(self) -> "GameState":
        """Create a deep copy of the game state."""
        state = GameState()
        state.board = [[piece for piece in row] for row in self.board]
        state.white_to_move = self.white_to_move
        state.white_kingside = self.white_kingside
        state.white_queenside = self.white_queenside
        state.black_kingside = self.black_kingside
        state.black_queenside = self.black_queenside
        state.en_passant_target = self.en_passant_target
        state.halfmove_clock = self.halfmove_clock
        state.fullmove_number = self.fullmove_number
        state.move_history = self.move_history.copy()
        return state
    
    def get_piece(self, pos: Position) -> Optional[Piece]:
        """Get the piece at a position."""
        row, col = pos.to_coords()
        return self.board[row][col]
    
    def set_piece(self, pos: Position, piece: Optional[Piece]) -> None:
        """Set a piece at a position."""
        row, col = pos.to_coords()
        self.board[row][col] = piece
    
    def is_white_to_move(self) -> bool:
        """Check if it's white's turn."""
        return self.white_to_move
    
    def get_active_color(self) -> Color:
        """Get the color of the player whose turn it is."""
        return Color.WHITE if self.white_to_move else Color.BLACK
    
    def get_opponent_color(self) -> Color:
        """Get the color of the opponent."""
        return Color.BLACK if self.white_to_move else Color.WHITE
    
    def setup_initial_position(self):
        """Set up the board with the standard chess starting position."""
        for file_char in "abcdefgh":
            self.set_piece(Position.from_algebraic(f"{file_char}2"), Piece(PieceType.PAWN, Color.WHITE))
            self.set_piece(Position.from_algebraic(f"{file_char}7"), Piece(PieceType.PAWN, Color.BLACK))
        
        back_row_white = [
            Piece(PieceType.ROOK, Color.WHITE),
            Piece(PieceType.KNIGHT, Color.WHITE),
            Piece(PieceType.BISHOP, Color.WHITE),
            Piece(PieceType.QUEEN, Color.WHITE),
            Piece(PieceType.KING, Color.WHITE),
            Piece(PieceType.BISHOP, Color.WHITE),
            Piece(PieceType.KNIGHT, Color.WHITE),
            Piece(PieceType.ROOK, Color.WHITE),
        ]
        for i, file_char in enumerate("abcdefgh"):
            self.set_piece(Position.from_algebraic(f"{file_char}1"), back_row_white[i])
        
        back_row_black = [
            Piece(PieceType.ROOK, Color.BLACK),
            Piece(PieceType.KNIGHT, Color.BLACK),
            Piece(PieceType.BISHOP, Color.BLACK),
            Piece(PieceType.QUEEN, Color.BLACK),
            Piece(PieceType.KING, Color.BLACK),
            Piece(PieceType.BISHOP, Color.BLACK),
            Piece(PieceType.KNIGHT, Color.BLACK),
            Piece(PieceType.ROOK, Color.BLACK),
        ]
        for i, file_char in enumerate("abcdefgh"):
            self.set_piece(Position.from_algebraic(f"{file_char}8"), back_row_black[i])


def setup_initial_board() -> GameState:
    """
    Set up the board with the standard chess starting position.
    
    Returns:
        GameState with pieces in starting positions
    """
    state = GameState()
    
    # Clear board
    for row in range(8):
        for col in range(8):
            state.board[row][col] = None
    
    # Set up pawns using Position.from_algebraic
    for file_char in "abcdefgh":
        state.set_piece(Position.from_algebraic(f"{file_char}2"), Piece(PieceType.PAWN, Color.WHITE))
        state.set_piece(Position.from_algebraic(f"{file_char}7"), Piece(PieceType.PAWN, Color.BLACK))
    
    # Set up white pieces (rank 1) using Position.from_algebraic
    back_row_white = [
        Piece(PieceType.ROOK, Color.WHITE),
        Piece(PieceType.KNIGHT, Color.WHITE),
        Piece(PieceType.BISHOP, Color.WHITE),
        Piece(PieceType.QUEEN, Color.WHITE),
        Piece(PieceType.KING, Color.WHITE),
        Piece(PieceType.BISHOP, Color.WHITE),
        Piece(PieceType.KNIGHT, Color.WHITE),
        Piece(PieceType.ROOK, Color.WHITE),
    ]
    for i, file_char in enumerate("abcdefgh"):
        state.set_piece(Position.from_algebraic(f"{file_char}1"), back_row_white[i])
    
    # Set up black pieces (rank 8) using Position.from_algebraic
    back_row_black = [
        Piece(PieceType.ROOK, Color.BLACK),
        Piece(PieceType.KNIGHT, Color.BLACK),
        Piece(PieceType.BISHOP, Color.BLACK),
        Piece(PieceType.QUEEN, Color.BLACK),
        Piece(PieceType.KING, Color.BLACK),
        Piece(PieceType.BISHOP, Color.BLACK),
        Piece(PieceType.KNIGHT, Color.BLACK),
        Piece(PieceType.ROOK, Color.BLACK),
    ]
    for i, file_char in enumerate("abcdefgh"):
        state.set_piece(Position.from_algebraic(f"{file_char}8"), back_row_black[i])
    
    return state
