# LLM Randomness Experiments

This project includes 12 controlled experiments with varying contexts, game modes, and personas. The results can be used to test an LLM's ability to generate random, independent numbers in the format of a (one-armed bandit) spin consisting of three integers (reel values). The project further includes relevant scripts for processing experiment outputs and adding the results to the included DuckDB database for further analysis.

### Contexts

The experiments cover three different contexts:
* No context: the LLM is not given a role, only the task to generate lines consisting of 3 random, independent integers.
* Basic one-armed bandit context: the LLM is given the role of a one-armed bandit.
* The one-armed bandit context with explicit credits: the LLM is given additional information stating that the game stops once the player runs out of credits or after a maximum of 50 spins.

### Game modes

* RNG (RNG): uses Python's random.randint() to generate a baseline experiment.
* Isolated spins (I): each spin is generated in a stateless LLM response.
* Full games (F): each full game with (intended) 50 spins are generated at once in a stateless LLM response.

### Personas

There are 6 personas (P[0-5]), which are added to the prompt in 4 of the 12 experiments. The personas are found and can be edited in Experiments/personas.txt. They must follow the format "X Persona description...", where X denotes a persona number (single or multi-digit number).

### Other elements

Both credits (C) and personas (P) are considered elemenents. There are two more elements:
* Stats (S): denotes summarized stats in terms of wins, credits, spin number, etc. for isolated spins, and implicit stats for full games.
* Unbiased (U): adds an additional unbiasing line to the experiment prompt.

### Experiment combinations

The game modes, roles, personas and elements are combined in 12 different experiments, where the name explains the experiment using letters:
* Game mode: RNG, I (isolates spins), or F (full games)
* Role: N (no role) or R (role)
* Elements: S (stats), C (credits), P (persona) and/or U (unbiased)

To give a few examples:
* I_N is an isolated-spins experiment without any provided role or other parameters (no context).
* I_R_SP is an isolated-spins experiment with the one-armed bandit role, summarized stats and personas (one-armed bandit context).
* F_R_SC is a full-game experiment with the one armed bandit role with explicit credits and implicit stats (one-armed bandit context with explicit credits).

## Pipeline

1. Generate LLM outputs by running all experiments
2. Convert raw full games into spins
3. Load data into DuckDB for analysis

## Project Structure

convert_full_to_spins.py
json_to_db.py

Experiments/
* personas.txt
* llm_util.py
* process_isolated_spin.py
* All experiment scripts from 01-12

Final_Json_Results/
* Currently empty, but will hold all json result files, including rng_\*.json, isolated_\*.json, raw_full_\*.json, and full_\*.json. 

Thesis_Database/
* thesis.duckdb
* db_schema.sql

## Installation

Install dependencies using:

pip install -r requirements.txt

## LLM Setup (Ollama)

This project relies on a locally hosted LLM provided by Ollama. This means that Ollama must be installed and running locally.

The experiments are currently configured to use gpt-oss:20b. The LLM setup is found in Experiments/llm_util.py. In this file, the API endpoint can be updated and the LLM model can be changed as desired. This is the way the LLM is accessed during the experiments.

Once Ollama has been set up, you can check that the required model is available with the following command: ollama run gpt-oss:20b

## Usage

### Run all experiments

* python Experiments/exp01_RNG.py
* python Experiments/exp02_I_N.py
* python Experiments/exp03_I_R.py
* python Experiments/exp04_I_R_S.py
* python Experiments/exp05_I_R_SC.py
* python Experiments/exp06_I_R_SP.py
* python Experiments/exp07_I_R_SPU.py   
* python Experiments/exp08_F_N_S.py
* python Experiments/exp09_F_R_S.py
* python Experiments/exp10_F_R_SC.py
* python Experiments/exp11_F_R_SP.py
* python Experiments/exp12_F_R_SPU.py 

### Convert full-game outputs to spins

* F_R_SC experiment: python convert_full_to_spins.py path/raw_example.json --starting_credits 10
* Other full-game experiments: python Final_Scripts/convert_full_to_spins.py path/raw_example.json

### Load data into DuckDB

python json_to_db.py

## Output

- Processed JSON files with spins.
- DuckDB database containing a Spins table. See DB/db_schema.sql for further information.
- Structured dataset for statistical analysis.

## Requirements

- duckdb
- pandas
- requests

## Evaluating LLM randomness

The LLM temperature, i.e., the parameter controlling output variability, has been left at the default temperature (1 for gpt-oss:20b) to test the default level of randomness.

Each experiment is currently configured to create 2000 spins for RNG and isolated-spin experiments and 40 games with an intended length of 50 spins for full-game experiments. These sample sizes were chosen to provide sufficient data for evaluating randomness across statistical metrics. Furthermore, they support reproducibility across experiments despite the stochastic nature of LLM outputs.

## Notes

- Experiments are computationally expensive and may take several hours or even days depending on the CPU and GPU power.

## Citation

This repository is publicly available for research and educational use. If you use this code, data, or findings in your research, please cite the following:

Nelander, S., Bergqvist, A., & Nørgaard, S. (2026). *Prompting luck: Bias and manipulability in LLM-generated "randomness"* (Master's thesis). IT University of Copenhagen. https://github.com/S-Nelander/Thesis2026