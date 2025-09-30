# Jogo Econômico Imersivo

Um jogo econômico interativo desenvolvido com PySide6 que simula cenários econômicos imersivos.

## Recursos

- Interface gráfica moderna com PySide6
- Simulações econômicas interativas
- Visualizações com matplotlib
- Análises numéricas com numpy

## Instalação

Este projeto usa Poetry para gerenciamento de dependências.

### Pré-requisitos

- Python 3.8+
- Poetry

### Configuração do ambiente

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd jogo-economico
```

2. Instale as dependências:
```bash
poetry install
```

3. Ative o ambiente virtual:
```bash
poetry shell
```

## Executando o projeto

```bash
poetry run jogo
```

ou

```bash
poetry shell
python src/main.py
```

## Desenvolvimento

### Ferramentas de desenvolvimento

Este projeto inclui várias ferramentas de desenvolvimento:

- **Black**: Formatação de código
- **isort**: Organização de imports
- **flake8**: Linting
- **mypy**: Verificação de tipos
- **pytest**: Testes

### Executando as ferramentas

```bash
# Formatação de código
poetry run black src/

# Organização de imports
poetry run isort src/

# Linting
poetry run flake8 src/

# Verificação de tipos
poetry run mypy src/

# Testes
poetry run pytest
```

## Estrutura do projeto

```
src/
├── main.py              # Ponto de entrada principal
├── emp_pyside6_orignal._py  # Código original (temporário)
├── config/              # Configurações
├── controller/          # Controladores
├── data/               # Dados
├── mecanicas/          # Mecânicas do jogo
├── utils/              # Utilitários
└── ux/                 # Interface do usuário
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.