#!/usr/bin/env python3
"""
Analyze all 960 Chess960 starting positions using Stockfish.
Saves results incrementally to allow resuming if interrupted.
"""

import chess
import chess.engine
import json
import os
from pathlib import Path

# Configuration
STOCKFISH_PATH = "/usr/games/stockfish"
OUTPUT_FILE = "chess960_best_moves.json"
ANALYSIS_TIME = 1.0  # seconds per position
ANALYSIS_DEPTH = 20  # depth for analysis

def load_existing_results():
    """Load existing results from JSON file if it exists."""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_results(results):
    """Save results to JSON file."""
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

def analyze_position(board, engine, position_number):
    """Analyze a single Chess960 position and return the best move."""
    try:
        # Analyze the position
        info = engine.analyse(board, chess.engine.Limit(time=ANALYSIS_TIME, depth=ANALYSIS_DEPTH))
        
        best_move = info["pv"][0] if "pv" in info and info["pv"] else None
        score = info.get("score", None)
        
        if best_move:
            return {
                "position_number": position_number,
                "fen": board.fen(),
                "best_move": best_move.uci(),
                "best_move_san": board.san(best_move),
                "score": str(score) if score else None
            }
    except Exception as e:
        print(f"Error analyzing position {position_number}: {e}")
        return None

def main():
    """Main function to analyze all 960 Chess960 positions."""
    print(f"Starting Chess960 analysis using Stockfish at {STOCKFISH_PATH}")
    print(f"Results will be saved to {OUTPUT_FILE}")
    print(f"Analysis settings: {ANALYSIS_TIME}s time, depth {ANALYSIS_DEPTH}")
    print("-" * 60)
    
    # Load existing results
    results = load_existing_results()
    analyzed_count = len(results)
    
    if analyzed_count > 0:
        print(f"Resuming from position {analyzed_count + 1} (already analyzed {analyzed_count} positions)")
    
    # Initialize Stockfish engine
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    except Exception as e:
        print(f"Error initializing Stockfish: {e}")
        print(f"Please ensure Stockfish is installed at {STOCKFISH_PATH}")
        return
    
    try:
        # Iterate through all 960 Chess960 positions
        for position_number in range(960):
            # Skip if already analyzed
            position_key = str(position_number)
            if position_key in results:
                continue
            
            # Create board with Chess960 starting position
            board = chess.Board.from_chess960_pos(position_number)
            
            # Analyze the position
            result = analyze_position(board, engine, position_number)
            
            if result:
                results[position_key] = result
                
                # Save after each position (allows resuming)
                save_results(results)
                
                print(f"Position {position_number:3d}/960: {result['best_move_san']:6s} ({result['best_move']}) - Score: {result['score']}")
            else:
                print(f"Position {position_number:3d}/960: Failed to analyze")
        
        print("-" * 60)
        print(f"Analysis complete! Analyzed {len(results)} positions.")
        print(f"Results saved to {OUTPUT_FILE}")
        
    finally:
        # Clean up engine
        engine.quit()

if __name__ == "__main__":
    main()