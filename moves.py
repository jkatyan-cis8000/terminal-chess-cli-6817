"""Move generation and validation logic."""

from typing import Optional

from pieces import Piece, PieceType, Color, Position
from board import GameState


class Move:
    """Represents a chess move."""
    
    def __init__(
        self,
        from_pos: Position,
        to_pos: Position,
        piece: Piece,
        captured: Optional[Piece] = None,
        promotion: Optional[PieceType] = None,
        castling: Optional[str] = None,
        en_passant: bool = False,
    ):
        """
        Initialize a move.
        
        Args:
            from_pos: Starting position
            to_pos: Ending position
            piece: The piece being moved
            captured: Piece captured, if any
            promotion: Piece type to promote to, if any
            castling: 'kingside' or 'queenside' if castling move
            en_passant: True if this is an en passant capture
        """
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.piece = piece
        self.captured = captured
        self.promotion = promotion
        self.castling = castling
        self.en_passant = en_passant
    
    def __repr__(self) -> str:
        """String representation of the move."""
        move_str = f"{self.from_pos.to_algebraic()}-{self.to_pos.to_algebraic()}"
        if self.promotion:
            move_str += f"={self.promotion.value[0].upper()}"
        if self.castling:
            move_str += f" ({self.castling} castling)"
        if self.en_passant:
            move_str += " (en passant)"
        return move_str
    
    def to_algebraic(self) -> str:
        """Convert move to standard algebraic notation."""
        if self.castling == "kingside":
            return "O-O"
        if self.castling == "queenside":
            return "O-O-O"
        
        piece_letter = "" if self.piece.piece_type == PieceType.PAWN else self.piece.piece_type.value[0].upper()
        
        capture = "x" if self.captured or self.en_passant else ""
        
        if self.piece.piece_type == PieceType.PAWN and capture:
            piece_letter = self.from_pos.file
        
        to_str = self.to_pos.to_algebraic()
        
        promotion = ""
        if self.promotion:
            promotion = f"={self.promotion.value[0].upper()}"
        
        return f"{piece_letter}{capture}{to_str}{promotion}"


def get_all_moves(state: GameState) -> list[Move]:
    """
    Get all legal moves for the current player.
    
    Args:
        state: Current game state
        
    Returns:
        List of all legal moves
    """
    active_color = state.get_active_color()
    moves = []
    
    # Generate all pseudo-legal moves (before checking for check)
    for row in range(8):
        for col in range(8):
            piece = state.board[row][col]
            if piece and piece.color == active_color:
                pos = Position.from_coords(row, col)
                piece_moves = generate_piece_moves(state, pos, piece)
                moves.extend(piece_moves)
    
    # Filter out moves that leave the king in check
    legal_moves = []
    for move in moves:
        if not move_leaves_king_in_check(state, move):
            legal_moves.append(move)
    
    return legal_moves


