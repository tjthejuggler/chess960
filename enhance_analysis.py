#!/usr/bin/env python3
"""
Enhance the chess960 analysis with piece information and pieces behind pawns.
"""

import json
import chess

def get_piece_name(piece):
    """Get the full name of a piece."""
    if piece is None:
        return None
    
    piece_names = {
        chess.PAWN: 'Pawn',
        chess.KNIGHT: 'Knight',
        chess.BISHOP: 'Bishop',
        chess.ROOK: 'Rook',
        chess.QUEEN: 'Queen',
        chess.KING: 'King'
    }
    return piece_names.get(piece.piece_type, 'Unknown')

def get_pieces_behind_pawn(board, move):
    """Get the pieces behind a pawn move (diagonal left, directly behind, diagonal right)."""
    from_square = move.from_square
    file = chess.square_file(from_square)
    rank = chess.square_rank(from_square)
    
    pieces_behind = {}
    
    # For white pawns, look at rank below (rank - 1)
    if rank > 0:
        behind_rank = rank - 1
        
        # Diagonal left (file - 1)
        if file > 0:
            square = chess.square(file - 1, behind_rank)
            piece = board.piece_at(square)
            if piece:
                pieces_behind['diagonal_left'] = {
                    'piece': get_piece_name(piece),
                    'square': chess.square_name(square)
                }
        
        # Directly behind
        square = chess.square(file, behind_rank)
        piece = board.piece_at(square)
        if piece:
            pieces_behind['directly_behind'] = {
                'piece': get_piece_name(piece),
                'square': chess.square_name(square)
            }
        
        # Diagonal right (file + 1)
        if file < 7:
            square = chess.square(file + 1, behind_rank)
            piece = board.piece_at(square)
            if piece:
                pieces_behind['diagonal_right'] = {
                    'piece': get_piece_name(piece),
                    'square': chess.square_name(square)
                }
    
    return pieces_behind if pieces_behind else None

def get_piece_order(fen):
    """Get the order of pieces on the back rank from the FEN."""
    # Extract just the first rank (back rank for black, which mirrors white's setup)
    back_rank = fen.split()[0].split('/')[0]
    
    # Convert to piece names
    piece_map = {
        'r': 'Rook',
        'n': 'Knight',
        'b': 'Bishop',
        'q': 'Queen',
        'k': 'King'
    }
    
    pieces = []
    for char in back_rank.lower():
        if char in piece_map:
            pieces.append(piece_map[char])
    
    return pieces

def enhance_analysis():
    """Enhance the existing analysis with additional information."""
    # Load existing results
    with open('chess960_best_moves.json', 'r') as f:
        results = json.load(f)
    
    print(f"Enhancing {len(results)} positions...")
    
    enhanced_results = {}
    
    for pos_num, data in results.items():
        fen = data['fen']
        board = chess.Board(fen)
        
        # Parse the best move
        best_move_uci = data['best_move']
        move = chess.Move.from_uci(best_move_uci)
        
        # Get the piece that moved
        piece = board.piece_at(move.from_square)
        piece_name = get_piece_name(piece)
        
        # Get piece order from FEN
        piece_order = get_piece_order(fen)
        
        # Create enhanced entry
        enhanced_entry = {
            'position_number': data['position_number'],
            'fen': fen,
            'piece_order': piece_order,
            'best_move': best_move_uci,
            'best_move_san': data['best_move_san'],
            'piece_moved': piece_name,
            'from_square': chess.square_name(move.from_square),
            'to_square': chess.square_name(move.to_square),
            'score': data['score']
        }
        
        # If it's a pawn move, add pieces behind
        if piece and piece.piece_type == chess.PAWN:
            pieces_behind = get_pieces_behind_pawn(board, move)
            if pieces_behind:
                enhanced_entry['pieces_behind_pawn'] = pieces_behind
        
        enhanced_results[pos_num] = enhanced_entry
        
        if int(pos_num) % 100 == 0:
            print(f"Processed {pos_num} positions...")
    
    # Save enhanced results
    with open('chess960_best_moves_enhanced.json', 'w') as f:
        json.dump(enhanced_results, f, indent=2)
    
    print(f"\nEnhanced analysis saved to chess960_best_moves_enhanced.json")
    
    # Print some examples
    print("\nExample entries:")
    for i in [0, 518, 959]:
        pos = str(i)
        if pos in enhanced_results:
            entry = enhanced_results[pos]
            print(f"\nPosition {i}:")
            print(f"  Piece order: {', '.join(entry['piece_order'])}")
            print(f"  Best move: {entry['best_move_san']} ({entry['piece_moved']} from {entry['from_square']} to {entry['to_square']})")
            if 'pieces_behind_pawn' in entry:
                print(f"  Pieces behind pawn:")
                for direction, info in entry['pieces_behind_pawn'].items():
                    print(f"    {direction}: {info['piece']} on {info['square']}")

if __name__ == '__main__':
    enhance_analysis()