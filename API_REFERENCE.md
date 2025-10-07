# 🔌 API REFERENCE

Documentação completa da API REST do Jogo de Produção.

---

## 🌐 Base URL

```
http://localhost:5000
```

---

## 📍 Endpoints Públicos

### GET /
Página inicial

**Response:** HTML

---

### GET /api/status
Retorna status geral do jogo

**Auth:** Não requerida

**Response:**
```json
{
  "total_empresas": 4,
  "empresas_confirmadas": 2,
  "empresas_pendentes": 2,
  "iteracao_atual": 3,
  "max_iteracoes": 12,
  "iteracao_aberta": true,
  "media_lucro": 15000.50,
  "progresso": 25.0
}
```

---

### GET /api/ranking
Retorna ranking de empresas

**Auth:** Não requerida

**Response:**
```json
[
  {
    "nome": "TechCorp",
    "equipe": "Equipe Alpha",
    "lucro_total": 25000.00,
    "recursos": {
      "dinheiro": 45000,
      "materia_prima": 800,
      "energia": 1200,
      "trabalhadores": 75
    }
  },
  {
    "nome": "InnovaTech",
    "equipe": "Equipe Beta",
    "lucro_total": 22000.00,
    "recursos": { ... }
  }
]
```

---

### GET /api/produtos
Retorna lista de produtos disponíveis

**Auth:** Não requerida

**Response:**
```json
{
  "📱 Smartphone": {
    "custo_materia": 28,
    "custo_energia": 22,
    "custo_trabalhadores": 3.5,
    "custo_dinheiro": 53.5,
    "preco_venda": 285,
    "tempo_producao": 2,
    "cor": "#E74C3C",
    "emoji": "📱"
  },
  "💻 Laptop": { ... },
  "🖥️ Desktop": { ... }
}
```

---

## 🔐 Endpoints Administrativos

**Auth Required:** Session cookie após login em `/admin/login`

### POST /admin/login
Login administrativo

**Body (form-data):**
```
senha=admin1064*
```

**Response:** Redirect to `/admin/dashboard`

---

### POST /admin/processar-turno
Processar turno atual

**Auth:** Admin session required

**Response:**
```json
{
  "sucesso": true,
  "turno_processado": 3,
  "proximo_turno": 4,
  "jogo_finalizado": false,
  "resultados": [
    {
      "empresa": "TechCorp",
      "status": "processado",
      "lucro": 5000.00,
      "detalhes": [
        {
          "produto": "📱 Smartphone",
          "quantidade": 50,
          "receita": 14250,
          "custo": 2675,
          "lucro": 11575
        }
      ]
    }
  ]
}
```

---

### POST /admin/abrir-iteracao
Abrir próxima iteração para envio de decisões

**Auth:** Admin session required

**Response:**
```json
{
  "sucesso": true,
  "iteracao": 4
}
```

---

### POST /admin/resetar-jogo
Resetar o jogo completamente

**Auth:** Admin session required

**Response:**
```json
{
  "sucesso": true
}
```

---

### POST /api/admin/criar-empresa
Criar nova empresa

**Auth:** Admin session required

**Body (JSON):**
```json
{
  "nome": "NovaEmpresa",
  "equipe": "Equipe Gamma",
  "senha": "NOVA2024"
}
```

**Response:**
```json
{
  "sucesso": true,
  "mensagem": "Empresa NovaEmpresa criada com sucesso"
}
```

**Errors:**
```json
{
  "sucesso": false,
  "mensagem": "Nome e senha são obrigatórios"
}
```
```json
{
  "sucesso": false,
  "mensagem": "Empresa já existe"
}
```

---

### DELETE /api/admin/remover-empresa/<nome>
Remover empresa

**Auth:** Admin session required

**Response:**
```json
{
  "sucesso": true
}
```

**Error:**
```json
{
  "sucesso": false,
  "mensagem": "Empresa não encontrada"
}
```

---

## 👥 Endpoints dos Alunos

**Auth Required:** Session cookie após login em `/aluno/login`

### POST /aluno/login
Login da empresa

**Body (form-data):**
```
nome=TechCorp
senha=TECH2024
```

**Response:** Redirect to `/aluno/dashboard`

---

### POST /aluno/enviar-decisao
Enviar decisão de produção

**Auth:** Empresa session required

**Body (form-data):**
```
produto_📱 Smartphone=50
produto_💻 Laptop=20
produto_🖥️ Desktop=10
```

**Response (Success):**
```json
{
  "sucesso": true,
  "mensagem": "Decisão registrada com sucesso!"
}
```

**Response (Error):**
```json
{
  "sucesso": false,
  "mensagem": "Recursos insuficientes ou erro ao registrar"
}
```

---

### POST /api/validar-decisao
Validar decisão sem salvar (tempo real)

**Auth:** Empresa session required

**Body (JSON):**
```json
{
  "📱 Smartphone": 50,
  "💻 Laptop": 20,
  "🖥️ Desktop": 10
}
```

**Response (Válida):**
```json
{
  "valido": true,
  "consumo": {
    "materia_prima": 2340,
    "energia": 2080,
    "trabalhadores": 279,
    "dinheiro": 5220
  },
  "metricas": {
    "receita": 33000,
    "custo": 5220,
    "lucro": 27780,
    "margem": 84.18
  },
  "violacoes": []
}
```

**Response (Inválida):**
```json
{
  "valido": false,
  "consumo": { ... },
  "metricas": { ... },
  "violacoes": [
    {
      "recurso": "materia_prima",
      "necessario": 2340,
      "disponivel": 1200,
      "deficit": 1140
    },
    {
      "recurso": "energia",
      "necessario": 2080,
      "disponivel": 1500,
      "deficit": 580
    }
  ]
}
```

