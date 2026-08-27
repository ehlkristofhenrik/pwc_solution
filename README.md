# PWC Medior AI Engineer Solution

## Problem statement

Fictive Inc. is a large multinational company who wants to have a user-friendly RAG system for its employees.
They have internal documentation in markdown in the data/ folder (courtesy of Gemini).

## Architecture

<img width="422" height="467" alt="diagram" src="https://github.com/user-attachments/assets/f5cdfa2e-977f-4f47-9ea7-b74159d55a47" />


The RAG system uses Query-Rewriting to ensure that the RAG process is not wasting time on vague questions.
It also uses CRAG (Corrective RAG), checking if the output is grounded in the data and answers the user's question. In addition the RAG system also utilizes vector database document similarity search. The LLM is lfm2.5-thinking:1.2B, the vector database is Chroma.

Tools:
- get_datetime
- get_usa_gdp
- calculate_revenue

> Why not use grep based RAG?

File search tool based RAG, like the one implemented by Claude Code, whilst generally perform better, also use more tokens and are mostly used for code RAG.

> Why not use graph based RAG?

Graph RAG performs really well, but as the dataset increases, the precomputation of the graph is going to be costly. For simpler systems the traditional Naive RAG is more appropriate.

> Why not use HyDE?

HyDE would be feasable, but harder to develop and maintain.

> Why use CRAG?

Since the model used is small, it has higher hallucination rate compared to SoTA models. Thus CRAG can catch the errors and retry. It could theorethically cause an infinite loop if the model gets stuck with an out-of-distribution.

> Why use Prompt-Refining?

Since Fictive Inc. is a non-tech business, it would be safe to assume that the employees have limited technical abilities, who might not be efficient at prompting. Prompt-Refining also helps reduce the failed queries due to ambiguity.

## Testing & Validation

The system couldn't be tested properly, as my machine can not run LLMs effectively (its very very very slow). Mocking would be more efficient, however that wouldn't reflect the quality of the RAG.
Still, the test data can be found in the test_dataset.csv file. Since my system is incredibly slow, the UI was made to work only one query per session, and does not include a complex chat interface.

The bottleneck in my system is ollama. My machine has around 256 MB of VRAM, severely limiting my options. Thus I choose lfm2.5-thinking:1.2b, as it is a relatively CPU friendly (Liquid model) SLM with decent quality. Still its very heavy because of the thinking. In early testing I also looked at smollm2:360m, but the quality is bad. I would also like to mention that other CPU friendly architectures might prove effective, such as Mamba, Hybrid Transformer-Mamba or RWKV. They have lesser "intelligence", but don't suffer from the O(n^2) computation as context increases.

## Build

> docker compose up

## Teardown

> docker compose down --volumes
