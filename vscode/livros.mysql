CREATE TABLE livros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    imagem VARCHAR(255),
    estrelas INT DEFAULT 0,
    resenha TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);