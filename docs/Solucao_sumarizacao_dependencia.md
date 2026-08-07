# Documento Técnico: Sumarização com Dependência entre Atributos (MAT-data)

Este documento analisa o problema de perda de coerência semântica na sumarização de trajetórias multiaspecto e propõe uma arquitetura extensível para lidar com dependências entre atributos (ex: `POI` e `price`), integrada ao framework MAT-data.

---

## 1. Análise Formal do Problema

### Definição de Dependência entre Atributos
No contexto de Trajetórias Multiaspecto (MAT), a **dependência entre atributos** ocorre quando o valor semântico de um aspecto $A$ está fortemente associado ou é condicionado pelo valor de um aspecto $B$. Atualmente, a matriz de fusão em `MATSummarize` (`_fuse_aspects()`) desmembra todos os atributos: calcula a **mediana** isolada para dados numéricos e a **frequência proporcional** para categóricos. Esse tratamento isolado ("naive") destrói correlações intrínsecas dos dados. 
Se em um cluster a maioria dos POIs visitados for "Restaurante" (preço alto) e uma minoria for "Parque" (preço zero), a sumarização individual pode resultar em um Centroid bizarro: `POI=Restaurante` com `price=zero` (devido a um viés no cálculo de mediana geral).

### Classificação de Dependências:
1. **Funcional**: Um atributo determina o outro unicamente (ex: `CEP` -> `Cidade`).
2. **Estatística**: Probabilidade condicional elevada (ex: `Tempo=Chuvoso` -> `Velocidade=Baixa`).
3. **Hierárquica**: Relação de granularidade (ex: `País` -> `Estado` -> `Cidade`).
4. **Contextual**: Depende da semântica de domínio de aplicação (ex: `rating` faz sentido atrelado a `establishment_type`, mas não isoladamente).

**Impacto na sumarização atual:**
A agregação em `_summarize_numerical_aspects` e `_summarize_categorical_aspects` agrupa dados em `_semantic_numeric_fusion_val` e `_semantic_categorical_summarization_val` perdendo o vínculo do registro de origem (`Point`). É impossível rastrear que o `price = 50` originou-se do `POI = Restaurante` na hora de eleger o sumário.

---

## 2. Estratégias Possíveis de Solução

### A) Feature Engineering Manual (Composição Rígida)
- **Mecânica:** Concatenar colunas na carga de dados gerando uma tupla `Feature_POI = (POI, price, rating)`.
- **Avaliação:** 
  - *Complexidade:* $O(1)$ na sumarização (tratada como um novo categórico único).
  - *Impactos:* Polui as estatísticas. Duas instâncias `(Restaurante, 50, 4)` e `(Restaurante, 55, 4)` seriam tratadas como entidades categóricas completamente distintas, anulando a flexibilidade da similaridade. Falha estrutural ao tratar contínuos como discretos.

### B) Similaridade Baseada em MUITAS (Clusterização Semântica Interna)
- **Mecânica:** Adaptar a lógica da classe `MUITAS` para operar *internamente* no grid. Grupo de atributos dependentes formam uma `CompoundFeature`. Em vez de mediana cega, calculamos a "medoide" da feature composta baseada numa distância de similaridade intra-célula.
- **Avaliação:**
  - *Complexidade:* $O(K^2)$ onde $K$ é o número de pontos na célula.
  - *Impactos:* Requer alterar `process_cell_points()` ou o fluxo de `_fuse_aspects()`. Muito aderente, pois o sistema já entende o modelo `MUITAS` para trajetórias globais (usado no thresholding espacial).
  - *Risco de Regressão:* Baixo se injetado como sobrecarga opcional no Template Method.

### C) Modelagem como Grafo de Dependência
- **Mecânica:** Construir DAGs instanciando hierarquias ($POI \rightarrow price$). A sumarização resolve de cima para baixo na árvore: primeiro sumariza a raiz ($POI$), depois filtra os sub-pontos cujo $POI$ foi o vencedor, e sumariza o $price$ apenas desse subconjunto.
- **Avaliação:**
  - *Complexidade:* Altamente complexa para implementar na arquitetura linear atual.
  - *Impactos:* Obriga a quebrar totalmente os arrays soltos de `MATSummarize`.

