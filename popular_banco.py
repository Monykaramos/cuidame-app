from sqlalchemy import create_engine, text

# Ajuste sua senha aqui
DATABASE_URL = "postgresql+psycopg2://postgres:senha@localhost:5432/cuidame"

cuidadores_falsos = [
    {
        "nome": "Marta Silva", "cpf": "11111111111", "gen": "F", 
        "bio": "Aposentada, muito paciente. Adoro conversar, ler livros para os idosos e fazer companhia. Tenho experiência cuidando da minha própria mãe com Alzheimer.",
        "vh": 25.0, "v12": 150.0, "cursos": ["Cuidador", "Primeiros Socorros"], 
        "pacientes": ["Companhia", "Mental"]
    },
    {
        "nome": "Roberto Carlos", "cpf": "22222222222", "gen": "M", 
        "bio": "Enfermeiro padrão com 10 anos de UTI. Especialista em pacientes de alta complexidade, sondas, curativos complexos e pós-operatório.",
        "vh": 80.0, "v12": 600.0, "cursos": ["Enfermeiro", "Primeiros Socorros"], 
        "pacientes": ["Acamado", "Pós Cirúrgico"]
    },
    {
        "nome": "Juliana Mendes", "cpf": "33333333333", "gen": "F", 
        "bio": "Técnica de enfermagem forte e disposta. Tenho facilidade em transferir pacientes da cama para a cadeira de rodas e dar banho no leito.",
        "vh": 40.0, "v12": 300.0, "cursos": ["Técnico Enf", "Cuidador"], 
        "pacientes": ["Acamado", "Dificuldade de locomoção"]
    },
    {
        "nome": "Fernando Souza", "cpf": "44444444444", "gen": "M", 
        "bio": "Estudante de fisioterapia no último semestre. Auxilio na reabilitação motora e caminhadas diárias para evitar perda de massa muscular.",
        "vh": 50.0, "v12": 400.0, "cursos": ["Fisioterapeuta", "Primeiros Socorros"], 
        "pacientes": ["Dificuldade de locomoção", "Pós Cirúrgico"]
    }
]

def semear_banco():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        for c in cuidadores_falsos:
            # 1. Insere o Cuidador já APROVADO
            res = conn.execute(text("""
                INSERT INTO cuidadores (
                    nome, cpf, data_nascimento, endereco_completo, telefone_contato, genero, atende_generos, 
                    bio_experiencia, valor_hora, valor_turno_6h, valor_turno_12h, dados_recebimento, status_aprovacao
                ) VALUES (
                    :nome, :cpf, '1980-01-01', 'Rua Fictícia, 123', '11999999999', :gen, 'AMBOS',
                    :bio, :vh, :vh * 6, :v12, 'pix@teste.com', 'APROVADO'
                ) RETURNING id;
            """), c)
            c_id = res.fetchone()[0]
            
            # 2. Insere a Disponibilidade
            conn.execute(text("""
                INSERT INTO disponibilidade (cuidador_id, trabalha_fds, turno_manha, turno_tarde, turno_noite)
                VALUES (:id, TRUE, TRUE, TRUE, FALSE);
            """), {"id": c_id})
            
            # 3. Insere os Cursos
            for curso in c["cursos"]:
                conn.execute(text("INSERT INTO cuidador_cursos (cuidador_id, curso_nome) VALUES (:id, :curso);"), {"id": c_id, "curso": curso})
                
            # 4. Insere as Modalidades
            for tipo in c["pacientes"]:
                conn.execute(text("INSERT INTO cuidador_tipo_paciente (cuidador_id, tipo) VALUES (:id, :tipo);"), {"id": c_id, "tipo": tipo})
                
    print("✅ Banco populado com sucesso! Seus dados falsos realistas estão prontos para a Inteligência Artificial.")

if __name__ == "__main__":
    semear_banco()