def generate_piece_moves(state: GameState, pos: Position, piece: Piece) -> list[Move]:
    """
    Generate all pseudo-legal moves for a piece at a position.
    
    Args:
        state: Current game state
        pos: Position of the piece
        piece: The piece to generate moves for
        
    Returns:
        List of moves (may include moves that leave king in check)
    """
    moves = []
    color = piece.color
    opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
    
    row, col = pos.to_coords()
    
    # Pawn moves
    if piece.piece_type == PieceType.PAWN:
        direction = 1 if color == Color.WHITE else -1
        start_rank = 1 if color == Color.WHITE else 6
        promotion_rank = 7 if color == Color.WHITE else 0
        
        # DEBUG: Print pawn info
        print(f"DEBUG: Pawn at {pos.to_algebraic()} (file={pos.file}, rank={pos.rank}), color={color}")
        print(f"  direction={direction}, start_rank={start_rank}, promotion_rank={promotion_rank}")
        
        # Forward move
        forward = pos.offset(0, direction)
        print(f"  forward offset: {forward.to_algebraic() if forward else None}")
        if forward and state.get_piece(forward) is None:
            if forward.rank == promotion_rank:
                moves.append(Move(pos, forward, piece, promotion=PieceType.QUEEN))
                moves.append(Move(pos, forward, piece, promotion=PieceType.ROOK))
                moves.append(Move(pos, forward, piece, promotion=PieceType.BISHOP))
                moves.append(Move(pos, forward, piece, promotion=PieceType.KNIGHT))
            else:
                moves.append(Move(pos, forward, piece))
                print(f"  added forward move: {pos.to_algebraic()} -> {forward.to_algebraic()}")
                
                # Double move from starting position
                if pos.rank == start_rank:
                    double = forward.offset(0, direction)
                    print(f"  double offset: {double.to_algebraic() if double else None}, pos.rank={pos.rank}, start_rank={start_rank}")
                    if double and state.get_piece(double) is None:
                        moves.append(Move(pos, double, piece))
                        print(f"  added double move: {pos.to_algebraic()} -> {double.to_algebraic()}")
        
        # Captures
        for file_delta in [-1, 1]:
            capture_pos = pos.offset(file_delta, direction)
            print(f"  capture offset file_delta={file_delta}: {capture_pos.to_algebraic() if capture_pos else None}")
            if capture_pos:
                target = state.get_piece(capture_pos)
                print(f"  target at {capture_pos.to_algebraic()}: {target}")
                if target and target.color == opponent_color:
                    if capture_pos.rank == promotion_rank:
                        moves.append(Move(pos, capture_pos, piece, captured=target, promotion=PieceType.QUEEN))
                        moves.append(Move(pos, capture_pos, piece, captured=target, promotion=PieceType.ROOK))
                        moves.append(Move(pos, capture_pos, piece, captured=target, promotion=PieceType.BISHOP))
                        moves.append(Move(pos, capture_pos, piece, captured=target, promotion=PieceType.KNIGHT))
                        print(f"  added capture+promotion: {pos.to_algebraic()} -> {capture_pos.to_algebraic()}")
                else:
                    moves.append(Move(pos, capture_pos, piece, captured=target))
                    print(f"  added capture: {pos.to_algebraic()} -> {capture_pos.to_algebraic()}")
                
                # En passant
                print(f"  en_passant_target={state.en_passant_target}, capture_pos={capture_pos.to_algebraic() if capture_pos else None}")
                if state.en_passant_target == capture_pos:
                    en_passant_captured_pos = Position(capture_pos.file, pos.rank)
                    en_passant_captured = state.get_piece(en_passant_captured_pos)
                    if en_passant_captured and en_passant_captured.piece_type == PieceType.PAWN:
                        moves.append(Move(pos, capture_pos, piece, captured=en_passant_captured, en_passant=True))
    
    # Knight moves
    elif piece.piece_type == PieceType.KNIGHT:
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_offsets:
            new_pos = pos.offset(dr, dc)
            if new_pos:
                target = state.get_piece(new_pos)
                if target is None or target.color == opponent_color:
                    moves.append(Move(pos, new_pos, piece, captured=target))
    
    # King moves
    elif piece.piece_type == PieceType.KING:
        king_offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dr, dc in king_offsets:
            new_pos = pos.offset(dr, dc)
            if new_pos:
                target = state.get_piece(new_pos)
                if target is None or target.color == opponent_color:
                    moves.append(Move(pos, new_pos, piece, captured=target))
        
        # Castling
        if color == Color.WHITE and row == 0 and col == 4:
            if state.white_kingside and state.board[0][5] is None and state.board[0][6] is None:
                if not is_square_attacked(state, Position.from_algebraic("e1"), Color.BLACK) and \
                   not is_square_attacked(state, Position.from_algebraic("f1"), Color.BLACK) and \
                   not is_square_attacked(state, Position.from_algebraic("g1"), Color.BLACK):
                    moves.append(Move(pos, Position.from_algebraic("g1"), piece, castling="kingside"))
            if state.white_queenside and state.board[0][3] is None and state.board[0][2] is None and state.board[0][1] is None:
                if not is_square_attacked(state, Position.from_algebraic("e1"), Color.BLACK) and \
                   not is_square_attacked(state, Position.from_algebraic("d1"), Color.BLACK) and \
                   not is_square_attacked(state, Position.from_algebraic("c1"), Color.BLACK):
                    moves.append(Move(pos, Position.from_algebraic("c1"), piece, castling="queenside"))
        
        if color == Color.BLACK and row == 7 and col == 4:
            if state.black_kingside and state.board[7][5] is None and state.board[7][6] is None:
                if not is_square_attacked(state, Position.from_algebraic("e8"), Color.WHITE) and \
                   not is_square_attacked(state, Position.from_algebraic("f8"), Color.WHITE) and \
                   not is_square_attacked(state, Position.from_algebraic("g8"), Color.WHITE):
                    moves.append(Move(pos, Position.from_algebraic("g8"), piece, castling="kingside"))
            if state.black_queenside and state.board[7][3] is None and state.board[7][2] is None and state.board[7][1] is None:
                if not is_square_attacked(state, Position.from_algebraic("e8"), Color.WHITE) and \
                   not is_square_attacked(state, Position.from_algebraic("d8"), Color.WHITE) and \
                   not is_square_attacked(state, Position.from_algebraic("c8"), Color.WHITE):
                    moves.append(Move(pos, Position.from_algebraic("c8"), piece, castling="queenside"))
    
    # Sliding pieces (bishop, rook, queen)
    else:
        directions = []
        if piece.piece_type in (PieceType.BISHOP, PieceType.QUEEN):
            # Diagonal directions
            directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
        if piece.piece_type in (PieceType.ROOK, PieceType.QUEEN):
            # Orthogonal directions
            directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])
        
        for dr, dc in directions:
            current = pos
            while True:
                new_pos = current.offset(dr, dc)
                if new_pos is None:
                    break
                target = state.get_piece(new_pos)
                if target is None:
                    moves.append(Move(pos, new_pos, piece))
                elif target.color == opponent_color:
                    moves.append(Move(pos, new_pos, piece, captured=target))
                    break
                else:
                    break
                current = new_pos
    
    return moves