### D) Embedding Semântico
- **Mecânica:** Transformar atributos usando Word2Vec/Doc2Vec e fundir os vetores contínuos, extraindo o atributo nominal mais próximo do vetor médio real no hiper-espaço.
- **Avaliação:**
  - *Complexidade:* Alta (requer tempo de treinamento e hiperparâmetros ML). Fora do escopo determinístico computacional atual das abordagens MAT.

---

## 3. Impactos Arquiteturais no Projeto

- **MATSummarize:** O `_fuse_aspects` não poderá mais ser genérico e isolado se o uso de Features for acionado. Precisamos de uma segregação entre atributos independentes (que continuam fluindo normalmente) e features dependentes.
- **Centroid & AttributeValue:** Não é preciso substituir o `AttributeValue` inteiro, mas introduzir uma nova interface `CompoundAttribute` (que contém uma coleção de `AttributeValue`). O dicionário de `Centroid` aceita lidar com qualquer classe que herde de `SemanticAspect`.
- **Template Method:** **Sim, deve ser estendido.** O ideal é adicionar um novo *hook* `_fuse_compound_features(self, points)` chamado no fim de `identify_and_process_cells()`.
- **Será necessário criar nova classe Feature?** Sim. Sugere-se `CompoundAspect` herdando de `SemanticAspect`.
- **Exportação CSV:** Precisa de um parser bidirecional, extraindo `CompoundAspect("POI_DOMINIO")` devolta para as colunas originárias (ex: `POI`, `Price`).

---

## 4. Proposta Arquitetural Recomendada

**Melhor Abordagem:** **B) Similaridade Baseada em MUITAS (com agregação por Medoide) unificada com conceito de CompoundFeature.**

**Justificativa Técnica:** Mantém o uso do ferramental matemático que o sistema já tem (`MUITAS.score()`) e permite avaliar features que misturam variáveis contínuas numéricas (tratadas com tolerância / Support Vector threshold) e categóricas exatas. 

**Como integrar ao Template Method sem quebrar compatibilidade:**
As classes `MATSG` e `MATSGT` continuam idênticas. Nós criaremos um mixin ou injetaremos a lógica no próprio `MATSummarize` habilitada por uma flag genérica de execução (ex: `dependent_aspects=[['POI', 'price']]`). 
Se a flag estiver vazia, o pipeline tradicional rege. Se estiver preenchida, o sistema cria um `CompoundAspect` interno, inibindo os fluxos individuais de POI e price.

---

## 5. Avaliação de Complexidade

- **Complexidade Atual:** No pior caso do Grid para processamento de células, a sumarização leva $O(N_c \times A)$ onde $N_c$ é número de pontos na célula e $A$ número de atributos. A fusão baseada em lista e mediana padrão do python/numpy é linear/quase linear.
- **Complexidade com Associação:** Para encontrar o **Medoide** representativo do CompoundFeature na célula, calcularemos a distância par-a-par baseada na classe `MUITAS`. Isso leva uma complexidade interna para $O(N_c^2 \times A_{dep})$. Escala quadraticamente, mas como $N_c$ (pontos dentro de um único quadrado de grid local) costuma ser pequeno, o custo da etapa STI continuará aceitável e dominando o processamento.

---

## 6. Plano de Implementação

- **Fase 1 – Modelagem de Feature:** Criar classes `CompoundAspect` e `CompoundAttributeValue`.
- **Fase 2 – Refatoração da fusão semântica:** Modificar `MATSummarize.load()` para aceitar agrupamento de colunas dependentes. Interceptar `fuse_aspects` para isolar instâncias da árvore acoplada.
- **Fase 3 – Integração com MATSG / Framework:** Desenvolver o método de extração do *Medoide* em `MATSummarize` para atributos compostos.
- **Fase 4 – Integração com MATSGT:** Garantir que o fatiamento temporal STI passe ileso pelas features conjuntas (o fluxo STI já atua em `process_cell_points` e usa `Centroid` normalmente).
- **Fase 5 – Ajustes de exportação:** Editar o descompactador `write_representative_trajectory()` do `MATSummarize` para printar colunas combinadas em suas rubricas separadas originais no formato `.csv`.
- **Fase 6 – Testes unitários:** Criar um grid falso unitário que comprove que `POI=Shopping, Price=100` prevalece na célula e não produz `POI=Shopping, Price=13`.

