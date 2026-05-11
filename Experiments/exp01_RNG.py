import random
import json
import time
from datetime import datetime

def run_experiment():
    """
    Run experiment RNG.

    Simulates 40 games consisting of 50 RNG spins. This experiment
    serves as a baseline for randomness.

    Outputs:
        A JSON file named "{results_file}_exp{exp_group_num}_{timestamp}.json"
        containing the full experiment results.

    Side effects:
        Prints progress to stdout.
    """
    # Experiment information
    exp_group_num = 1
    exp_name = "RNG"
    prompt_file = None
    results_file =  "rng"
    games_per_prompt = 40
    spins_in_game = 50 # Also the amount of starting credits
    win_amount = 3

    # Game info
    results = []

    # Track overall timer (whole experiment)
    process_start_time = time.perf_counter()

    # Play games_per_prompt number of games
    for game_num in range(games_per_prompt):
        current_game = {"spin_number": 0, "credit_balance": spins_in_game, "current_consecutive_wins": 0, "current_consecutive_losses": 0, "total_wins": 0, "total_losses": 0}
        
        # Do spins_in_game spins
        while current_game["spin_number"] < spins_in_game:
            win = False
            
            # Start spin
            current_game["spin_number"] += 1
            current_game["credit_balance"] -= 1
            
            # Create spin using an RNG
            start = time.perf_counter_ns()
            reel_one = random.randint(1,10)
            reel_two = random.randint(1,10)
            reel_three = random.randint(1,10)
            end = time.perf_counter_ns()

            time_ns = end - start

            # Update stats
            if reel_one == reel_two == reel_three:
                current_game["credit_balance"] += win_amount
                current_game["current_consecutive_losses"] = 0
                current_game["current_consecutive_wins"] += 1
                current_game["total_wins"] += 1
                win = True
            else:
                current_game["current_consecutive_losses"] += 1
                current_game["current_consecutive_wins"] = 0
                current_game["total_losses"] += 1

            # Append result to results list
            results.append({
                "exp_group_num": exp_group_num,
                "exp_name": exp_name,
                "persona_num": None,
                "game_num": game_num,
                "spin_num": current_game['spin_number'],
                "prompt": None,
                "valid_spin": True,
                "reel_one": reel_one,
                "reel_two": reel_two,
                "reel_three": reel_three,
                "consecutive_losses": current_game["current_consecutive_losses"],
                "consecutive_wins": current_game["current_consecutive_wins"],
                "credits": current_game["credit_balance"],
                "win": win,
                "text_output": None,
                "time_ns": time_ns,
                "attempts": 1,
                "error": None
            })

    # Save the results to a file even if the experiment fails
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    full_file_name = f"Final_Json_Results/{results_file}_exp{exp_group_num}_{timestamp}.json"
    with open(full_file_name, "w") as f:
        json.dump(results, f, indent=2)

    process_time_seconds = time.perf_counter() - process_start_time
    hours = int(process_time_seconds // 3600)
    minutes = int((process_time_seconds % 3600) // 60)
    seconds = int(process_time_seconds % 60)
    print(f"Done! Experiment ran for {hours} hours, {minutes} minutes and {seconds} seconds. Results are saved in {full_file_name}")

if __name__ == "__main__":
    run_experiment()