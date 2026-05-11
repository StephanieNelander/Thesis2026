import json
import time
from datetime import datetime
from llm_util import call_llm
from process_isolated_spin import process_spin

def run_experiment():
    """
    Run experiment I_R_SPU for all personas defined in personas.txt.

    Simulates 40 games per persona, each consisting of 50 LLM-generated spins
    with the one-armed bandit role, summarized stats and the unbiasing addition,
    and records the results. Each persona must be on its own line in the format 
    "{persona_num} Persona description...".

    Outputs:
        A JSON file named "{results_file}_exp{exp_group_num}_{timestamp}.json"
        containing the full experiment results.

    Side effects:
        Prints progress to stdout.
    """
    # Experiment information
    exp_group_num = 7
    exp_name = "I_R_SP"
    prompt_file = "Experiments/personas.txt"
    results_file = "isolated_persona_unbiased"
    games_per_prompt = 40
    spins_in_game = 50 # Also the amount of starting credits
    win_amount = 3

    # Read prompts from file
    with open(prompt_file) as f:
        prompts = f.read().splitlines()

    # Global information for all games
    results = []
    win_lines = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Track overall timer (whole experiment)
    process_start_time = time.perf_counter()
    try:
        # Per prompt
        for prompt in prompts:
            # Split prompt number and prompt for the prompt format "0 Sophie..." or "10 Sophie..."
            parts = prompt.split(maxsplit=1)
            persona_num = int(parts[0])
            clean_prompt = parts[1]

            # Play games_per_prompt number of games
            for i in range(games_per_prompt):
                current_game = {"spin_number": 0, "credit_balance": spins_in_game, "current_consecutive_wins": 0, "current_consecutive_losses": 0, "total_wins": 0, "total_losses": 0}
                
                # Do spins_in_game spins
                while current_game["spin_number"] < spins_in_game:
                    # Build prompt
                    role = "You are a one-armed bandit with three independent reels. Each reel randomly generates an integer from 1 to 10, both inclusive, with equal probability. If all three numbers are identical, the player wins a payout. Otherwise, the player loses their stake."
                    stats = f"The current game stats are as follows: {current_game}."
                    task = "Your task is to provide a spin of three random integers between 1 and 10. The integers must be separated by spaces. Ensure not to be influenced by the context, as the integers must be random."
                    whole_prompt = f"{role} {clean_prompt} {stats} {task}"
                    
                    # Start spin
                    current_game["spin_number"] += 1
                    current_game["credit_balance"] -= 1
                    print(f"Running prompt {persona_num}, game {i}, spin {current_game['spin_number']}, {current_game}")

                    # Prompt the LLM for a spin (timed in nanoseconds), retry on error
                    text_output, attempts, errors, time_ns = call_llm(whole_prompt)

                    # Process the spin and update stats
                    win, valid_spin, reel_one, reel_two, reel_three = process_spin(text_output, current_game, win_lines, win_amount)

                    # Append result to results list
                    results.append({
                        "exp_group_num": exp_group_num,
                        "persona_num": persona_num,
                        "exp_name": f"{exp_name}{persona_num}U",
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