import re

def process_spin(text_output, stats, win_lines, win_amount):
    """
    Process an isolated-spin LLM response.

    Extracts and evaluates a spin consisting of three integers within range
    if such exists in the given LLM response.

    Args:
        text_output (str): The LLM response from an isolated-spin experiment.
        stats (dict): Expected keys include "credit_balance", "current_consecutive_wins", "current_consecutive_losses", "total_wins" and "total_losses".
        win_lines (list[int]): Numbers for which 3 identical reels results in a win.
        win_amount (int): Payout of credits upon a win.

    Returns:
        tuple:
            win (bool): Three identical and valid reel numbers are found.
            valid_spin (bool): The spin has exactly three numbers between 1 and 10, separated by spaces.
            reel_one (int | None): First extracted number.
            reel_two (int | None): Second extracted number.
            reel_three (int | None): Third extracted number.
    """
    # Find matches
    match = re.search(r"(\d+)\s+(\d+)\s+(\d+)", text_output)
    invalid_match = re.search(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", text_output)

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

        # Check that the spin is valid (exactly 3 numbers within range)
        valid_nums = reel_one in win_lines and reel_two in win_lines and reel_three in win_lines
        if valid_nums and not invalid_match:
            valid_spin = True

        # Update relevant stats for a win or loss
        if reel_one == reel_two == reel_three and valid_nums:
            stats["credit_balance"] += win_amount
            stats["current_consecutive_losses"] = 0
            stats["current_consecutive_wins"] += 1
            stats["total_wins"] += 1
            win = True
        else:
            stats["current_consecutive_losses"] += 1
            stats["current_consecutive_wins"] = 0
            stats["total_losses"] += 1
    else:
        # Treat non-matches (e.g. text only) as a loss
        stats["current_consecutive_losses"] += 1
        stats["current_consecutive_wins"] = 0
        stats["total_losses"] += 1
    
    return (win, valid_spin, reel_one, reel_two, reel_three)