---

### GET /api/empresa/<nome>
Dados de uma empresa específica

**Auth:** Empresa session required (só acessa própria empresa)

**Response:**
```json
{
  "nome": "TechCorp",
  "equipe": "Equipe Alpha",
  "senha": "TECH2024",
  "recursos_disponiveis": {
    "dinheiro": 45000,
    "materia_prima": 800,
    "energia": 1200,
    "trabalhadores": 75
  },
  "decisao_atual": {
    "📱 Smartphone": 30,
    "💻 Laptop": 15
  },
  "decisao_confirmada": true,
  "historico_decisoes": [
    {
      "turno": 1,
      "producao": { ... },
      "lucro": 5000,
      "recursos_apos": { ... }
    }
  ],
  "historico_recursos": {
    "turnos": [1, 2, 3],
    "dinheiro": [38000, 42000, 45000],
    "materia_prima": [1200, 1000, 800],
    "energia": [1500, 1300, 1200],
    "trabalhadores": [90, 85, 75]
  },
  "lucro_total": 15000,
  "criada_em": "2025-10-06T10:30:00"
}
```

---

## 🔧 Exemplos de Uso

### cURL

**Status do jogo:**
```bash
curl http://localhost:5000/api/status
```

**Ranking:**
```bash
curl http://localhost:5000/api/ranking
```

**Criar empresa (admin):**
```bash
curl -X POST http://localhost:5000/api/admin/criar-empresa \
  -H "Content-Type: application/json" \
  -d '{"nome":"NovaEmpresa","equipe":"Team X","senha":"PASS123"}' \
  --cookie "session=admin_session_cookie"
```

**Validar decisão:**
```bash
curl -X POST http://localhost:5000/api/validar-decisao \
  -H "Content-Type: application/json" \
  -d '{"📱 Smartphone":50,"💻 Laptop":20,"🖥️ Desktop":10}' \
  --cookie "session=empresa_session_cookie"
```

---

### JavaScript (AJAX)

**Buscar status:**
```javascript
$.get('/api/status', function(data) {
    console.log('Iteração atual:', data.iteracao_atual);
    console.log('Empresas pendentes:', data.empresas_pendentes);
});
```

**Validar decisão:**
```javascript
const decisoes = {
    "📱 Smartphone": 50,
    "💻 Laptop": 20,
    "🖥️ Desktop": 10
};

$.ajax({
    url: '/api/validar-decisao',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(decisoes),
    success: function(response) {
        if (response.valido) {
            console.log('Decisão válida!');
            console.log('Lucro projetado:', response.metricas.lucro);
        } else {
            console.log('Recursos insuficientes:', response.violacoes);
        }
    }
});
```

**Criar empresa:**
```javascript
$.ajax({
    url: '/api/admin/criar-empresa',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        nome: 'NovaEmpresa',
        equipe: 'Team X',
        senha: 'PASS123'
    }),
    success: function(response) {
        if (response.sucesso) {
            alert(response.mensagem);
        }
    }
});
```

**Processar turno:**
```javascript
$.post('/admin/processar-turno', function(response) {
    if (response.sucesso) {
        console.log('Turno processado:', response.turno_processado);
        console.log('Resultados:', response.resultados);
    }
});
```

---

### Python (requests)

```python
import requests

BASE_URL = 'http://localhost:5000'

# Status do jogo
response = requests.get(f'{BASE_URL}/api/status')
print(response.json())

# Ranking
response = requests.get(f'{BASE_URL}/api/ranking')
ranking = response.json()
for empresa in ranking:
    print(f"{empresa['nome']}: R$ {empresa['lucro_total']}")

# Criar empresa (com sessão admin)
session = requests.Session()
session.post(f'{BASE_URL}/admin/login', data={'senha': 'admin1064*'})

response = session.post(
    f'{BASE_URL}/api/admin/criar-empresa',
    json={
        'nome': 'NovaEmpresa',
        'equipe': 'Team X',
        'senha': 'PASS123'
    }
)
print(response.json())

# Validar decisão (com sessão empresa)
session = requests.Session()
session.post(f'{BASE_URL}/aluno/login', data={
    'nome': 'TechCorp',
    'senha': 'TECH2024'
})

response = session.post(
    f'{BASE_URL}/api/validar-decisao',
    json={
        '📱 Smartphone': 50,
        '💻 Laptop': 20,
        '🖥️ Desktop': 10
    }
)
result = response.json()
print(f"Válido: {result['valido']}")
print(f"Lucro: R$ {result['metricas']['lucro']}")
```

---

## 📊 Status Codes

- **200 OK** - Requisição bem-sucedida
- **302 Found** - Redirect (após login)
- **403 Forbidden** - Sem autorização
- **404 Not Found** - Recurso não encontrado
- **500 Internal Server Error** - Erro no servidor

---

## 🔒 Autenticação

A API usa **session cookies** do Flask para autenticação:

1. **Login**: POST para `/admin/login` ou `/aluno/login`
2. **Session Cookie**: Servidor retorna cookie de sessão
3. **Requests Subsequentes**: Incluir cookie nas requisições
4. **Logout**: GET para `/admin/logout` ou `/aluno/logout`

**Nota**: Endpoints da API pública não requerem autenticação.

---

## 📝 Notas

- Todos os endpoints JSON retornam `Content-Type: application/json`
- Datas/horários em formato ISO 8601
- Valores monetários em float (2 casas decimais)
- Arrays ordenados por relevância

---

**API RESTful completa e bem documentada! 🚀**
