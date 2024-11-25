import os
import bz2
import json
from tqdm import tqdm
from loguru import logger
import argparse

from models.load_model import load_chat_model
from models.retrieve.retriever import Retriever, Retriever_Milvus
from models.model import *

def load_data_in_batches(dataset_path, batch_size):
    """
    Generator function that reads data from a compressed file and yields batches of data.
    Each batch is a dictionary containing lists of interaction_ids, queries, search results, query times, and answers.
    
    Args:
    dataset_path (str): Path to the dataset file.
    batch_size (int): Number of data items in each batch.
    
    Yields:
    dict: A batch of data.
    """
    def initialize_batch():
        """ Helper function to create an empty batch. """
        return {"interaction_id": [], "query": [], "search_results": [], "query_time": [], "answer": [], "domain": [], "static_or_dynamic": [], "question_type": []}

    try:
        if dataset_path.endswith(".bz2"):
            with bz2.open(dataset_path, "rt", encoding='utf-8') as file:
                batch = initialize_batch()
                for line in file:
                    try:
                        item = json.loads(line)
                        for key in batch:
                            batch[key].append(item[key])
                            # print(key)
                        
                        if len(batch["query"]) == batch_size:
                            yield batch
                            batch = initialize_batch()
                    except json.JSONDecodeError:
                        logger.warn("Warning: Failed to decode a line.")
                # Yield any remaining data as the last batch
                if batch["query"]:
                    yield batch
        else:
            with open(dataset_path, "r") as file:
                batch = initialize_batch()
                for line in file:
                    try:
                        item = json.loads(line)
                        for key in batch:
                            batch[key].append(item[key])
                        
                        if len(batch["query"]) == batch_size:
                            yield batch
                            batch = initialize_batch()
                    except json.JSONDecodeError:
                        logger.warn("Warning: Failed to decode a line.")
                # Yield any remaining data as the last batch
                if batch["query"]:
                    yield batch
    except FileNotFoundError as e:
        logger.error(f"Error: The file {dataset_path} was not found.")
        raise e
    except IOError as e:
        logger.error(f"Error: An error occurred while reading the file {dataset_path}.")
        raise e
    
def generate_predictions(dataset_path, participant_model, batch_size):
    """
    Processes batches of data from a dataset to generate predictions using a model.
    
    Args:
    dataset_path (str): Path to the dataset.
    participant_model (object): UserModel that provides `get_batch_size()` and `batch_generate_answer()` interfaces.
    
    Returns:
    tuple: A tuple containing lists of queries, ground truths, and predictions.
    """
    queries, ground_truths, predictions, contexts, kg_infos = [], [], [], [], []
    domains, static_or_dynamics, question_types= [], [], []

    for batch in tqdm(load_data_in_batches(dataset_path, batch_size), desc="Generating predictions"):
        batch_ground_truths = batch.pop("answer")  # Remove answers from batch and store them
        batch_predictions, batch_contexts, batch_kg_infos = participant_model.batch_generate_answer(batch)
        queries.extend(batch["query"])
        domains.extend(batch["domain"])
        static_or_dynamics.extend(batch["static_or_dynamic"])
        question_types.extend(batch["question_type"])
        ground_truths.extend(batch_ground_truths)
        predictions.extend(batch_predictions)
        contexts.extend(batch_contexts)
        kg_infos.extend(batch_kg_infos)
        logger.info(f"Query Example: {queries[-1]}")
        logger.info(f"Ground Truth Example: {ground_truths[-1]}")
        logger.info(f"Prediction Example: {predictions[-1]}")
    return queries, ground_truths, predictions, contexts , kg_infos,  domains, static_or_dynamics, question_types

