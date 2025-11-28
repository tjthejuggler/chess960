#!/usr/bin/env python3
"""
Test script to analyze just the first 5 Chess960 positions.
"""

import chess
import chess.engine
import json

STOCKFISH_PATH = "/usr/games/stockfish"

def main():
    print("Testing Stockfish analysis on first 5 Chess960 positions...")
    print("-" * 60)
    
    # Initialize Stockfish engine
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    
    try:
        for position_number in range(5):
            # Create board with Chess960 starting position
            board = chess.Board.from_chess960_pos(position_number)
            
            print(f"\nPosition {position_number}:")
            print(f"FEN: {board.fen()}")
            print(board)
            
            # Analyze the position
            info = engine.analyse(board, chess.engine.Limit(time=1.0, depth=20))
            
            if "pv" in info and info["pv"]:
                best_move = info["pv"][0]
                score = info.get("score", None)
                
                print(f"Best move: {board.san(best_move)} ({best_move.uci()})")
                print(f"Score: {score}")
            
            print("-" * 60)
    
    finally:
        engine.quit()
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()