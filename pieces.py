"""Chess piece definitions and board representation."""

from enum import Enum
from typing import Optional
from dataclasses import dataclass

class PieceType(Enum):
    PAWN = 'p'
    KNIGHT = 'n'
    BISHOP = 'b'
    ROOK = 'r'
    QUEEN = 'q'
    KING = 'k'

class Color(Enum):
    WHITE = 'white'
    BLACK = 'black'

class Piece:
    def __init__(self, piece_type: PieceType, color: Color):
        self.piece_type = piece_type
        self.color = color
        self.has_moved = False

    def __repr__(self):
        symbol = self.piece_type.value.upper() if self.color == Color.WHITE else self.piece_type.value.lower()
        return symbol

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.piece_type == other.piece_type and self.color == other.color


@dataclass
class Position:
    file: int  # 0-7 (a-h)
    rank: int  # 0-7 (1-8)

    def __post_init__(self):
        if not (0 <= self.file <= 7 and 0 <= self.rank <= 7):
            raise ValueError(f"Invalid position: ({self.file}, {self.rank})")

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Position):
            return False
        return self.file == other.file and self.rank == other.rank

    def to_algebraic(self) -> str:
        """Convert to algebraic notation like 'e4'."""
        file_char = chr(ord('a') + self.file)
        rank_char = str(self.rank + 1)
        return f"{file_char}{rank_char}"

    @classmethod
    def from_algebraic(cls, notation: str) -> 'Position':
        """Parse algebraic notation like 'e4' to Position."""
        if len(notation) != 2:
            raise ValueError(f"Invalid algebraic notation: {notation}")
        file_char, rank_char = notation[0], notation[1]
        if file_char not in 'abcdefgh' or rank_char not in '12345678':
            raise ValueError(f"Invalid algebraic notation: {notation}")
        return cls(ord(file_char) - ord('a'), int(rank_char) - 1)

    def __hash__(self):
        return hash((self.file, self.rank))

    def to_coords(self) -> tuple[int, int]:
        """Convert to (row, col) coordinates for board array access."""
        return (self.rank, self.file)

    @classmethod
    def from_coords(cls, row: int, col: int) -> 'Position':
        """Create Position from (row, col) board coordinates."""
        return cls(col, row)

    def offset(self, file_delta: int, rank_delta: int) -> 'Position':
        """Return a new position offset by the given amounts, or None if out of bounds."""
        new_file = self.file + file_delta
        new_rank = self.rank + rank_delta
        if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
            return Position(new_file, new_rank)
        return None


class Board:
    def __init__(self):
        self.squares: list[list[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.setup_initial_position()

    def setup_initial_position(self):
        """Set up pieces in starting positions."""
        # Black pieces (rank 0 and 1)
        back_row = [
            Piece(PieceType.ROOK, Color.BLACK),
            Piece(PieceType.KNIGHT, Color.BLACK),
            Piece(PieceType.BISHOP, Color.BLACK),
            Piece(PieceType.QUEEN, Color.BLACK),
            Piece(PieceType.KING, Color.BLACK),
            Piece(PieceType.BISHOP, Color.BLACK),
            Piece(PieceType.KNIGHT, Color.BLACK),
            Piece(PieceType.ROOK, Color.BLACK)
        ]
        for i, piece in enumerate(back_row):
            self.squares[0][i] = piece
            self.squares[1][i] = Piece(PieceType.PAWN, Color.BLACK)

        # White pieces (rank 6 and 7)
        for i, piece in enumerate(back_row):
            self.squares[7][i] = Piece(piece.piece_type, Color.WHITE)
            self.squares[6][i] = Piece(PieceType.PAWN, Color.WHITE)

    def __getitem__(self, pos: Position) -> Optional[Piece]:
        return self.squares[pos.rank][pos.file]

    def __setitem__(self, pos: Position, piece: Optional[Piece]):
        self.squares[pos.rank][pos.file] = piece

    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        new_board = Board.__new__(Board)
        new_board.squares = []
        for rank in self.squares:
            new_rank = []
            for piece in rank:
                if piece is not None:
                    new_piece = Piece(piece.piece_type, piece.color)
                    new_piece.has_moved = piece.has_moved
                    new_rank.append(new_piece)
                else:
                    new_rank.append(None)
            new_board.squares.append(new_rank)
        return new_board

    def get_piece(self, file: int, rank: int) -> Optional[Piece]:
        """Get piece at given coordinates."""
        if 0 <= file <= 7 and 0 <= rank <= 7:
            return self.squares[rank][file]
        return None

    def is_empty(self, pos: Position) -> bool:
        """Check if a square is empty."""
        return self.squares[pos.rank][pos.file] is None

    def is_own_piece(self, pos: Position, color: Color) -> bool:
        """Check if piece at position belongs to the given color."""
        piece = self.squares[pos.rank][pos.file]
        return piece is not None and piece.color == color

    def is_opponent_piece(self, pos: Position, color: Color) -> bool:
        """Check if piece at position is opponent's."""
        piece = self.squares[pos.rank][pos.file]
        return piece is not None and piece.color != color