def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--api_key", type=str, default="<your-api-key>")
    parser.add_argument("--base_url", type=str, default="http://localhost:8000/v1/")
    parser.add_argument("--model_name", type=str, default="Meta-Llama-3.1-8B-Instruct") 
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--top_p", type=float, default=None)
    parser.add_argument("--embedding_model_path", type=str, default="models/retrieve/embedding_models/bge-m3")
    parser.add_argument("--reranker_model_path", type=str, default="models/retrieve/reranker_models/bge-reranker-v2-m3") 
    parser.add_argument("--top_k", type=int, default=3)
    parser.add_argument("--top_n", type=int, default=3)
    parser.add_argument("--device", type=str, default="cuda:1")
    parser.add_argument("--sparse", type=int, default=0)
    parser.add_argument("--rerank", action="store_true")
    parser.add_argument("--chunk_size", type=int, default=200)
    parser.add_argument("--chunk_overlap", type=int, default=0)
    parser.add_argument("--knowledge_source", type=str, default="web")
    parser.add_argument("--prompt_type", type=str, default="base")
    parser.add_argument("--dataset_path", type=str, default="task1_split_0_no_link.jsonl.bz2") #task3_split0.jsonl.bz2
    parser.add_argument("--icl", type=int, default=0)
    parser.add_argument("--broad_retrieval", action="store_true")
    parser.add_argument("--cache_context", action="store_true")
    parser.add_argument("--hyde", action="store_true")
    parser.add_argument("--noise", type=int, default=0)
    parser.add_argument("--confidence", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    # Set the environment variable for the mock API
    os.environ["CRAG_MOCK_API_URL"] = "http://localhost:8001"

    args = parse_arg()
    # Load the model
    api_key = args.api_key
    # base_url = "http://210.45.70.162:28083/v1/"
    base_url = args.base_url
    model_name = args.model_name
    temperature = args.temperature
    top_p = args.top_p
    chat_model = load_chat_model(model_name=model_name, api_key=api_key, base_url=base_url, temperature=temperature, top_p=top_p, max_tokens=500)
    select_model = load_chat_model(model_name="llama3-1_lora_sft", api_key=api_key, base_url="http://localhost:8002/v1/", temperature=temperature, top_p=top_p, max_tokens=500)
    # Load the retriever
    embedding_model_path = args.embedding_model_path
    reranker_model_path = args.reranker_model_path
    top_k = args.top_k
    top_n = args.top_n
    rerank = args.rerank
    chunk_size = args.chunk_size
    chunk_overlap = args.chunk_overlap
    sparse = args.sparse
    device = args.device
    broad_retrieval = args.broad_retrieval
    cache_context = args.cache_context
    hyde = args.hyde
    noise = args.noise
    confidence = args.confidence

    retriever = Retriever(top_k, top_n, embedding_model_path, reranker_model_path, rerank, chunk_size, chunk_overlap, sparse, broad_retrieval,  device, noise)
    # To use the retriever with Milvus, uncomment the following lines and comment the previous line
    # collection_name = "bge_m3_crag_task_1_dev_v3_llamaindex"
    # uri = "http://localhost:19530"
    # # uri = ".models/retrieve/milvus.db"
    # # retriever = Retriever_Milvus(10, 5, collection_name, uri, embedding_model_path, reranker_model_path, rerank=True)
    # retriever = Retriever_Milvus(5, 5, collection_name, uri, embedding_model_path, reranker_model_path, rerank=False)
    knowledge_source = args.knowledge_source
    prompt_type = args.prompt_type
    icl = args.icl
    # rag_model = RAGModel(chat_model, retriever, knowledge_source, prompt_type, cache_context=cache_context, icl=None)
    # rag_model = RAGModel_2Stage(chat_model, retriever, knowledge_source)
    use_router = 0
    if hyde:
        rag_model = RAGModel_HYDE(chat_model, retriever, knowledge_source)
    else:
        # rag_model = RAGModel_4Stage(chat_model, retriever, knowledge_source, select_model=select_model)
        # use_router = 1
        rag_model = RAGModel(chat_model, retriever, knowledge_source, prompt_type, cache_context=cache_context, icl=icl)
        # rag_model = RAGModel_2Stage(chat_model, retriever, knowledge_source, prompt_type)
    # Generate predictions
    dataset_path = args.dataset_path
    queries, ground_truths, predictions, contexts, kg_infos, domains, static_or_dynamics, question_types  = generate_predictions(dataset_path, rag_model, args.batch_size)
    
    # Save the predictions
    # output_path = f"result/{model_name}_stage_3_predictions.jsonl"
    if hyde:
        output_path = f"result1/{model_name}_{knowledge_source}_predictions_hyde.jsonl"
    elif confidence:
        output_path = f"result1/{model_name}_{knowledge_source}_predictions_logit0.2_confidence_miss.jsonl"
    elif use_router:
        if noise > 0:
            output_path = f"result1/{model_name}_router_predictions_noise{noise}.jsonl"
        else:
            output_path = f"result1/{model_name}_router_predictions_task3.jsonl"
    elif rerank:
        output_path = f"result1/{model_name}_{knowledge_source}_predictions_rerank{top_k}{top_n}.jsonl"
    elif noise > 0:
        output_path = f"result1/{model_name}_{knowledge_source}_predictions_noise{noise}.jsonl"
    elif sparse > 0:
        output_path = f"result1/{model_name}_{knowledge_source}_predictions_sparse" + str(sparse) + ".jsonl"
    elif top_k > 0:
        output_path = f"result1/{model_name}_{knowledge_source}_predictions_topk{top_k}.jsonl"
    elif chunk_overlap >= 0:
        output_path = f"result1/{model_name}_{knowledge_source}_predictions_size{chunk_size}_overlap{chunk_overlap}.jsonl"
        
        
    else:
        if noise >0:
            output_path = f"result1/{model_name}_{knowledge_source}_predictions_noise{noise}.jsonl"
        else:
            output_path = f"result1/{model_name}_{knowledge_source}_predictions.jsonl"
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    with open(output_path, "w") as file:
        for query, ground_truth, prediction, context, kg_info, domain, static_or_dynamic, question_type in zip(queries, ground_truths, predictions, contexts , kg_infos, domains, static_or_dynamics, question_types ):
            item = {"question": query, "answer": prediction, "ground_truth": ground_truth, "contexts": context, "kg_infos":kg_info,  "domain": domain, "static_or_dynamic": static_or_dynamic, "question_type": question_type}
            file.write(json.dumps(item) + "\n")
    
    logger.info(f"Predictions saved to {output_path}.") 
    
    
    
    
    
#     Traceback (most recent call last):
#   File "/data/yu12345/AAAI-CRAG/main.py", line 179, in <module>
#     queries, ground_truths, predictions, contexts, kg_infos, domains, static_or_dynamics, question_types  = generate_predictions(dataset_path, rag_model, args.batch_size)
#   File "/data/yu12345/AAAI-CRAG/main.py", line 87, in generate_predictions
#     batch_predictions, batch_contexts, batch_kg_infos = participant_model.batch_generate_answer(batch)
#   File "/data/yu12345/AAAI-CRAG/models/model.py", line 1389, in batch_generate_answer
#     kg_infos = self.api.get_kg_info(query_res, query_times, domains)
#   File "/data/yu12345/AAAI-CRAG/models/mock_api/api.py", line 1301, in get_kg_info
#     kg_info = self.get_sports_info(query, query_time, matched_entities)
#   File "/data/yu12345/AAAI-CRAG/models/mock_api/api.py", line 1019, in get_sports_info
#     date, date_str = find_date_from_text(query_time, query)
#   File "/data/yu12345/AAAI-CRAG/models/mock_api/tools/generaltools.py", line 65, in find_date_from_text
#     date_str = "last " + match2.group(0) + "day"
# AttributeError: 'NoneType' object has no attribute 'group'