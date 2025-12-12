#!/usr/bin/env python3
"""
Create Anki deck for Chess960 starting positions.

This script creates 960 Anki flashcards, one for each Chess960 starting position.
Each card shows the starting position with the best first move on the front (PGN field),
and the top 3 moves with their scores on the back (textField).

Requirements:
- Anki must be running
- AnkiConnect add-on must be installed
- AnkiChess add-on must be installed for the Chess 2.0 card type
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List

# AnkiConnect configuration
ANKI_CONNECT_URL = "http://localhost:8765"
ANKI_CONNECT_VERSION = 6

# Deck configuration
DECK_NAME = "chess960moves"
MODEL_NAME = "Chess 2.0"

def invoke_anki(action: str, **params) -> Dict:
    """
    Invoke an AnkiConnect API action.
    
    Args:
        action: The AnkiConnect action to invoke
        **params: Parameters for the action
        
    Returns:
        The response from AnkiConnect
        
    Raises:
        Exception: If AnkiConnect returns an error or is not available
    """
    request_json = json.dumps({
        'action': action,
        'version': ANKI_CONNECT_VERSION,
        'params': params
    }).encode('utf-8')
    
    try:
        request = urllib.request.Request(ANKI_CONNECT_URL, request_json)
        response = urllib.request.urlopen(request).read()
        response_data = json.loads(response.decode('utf-8'))
        
        if len(response_data) != 2:
            raise Exception('Response has an unexpected number of fields')
        if 'error' not in response_data:
            raise Exception('Response is missing required error field')
        if 'result' not in response_data:
            raise Exception('Response is missing required result field')
        if response_data['error'] is not None:
            raise Exception(response_data['error'])
            
        return response_data['result']
    except urllib.error.URLError as e:
        raise Exception(
            f"Failed to connect to AnkiConnect. "
            f"Make sure Anki is running and AnkiConnect is installed. "
            f"Error: {e}"
        )

def ensure_deck_exists() -> None:
    """
    Ensure the chess960moves deck exists in Anki.
    Creates it if it doesn't exist.
    """
    try:
        decks = invoke_anki('deckNames')
        if DECK_NAME not in decks:
            invoke_anki('createDeck', deck=DECK_NAME)
            print(f"✓ Created deck: {DECK_NAME}")
        else:
            print(f"✓ Deck exists: {DECK_NAME}")
    except Exception as e:
        raise Exception(f"Failed to ensure deck exists: {e}")

def format_pgn(fen: str, best_move_san: str) -> str:
    """
    Format the PGN field with FEN and best move.
    
    Args:
        fen: The FEN string for the starting position
        best_move_san: The best move in SAN notation
        
    Returns:
        Formatted PGN string
    """
    return f'[FEN "{fen}"]\n1. {best_move_san}'

def format_text_field(top_moves: List[Dict]) -> str:
    """
    Format the textField with the top 3 moves and their scores.
    
    Args:
        top_moves: List of top move dictionaries
        
    Returns:
        Formatted text field string
    """
    lines = []
    for i, move in enumerate(top_moves, 1):
        move_san = move['move_san']
        score_cp = move['score_cp']
        # Format score with + for positive values
        score_str = f"+{score_cp}" if score_cp >= 0 else str(score_cp)
        lines.append(f"{i}. {move_san} ({score_str})")
    
    return "\n".join(lines)

def create_chess960_cards(json_file: str) -> None:
    """
    Create all 960 Chess960 cards from the JSON file.
    
    Args:
        json_file: Path to the chess960_best_moves.json file
    """
    print(f"Loading Chess960 data from {json_file}...")
    
    # Load the JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"✓ Loaded {len(data)} positions")
    
    # Ensure deck exists
    ensure_deck_exists()
    
    # Prepare all notes
    notes = []
    for position_key, position_data in data.items():
        position_number = position_data['position_number']
        fen = position_data['fen']
        best_move_san = position_data['best_move_san']
        top_moves = position_data['top_moves']
        
        # Format the fields
        pgn = format_pgn(fen, best_move_san)
        text_field = format_text_field(top_moves)
        
        # Create the note
        note = {
            "deckName": DECK_NAME,
            "modelName": MODEL_NAME,
            "fields": {
                "PGN": pgn,
                "textField": text_field
            },
            "tags": ["chess960", "opening", f"position-{position_number}"],
            "options": {
                "allowDuplicate": False,
                "duplicateScope": "deck"
            }
        }
        notes.append(note)
    
    print(f"\nCreating {len(notes)} cards...")
    
    # Create all notes at once
    try:
        note_ids = invoke_anki('addNotes', notes=notes)
        
        # Count successful creations (non-null IDs)
        successful = sum(1 for note_id in note_ids if note_id is not None)
        failed = len(note_ids) - successful
        
        print(f"\n✓ Successfully created {successful} cards")
        if failed > 0:
            print(f"⚠ {failed} cards were duplicates or failed to create")
        
        return note_ids
    except Exception as e:
        raise Exception(f"Failed to create cards: {e}")

def test_anki_connection() -> bool:
    """
    Test if AnkiConnect is available and working.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        version = invoke_anki('version')
        print(f"✓ AnkiConnect is available (version {version})")
        return True
    except Exception as e:
        print(f"✗ AnkiConnect connection failed: {e}")
        return False

def check_model_exists() -> bool:
    """
    Check if the Chess 2.0 model exists in Anki.
    
    Returns:
        True if model exists, False otherwise
    """
    try:
        models = invoke_anki('modelNames')
        if MODEL_NAME in models:
            print(f"✓ Model '{MODEL_NAME}' found")
            return True
        else:
            print(f"✗ Model '{MODEL_NAME}' not found")
            print(f"Available models: {', '.join(models)}")
            return False
    except Exception as e:
        print(f"✗ Failed to check models: {e}")
        return False

if __name__ == "__main__":
    """
    Main execution: Create the Chess960 Anki deck.
    """
    print("=" * 60)
    print("CHESS960 ANKI DECK CREATOR")
    print("=" * 60)
    
    # Test connection
    print("\n1. Testing AnkiConnect connection...")
    if not test_anki_connection():
        print("\n✗ Cannot proceed without AnkiConnect")
        print("Please ensure:")
        print("  1. Anki is running")
        print("  2. AnkiConnect add-on is installed")
        print("  3. AnkiConnect is configured to allow localhost connections")
        exit(1)
    
    # Check if Chess 2.0 model exists
    print("\n2. Checking for Chess 2.0 model...")
    if not check_model_exists():
        print("\n✗ Cannot proceed without Chess 2.0 model")
        print("Please ensure:")
        print("  1. AnkiChess add-on is installed")
        print("  2. The 'Chess 2.0' card type is available")
        exit(1)
    
    # Create the cards
    print("\n3. Creating Chess960 cards...")
    try:
        create_chess960_cards('chess960_best_moves.json')
        print("\n" + "=" * 60)
        print("✓ Chess960 deck created successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Failed to create deck: {e}")
        exit(1)