import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import re
import numpy as np
from sklearn.tree import DecisionTreeClassifier

# ==========================================
# 1. CONFIGURAÇÃO E IA (MACHINE LEARNING)
# ==========================================
st.set_page_config(page_title="CuidaMe - Conectando Cuidados", page_icon="logo.png", layout="wide")

DATABASE_URL = "postgresql+psycopg2://postgres:senha@localhost:5432/cuidame"

if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = 'home'

def navegar_para(pagina):
    st.session_state.pagina_atual = pagina

def processar_pnl_descricao(texto):
    if not texto: return []
    texto = texto.lower()
    palavras_chave = []
    mapeamento = {
        'acamado': 'Acamado', 'alzheimer': 'Mental', 'demência': 'Mental',
        'cadeirante': 'Dificuldade de locomoção', 'locomoção': 'Dificuldade de locomoção',
        'cirurgia': 'Pós Cirúrgico', 'companhia': 'Companhia'
    }
    for termo, categoria in mapeamento.items():
        if re.search(r'\b' + termo + r'\b', texto):
            palavras_chave.append(categoria)
    return list(set(palavras_chave))

# --- NOVO: TREINAMENTO DO MODELO DE ÁRVORE DE DECISÃO ---
@st.cache_resource
def treinar_arvore_matchmaking():
    """ Treina a Árvore de Decisão com dados sintéticos simulando o 'Match Ideal' """
    # Features (Colunas): [Gênero Bateu? (0/1), % de Modalidades Atendidas (0 a 1), Tem Cursos? (0/1)]
    X = np.array([
        [1, 1.0, 1], # Cenário 1: Perfeito (Bateu gênero, todas modalidades e tem curso) -> Classe 2 (Match Ideal)
        [1, 1.0, 0], # Cenário 2: Ótimo (Bateu gênero e modalidades, sem curso extra) -> Classe 2
        [1, 0.5, 1], # Cenário 3: Bom (Bateu gênero, metade das modalidades, tem curso) -> Classe 1 (Match Parcial)
        [1, 0.5, 0], # Cenário 4: Regular (Bateu gênero, metade das modalidades) -> Classe 1
        [0, 1.0, 1], # Cenário 5: Gênero diferente, mas atende todas as modalidades e tem curso -> Classe 1
        [0, 0.5, 0], # Cenário 6: Ruim (Gênero diferente, atende pouco) -> Classe 0 (Sem Match)
        [0, 0.0, 0], # Cenário 7: Péssimo (Não atende nada) -> Classe 0
        [1, 0.0, 0]  # Cenário 8: Só bateu o gênero, mas não atende a modalidade -> Classe 0
    ])
    # Classes Alvo: 2 (Match Ideal), 1 (Match Parcial), 0 (Sem Match)
    y = np.array([2, 2, 1, 1, 1, 0, 0, 0])
    
    # Criando e treinando a IA
    modelo_arvore = DecisionTreeClassifier(max_depth=4, random_state=42)
    modelo_arvore.fit(X, y)
    return modelo_arvore

ia_matchmaking = treinar_arvore_matchmaking()

# (MANTENHA AQUI AS SEÇÕES 2 E 3 DA SUA NAVBAR E CSS EXATAMENTE COMO ESTÃO)

# ... [Omitido aqui no chat as marcações de CSS e Header para focar na Busca] ...

