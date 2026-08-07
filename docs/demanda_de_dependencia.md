🧠 Prompt para Antigravity — Implementação de Sumarização com Dependência entre Atributos

Você é um sistema de agentes especialistas em:
	•	Mineração de Trajetórias Multiaspecto
	•	Engenharia de Software científica
	•	Modelagem de Similaridade
	•	Arquitetura baseada em Template Method
	•	Refatoração orientada a extensibilidade

Seu objetivo é propor e estruturar a implementação de um novo método de sumarização que considere dependência entre atributos, integrando-o à arquitetura atual do projeto MAT-data.

⸻

🎯 Problema

Atualmente, o sistema realiza sumarização por atributo individual:
	•	Atributos numéricos → mediana
	•	Atributos categóricos → frequência proporcional

Entretanto, alguns atributos possuem dependência semântica explícita, por exemplo:
	•	price depende do POI
	•	weather pode depender da location
	•	rating depende do establishment_type

A sumarização isolada desses atributos pode gerar perda de coerência semântica.

⸻

🎯 Nova Proposta

Implementar uma sumarização baseada em features compostas, onde:
	•	Um conjunto de atributos dependentes é tratado como uma unidade semântica
	•	A agregação é realizada com base em similaridade entre features
	•	A lógica de similaridade pode usar como referência a abordagem do artigo MUITAS

Ou seja:

Em vez de sumarizar atributos individualmente, sumarizar features compostas derivadas da associação entre atributos dependentes.

⸻

📌 Tarefa 1 – Gerar Arquivo de Análise

Primeiro, você deve gerar um documento técnico:

Solucao_sumarizacao_dependencia.md

Este arquivo deve conter:

⸻

1️⃣ Análise Formal do Problema
	•	Definir formalmente o que é dependência entre atributos no contexto de MAT
	•	Classificar tipos de dependência:
	•	Funcional
	•	Estatística
	•	Hierárquica
	•	Contextual
	•	Identificar impactos na sumarização atual

⸻

2️⃣ Estratégias Possíveis de Solução

Apresentar e comparar no mínimo 4 abordagens:

A) Feature Engineering Manual
	•	Agrupar atributos dependentes em uma estrutura Feature
	•	Exemplo:

Feature_POI = (POI, price, rating)


	•	Impacto na estrutura AttributeValue

B) Similaridade Baseada em MUITAS
	•	Adaptar a função de similaridade do MUITAS
	•	Construir vetores de feature
	•	Calcular score composto
	•	Realizar clusterização semântica antes da fusão

C) Modelagem como Grafo de Dependência
	•	Criar grafo atributo → atributo
	•	Realizar sumarização por componentes conexos
	•	Impacto estrutural na arquitetura

D) Embedding Semântico
	•	Mapear features para vetores numéricos
	•	Usar distância vetorial na fusão
	•	Complexidade computacional

Para cada alternativa, avaliar:
	•	Complexidade computacional
	•	Impacto na classe MATSummarize
	•	Impacto na fusão _fuse_aspects()
	•	Compatibilidade com MATSG e MATSGT
	•	Impacto na exportação CSV
	•	Risco de regressão
	•	Impacto na interpretabilidade

⸻

3️⃣ Impactos Arquiteturais no Projeto

Avaliar impacto nos seguintes componentes:
	•	MATSummarize
	•	_summarize_numerical_aspects
	•	_summarize_categorical_aspects
	•	Centroid
	•	AttributeValue
	•	Modelo de saída CSV
	•	Runner
	•	Compatibilidade com ferramenta visual

Responder:
	•	Será necessário criar nova classe Feature?
	•	Feature deve substituir AttributeValue?
	•	Feature deve ser agregada ao Centroid?
	•	Template Method deve ser estendido?

⸻

4️⃣ Proposta Arquitetural Recomendada

Indicar:
	•	Melhor abordagem
	•	Justificativa técnica
	•	Como integrar ao Template Method sem quebrar compatibilidade
	•	Se deve ser:
	•	Novo método (ex: MATSGF)
	•	Extensão do MATSummarize
	•	Nova flag de execução

⸻

5️⃣ Avaliação de Complexidade

Comparar:
	•	Complexidade atual O(n²)
	•	Complexidade com associação de features
	•	Impacto na etapa de grid
	•	Impacto na etapa STI

⸻

6️⃣ Plano de Implementação

Definir:

Fase 1 – Modelagem de Feature
Fase 2 – Refatoração da fusão semântica
Fase 3 – Integração com MATSG
Fase 4 – Integração com MATSGT
Fase 5 – Ajustes de exportação
Fase 6 – Testes unitários

⸻

🎯 Tarefa 2 – Proposta Técnica para Implementação

Após o documento de análise, você deverá propor:
	•	Estrutura de classes
	•	Alterações no Template Method
	•	Pseudocódigo
	•	Estratégia de retrocompatibilidade
	•	Exemplo concreto usando:

POI + price



⸻

⚠️ Restrições
	•	Não quebrar a compatibilidade com MATSG e MATSGT
	•	Manter o contrato de saída CSV
	•	Preservar o padrão Template Method
	•	Manter coerência com o design descrito em:
	•	README
	•	approaches.md
	•	architecture.md
	•	Avaliar explicitamente a relação com o algoritmo MUITAS

⸻

🎯 Saída Esperada
	1.	Documento técnico completo: Solucao_sumarizacao_dependencia
	2.	Análise crítica comparativa das alternativas
	3.	Proposta arquitetural recomendada
	4.	Impactos técnicos e científicos
	5.	Plano estruturado de implementação

⸻

Se necessário, você pode:
	•	Propor nova camada de abstração
	•	Sugerir interface FeatureAggregator
	•	Propor separação entre:
	•	Fusão estrutural
	•	Fusão semântica
	•	Avaliar se composição é superior à herança