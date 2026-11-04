<?php

	//Initializes PDO database if not already created
	function openDBConnection($dsn,$dbuser,$dbpass) {

		$db = null;
		try{
			// Get db connection and set errormode to exceptions
			$db = new pdo( $dsn,$dbuser,$dbpass,
							array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
			initDatabase($db);		
		}
		catch(PDOException $ex){
			die("Database problem: ". $ex->getMessage());
		}
		return $db;
	}

	//Create DB and add sample data
	function initDatabase($db) {

		try {
			$db->query("SELECT 1 FROM notes LIMIT 1");
		} catch (Exception $e) {
			// table not found

			$query="CREATE TABLE notes (
						id INTEGER PRIMARY KEY AUTO_INCREMENT,
						title VARCHAR(30),
						text VARCHAR(255),
						hidden INTEGER)";
			try {
				$db->exec($query);
				//Create sample data
				$query="INSERT INTO notes (title,text,hidden) VALUES
							('first','Hello world',0),
							('second','Hidden',1)";
				$db->exec($query);
			} catch (PDOException $e) {
				die("Database problem: ". $e->getMessage());	
			}
		}
			
	}
?>
