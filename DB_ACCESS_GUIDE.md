# Guia de Acesso ao Banco de Dados (VS Code)

Para visualizar e manipular seu banco de dados PostgreSQL diretamente do VS Code, recomendamos o uso de extensões.

## Opção Recomendada: SQLTools

A extensão **SQLTools** é leve e muito popular.

### 1. Instalação
1.  Abra a aba de Extensões do VS Code (`Ctrl+Shift+X`).
2.  Pesquise por **"SQLTools"** (autor: *Matheus Teixeira*).
3.  Instale também o driver **"SQLTools PostgreSQL/Cockroach Driver"**.

### 2. Configurando a Conexão
1.  Na barra lateral esquerda, clique no ícone do SQLTools (ícone de banco de dados).
2.  Clique em **"Add New Connection"**.
3.  Selecione **PostgreSQL**.
4.  Preencha com os dados do ambiente de desenvolvimento (baseados no `docker-compose.yml`):

| Campo | Valor |
| :--- | :--- |
| **Connection Name** | `GoDrive Local` |
| **Server/Host** | `localhost` |
| **Port** | `5432` |
| **Database** | `godrive_db` |
| **Username** | `godrive` |
| **Password** | `godrive_dev_password` |

5.  Clique em **"Save Connection"**.

### 3. Usando
1.  Na aba do SQLTools, clique na conexão `GoDrive Local` para conectar.
2.  Você verá a lista de tabelas.
3.  Clique em uma tabela para ver os dados ou clique com o botão direito para opções avançadas.

---

## Opção Alternativa: Database Client

Outra excelente opção é a extensão **Database Client** (autor: *cweijan*), que oferece uma interface visual mais moderna.

### Instalação e Uso
1.  Instale a extensão **"Database Client"**.
2.  Clique no ícone de banco de dados na barra lateral.
3.  Clique no **"+"** para criar conexão.
4.  Use as mesmas credenciais listadas acima.
