import json, os
import random
from sentence_transformers import SentenceTransformer, util

def load_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def input_text_embedding(text, model):
    return model.encode(text)

def prepare_overlays_dataset_for_embedding(overlays_data):
    prepared_data = []
    for key, value in overlays_data.items():
        # combined_text = 'search_document: ' + ' '.join(value['Keywords']) + ' ' + value['Description']
        combined_text = ' '.join(value['Keywords']) + ' ' + value['Description']
        # combined_text = ' '.join(value['Keywords'])
        prepared_data.append((key, combined_text, value['Blob_URL']))
    return prepared_data

# Function to calculate embeddings for the prepared data
def calculate_dataset_embeddings(prepared_data, model):
    sentences = [data[1] for data in prepared_data]
    embeddings = model.encode(sentences)
    return embeddings

# Function to find the closest B-roll footage based on cosine similarity
def find_closest_overlays(target_embedding, prepared_data, embeddings):
    max_similarity = -1
    closest_match = None
    for (key, text, urls), embedding in zip(prepared_data, embeddings):
        similarity = util.pytorch_cos_sim(target_embedding, embedding)
        if similarity > max_similarity:
            max_similarity = similarity
            # Choose between portrait and landscape based on your need here
            # selected_url = portrait_url if is_portrait else landscape_url
            selected_url_random = random.choice(urls) # custom 
            closest_match = (key, selected_url_random, similarity.item())
    return closest_match

def update_with_overlays(inputData, model, prepared_overlays_data, overlays_embeddings):
    for segment in inputData["segments"]:
        # Determine if the segment's predicted emotion is neutral
        
        # Convert segment's text to embeddings if emotion is neutral
        target_embedding = input_text_embedding(segment["text"], model)
        
        # Find the closest light leak match
        closest_match = find_closest_overlays(target_embedding, prepared_overlays_data, overlays_embeddings)

        # Update the segment based on whether a close match was found
        if closest_match and closest_match[2] > 0.58:  # Assume closest_match[2] is the similarity score
            segment["overlays_on"] = True
            segment["overlay_confidence_score"] = closest_match[2]
            segment["overlays_uri"] = closest_match[1]  # Assuming the URI is at position 1
            segment["overlays_start_time"] = segment["start"]
            segment["overlays_end_time"] = segment["end"]
        else:
            segment["overlays_on"] = False
            segment["overlay_confidence_score"] = 0
            segment["overlays_uri"] = ""  # No URI since no match was found
            segment["overlays_start_time"] = None
            segment["overlays_end_time"] = None
    
    return inputData

def save_json_file(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    return 200

def main_apply_overlays(input_json_path, dataset_path, embedding_model, output_json_path):
    try:
        segments_data = load_json_file(input_json_path)
        overlays_dataset = load_json_file(dataset_path)
        # Prepare data for embedding
        prepared_overlays_data = prepare_overlays_dataset_for_embedding(overlays_dataset)
        # Calculate embeddings
        overlays_embeddings = calculate_dataset_embeddings(prepared_overlays_data, embedding_model)
        
        updated_segments_data = update_with_overlays(segments_data, embedding_model, prepared_overlays_data, overlays_embeddings)
        status = save_json_file(output_json_path, updated_segments_data)
        
        return (200, updated_segments_data)
    except Exception as e:
        print("Error in main_apply_overlays: ", e)
        return (500, None)



# if __name__ == "__main__":
#     ## load the data
#     inputData_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/data"
#     dataset_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data"
#     dataset = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/overlays_dataset.json"
#     file_name = "steve_8words.json"
#     file_path = os.path.join(inputData_folder, file_name)

#     # Load the JSON file
#     segments_data = load_json_file(file_path)
#     overlays_dataset = load_json_file(dataset)

#     # Prepare data for embedding
#     prepared_overlays_data = prepare_overlays_dataset_for_embedding(overlays_dataset)

#     # loading embedding model
#     model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True, device="cpu")

#     # Calculate embeddings
#     overlays_embeddings = calculate_dataset_embeddings(prepared_overlays_data, model)

#     # Process segments (Change 'is_portrait' based on your video orientation)
#     updated_segments_data = update_with_overlays(segments_data, model, prepared_overlays_data, overlays_embeddings)

#     # Write the updated data back to a JSON file
#     output_file_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json'
#     status = save_json_file(output_file_path, updated_segments_data)
#     print(f"Updated data has been written to {output_file_path}")






















