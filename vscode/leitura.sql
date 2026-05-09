USE leitura;

CREATE TABLE usuarios(
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    senha VARCHAR(255) NOT NULL
    );
    
CREATE TABLE livros(
	id INT AUTO_INCREMENT PRIMARY KEY,
	titulo VARCHAR(100),
    autor VARCHAR(100),
    genero VARCHAR(100)
   );
   