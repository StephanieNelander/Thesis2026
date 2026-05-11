-- Create a table Spins 
DROP TABLE IF EXISTS Spins;
DROP SEQUENCE IF EXISTS spin_seq;
CREATE SEQUENCE spin_seq START 1;

CREATE TABLE Spins (
	id INT PRIMARY KEY DEFAULT nextval('spin_seq'),
	exp_group_num INT,
	exp_name STRING,
	persona_num INT,
	game_num INT,
	spin_num INT,
	prompt STRING,
	valid_spin BOOL,
	reel_one INT,
	reel_two INT,
	reel_three INT,
	consecutive_losses INT,
	consecutive_wins INT,
	credits INT,
	win BOOL,
	text_output STRING,
	time_ns BIGINT,
	attempts INT,
	error STRING
);