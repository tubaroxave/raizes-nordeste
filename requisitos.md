# Requisitos Funcionais

RF01: O sistema deve permitir o cadastro e a autenticação de usuários, incluindo diferentes perfis de acesso.
RF02: O sistema deve permitir o cadastro e a gestão das unidades da rede.
RF03: O sistema deve permitir o cadastro e a consulta de cardápios por unidade.
RF04: O sistema deve permitir a realização de pedidos, contendo itens, valores, status e canal de origem.
RF05: O sistema deve permitir a atualização do status dos pedidos, incluindo os estados de cozinha, pronto, entregue e cancelado.
RF06: O sistema deve permitir o controle de estoque por unidade, incluindo entradas e saídas de produtos.
RF07: O sistema deve impedir a venda de produtos quando não houver estoque disponível.
RF08: O sistema deve permitir o gerenciamento de um programa de fidelização, com acúmulo e resgate de pontos mediante consentimento do usuário.
RF09: O sistema deve permitir o cadastro e a aplicação de promoções e campanhas.
RF10: O sistema deve permitir a solicitação de pagamento por meio de um serviço externo simulado (mock) e registrar o resultado da operação.
RF11: O sistema deve registrar o canal de origem de cada pedido, permitindo os canais APP, TOTEM, BALCÃO, PICKUP e WEB.
RF12: O sistema deve permitir a consulta e filtragem de pedidos por canal de origem.

# Requisitos Não Funcionais
RNF01: A autenticação dos usuários deve ser realizada de forma segura, utilizando token de autenticação.
RNF02: As senhas dos usuários devem ser armazenadas utilizando hash seguro, sem armazenamento em texto puro.
RNF03: O sistema deve possuir controle de acesso baseado nos perfis/roles dos usuários.
RNF04: O sistema deve proteger os dados pessoais dos usuários de acordo com os princípios aplicáveis da LGPD.
RNF05: O sistema deve registrar logs e/ou auditoria de ações sensíveis, como criação, cancelamento e alteração de status de pedidos.
RNF06: O sistema deve apresentar desempenho adequado durante períodos de maior demanda, mantendo o funcionamento das operações principais.
RNF07: O sistema deve possuir disponibilidade suficiente para permitir a utilização contínua de suas principais funcionalidades.
RNF08: O sistema deve possuir tratamento de falhas na integração com o serviço externo de pagamento, evitando que uma falha externa comprometa o funcionamento da API.
RNF09: A API deve possuir documentação técnica utilizando OpenAPI/Swagger.
RNF10: A API deve utilizar respostas de erro padronizadas e códigos HTTP coerentes.


# MVP
Fluxo A -> Pedido -> Pagamento Mock -> Atualização de Status

# Python com FastAPI:
Escolhi Python com FastAPI por ser uma tecnologia adequada para o desenvolvimento de APIs REST, permitindo implementar os endpoints necessários para o fluxo de pedidos e facilitar a documentação da API com Swagger

# SQLite:
Escolhi SQLite por ser um banco de dados simples, permitindo realizar a persistência real dos usuários, produtos, pedidos e outros dados sem a necessidade de configurar um servidor de banco separadamente.

# Baixa do estoque na criação do pedido:
O estoque será baixado no momento da criação do pedido para poder reservar os produtos solicitados e evitar que a quantidade disponível no momento do pedido seja utilizada por outros pedidos. Caso não exista estoque suficiente, o pedido não será criado.