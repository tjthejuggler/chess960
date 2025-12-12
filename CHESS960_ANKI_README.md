# Chess960 Anki Deck Creator

This script creates an Anki deck with 960 flashcards, one for each Chess960 starting position. Each card displays the starting position with the best first move and shows the top 3 moves with their evaluation scores.

## Prerequisites

1. **Anki** must be running
2. **AnkiConnect add-on** must be installed
   - Install from: https://ankiweb.net/shared/info/2055492159
3. **AnkiChess add-on** must be installed for the "Chess 2.0" card type
   - This provides the chess board visualization in Anki

## Card Format

### Front (PGN field)
Shows the Chess960 starting position with the best first move:
```
[FEN "rkrnnqbb/pppppppp/8/8/8/8/PPPPPPPP/RKRNNQBB w KQkq - 0 1"]
1. g4
```

### Back (textField)
Shows the top 3 moves with their centipawn scores:
```
1. g4 (+15)
2. f4 (+5)
3. Nd3 (+3)
```

## Usage

1. Make sure Anki is running
2. Run the script:
   ```bash
   python3 create_chess960_anki_deck.py
   ```

The script will:
- Check AnkiConnect connection
- Verify the "Chess 2.0" model exists
- Create the "chess960moves" deck
- Generate all 960 cards

## Output

- **Deck name**: `chess960moves`
- **Number of cards**: 960 (one for each Chess960 starting position)
- **Tags**: Each card is tagged with:
  - `chess960`
  - `opening`
  - `position-{number}` (e.g., `position-959`)

## Data Source

The script reads from `chess960_best_moves.json`, which contains:
- All 960 Chess960 starting positions
- FEN notation for each position
- Top 3 moves with engine evaluation scores
- Best move in both UCI and SAN notation

## Troubleshooting

### "Cannot proceed without AnkiConnect"
- Ensure Anki is running
- Install AnkiConnect add-on if not already installed
- Check that AnkiConnect allows localhost connections

### "Cannot proceed without Chess 2.0 model"
- Install the AnkiChess add-on
- Restart Anki after installation
- Verify the "Chess 2.0" card type appears in Anki's card types

### "Failed to create cards"
- Check that the `chess960_best_moves.json` file exists
- Ensure you have write permissions for the Anki collection
- Try creating a single test card manually to verify the setup

## Created: 2025-12-12