def is_square_attacked(state: GameState, pos: Position, by_color: Color) -> bool:
    """
    Check if a square is attacked by any piece of the given color.
    
    Args:
        state: Current game state
        pos: Position to check
        by_color: Color of pieces that might be attacking
        
    Returns:
        True if the square is attacked
    """
    # Check for pawn attacks
    pawn_direction = -1 if by_color == Color.WHITE else 1
    for file_delta in [-1, 1]:
        attacker_pos = pos.offset(pawn_direction, file_delta)
        if attacker_pos:
            attacker = state.get_piece(attacker_pos)
            if attacker and attacker.color == by_color and attacker.piece_type == PieceType.PAWN:
                return True
    
    # Check for knight attacks
    knight_offsets = [
        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
        (1, -2), (1, 2), (2, -1), (2, 1)
    ]
    for dr, dc in knight_offsets:
        attacker_pos = pos.offset(dr, dc)
        if attacker_pos:
            attacker = state.get_piece(attacker_pos)
            if attacker and attacker.color == by_color and attacker.piece_type == PieceType.KNIGHT:
                return True
    
    # Check for king attacks
    king_offsets = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    for dr, dc in king_offsets:
        attacker_pos = pos.offset(dr, dc)
        if attacker_pos:
            attacker = state.get_piece(attacker_pos)
            if attacker and attacker.color == by_color and attacker.piece_type == PieceType.KING:
                return True
    
    # Check for sliding piece attacks
    diagonal_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    orthogonal_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in diagonal_dirs:
        current = pos
        while True:
            current = current.offset(dr, dc)
            if current is None:
                break
            attacker = state.get_piece(current)
            if attacker:
                if attacker.color == by_color and attacker.piece_type in (PieceType.BISHOP, PieceType.QUEEN):
                    return True
                break
    
    for dr, dc in orthogonal_dirs:
        current = pos
        while True:
            current = current.offset(dr, dc)
            if current is None:
                break
            attacker = state.get_piece(current)
            if attacker:
                if attacker.color == by_color and attacker.piece_type in (PieceType.ROOK, PieceType.QUEEN):
                    return True
                break
    
    return False


