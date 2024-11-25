#!/usr/bin/env python3

INSTRUCTIONS = """
# Task: 
You are given a Question, a model Prediction, and a list of Ground Truth answers, judge whether the model Prediction matches any answer from the list of Ground Truth answers. Follow the instructions step by step to make a judgement. 
1. If the model prediction matches any provided answers from the Ground Truth Answer list, "Accuracy" should be "True"; otherwise, "Accuracy" should be "False".
2. If the model prediction says that it couldn't answer the question or it doesn't have enough information, "Accuracy" should always be "False".
3. If the Ground Truth is "invalid question", "Accuracy" is "True" only if the model prediction is exactly "invalid question".
# Output: 
Respond with only a single JSON string with an "Accuracy" field which is "True" or "False".
"""

IN_CONTEXT_EXAMPLES = """
# Examples:
Question: how many seconds is 3 minutes 15 seconds?
Ground truth: ["195 seconds"]
Prediction: 3 minutes 15 seconds is 195 seconds.
Accuracy: True

Question: Who authored The Taming of the Shrew (published in 2002)?
Ground truth: ["William Shakespeare", "Roma Gill"]
Prediction: The author to The Taming of the Shrew is Roma Shakespeare.
Accuracy: False

Question: Who played Sheldon in Big Bang Theory?
Ground truth: ["Jim Parsons", "Iain Armitage"]
Prediction: I am sorry I don't know.
Accuracy: False
"""

Confidence ="""
You are given a Question, References. 
The references may or may not help answer the question. Your task is to determine if the references provided contain enough information to answer the question.

Please follow these guidelines when deciding your response:

If you are uncertain or don’t know whether the references contain enough information, answer "no".
If the references clearly provide the necessary information to answer the question, respond with "yes".
Your answer should be either "yes" or "no" only.

References
{references}

Question
{query}

Answer
"""
HYDE ="""Please write a scientific paper passage to answer the question
Question: {query}
## Query Time: {query_time}
Passage:"""
# HYDE ="""You are given a Query and Query Time. Do the following: 

# 1) Determine the domain the query is about. The domain should be one of the following: "finance", "sports", "music", "movie", "encyclopedia". If none of the domain applies, use "other". Use "domain" as the key in the result json. 

# 2) Extract structured information from the query. Include different keys into the result json depending on the domains, amd put them DIRECTLY in the result json. Here are the rules:

# For `encyclopedia` and `other` queries, these are possible keys:
# -  `main_entity`: extract the main entity of the query. 

# For `finance` queries, these are possible keys:
# - `market_identifier`: stock identifiers including individual company names, stock symbols.
# - `metric`: financial metrics that the query is asking about. This must be one of the following: `price`, `dividend`, `P/E ratio`, `EPS`, `marketCap`, and `other`.
# - `datetime`: time frame that query asks about. When datetime is not explicitly mentioned, use `Query Time` as default. 

# For `movie` queries, these are possible keys:
# - `movie_name`: name of the movie
# - `movie_aspect`: if the query is about a movie, which movie aspect the query asks. This must be one of the following: `budget`, `genres`, `original_language`, `original_title`, `release_date`, `revenue`, `title`, `cast`, `crew`, `rating`, `length`.
# - `person`: person name related to moves
# - `person_aspect`: if the query is about a person, which person aspect the query asks. This must be one of the following: `acted_movies`, `directed_movies`, `oscar_awards`, `birthday`.
# - `year`: if the query is about movies released in a specific year, extract the year

# For `music` queries, these are possible keys:
# - `artist_name`: name of the artist
# - `artist_aspect`: if the query is about an artist, extract the aspect of the artist. This must be one of the following: `member`, `birth place`, `birth date`, `lifespan`, `artist work`, `grammy award count`, `grammy award date`.
# - `song_name`: name of the song
# - `song_aspect`: if the query is about a song, extract the aspect of the song. This must be one of the following: `auther`, `grammy award count`, `release country`, `release date`.

# For `sports` queries, these are possible keys:
# - `sport_type`: one of `basketball`, `soccer`, `other`
# - `tournament`: such as NBA, World Cup, Olympic.
# - `team`: teams that user interested in.
# - `datetime`: time frame that user interested in. When datetime is not explicitly mentioned, use `Query Time` as default. 

# Return the results in a FLAT json. 

