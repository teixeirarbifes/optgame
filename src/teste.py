from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Estudo de Caso: Qualidade no Pão de Queijo da Dona Maria", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 11)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, body)
        self.ln()

    def add_table(self, data, col_widths, headings):
        self.set_font("Arial", "B", 11)
        for i, heading in enumerate(headings):
            self.cell(col_widths[i], 10, heading, border=1, align='C')
        self.ln()
        self.set_font("Arial", "", 11)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, str(item), border=1, align='C')
            self.ln()
        self.ln()

pdf = PDF()
pdf.add_page()

context = (
    "Dona Maria é uma microempreendedora que vende pães de queijo artesanais em sua cidade. "
    "Ela prepara e assa os pães de queijo todos os dias e quer garantir que eles tenham um tamanho padrão "
    "para que os clientes fiquem satisfeitos e o custo de produção fique equilibrado.\n\n"
    "Ela decidiu medir o peso de 5 pães de queijo por dia, durante 5 dias consecutivos, "
    "para verificar se a produção está dentro do padrão.\n\n"
    "O peso ideal de cada pão de queijo é 50 gramas, com uma tolerância de ±5 gramas (ou seja, entre 45g e 55g)."
)
pdf.chapter_title("📘 Contexto")
pdf.chapter_body(context)

table_data = [
    ["Segunda", "49, 51, 50, 52, 48"],
    ["Terça", "47, 46, 50, 49, 48"],
    ["Quarta", "52, 54, 53, 55, 51"],
    ["Quinta", "44, 46, 45, 47, 43"],
    ["Sexta", "50, 49, 51, 50, 52"]
]
pdf.chapter_title("📊 Dados coletados por Dona Maria:")
pdf.add_table(table_data, [40, 130], ["Dia", "Peso dos Pães de Queijo (em gramas)"])

activities = (
    "1. Média diária:\n"
    "   - Calcule a média do peso dos pães de queijo de cada dia.\n\n"
    "2. Verificação de controle:\n"
    "   - Verifique se a média de cada dia está dentro dos limites de controle (entre 45g e 55g).\n"
    "   - Qual dia está fora do padrão?\n\n"
    "3. Construção de uma Carta de Controle Simples (Gráfico de Linha):\n"
    "   - Em sala ou em casa, construa um gráfico com:\n"
    "     • Eixo X: Dias da semana\n"
    "     • Eixo Y: Média do peso dos pães\n"
    "     • Trace linhas horizontais para o Limite Inferior (45g), o Limite Superior (55g) e a Média Ideal (50g)\n"
    "     • Plote a média de cada dia no gráfico\n\n"
    "4. Análise e Conclusão:\n"
    "   - O processo de produção da Dona Maria está sob controle?\n"
    "   - O que pode ter acontecido no(s) dia(s) em que os valores se aproximaram ou ultrapassaram os limites?\n"
    "   - Que medidas ela poderia tomar para melhorar a padronização?"
)
pdf.chapter_title("🎯 Atividades Propostas:")
pdf.chapter_body(activities)

concepts = (
    "- Carta de controle simples (média)\n"
    "- Controle de qualidade\n"
    "- Limites de controle\n"
    "- Importância da padronização na produção\n"
    "- Tomada de decisão com base em dados"
)
pdf.chapter_title("✅ Conceitos Trabalhados:")
pdf.chapter_body(concepts)

pdf.output("Estudo_de_Caso_Controle_de_Qualidade.pdf")
