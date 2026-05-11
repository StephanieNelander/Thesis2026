"""
Loads experiment JSON results into a DuckDB database.

This module provides functionality to parse multiple experiment
result files (RNG, isolaed spins and processed full games) and 
insert them into a structured Spins table.
"""

import duckdb

# Global column names in both JSON files and the database
COLS = [
    "exp_group_num",
    "exp_name",
    "persona_num",
    "game_num",
    "spin_num",
    "prompt",
    "valid_spin",
    "reel_one",
    "reel_two",
    "reel_three",
    "consecutive_losses",
    "consecutive_wins",
    "credits",
    "win",
    "text_output",
    "time_ns",
    "attempts",
    "error"
]

COL_STR = ", ".join(COLS)

def load_json_into_duckdb(db_path, json_folder):
    """
    Load experiment spin data from JSON files into a DuckDB database.

    This function resets the target Spins table, reinitialises the spin
    sequence, and imports all experiment result files matching predefined
    patterns (e.g., rng, isolated, full experiments) from a directory
    into a structured DuckDB table.

    The function assumes that all input JSON files share a compatible
    schema corresponding to isolated spin experiment outputs.

    Args:
        db_path (str): Path to the DuckDB database file.
        json_folder (str): Directory containing experiment JSON files.

    Returns:
        pandas.DataFrame: The full contents of the Spins table after
        loading, ordered by spin ID.

    Side effects:
        - Drops and recreates the spin sequence
        - Deletes existing rows in the Spins table
        - Inserts data into the DuckDB database
    """
    with duckdb.connect(db_path) as con:
        con.execute("TRUNCATE TABLE Spins")
        con.execute("DROP SEQUENCE IF EXISTS spin_seq")
        con.execute("CREATE SEQUENCE spin_seq START 1")

        # Load results into the db in this order: RNG, isolated spins, full game spins
        patterns = [
            f"{json_folder}/rng_*.json",
            f"{json_folder}/isolated_*.json",
            f"{json_folder}/full_*.json",
        ]

        for pattern in patterns:
            con.execute(f"""
                INSERT INTO Spins ({COL_STR})
                SELECT {COL_STR}
                FROM read_json('{pattern}', union_by_name=true)
            """)

        return con.execute("SELECT * FROM Spins ORDER BY id").fetchdf()

if __name__ == "__main__":
    df = load_json_into_duckdb(
        db_path="DB/thesis.duckdb",
        json_folder="Final_Json_Results"
    )

    print(df)