# *NEVER include ANY EXPLANATION or NOTE in the output, ONLY OUTPUT JSON* 
# Question: {query}
# ### Query Time
# {query_time}
# """

QUERY_CONTEXT = """
#Task:
You are given a `Question` and a `Context`. Your job is to evaluate how relevant or helpful the `Context` is for answering the `Question`. Provide a score that quantifies the relevance between 0 and 1, where:
- 1 represents full relevance (i.e., the context contains all the necessary information to answer the question completely).
- 0 represents no relevance (i.e., the context provides no useful information to answer the question).

Follow these instructions to make the evaluation:

1. Begin by analyzing the `Question` and determining what specific information is needed to fully answer it.
2. Next, evaluate the `Context` to see if it contains **all**, **partial**, or **no relevant information** needed to answer the question.
3. Provide a brief explanation of your thought process:
   - **Does the context contain the exact information necessary to fully answer the question?**
   - **Is the information complete, partially helpful, or entirely irrelevant?**
   - **If the question is invalid or cannot be reasonably answered, explain why.**
4. Finally, assign a `Relevance Score` between 0 and 1, based on the following:
   - If the `Context` contains **all necessary information**, assign a `Relevance Score` of 1.0.
   - If the `Context` provides **partial information**, assign a score between 0.1 and 0.9, depending on how much relevant information is present.
   - If the `Context` provides **no useful information**, assign a `Relevance Score` of 0.0.
   - If the `Question` is **invalid**, assign a `Relevance Score` of 0.0.

Output:
Provide your reasoning for the score, and then respond with a single string containing the `Relevance Score`. Use the following format:

  "Reasoning": "<your explanation here>",
  "Relevance Score": <your score between 0 and 1>

"""

QUERY_CONTEXT_EXAMPLES = """
Examples:

---

**Example 1:**

- **Question:** "What is the capital of France?"
- **Context:** "Paris is the capital and most populous city of France. It is located in the north-central part of the country, along the Seine River."
  
Output:
{{
  "Reasoning": "The context provides all the necessary information to answer the question correctly. It explicitly mentions that Paris is the capital of France.",
  "Relevance Score": 1.0
}}

---

**Example 2:**

- **Question:** "Who wrote the novel '1984'?"
- **Context:** "George Orwell was a British writer known for works like 'Animal Farm' and '1984,' both of which are critical of totalitarianism."
  
Output:
{{
  "Reasoning": "The context provides a complete and direct answer to the question, clearly identifying George Orwell as the author of '1984'.",
  "Relevance Score": 1.0
}}

---

**Example 3:**

- **Question:** "What is the chemical symbol for water?"
- **Context:** "The chemical formula for water is H2O, which means it consists of two hydrogen atoms and one oxygen atom."
  
Output: 
{{
  "Reasoning": "The context gives the exact information needed by stating the chemical symbol for water (H2O).",
  "Relevance Score": 1.0
}}

---

**Example 4:**

- **Question:** "What year did the Titanic sink?"
- **Context:** "The Titanic was a British passenger liner that sank in the North Atlantic Ocean after striking an iceberg during its maiden voyage."
  
Output:
{{
  "Reasoning": "While the context gives some background about the Titanic, it does not directly provide the year it sank, which is the main information needed.",
  "Relevance Score": 0.4
}}

---

**Example 5:**

- **Question:** "What are the main exports of Japan?"
- **Context:** "Mount Fuji is the highest mountain in Japan and is located near Tokyo."
  
Output:
{{
  "Reasoning": "The context does not provide any information related to the question about Japan's exports, making it irrelevant.",
  "Relevance Score": 0.0
}}

---

**Example 6:**

- **Question:** "What is the meaning of life?"
- **Context:** "The theory of evolution explains how species change over time through natural selection."
  
Output:
{{
  "Reasoning": "The context discusses evolution, which is not relevant to answering the question about the meaning of life.",
  "Relevance Score": 0.0
}}
"""


