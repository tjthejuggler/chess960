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
ANALYSIS_TIME = 5.0  # seconds per position (increased for higher accuracy)
ANALYSIS_DEPTH = 30  # depth for analysis (increased for first move accuracy)
MULTI_PV = 3  # number of best moves to analyze (top 3)

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
    """Analyze a single Chess960 position and return the top 3 best moves with scores."""
    try:
        # Analyze the position with MultiPV to get top 3 moves
        # python-chess automatically sets UCI_Chess960 when board.chess960 is True
        info_list = engine.analyse(
            board,
            chess.engine.Limit(time=ANALYSIS_TIME, depth=ANALYSIS_DEPTH),
            multipv=MULTI_PV
        )
        
        # Extract top moves with their scores
        top_moves = []
        for i, info in enumerate(info_list):
            if "pv" in info and info["pv"]:
                move = info["pv"][0]
                score = info.get("score", None)
                
                # Convert score to centipawns for easier comparison
                score_cp = None
                if score:
                    if score.is_mate():
                        # Mate scores: positive for white advantage, negative for black
                        mate_in = score.white().mate()
                        score_cp = f"M{mate_in}" if mate_in > 0 else f"M{mate_in}"
                    else:
                        # Regular centipawn score
                        score_cp = score.white().score()
                
                top_moves.append({
                    "move": move.uci(),
                    "move_san": board.san(move),
                    "score_cp": score_cp,
                    "score_raw": str(score) if score else None
                })
        
        if top_moves:
            return {
                "position_number": position_number,
                "fen": board.fen(),
                "top_moves": top_moves,
                "best_move": top_moves[0]["move"],
                "best_move_san": top_moves[0]["move_san"],
                "best_score": top_moves[0]["score_cp"]
            }
    except Exception as e:
        print(f"Error analyzing position {position_number}: {e}")
        return None

def main():
    """Main function to analyze all 960 Chess960 positions."""
    print(f"Starting Chess960 analysis using Stockfish at {STOCKFISH_PATH}")
    print(f"Results will be saved to {OUTPUT_FILE}")
    print(f"Analysis settings: {ANALYSIS_TIME}s time, depth {ANALYSIS_DEPTH}, MultiPV {MULTI_PV}")
    print("-" * 60)
    
    # Load existing results
    results = load_existing_results()
    analyzed_count = len(results)
    
    if analyzed_count > 0:
        print(f"Resuming from position {analyzed_count + 1} (already analyzed {analyzed_count} positions)")
    
    # Initialize Stockfish engine
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        # Note: UCI_Chess960 is automatically managed by python-chess when using
        # chess.Board.from_chess960_pos(), so we don't need to set it manually
        print("✓ Stockfish initialized (Chess960 mode will be auto-enabled per position)")
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
                
                # Display best move and score difference to 2nd best
                best_score = result['best_score']
                score_display = f"{best_score:+4d}" if isinstance(best_score, int) else str(best_score)
                
                # Show score difference if we have multiple moves
                if len(result['top_moves']) > 1:
                    second_score = result['top_moves'][1]['score_cp']
                    if isinstance(best_score, int) and isinstance(second_score, int):
                        diff = best_score - second_score
                        print(f"Position {position_number:3d}/960: {result['best_move_san']:6s} ({score_display} cp, +{diff} vs 2nd)")
                    else:
                        print(f"Position {position_number:3d}/960: {result['best_move_san']:6s} ({score_display} cp)")
                else:
                    print(f"Position {position_number:3d}/960: {result['best_move_san']:6s} ({score_display} cp)")
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