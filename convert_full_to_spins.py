import argparse
import json
import re
from pathlib import Path

# Global information for all games
win_lines = set(range(1, 11))
win_amount = 3

# Process one game
def process_entry(entry, starting_credits):
    """
    Convert a single full-game LLM output into spins.

    Parses the text output of a full game line-by-line, extracts valid spins,
    updates game state (credits, wins, losses), and handles malformed or
    non-numeric outputs.

    Args:
        entry (dict): A single game entry containing LLM output and experiment information.
        starting_credits (int): Initial credit balance for the game.

    Returns:
        list[dict]: A list of spin records with reconstructed game state.
    """
    all_spins = entry.get("text_output", "").split("\n")
    results = []

    # Save early if the output is a python script
    if all_spins[0].strip().startswith("```python"):
        results.append({
            "exp_group_num": entry["exp_group_num"],
            "exp_name": entry["exp_name"],
            "persona_num": entry["persona_num"],
            "game_num": entry["game_num"],
            "spin_num": 1,
            "prompt": entry["prompt"],
            "valid_spin": False,
            "reel_one": None,
            "reel_two": None,
            "reel_three": None,
            "consecutive_losses": None,
            "consecutive_wins": None,
            "credits": None,
            "win": None,
            "text_output": entry["text_output"],
            "time_ns": entry["time_ns"],
            "attempts": entry["attempts"],
            "error": entry["error"]
        })

        return results

    # Global variables for the game
    current_game = {"spin_number": 0, "credit_balance": starting_credits, "current_consecutive_wins": 0, "current_consecutive_losses": 0, "total_wins": 0, "total_losses": 0}
    reasoning = ""

    for i in range(len(all_spins)):
        # Match number groups of the spin: find at least 3 numbers and find at least 4 numbers
        match = re.search(r"(\d+)\s+(\d+)\s+(\d+)", all_spins[i])
        invalid_match = re.search(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", all_spins[i])
        
        # If the spin is an empty line, disregard it
        if all_spins[i] == "":
            continue

        # If there are not exactly 3 numbers, write the spin text to reasoning
        if not match or invalid_match:
            reasoning += all_spins[i]

            # If this spin isn't the last one
            if i != len(all_spins) - 1:
                j = i + 1

                # Skip all empty spins
                while j < len(all_spins) and all_spins[j].strip() == "":
                    j += 1

                # Match the next non-empty spin, same logic
                if j < len(all_spins):
                    next_match = re.search(r"(\d+)\s+(\d+)\s+(\d+)", all_spins[j])
                    next_invalid_match = re.search(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", all_spins[j])
                else:
                    next_match = None
                    next_invalid_match = None

                # If the next spin is not a match or is invalid, don't save the data yet
                if not next_match or next_invalid_match:
                    reasoning += "\n"
                    continue

        # Start spin
        current_game["spin_number"] += 1
        current_game["credit_balance"] -= 1

        # Prepare stats
        win = False
        valid_spin = False
        reel_one = None
        reel_two = None
        reel_three = None

        # Update stats
        if match:
            reel_one, reel_two, reel_three = match.groups()
            reel_one = int(reel_one)
            reel_two = int(reel_two)
            reel_three = int(reel_three)

            # Check that the spin is valid (exactly 3 numbers within range, even if there is text around it, e.g., "Spin: 1 2 3")
            valid_nums = reel_one in win_lines and reel_two in win_lines and reel_three in win_lines
            if valid_nums and not invalid_match:
                valid_spin = True
                reasoning = ""

            # Update relevant stats for a win or loss
            if reel_one == reel_two == reel_three and valid_nums:
                current_game["credit_balance"] += win_amount
                current_game["current_consecutive_losses"] = 0
                current_game["current_consecutive_wins"] += 1
                current_game["total_wins"] += 1
                win = True
            else:
                current_game["current_consecutive_losses"] += 1
                current_game["current_consecutive_wins"] = 0
                current_game["total_losses"] += 1
        else:
            # Treat non-matches (e.g. text only) as a loss
            current_game["current_consecutive_losses"] += 1
            current_game["current_consecutive_wins"] = 0
            current_game["total_losses"] += 1

        # Append result to results list
        results.append({
            "exp_group_num": entry["exp_group_num"],
            "exp_name": entry["exp_name"],
            "persona_num": entry["persona_num"],
            "game_num": entry["game_num"],
            "spin_num": current_game['spin_number'],
            "prompt": entry["prompt"],
            "valid_spin": valid_spin,
            "reel_one": reel_one,
            "reel_two": reel_two,
            "reel_three": reel_three,
            "consecutive_losses": current_game["current_consecutive_losses"],
            "consecutive_wins": current_game["current_consecutive_wins"],
            "credits": current_game["credit_balance"],
            "win": win,
            "text_output": reasoning if reasoning != "" else all_spins[i],
            "time_ns": entry["time_ns"],
            "attempts": entry["attempts"],
            "error": entry["error"]
        })

    return results

def main():
    """
    Convert JSON file with full game LLM outputs into spins.

    Each full game is parsed line-by-line to extract valid spins,
    update game state (credits, wins, losses), and handle malformed
    or non-numeric outputs. The output file resembles that of an 
    isolated-spin experiment results file.

    Inputs:
        A JSON file containing full-game experiment results, where each
        entry includes a "text_output" field with multiple spins separated
        by new line. Name should start with "raw_".

    Outputs:
        A new JSON file in the same directory, containing one record per
        spin with reconstructed game state and metadata. The name is the 
        same without "raw_".

    Usage:
        python convert_full_to_spins.py raw_example.json
        python convert_full_to_spins.py raw_example.json --starting_credits 10

    Side effects:
        Prints the output path to stdout.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert full game to single spins")
    parser.add_argument("file", help="Path to the JSON file")
    parser.add_argument(
        "--starting_credits", "-c",
        type=int,
        default=50,  # default value if not specified
        help="Number of starting credits for each game"
    )
    args = parser.parse_args()

    # Get directory and define output directory and name
    file_path = Path(args.file).resolve()
    file_dir = file_path.parent
    new_name = file_path.name.removeprefix("raw_")
    out_file = file_dir / new_name

    # Get the JSON data
    with open(file_path) as f:
        data = json.load(f)

    all_results = []

    # Change all full games to spins and save them
    for entry in data:
        all_results.extend(process_entry(entry, starting_credits=args.starting_credits))

    with open(out_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print("Saved", out_file)

if __name__ == "__main__":
    main()