---

## 🎯 Tarefa 2: Proposta Técnica para Implementação

### 1. Estrutura de Classes (Camada de Abstração)
Foi feita a escolha por **Composição** em vez de Herança pesada, garantindo menor choque arquitetural:

```python
# Em model/SemanticAspect.py (Extensão)
class CompoundAspect(SemanticAspect):
    def __init__(self, name: str, order: int, sub_aspects: List[SemanticAspect]):
        super().__init__(name, order, SemanticType.CATEGORICAL)
        self.sub_aspects = sub_aspects # Referência para [Aspect_POI, Aspect_Price]

# Em model/AttributeValue.py (Extensão)
class CompoundAttributeValue(AttributeValue):
    def __init__(self, compound_aspect, list_of_atvs):
        super().__init__(value=list_of_atvs, attribute=compound_aspect)
```

### 2. Alterações no Template Method (`MATSummarize`)

Dentro do `execute()`, recebemos o novo parâmetro: `dependent_features=[('POI', 'price')]`.
Durante o `load()`, em vez de apensar `POI` e `price` individualmente, empacotamos eles no `CompoundAspect`. No parseamento das linhas iteradas:
```python
# Pseudo-code MATSummarize.load()
if column in compound_map:
    # Coleta temporária, depois instancia o CompoundAttributeValue e atrela a Point
```

Na geração, introduzimos o hook de Medoide Semântico (apenas quando CompoundAspect está configurado):

```python
# Pseudo-código de sumarização dependente
def _summarize_compound_aspects(self, rep_point, cell_points, compound_aspect):
    best_score = -1
    medoid_idx = 0
    
    # MUITAS adaptado localmente para os sub-atributos
    for i, candidate in enumerate(cell_points):
        score_sum = 0
        for j, peer in enumerate(cell_points):
            score_sum += local_muitas_score(candidate, peer, compound_aspect)
        
        if score_sum > best_score:
            best_score = score_sum
            medoid_idx = i
            
    # O valor vencedor do par associado é o eleito para o Centroid!
    rep_point.add_attr_value(cell_points[medoid_idx].get_attribute_value(compound_aspect))
```

### 3. Exemplo Concreto (POI + price)

- **Dados de Entrada na Célula X:**
  - P1: `POI='Restaurante', price=80` (Cenário Dominante)
  - P2: `POI='Restaurante', price=90` (Cenário Dominante)
  - P3: `POI='Parque', price=0` (Ruído Esporádico)

- **Fluxo Tradicional (BUG de dependência):**
  - Categórico (POI): Moda = Restaurante.
  - Numérico (price): Mediana = 80.
  - Resultado pode até bater, mas se P3 e P4 fossem Parques a R$ 0, e P1 e P2 ficassem ali, a mediana poderia puxar pro `40`, criando um `Restaurante` fictício de preço `40`.

- **Fluxo Compound Feature:**
  - `Compound(POI, price)` cria as tuplas: `T1=(Restaurante, 80)`, `T2=(Restaurante, 90)`, `T3=(Parque, 0)`.
  - Distância (Base MUITAS):
    - Score(T1, T2) = Alto (pois ambos são Restaurantes e a variação numérica é tolerável pelo limiar).
    - Score(T1, T3) = 0.
  - O candidato que agrega mais similaridade ao seu redor é `T1`.
  - **Centroid Final Salvo:** `POI=Restaurante, price=80`. Coerência semântica absoluta garantida.

### 4. Estratégia de Retrocompatibilidade
Para **NÃO** quebrar o Output CSV nem as subclasses `MATSG` / `MATSGT`, o sistema sobreescreve a exibição dos atributos compostos na função `write_representative_trajectory`. Ao invés de acessar a propiedade `.value` livre, ele varre iterativamente a árvore da Composição (que guarda a referência correta para `POI` e `price`) transcrevendo exatamente na estrutura posicional que o *header* do arquivo espera. O runner mantém `dependent_features=None` por padrão na v1.0, blindando legados.
