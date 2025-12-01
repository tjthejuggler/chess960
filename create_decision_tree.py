import json
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import OneHotEncoder

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================

FILE_PATH = '/home/twain/Projects/chess960/chess960_best_moves.json'

# --- THE "MEMORIZATION" DIAL ---

# ALLOWANCE: Score sacrifice you accept (centipawns).
# 0 = Absolute best engine moves only (Result: Massive, complex tree).
# 25 = Good human moves (Result: Medium tree).
# 100 = Broad opening principles (Result: Small, simple tree).
ALLOWANCE = 25

# MIN_SAMPLES: Minimum positions required to create a specific rule.
# Increase this (e.g. 20, 50) to force the tree to be simpler and ignore 
# rare exceptions.
# Decrease this (e.g. 1) to get 100% accuracy but a huge tree.
MIN_SAMPLES = 2

# PRIORITY: Group diverse moves into these standard openings if possible.
# Ensure moves like 'c4', 'b3', 'g3' are here as they are common in 960.
MOVE_PRIORITY = ['e4', 'd4', 'c4', 'Nf3', 'g3', 'b3', 'f4', 'b4', 'c3']

# ==============================================================================
# 2. PROCESSING LOGIC
# ==============================================================================

def load_and_process_data(filepath, allowance):
    try:
        with open(filepath, 'r') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None

    dataset = []

    for _, entry in raw_data.items():
        # Parse White's starting rank (Index 7 in split FEN)
        # FEN: "bbqnnrkr/pppppppp/..." -> White is usually uppercase in standard FEN
        # However, looking at your specific data structure, the FEN string starts 
        # with lowercase black pieces. The white pieces are the uppercase ones 
        # at the end of the board string.
        fen_board = entry['fen'].split(' ')[0]
        rows = fen_board.split('/')
        # In standard 960 FEN, white pieces are the last row (index 7)
        white_rank = rows[7] 
        
        # Features: What piece is on a1, b1, etc.
        features = {}
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i, char in enumerate(white_rank):
            features[f"{files[i]}1"] = char 

        # Target Smoothing
        best_score = int(entry['best_score'])
        valid_moves = []
        
        # Collect all moves within allowance
        for m in entry['top_moves']:
            if int(m['score_cp']) >= (best_score - allowance):
                valid_moves.append(m['move_san'])
        
        # Default to the absolute best move
        chosen_move = entry['best_move_san']
        
        # If a priority move is valid, overwrite the choice
        # (This homogenizes the data to make the tree simpler)
        for p_move in MOVE_PRIORITY:
            if p_move in valid_moves:
                chosen_move = p_move
                break
        
        features['target'] = chosen_move
        dataset.append(features)

    return pd.DataFrame(dataset)

def clean_tree_output(tree_text):
    lines = tree_text.split('\n')
    clean_lines = []
    
    piece_map = {'Q': 'Queen', 'K': 'King', 'R': 'Rook', 'B': 'Bishop', 'N': 'Knight'}

    for line in lines:
        if not line.strip(): continue
        
        # Indentation
        indent = line.count("|   ") * "    "
        if "|---" in line: indent += "├─ "
        
        content = line.split("--- ")[-1]
        
        if "class:" in content:
            move = content.split(":")[1].strip()
            clean_lines.append(f"{indent}PLAY: {move}")
        else:
            # Parse "c1_Q <= 0.50"
            parts = content.split(" ")
            feature = parts[0]
            condition = parts[1] # <= or >
            
            if "_" in feature:
                sq, piece = feature.split("_")
                p_name = piece_map.get(piece, piece)
                
                # In OneHot: <= 0.50 means False (Piece NOT there)
                # > 0.50 means True (Piece IS there)
                if condition == "<=":
                    clean_lines.append(f"{indent}Is {p_name} on {sq}? NO")
                else:
                    clean_lines.append(f"{indent}Is {p_name} on {sq}? YES")
            else:
                clean_lines.append(f"{indent}{content}")

    return "\n".join(clean_lines)

# ==============================================================================
# 3. MAIN
# ==============================================================================

if __name__ == "__main__":
    df = load_and_process_data(FILE_PATH, ALLOWANCE)
    
    if df is not None:
        X = df.drop('target', axis=1)
        y = df['target']

        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        X_encoded = encoder.fit_transform(X)
        feature_names = encoder.get_feature_names_out(X.columns)

        # We remove MAX_DEPTH to let the tree decide based on MIN_SAMPLES
        clf = DecisionTreeClassifier(
            criterion='gini',
            max_depth=None,       # Let it grow as needed
            min_samples_leaf=MIN_SAMPLES, 
            class_weight='balanced'
        )
        clf.fit(X_encoded, y)

        print("\n" + "="*60)
        print(f"CHESS960 MEMORY TREE")
        print(f"Allowance: {ALLOWANCE}cp (Tolerance)")
        print(f"Min Samples: {MIN_SAMPLES} (Grouping Strength)")
        print("="*60 + "\n")
        
        raw_tree = export_text(clf, feature_names=list(feature_names))
        print(clean_tree_output(raw_tree))
        
        accuracy = clf.score(X_encoded, y)*100
        print("\n" + "="*60)
        print(f"Tree Accuracy: {accuracy:.1f}%")
        print(f"Tree Depth: {clf.get_depth()}")
        print("Tip: If accuracy is low, DECREASE 'Min Samples' or INCREASE 'Allowance'.")
        print("="*60)