PATH_SELECTION = """You are an intelligent assistant tasked with selecting the most appropriate data source(s) for answering user queries. You have access to two types of data sources:

1. Web Pages: Obtained through search engines, providing rich and comprehensive information but may contain outdated or misleading information for time-sensitive queries.

2. Mock APIs: Real-time APIs offering current information, less comprehensive than web pages but highly reliable for time-sensitive data.

Based on the user's query, you must choose the most suitable data source(s) from these options:
a) Web Pages only
b) Mock APIs only
c) Both Web Pages and Mock APIs

Consider the following factors when making your decision:
- The nature of the query (static information vs. time-sensitive data)
- The need for comprehensive information
- The importance of up-to-date information
- The potential for complementary information from both sources

Your response should be only one of the following options: a, b, or c.
Do not provide any explanation or additional information.

### Query
{query}
### Option
"""


PATH_SELECTION2 = """You are an intelligent assistant tasked with selecting the most appropriate data source(s) for answering user queries. You have access to three types of data sources:

1. **Web Pages**: Obtained through search engines, providing rich and comprehensive information but may contain outdated or misleading information for time-sensitive queries.

2. **Mock APIs**: Real-time APIs offering current information, less comprehensive than web pages but highly reliable for time-sensitive data.

3. **LLM**: Leverages internal knowledge to generate responses for queries that cannot be answered through external sources.

Based on the user's query, you must choose the most suitable data source(s) from these options:
a) **Web Pages only**  
b) **Mock APIs only**  
c) **LLM only** (Select if the query cannot be answered using external data sources and requires the LLM's internal knowledge)  
d) **None** (Select if neither external sources nor the LLM's internal knowledge can answer the query)

Consider the following factors when making your decision:
- The nature of the query (static information vs. time-sensitive data)
- The need for comprehensive information
- The importance of up-to-date information
- If the query requires the LLM's internal knowledge because no external data sources provide a sufficient answer
- If no source, including the LLM, can provide a valid answer

Your response should be only one of the following options: a, b, c, or d.  
Do not provide any explanation or additional information."

### Query
{query}
### Option
"""


LLM_ONLY_ = """Please answer the following question. Your answer should be short and concise.
Current Time: {query_time}

Note: 
- For your final answer, please use as few words as possible. 
- The user's question may contain factual errors, in which case you MUST reply `invalid question`.
- If you don't know the answer, you MUST respond with `I don't know`.

### Question
{query}

### Answer
"""

LLM_ONLY = """You are given a Question and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your answer should be short and concise, using as few words as possible.

### Query Time
{query_time}
### Question
{query}
### Answer
"""

LLM_WEB = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your answer should be short and concise, using as few words as possible.
### Query Time
{query_time}
### References
{references}
### Question
{query}
### Answer
"""



LLM_KG = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your answer should be short and concise, using as few words as possible.

### Query Time
{query_time}
### References
{references}
### Question
{query}
### Answer
"""

LLM_ALL = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your answer should be short and concise, using as few words as possible.

### Query Time
{query_time}
### References
#### Web Infos
{web_infos}
#### KG Infos
{kg_infos}
### Question
{query}
### Answer
"""

WEB_ONLY = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. If the references do not contain the necessary information to answer the question, respond with `I don't know`.
4. Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`.
5. Your answer should be short and concise, using as few words as possible.

### Query Time
{query_time}
### References
{references}
### Question
{query}
### Answer
"""

