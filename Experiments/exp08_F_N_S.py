import json
import time
from datetime import datetime
from llm_util import call_llm

def run_experiment():
    """
    Run experiment F_N_S.

    Simulates 40 LLM-generated full games with an intended length of 50 spins
    without the one-armed bandit role, but with implicit stats, and records the games.
    The full games are intended to be processed with the convert_full_to_spins.py
    script to resemble isolated-spin experiments.

    Outputs:
        A JSON file named "raw_{results_file}_exp{exp_group_num}_{timestamp}.json"
        containing the full experiment results.

    Side effects:
        Prints progress to stdout.
    """
    # Experiment information
    exp_group_num = 8
    exp_name = "F_N_S"
    prompt_file = None
    results_file = "full_roleless"
    games_per_prompt = 40

    # Global information for all games
    results = []

    # Track overall timer (whole experiment)
    process_start_time = time.perf_counter()
    try:
        # Play games_per_prompt number of games
        for i in range(games_per_prompt):
            # Build prompt
            role = None
            task = "Your task is to provide 50 separate lines with three random and independent integers between 1 and 10, both inclusive, with equal probability. The integers must be separated by spaces."
            whole_prompt = f"{task}"

            print(f"Running game {i}")

            # Prompt the LLM for a spin (timed in nanoseconds), retry on error
            text_output, attempts, errors, time_ns = call_llm(whole_prompt)

            # Append result to results list
            results.append({
                "exp_group_num": exp_group_num,
                "exp_name": exp_name,
                "persona_num": None,
                "game_num": i,
                "prompt": whole_prompt,
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
        full_file_name = f"Final_Json_Results/raw_{results_file}_exp{exp_group_num}_{timestamp}.json"
        with open(full_file_name, "w") as f:
            json.dump(results, f, indent=2)

        process_time_seconds = time.perf_counter() - process_start_time
        hours = int(process_time_seconds // 3600)
        minutes = int((process_time_seconds % 3600) // 60)
        seconds = int(process_time_seconds % 60)
        print(f"Done! Experiment ran for {hours} hours, {minutes} minutes and {seconds} seconds. Results are saved in {full_file_name}")

if __name__ == "__main__":
    run_experiment()