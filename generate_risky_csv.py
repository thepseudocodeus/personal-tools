import csv
import random
import os
from pathlib import Path

ROWS = 1000 # Default
OUT_FILE = "risky.csv"
CSV_DIR = "sample_data"

safe_text = [
    "invoice", "payment", "summary", "note", "value", "description",
    "update", "record", "customer", "portfolio"
]

# Risky patterns
formula_like = [
    "=SUM(A1:A3)", "+AVG(B2:B10)", "-12345", "@HYPERLINK('url')",
    "=CMD('example')", "+OPEN('file')", "-CALC()", "@SHELL('cmd')"
]

# [] TODO: consider using match
def random_cell(flag1: float = 0.2, flag2: float = 0.4, low: int = 1, high: int = 10000):
    """Return either a normal or a formula-like text value."""
    if random.random() < flag1:
        return random.choice(formula_like)
    elif random.random() < flag2:
        return str(random.randint(low, high))
    else:
        return random.choice(safe_text)

def generate_csv(path, rows=ROWS, cols=5):
    """Make the CSV"""
    header = [f"col{i}" for i in range(cols)]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for _ in range(rows):
            writer.writerow([random_cell() for _ in range(cols)])
    print(f"Generated {rows} rows to {path}")

if __name__ == "__main__":
    dir_path = Path(CSV_DIR)
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / OUT_FILE
    generate_csv(file_path)