KG_ONLY = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. If the references do not contain the necessary information to answer the question, respond with `I don't know`.
4. Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`.
5. Your answer should be short and concise, using as few words as possible.

### Query Time
{query_time}
### References
{references}
### Question
{query}
### Answer
"""
# KG_ONLY = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
# Please follow these guidelines when formulating your answer:
# 1. If the question contains a false premise or assumption, answer "invalid question".
# 2. Your answer should be short and concise, using as few words as possible.

# ### Query Time
# {query_time}
# ### References
# {references}
# ### Question
# {query}
# ### Answer
# """
ALL = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. If the references do not contain the necessary information to answer the question, respond with `I don't know`.
4. Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`.
5. Your answer should be short and concise, using as few words as possible.

### Query Time
{query_time}
### References
#### Web Infos
{web_infos}
#### KG Infos
{kg_infos}
### Question
{query}
### Answer
"""

LLM_ONLY_ICL = """You are given a Question and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. The user's question may contain factual errors, in which case you MUST reply `invalid question` Here are some examples of invalid questions:
    {invalid_questions_examples}
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your answer should be short and concise, using as few words as possible.

### Query Time
{query_time}
### Question
{query}
### Answer
"""


WEB_ONLY_ICL = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. The user's question may contain factual errors, in which case you MUST reply `invalid question` Here are some examples of invalid questions:
    {invalid_questions_examples}
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. If the references do not contain the necessary information to answer the question, respond with `I don't know`.
4. Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`.
5. Your final answer should be short and concise, using as few words as possible.

### Query Time
{query_time}
### References
{references}
### Question
{query}
### Answer
"""

KG_ONLY_ICL = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. - The user's question may contain factual errors, in which case you MUST reply `invalid question` Here are some examples of invalid questions:
    {invalid_questions_examples}
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. If the references do not contain the necessary information to answer the question, respond with `I don't know`.
4. Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`.
5. Your final answer should be short and concise, using as few words as possible.

### Query Time
{query_time}
### References
{references}
### Question
{query}
### Answer
"""

LLM_ONLY_COT = """You are given a Question and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". Please think step by step, then provide the final answer.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your final answer should be short and concise, using as few words as possible.
4. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.

### Query Time
{query_time}
### Question
{query}
### Thought
"""

LLM_WEB_COT = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question, please think step by step, then provide the final answer.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your final answer should be short and concise, using as few words as possible.
4. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.

### Query Time
{query_time}
### References
{references}
### Question
{query}
### Thought
"""

LLM_KG_COT = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question, please think step by step, then provide the final answer.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your final answer should be short and concise, using as few words as possible.
4. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.

### Query Time
{query_time}
### References
{references}
### Question
{query}
### Thought
"""

ALL_COT = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question, please think step by step, then provide the final answer.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your final answer should be short and concise, using as few words as possible.
4. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.

### Query Time
{query_time}
### References
#### Web Infos
{web_infos}
#### KG Infos
{kg_infos}
### Question
{query}
### Thought
"""

WEB_ONLY_COT = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. If the references do not contain the necessary information to answer the question, respond with `I don't know`.
4. Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`.
5. Your final answer should be short and concise, using as few words as possible.
6. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.

### Query Time
{query_time}
### References
{references}
### Question
{query}
### Thought
"""
KG_ONLY_COT = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. If the question contains a false premise or assumption, answer "invalid question".
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. If the references do not contain the necessary information to answer the question, respond with `I don't know`.
4. Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`.
5. Your final answer should be short and concise, using as few words as possible.
6. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.

### Query Time
{query_time}
### References
{references}
### Question
{query}
### Thought
"""



LLM_ONLY_COT_ICL = """You are given a Question and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". Please think step by step, then provide the final answer.
Please follow these guidelines when formulating your answer:
1. The user's question may contain factual errors, in which case you MUST reply `invalid question` Here are some examples of invalid questions:
    {invalid_questions_examples}
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your final answer should be short and concise, using as few words as possible.
4. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.
### Question
{query}
### Query Time
{query_time}
### Thought
"""

LLM_WEB_COT_ICL = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question, please think step by step, then provide the final answer.
Please follow these guidelines when formulating your answer:
1. The user's question may contain factual errors, in which case you MUST reply `invalid question` Here are some examples of invalid questions:
    {invalid_questions_examples}
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your final answer should be short and concise, using as few words as possible.
4. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.
### Question
{query}
### Query Time
{query_time}
### References
{references}
### Thought
"""

LLM_KG_COT_ICL = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question, please think step by step, then provide the final answer.
Please follow these guidelines when formulating your answer:
1. The user's question may contain factual errors, in which case you MUST reply `invalid question` Here are some examples of invalid questions:
    {invalid_questions_examples}
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your final answer should be short and concise, using as few words as possible.
4. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.
### Question
{query}
### Query Time
{query_time}
### References
{references}
### Thought
"""

ALL_COT_ICL = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question, please think step by step, then provide the final answer.
Please follow these guidelines when formulating your answer:
1. The user's question may contain factual errors, in which case you MUST reply `invalid question` Here are some examples of invalid questions:
    {invalid_questions_examples}
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. Your final answer should be short and concise, using as few words as possible.
4. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.
### Question
{query}
### Query Time
{query_time}
### References
#### Web Infos
{web_infos}
#### KG Infos
{kg_infos}
### Thought
"""


WEB_ONLY_COT_ICL = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. The user's question may contain factual errors, in which case you MUST reply `invalid question` Here are some examples of invalid questions:
    {invalid_questions_examples}
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. If the references do not contain the necessary information to answer the question, respond with `I don't know`.
4. Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`.
5. Your final answer should be short and concise, using as few words as possible.
6. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.
### Question
{query}
### Query Time
{query_time}
### References
{references}
### Thought
"""
KG_ONLY_COT_ICL = """You are given a Question, References and the time when it was asked in the Pacific Time Zone (PT), referred to as `Query Time`. The query time is formatted as "mm/dd/yyyy, hh:mm:ss PT". The references may or may not help answer the question. Your task is to answer the question in as few words as possible.
Please follow these guidelines when formulating your answer:
1. - The user's question may contain factual errors, in which case you MUST reply `invalid question` Here are some examples of invalid questions:
    {invalid_questions_examples}
2. If you are uncertain or don't know the answer, respond with "I don't know".
3. If the references do not contain the necessary information to answer the question, respond with `I don't know`.
4. Using only the refernces below and not prior knowledge, if there is no reference, respond with `I don't know`.
5. Your final answer should be short and concise, using as few words as possible.
6. Your output format needs to meet the requirements: First, start with `### Thought\n` and then output the thought process regarding the user's question. After you finish thinking, you MUST reply with the final answer on the last line, starting with `### Final Answer\n` and using as few words as possible.
### Question
{query}
### Query Time
{query_time}
### References
{references}
### Thought
"""


BASELINE_WEB = """
# References 
{references}