# ==========================================
# 2. ESTILIZAÇÃO CSS AVANÇADA (NAVBAR)
# ==========================================
st.markdown("""
    <style>
    /* Ocultar elementos nativos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1.5rem !important;
        max-width: 100% !important;
    }
    
    .stApp { background-color: #f8fafc; }

    /* Alinhar verticalmente todos os itens nas colunas (Navbar) */
    [data-testid="stHorizontalBlock"] {
        align-items: center;
    }

    /* Estilo dos Botões de Navegação (Links normais) */
    button[kind="secondary"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #64748b !important; /* Cor cinza escuro */
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    button[kind="secondary"]:hover {
        color: #63328E !important; /* Roxo CuidaMe ao passar o rato */
        background-color: transparent !important;
    }

    /* Estilo do Botão de Destaque (Acesso Restrito) e Botões de Envio */
    button[kind="primary"] {
        background-color: #00BFA5 !important; /* Verde Turquesa */
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 8px 24px !important;
    }
    button[kind="primary"]:hover { 
        background-color: #008f7a !important; 
        color: white !important;
    }
    
    .conteudo-principal { padding: 0px 10%; margin-top: 10px; }

    /* Estilização dos inputs e cards */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stForm"], div.stCard {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(99, 50, 142, 0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. RENDERIZAÇÃO DA NAVBAR
# ==========================================
# Usamos proporções para garantir que a logo e os botões fiquem bem espaçados
col_logo, col_espaco, col_link1, col_link2, col_link3, col_btn = st.columns([2, 1, 2, 2, 2, 2])

with col_logo:
    st.image("logo.png", width=130)

with col_link1:
    if st.button("🔎 Buscar Cuidadores", use_container_width=True): navegar_para('home')
with col_link2:
    if st.button("📝 Seja Cuidador", use_container_width=True): navegar_para('cadastro')
with col_link3:
    if st.button("ℹ️ Sobre Nós", use_container_width=True): navegar_para('sobre')
with col_btn:
    # A magia acontece aqui: type="primary" aplica o estilo do botão Verde/Destacado
    if st.button("⚙️ Acesso Restrito", type="primary", use_container_width=True): navegar_para('admin')

# Linha divisória suave abaixo do menu
st.markdown("<hr style='margin-top: 5px; margin-bottom: 30px; border-color: #e2e8f0;'>", unsafe_allow_html=True)

# ==========================================
# 4. PÁGINA: HOME (BUSCA COM MACHINE LEARNING)
# ==========================================
st.markdown('<div class="conteudo-principal">', unsafe_allow_html=True)

if st.session_state.pagina_atual == 'home':
    st.markdown("<h1 style='text-align: center; color: #333; font-size: 2.5rem;'>Encontre cuidadores por horas ou plantões</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-bottom: 40px;'>Início &nbsp;→&nbsp; Busca de Profissionais</p>", unsafe_allow_html=True)
    
    col_vazia_esq, col_conteudo, col_vazia_dir = st.columns([1, 4, 1])
    with col_conteudo:
        st.markdown("#### Filtros da Busca")
        
        modalidades = st.multiselect(
            "Modalidade (selecione uma ou mais):", 
            ["Acamado", "Dificuldade de locomoção", "Pós Cirúrgico", "Mental", "Companhia"],
            placeholder="Deixe em branco para buscar qualquer modalidade"
        )
        
        genero_pref = st.radio("Preferência de gênero do cuidador:", ["Indiferente", "Feminino", "Masculino"], horizontal=True)
        descricao_necessidade = st.text_area("Descreva a situação com suas palavras (Ex: 'Preciso de alguém para cuidar de idoso acamado com Alzheimer'):")
        
        btn_buscar = st.button("Buscar Cuidador com IA ✨", type="primary", use_container_width=True)
        
        if btn_buscar:
            tags_pnl = processar_pnl_descricao(descricao_necessidade)
            necessidades_busca = list(set(modalidades + tags_pnl))
            
            st.markdown("---")
            st.markdown("<h3 style='color: #63328E;'>Resultados do Matchmaking IA 🧠</h3>", unsafe_allow_html=True)
            if tags_pnl:
                st.success(f"**PNL (Análise de Texto) Identificou as necessidades:** {', '.join(tags_pnl)}")
            
            try:
                engine = create_engine(DATABASE_URL)
                with engine.connect() as conn:
                    # Puxamos TODOS os aprovados com seus respectivos cursos e modalidades!
                    query = text("""
                        SELECT c.id, c.nome, c.telefone_contato, c.genero, c.bio_experiencia, c.valor_hora, c.valor_turno_12h,
                               COALESCE((SELECT STRING_AGG(curso_nome, ', ') FROM cuidador_cursos WHERE cuidador_id = c.id), '') as cursos,
                               COALESCE((SELECT STRING_AGG(tipo, ', ') FROM cuidador_tipo_paciente WHERE cuidador_id = c.id), '') as modalidades
                        FROM cuidadores c
                        WHERE c.status_aprovacao = 'APROVADO';
                    """)
                    todos_cuidadores = conn.execute(query).fetchall()
                    
                    if not todos_cuidadores:
                        st.info("Nenhum cuidador APROVADO disponível no momento.")
                    else:
                        cuidadores_pontuados = []
                        
                        for row in todos_cuidadores:
                            c_id, nome, tel, genero, bio, v_hora, v_12h, cursos_str, mod_str = row
                            
                            # FEATURE 1: Match de Gênero
                            gen_match = 1 if (genero_pref == "Indiferente") or (genero_pref == "Feminino" and genero == "F") or (genero_pref == "Masculino" and genero == "M") else 0
                            
                            # FEATURE 2: Taxa de Modalidades Atendidas
                            modalidades_cuidador = [m.strip().lower() for m in mod_str.split(',') if m.strip()]
                            necessidades_lower = [n.lower() for n in necessidades_busca]
                            
                            if len(necessidades_lower) == 0:
                                mod_ratio = 1.0 # Se não pediu filtro, atende 100%
                            else:
                                atendidas = sum(1 for nec in necessidades_lower if nec in modalidades_cuidador)
                                mod_ratio = atendidas / len(necessidades_lower)
                                
                            # FEATURE 3: Tem Cursos Extras?
                            tem_cursos = 1 if len(cursos_str.strip()) > 0 else 0
                            
                            # PREVISÃO DA ÁRVORE DE DECISÃO
                            features_cuidador = np.array([[gen_match, mod_ratio, tem_cursos]])
                            probabilidades = ia_matchmaking.predict_proba(features_cuidador)[0]
                            
                            # Calcula o Score final
                            if len(probabilidades) == 3:
                                score = (probabilidades[2] * 100) + (probabilidades[1] * 50)
                            else:
                                score = probabilidades[-1] * 100 
                                
                            # Adiciona no dicionário (AGORA INCLUINDO AS MODALIDADES!)
                            if score > 0:
                                cuidadores_pontuados.append({
                                    "nome": nome, "tel": tel, "genero": genero, "bio": bio, 
                                    "cursos": cursos_str, "modalidades": mod_str,
                                    "v_hora": v_hora, "v_12h": v_12h, "score": score
                                })
                        
                        # Ordena os cuidadores do maior Score para o menor
                        cuidadores_pontuados = sorted(cuidadores_pontuados, key=lambda x: x["score"], reverse=True)
                        
                        if not cuidadores_pontuados:
                            st.warning("Nenhum profissional atinge o grau mínimo de compatibilidade com os filtros atuais.")
                        else:
                            for c in cuidadores_pontuados:
                                score_formatado = f"{c['score']:.0f}%"
                                cor_score = "#00BFA5" if c['score'] >= 80 else "#F59E0B"
                                
                                st.markdown(f"""
                                    <div class="stCard">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <h3 style="color: #63328E; margin-bottom: 5px; margin-top: 0;">👤 {c['nome']}</h3>
                                            <span style="background-color: {cor_score}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                                                Match: {score_formatado}
                                            </span>
                                        </div>
                                        <p style="color: #64748b; margin-bottom: 10px;">
                                            <b>Gênero:</b> {"Feminino" if c['genero'] == "F" else "Masculino"} | 
                                            <b>Cursos:</b> {c['cursos'] if c['cursos'] else 'Nenhum'} <br>
                                            <span style="color: #63328E; font-weight: 600;">Atende:</span> {c['modalidades'] if c['modalidades'] else 'Geral'}
                                        </p>
                                        <p><b>Sobre:</b> {c['bio'] if c['bio'] else "Profissional qualificado em cuidados."}</p>
                                        <hr style="border-color: #f1f5f9;">
                                        <p style="color: #00BFA5; font-weight: bold; font-size: 16px;">
                                            💵 R$ {c['v_hora']:.2f} / hora &nbsp;&nbsp;|&nbsp;&nbsp; R$ {c['v_12h']:.2f} / Turno 12h
                                        </p>
                                    </div>
                                """, unsafe_allow_html=True)
                                
            except Exception as e:
                st.error(f"Erro no processamento da IA ou Banco de Dados: {e}")

                

# ----------------- PÁGINA: CADASTRO -----------------
elif st.session_state.pagina_atual == 'cadastro':
    st.markdown("<h1 style='text-align: center; color: #333; font-size: 2.5rem;'>Faça parte da nossa rede</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-bottom: 40px;'>Início &nbsp;→&nbsp; Cadastro de Cuidador</p>", unsafe_allow_html=True)
    
    col_vazia1, col_form, col_vazia2 = st.columns([1, 4, 1])
    with col_form:
        with st.form("form_cadastro_cuidador"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h4 style='color: #63328E;'>Dados Pessoais</h4>", unsafe_allow_html=True)
                nome = st.text_input("Nome Completo")
                cpf = st.text_input("CPF (apenas números)")
                dt_nasc = st.date_input("Data de Nascimento")
                endereco = st.text_input("Endereço Completo")
                telefone = st.text_input("Telefone / WhatsApp")
                genero = st.selectbox("Seu Gênero", ["F", "M"], format_func=lambda x: "Feminino" if x == "F" else "Masculino")
                bio = st.text_area("Breve resumo da sua experiência profissional")
                
            with col2:
                st.markdown("<h4 style='color: #63328E;'>Dados Profissionais e Valores</h4>", unsafe_allow_html=True)
                cursos_sel = st.multiselect("Qualificações / Cursos", ["Cuidador", "Técnico Enf", "Enfermeiro", "Fisioterapeuta", "Primeiros Socorros"])
                pacientes_sel = st.multiselect("Tipos de paciente que atende", ["Companhia", "Acamado", "Dificuldade de locomoção", "Pós Cirúrgico", "Mental"])
                atende_gen = st.selectbox("Atende pacientes do sexo:", ["AMBOS", "F", "M"])
                valor_hora = st.number_input("Valor por Hora (R$)", min_value=0.0, step=5.0)
                valor_6h = st.number_input("Valor Turno 6h (R$)", min_value=0.0, step=10.0)
                valor_12h = st.number_input("Valor Turno 12h (R$)", min_value=0.0, step=10.0)
                dados_pix = st.text_input("Chave PIX / Dados para Recebimento")

            st.markdown("---")
            st.markdown("<h4 style='color: #63328E;'>Disponibilidade & Documentação</h4>", unsafe_allow_html=True)
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1: t_manha = st.checkbox("Turno Manhã")
            with col_t2: t_tarde = st.checkbox("Turno Tarde")
            with col_t3: t_noite = st.checkbox("Turno Noite")
            with col_t4: trab_fds = st.checkbox("Trabalha Fins de Semana")
            
            col_doc1, col_doc2 = st.columns(2)
            with col_doc1: curriculo = st.file_uploader("Anexar Currículo (PDF)", type=["pdf"])
            with col_doc2: antecedentes = st.file_uploader("Antecedentes Criminais (PDF)", type=["pdf"])

            st.markdown("---")
            submit_cadastro = st.form_submit_button("Enviar Cadastro para Aprovação", use_container_width=True)
            
            if submit_cadastro:
                if not nome or not cpf or not telefone:
                    st.error("Por favor, preencha os campos obrigatórios (Nome, CPF e Telefone).")
                else:
                    try:
                        engine = create_engine(DATABASE_URL)
                        with engine.begin() as conn:
                            res = conn.execute(text("""
                                INSERT INTO cuidadores (
                                    nome, cpf, data_nascimento, endereco_completo, telefone_contato,
                                    genero, atende_generos, bio_experiencia, valor_hora, valor_turno_6h,
                                    valor_turno_12h, dados_recebimento, status_aprovacao
                                ) VALUES (
                                    :nome, :cpf, :dt_nasc, :endereco, :telefone,
                                    :genero, :atende_gen, :bio, :valor_hora, :valor_6h,
                                    :valor_12h, :dados_pix, 'PENDENTE'
                                ) RETURNING id;
                            """), {
                                "nome": nome, "cpf": cpf, "dt_nasc": dt_nasc, "endereco": endereco,
                                "telefone": telefone, "genero": genero, "atende_gen": atende_gen,
                                "bio": bio, "valor_hora": valor_hora, "valor_6h": valor_6h,
                                "valor_12h": valor_12h, "dados_pix": dados_pix
                            })
                            cuidador_id = res.fetchone()[0]
                            
                            conn.execute(text("""
                                INSERT INTO disponibilidade (cuidador_id, trabalha_fds, turno_manha, turno_tarde, turno_noite)
                                VALUES (:id, :fds, :manha, :tarde, :noite);
                            """), {"id": cuidador_id, "fds": trab_fds, "manha": t_manha, "tarde": t_tarde, "noite": t_noite})
                            
                            for curso in cursos_sel:
                                conn.execute(text("INSERT INTO cuidador_cursos (cuidador_id, curso_nome) VALUES (:id, :curso);"), {"id": cuidador_id, "curso": curso})
                            for tipo in pacientes_sel:
                                conn.execute(text("INSERT INTO cuidador_tipo_paciente (cuidador_id, tipo) VALUES (:id, :tipo);"), {"id": cuidador_id, "tipo": tipo})
                                
                        st.success(f"Cadastro de {nome} enviado com sucesso! Status: PENDENTE de aprovação.")
                    except Exception as e:
                        st.error(f"Erro ao salvar no banco de dados: {e}")

                        

# ----------------- PÁGINA: ADMIN -----------------
elif st.session_state.pagina_atual == 'admin':
    st.markdown("<h1 style='text-align: center; color: #333; font-size: 2.5rem;'>Painel Administrativo</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-bottom: 40px;'>Acesso Restrito</p>", unsafe_allow_html=True)
    
    try:
        engine = create_engine(DATABASE_URL)
        st.markdown("<h3 style='color: #63328E;'>⏳ Cadastros Pendentes</h3>", unsafe_allow_html=True)
        
        with engine.connect() as conn:
            # Consulta SQL avançada usando Subqueries e STRING_AGG para agrupar os itens
            pendentes = conn.execute(text("""
                SELECT c.id, c.nome, c.cpf, c.telefone_contato, c.genero, c.bio_experiencia, c.valor_hora, c.valor_turno_12h,
                       (SELECT STRING_AGG(curso_nome, ', ') FROM cuidador_cursos WHERE cuidador_id = c.id) as cursos,
                       (SELECT STRING_AGG(tipo, ', ') FROM cuidador_tipo_paciente WHERE cuidador_id = c.id) as pacientes
                FROM cuidadores c 
                WHERE c.status_aprovacao = 'PENDENTE' 
                ORDER BY c.id DESC;
            """)).fetchall()
            
            if not pendentes:
                st.info("Nenhum cadastro pendente no momento!")
            else:
                for p in pendentes:
                    # Desempacota as novas variáveis da consulta
                    p_id, p_nome, p_cpf, p_tel, p_gen, p_bio, p_vh, p_v12, p_cursos, p_pacientes = p
                    
                    with st.expander(f"📌 {p_nome} — CPF: {p_cpf}", expanded=True):
                        st.write(f"**Telefone:** {p_tel} | **Gênero:** {'Feminino' if p_gen == 'F' else 'Masculino'}")
                        st.write(f"**Valores:** R$ {p_vh:.2f}/h | R$ {p_v12:.2f}/12h")
                        
                        # Exibe os dados agrupados
                        st.write(f"**Qualificações / Cursos:** {p_cursos if p_cursos else 'Nenhum informado'}")
                        st.write(f"**Tipos de Paciente (Modalidade):** {p_pacientes if p_pacientes else 'Nenhuma informada'}")
                        
                        st.write(f"**Bio:** {p_bio if p_bio else 'Não informada'}")
                        
                        col_ap, col_rej = st.columns(2)
                        with col_ap:
                            if st.button("Aprovar Cadastro ✅", key=f"ap_{p_id}"):
                                conn.execute(text("UPDATE cuidadores SET status_aprovacao = 'APROVADO' WHERE id = :id"), {"id": p_id})
                                conn.commit()
                                st.rerun()
                        with col_rej:
                            if st.button("Rejeitar Cadastro ❌", key=f"rej_{p_id}"):
                                conn.execute(text("UPDATE cuidadores SET status_aprovacao = 'REJEITADO' WHERE id = :id"), {"id": p_id})
                                conn.commit()
                                st.rerun()

        st.markdown("---")
        st.markdown("<h3 style='color: #63328E;'>📋 Todos os Cuidadores</h3>", unsafe_allow_html=True)
        
        with engine.connect() as conn:
            # Trazemos as especialidades para a tabela geral também
            todos = conn.execute(text("""
                SELECT c.id, c.nome, c.cpf, c.telefone_contato, c.genero, c.valor_hora, 
                       (SELECT STRING_AGG(curso_nome, ', ') FROM cuidador_cursos WHERE cuidador_id = c.id) as cursos,
                       (SELECT STRING_AGG(tipo, ', ') FROM cuidador_tipo_paciente WHERE cuidador_id = c.id) as pacientes,
                       c.status_aprovacao 
                FROM cuidadores c 
                ORDER BY c.id DESC;
            """)).fetchall()
            
            if todos:
                # Adiciona as novas colunas no DataFrame
                df_todos = pd.DataFrame(todos, columns=["ID", "Nome", "CPF", "Telefone", "Gênero", "Valor/Hora", "Cursos", "Modalidades", "Status"])
                st.dataframe(df_todos, use_container_width=True)
            else:
                st.info("Nenhum cuidador encontrado no banco de dados.")
                
    except Exception as e:
        st.error(f"Erro ao carregar painel administrativo: {e}")



# ----------------- PÁGINA: SOBRE -----------------
elif st.session_state.pagina_atual == 'sobre':
    st.markdown("<h1 style='text-align: center; color: #333; font-size: 2.5rem;'>Sobre a CuidaMe</h1>", unsafe_allow_html=True)
    st.write("Somos uma plataforma focada em conectar famílias aos melhores profissionais.")

st.markdown('</div>', unsafe_allow_html=True)