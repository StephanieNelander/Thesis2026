import json
import time
from datetime import datetime
from llm_util import call_llm
from process_isolated_spin import process_spin

def run_experiment():
    """
    Run experiment I_R_SC.

    Simulates 40 games consisting of 50 LLM-generated spins with the one-armed
    bandit role, summarized stats, and explicit credits (starting at 10 credits),
    and records the results.

    Outputs:
        A JSON file named "{results_file}_exp{exp_group_num}_{timestamp}.json"
        containing the full experiment results.

    Side effects:
        Prints progress to stdout.
    """
    # Experiment information
    exp_group_num = 5
    exp_name = "I_R_SC"
    prompt_file = None
    results_file = "isolated_credits"
    games_per_prompt = 40
    max_spins_in_game = 50
    starting_credits = 10
    win_amount = 3

    # Global information for all games
    results = []
    win_lines = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Track overall timer (whole experiment)
    process_start_time = time.perf_counter()
    try:
        # Play games_per_prompt number of games
        for i in range(games_per_prompt):
            current_game = {"spin_number": 0, "credit_balance": starting_credits, "current_consecutive_wins": 0, "current_consecutive_losses": 0, "total_wins": 0, "total_losses": 0}
            
            # Spin until there are no more credits or 50 spins
            while current_game["credit_balance"] > 0 and current_game["spin_number"] < max_spins_in_game:
                # Build prompt
                role = "You are a one-armed bandit with three independent reels. Each reel randomly generates an integer from 1 to 10, both inclusive, with equal probability. If all three numbers are identical, the player wins a payout of three credits. Otherwise, the player loses their stake. The player starts with 10 credits and bets 1 credit per spin. The player stops playing if they have no more credits or if they have played 50 rounds."
                stats = f"The current game stats are as follows: {current_game}."
                task = "Your task is to provide a spin of three random integers between 1 and 10. The integers must be separated by spaces."
                whole_prompt = f"{role} {stats} {task}"
                
                # Start spin
                current_game["spin_number"] += 1
                current_game["credit_balance"] -= 1
                print(f"Running game {i}, spin {current_game['spin_number']}, {current_game}")

                # Prompt the LLM for a spin (timed in nanoseconds), retry on error
                text_output, attempts, errors, time_ns = call_llm(whole_prompt)

                # Process the spin and update stats
                win, valid_spin, reel_one, reel_two, reel_three = process_spin(text_output, current_game, win_lines, win_amount)

                # Append result to results list
                results.append({
                    "exp_group_num": exp_group_num,
                    "exp_name": exp_name,
                    "persona_num": None,
                    "game_num": i,
                    "spin_num": current_game['spin_number'],
                    "prompt": whole_prompt,
                    "valid_spin": valid_spin,
                    "reel_one": reel_one,
                    "reel_two": reel_two,
                    "reel_three": reel_three,
                    "consecutive_losses": current_game["current_consecutive_losses"],
                    "consecutive_wins": current_game["current_consecutive_wins"],
                    "credits": current_game["credit_balance"],
                    "win": win,
                    "text_output": text_output,
                    "time_ns": time_ns,
                    "attempts": attempts,
                    "error": " | ".join(errors) if errors else None
                })

    except Exception as e:
        print(f"\nERROR OCCURRED: {e}")
        print("Saving partial results before exiting...")

    # Save the results to a file even if the experiment fails
    finally:
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