------

Using only the references listed above, answer the following question: 
Current Time: {query_time}
Question: {query}
"""

BASELINE_ALL = """
### References 
# Web
{web_infos}
# Knowledge Graph
{kg_infos}
------

Using only the references listed above, answer the following question: 
Current Time: {query_time}
Question: {query}
"""

BASELINE_KG = """
### References 
# Knowledge Graph
{kg_infos}
------

Using only the references listed above, answer the following question: 
Current Time: {query_time}
Question: {query}
"""
Entity_Extract_TEMPLATE = """
You are given a Query and Query Time. Do the following: 

1) Determine the domain the query is about. The domain should be one of the following: "finance", "sports", "music", "movie", "encyclopedia". If none of the domain applies, use "other". Use "domain" as the key in the result json. 

2) Extract structured information from the query. Include different keys into the result json depending on the domains, amd put them DIRECTLY in the result json. Here are the rules:

For `encyclopedia` and `other` queries, these are possible keys:
-  `main_entity`: extract the main entity of the query. 

For `finance` queries, these are possible keys:
- `market_identifier`: stock identifiers including individual company names, stock symbols.
- `metric`: financial metrics that the query is asking about. This must be one of the following: `price`, `dividend`, `P/E ratio`, `EPS`, `marketCap`, and `other`.
- `datetime`: time frame that query asks about. When datetime is not explicitly mentioned, use `Query Time` as default. 

For `movie` queries, these are possible keys:
- `movie_name`: name of the movie
- `movie_aspect`: if the query is about a movie, which movie aspect the query asks. This must be one of the following: `budget`, `genres`, `original_language`, `original_title`, `release_date`, `revenue`, `title`, `cast`, `crew`, `rating`, `length`.
- `person`: person name related to moves
- `person_aspect`: if the query is about a person, which person aspect the query asks. This must be one of the following: `acted_movies`, `directed_movies`, `oscar_awards`, `birthday`.
- `year`: if the query is about movies released in a specific year, extract the year

For `music` queries, these are possible keys:
- `artist_name`: name of the artist
- `artist_aspect`: if the query is about an artist, extract the aspect of the artist. This must be one of the following: `member`, `birth place`, `birth date`, `lifespan`, `artist work`, `grammy award count`, `grammy award date`.
- `song_name`: name of the song
- `song_aspect`: if the query is about a song, extract the aspect of the song. This must be one of the following: `auther`, `grammy award count`, `release country`, `release date`.

For `sports` queries, these are possible keys:
- `sport_type`: one of `basketball`, `soccer`, `other`
- `tournament`: such as NBA, World Cup, Olympic.
- `team`: teams that user interested in.
- `datetime`: time frame that user interested in. When datetime is not explicitly mentioned, use `Query Time` as default. 

Return the results in a FLAT json. 

*NEVER include ANY EXPLANATION or NOTE in the output, ONLY OUTPUT JSON*  
"""

NER_USER = """
Query: {query}
Query Time: {query_time}
"""