def find_king(state: GameState, color: Color) -> Optional[Position]:
    """Find the king of the given color."""
    for row in range(8):
        for col in range(8):
            piece = state.board[row][col]
            if piece and piece.color == color and piece.piece_type == PieceType.KING:
                return Position.from_coords(row, col)
    return None


def is_in_check(state: GameState, color: Color) -> bool:
    """
    Check if the king of the given color is in check.
    
    Args:
        state: Current game state
        color: Color of the king to check
        
    Returns:
        True if the king is in check
    """
    king_pos = find_king(state, color)
    if king_pos is None:
        return False
    opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
    return is_square_attacked(state, king_pos, opponent_color)


def move_leaves_king_in_check(state: GameState, move: Move) -> bool:
    """
    Check if making a move would leave the mover's king in check.
    
    Args:
        state: Current game state
        move: The move to test
        
    Returns:
        True if the move leaves the king in check
    """
    # Make the move on a copy
    new_state = state.copy()
    
    # Execute the move
    piece = new_state.get_piece(move.from_pos)
    new_state.set_piece(move.from_pos, None)
    
    # Handle en passant capture
    if move.en_passant:
        captured_pos = Position(move.to_pos.file, move.from_pos.rank)
        new_state.set_piece(captured_pos, None)
    
    # Handle castling (move the rook)
    if move.castling == "kingside":
        rook_from = Position(move.from_pos.file, move.from_pos.rank)
        rook_to_file = 5 if move.piece.color == Color.WHITE else 5  # f-file
        rook_to = Position(rook_to_file, move.from_pos.rank)
        new_state.set_piece(rook_from, None)
        new_state.set_piece(rook_to, Piece(PieceType.ROOK, move.piece.color))
    elif move.castling == "queenside":
        rook_from = Position(move.from_pos.file, move.from_pos.rank)
        rook_to_file = 3 if move.piece.color == Color.WHITE else 3  # d-file
        rook_to = Position(rook_to_file, move.from_pos.rank)
        new_state.set_piece(rook_from, None)
        new_state.set_piece(rook_to, Piece(PieceType.ROOK, move.piece.color))
    
    new_state.set_piece(move.to_pos, piece)
    
    # Check if own king is in check
    return is_in_check(new_state, move.piece.color)


def is_checkmate(state: GameState, color: Color) -> bool:
    """
    Check if the given color is in checkmate.
    
    Args:
        state: Current game state
        color: Color to check
        
    Returns:
        True if the color is in checkmate
    """
    if not is_in_check(state, color):
        return False
    moves = get_all_moves(state)
    return len(moves) == 0


def is_stalemate(state: GameState, color: Color) -> bool:
    """
    Check if the given color is in stalemate.
    
    Args:
        state: Current game state
        color: Color to check
        
    Returns:
        True if the color is in stalemate
    """
    if is_in_check(state, color):
        return False
    moves = get_all_moves(state)
    return len(moves) == 0


def is_checkmate(state: GameState, color: Color) -> bool:
    """
    Check if the given color is in checkmate.
    
    Args:
        state: Current game state
        color: Color of the player to check
        
    Returns:
        True if the player is in checkmate
    """
    if not is_in_check(state, color):
        return False
    
    # Check if any legal move exists
    moves = get_all_moves(state)
    return len(moves) == 0


def is_stalemate(state: GameState, color: Color) -> bool:
    """
    Check if the given color is in stalemate.
    
    Args:
        state: Current game state
        color: Color of the player to check
        
    Returns:
        True if the player is in stalemate
    """
    if is_in_check(state, color):
        return False
    
    # Check if any legal move exists
    moves = get_all_moves(state)
    return len(moves) == 0
