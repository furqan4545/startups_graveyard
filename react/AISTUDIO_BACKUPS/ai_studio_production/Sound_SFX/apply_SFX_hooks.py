
import json, os
import random
from sentence_transformers import SentenceTransformer, util
from qdrant_client import QdrantClient
from qdrant_client.http import models


# load json data
def load_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def input_text_embedding(text, model):
    return model.encode(text)


def prepare_soundSFX_dataset_for_embedding(soundSFX_data):
    prepared_data = []
    for key, value in soundSFX_data.items():
        # combined_text = 'search_document: ' + ' '.join(value['Keywords']) + ' ' + value['Description']
        # combined_text = 'search_document: ' + ' '.join(value['Keywords'])
        combined_text = ' '.join(value['Keywords']) + ' ' +value['Description']
        # combined_text = ' '.join(value['Keywords'])
        prepared_data.append((key, combined_text, value['Blob_URL']))
    return prepared_data


# Function to calculate embeddings for the prepared data
# def calculate_dataset_embeddings(prepared_data, model):
#     sentences = [data[1] for data in prepared_data]
#     embeddings = model.encode(sentences)
#     return embeddings

def calculate_dataset_embeddings(prepared_data, model, client, collection_name):
    sentences = [data[1] for data in prepared_data]
    embeddings = model.encode(sentences)
    # Upload the embeddings to Qdrant
    # vectors = []
    vector_dim = embeddings.shape[1]
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=vector_dim, distance=models.Distance.COSINE),
    )
    # Upload the embeddings to Qdrant
    vectors = []
    for i, embedding in enumerate(embeddings):
        key = prepared_data[i][0]
        bloburl = prepared_data[i][2]
        vectors.append(models.PointStruct(id=i, vector=embedding.tolist(), payload={"key": key, "bloburl": bloburl}))

    client.upsert(collection_name=collection_name, points=vectors, wait=True)
    
    return embeddings

def find_closest_soundSFX(target_embedding, client, collection_name):
    search_result = client.search(
        collection_name=collection_name,
        query_vector=target_embedding.tolist(),
        limit=1,
    )

    if search_result:
        point = search_result[0]
        key = point.payload["key"]
        url = random.choice(point.payload["bloburl"])
        # similarity = 1 - point.score  # Convert distance to similarity, it uses cosine distance
        similarity = point.score  # Convert distance to similarity, it uses cosine distance
        closest_match = (key, url, similarity)
        # return key, url, similarity
        return closest_match
    else:
        return None
    
# Function to update the segments with sound effect based on the closest match
def update_with_soundSFX(inputData, model, client, collection_name, desired_skip_segments=3):
    skip_segments = 0  # Counter to keep track of segments to skip

    for segment in inputData["segments"]:
        if skip_segments > 0:
            # Decrement the skip counter and continue to the next segment without checking for sound effect
            skip_segments -= 1
            continue

        # Convert segment's text to embeddings
        inputText_embedding = input_text_embedding(segment["text"], model)
        
        # Find the closest sound effect match
        closest_match = find_closest_soundSFX(inputText_embedding, client, collection_name)
        
        # Update the segment based on whether a close match was found
        if closest_match and closest_match[2] > 0.58:  # Assuming closest_match[2] is the similarity score
            segment["soundSFX_on"] = True
            segment["soundSFX_confidence_score"] = closest_match[2]
            segment["soundSFX_uri"] = closest_match[1]  # Assuming the URI is at position 1
            segment["soundSFX_start_time"] = segment["start"]
            segment["soundSFX_end_time"] = segment["end"]
            
            # Sound effect was added, so skip the next 3 segments
            skip_segments = desired_skip_segments
        else:
            segment["soundSFX_on"] = False
            segment["soundSFX_confidence_score"] = 0
            segment["soundSFX_uri"] = ""  # No URI since no match was found
            segment["soundSFX_start_time"] = None
            segment["soundSFX_end_time"] = None
    
    return inputData


######################## Applying Transition SoundSFX Hooks below ############################

# here we are performing transition at the start of broll and at the end of broll
def update_segments_with_BrollTransitions(segments, soundSFX_dataset, transition_lightLeaks_dataset, allow_ending_transition=True):
    
    TRANSITIONS_TYPE_WITH_SFX = { "glitch": "Glitch_Transitions", "light_leak": "No_need", "Dissolve": "Warp_Transitions", "SlidingDoors": "Warp_Transitions", 
                    "LinearWipe": "Warp_Transitions", "CircularWipe": "Animating_Effects", "Pan": "Animating_Effects" }    
    # Adjust the loop to stop before the last segment to avoid index out of range error when checking the next segment
    for i in range(1, len(segments["segments"]) - 1):  
        current_segment = segments["segments"][i]
        previous_segment = segments["segments"][i-1]
        next_segment = segments["segments"][i+1]

        # Check conditions for triggering transition1.. check previous segment's motionbg = False
        if current_segment.get("brolls_on", False) and not previous_segment.get("motionbg", False):
            transition_type = random.choice(list(TRANSITIONS_TYPE_WITH_SFX.keys()))
            current_segment["transition1_sfx"] = True

            # Assign the transition effect based on the transition type
            if transition_type == "light_leak":
                transition_lightLeak_with_sfx = random.choice(transition_lightLeaks_dataset["Transition_Light_Leaks"])
                current_segment["transition1_effect_with_sfx_uri"] = transition_lightLeak_with_sfx
            else:
                predicted_sfx = TRANSITIONS_TYPE_WITH_SFX[transition_type]
                transition_sfx_uris = soundSFX_dataset.get(predicted_sfx, {}).get("Blob_URL", [])
                if transition_sfx_uris:
                    current_segment["transition1_sfx_uri"] = random.choice(transition_sfx_uris)
                else:
                    # Handle case where there is no SFX URI available
                    current_segment["transition1_sfx_uri"] = ""

            # Update the segment with the transition details
            current_segment["transition1Effect_type"] = transition_type
            current_segment["transition1SFX_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
            current_segment["transition1_start"] = current_segment["start"] - 0.10
            current_segment["transition1_end"] = current_segment["start"] + 0.15
        
        else:
            # Condition not met, ensure 'transition1_sfx' is not mistakenly set
            current_segment["transition1_sfx"] = False
        
        # New check for transition2: Only if the next segment's motionbg is False
        if allow_ending_transition:
            if current_segment.get("brolls_on", False) and not next_segment.get("motionbg", False):
                transition_type = random.choice(list(TRANSITIONS_TYPE_WITH_SFX.keys()))
                current_segment["transition2_sfx"] = True

                # Logic for choosing transition2 effect is similar to transition1
                if transition_type == "light_leak":
                    transition_lightLeak_with_sfx = random.choice(transition_lightLeaks_dataset["Transition_Light_Leaks"])
                    current_segment["transition2_effect_with_sfx_uri"] = transition_lightLeak_with_sfx
                else:
                    predicted_sfx = TRANSITIONS_TYPE_WITH_SFX[transition_type]
                    transition_sfx_uris = soundSFX_dataset.get(predicted_sfx, {}).get("Blob_URL", [])
                    if transition_sfx_uris:
                        current_segment["transition2_sfx_uri"] = random.choice(transition_sfx_uris)
                    else:
                        current_segment["transition2_sfx_uri"] = ""
                
                # Update the segment with the additional transition2 details
                current_segment["transition2Effect_type"] = transition_type
                current_segment["transition2SFX_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
                current_segment["transition2_start"] = current_segment["brolls_end_time"]
                current_segment["transition2_end"] = current_segment["brolls_end_time"] + 0.20
            else:
                # Condition not met for transition2, ensure 'transition2_sfx' and related properties are not mistakenly set
                current_segment["transition2_sfx"] = False
                # Optionally, clear any transition2-related properties

    return segments

## Original code: it only triggers transition effect on the start of motionbg segment. 
# def update_trimmed_segments_with_MotionbgTransitions(trimmed_segments, soundSFX_dataset, transition_lightleaks_dataset):
#     last_motionbg_segment = None
#     for segment in trimmed_segments["Trimmed_segments"]:
#         motionbg_segment = segment.get("motionbg_segment")

#         if motionbg_segment is not None and motionbg_segment != last_motionbg_segment:
#             transition_type = random.choice(list(TRANSITIONS_TYPE_WITH_SFX.keys()))

#             # Assign transition SFX only to the first segment of the changed motionbg_segment
#             if transition_type == "light_leak":
#                 transition_lightLeak_with_sfx = random.choice(transition_lightleaks_dataset["Transition_Light_Leaks"])
#                 segment["transition1_sfx"] = True
#                 segment["transition1_effect_with_sfx_uri"] = transition_lightLeak_with_sfx
#                 # segment["transition_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
#                 segment["transition1Effect_type"] = transition_type
#                 segment["transition1SFX_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
#                 segment["transition1_start"] = segment["start"] - 0.10
#                 segment["transition1_end"] = 0.15  # Assuming this is a constant value you wanted to set
#             else:
#                 transition_sfx_uris = soundSFX_dataset.get(TRANSITIONS_TYPE_WITH_SFX[transition_type], {}).get("Blob_URL", [])
#                 if transition_sfx_uris:
#                     segment["transition1_sfx"] = True
#                     segment["transition1_sfx_uri"] = random.choice(transition_sfx_uris)
#                     # segment["transition_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
#                     segment["transition1Effect_type"] = transition_type
#                     segment["transition1SFX_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
#                     segment["transition1_start"] = segment["start"] - 0.10
#                     segment["transition1_end"] = segment["start"] + 0.10   # Assuming this is a constant value you wanted to set
#                 else:
#                     segment["transition1_sfx"] = False
#                     segment["transition1_sfx_uri"] = ""

#         last_motionbg_segment = motionbg_segment

#     return trimmed_segments

### Here we are performing transition at the start of motionbg and also there is transition at the end of motionbg..
# provided that there is no brolls_on = True after the motionbg. 
def update_trimmed_segments_with_MotionbgTransitions(trimmed_segments, soundSFX_dataset, transition_lightleaks_dataset):
    last_motionbg_segment = None

    # Iterate over all segments to apply transitions based on motionbg_segment changes
    for i, segment in enumerate(trimmed_segments["Trimmed_segments"]):
        motionbg_segment = segment.get("motionbg_segment")

        if motionbg_segment is not None:
            if motionbg_segment != last_motionbg_segment:
                # Apply transition1 at the start of a new motionbg_segment group
                apply_transition1_to_motionBG_segment(segment, soundSFX_dataset, transition_lightleaks_dataset)

            if i == len(trimmed_segments["Trimmed_segments"]) - 1 or trimmed_segments["Trimmed_segments"][i + 1].get("motionbg_segment") != motionbg_segment:
                # Apply transition2 at the end of a motionbg_segment group or on the last segment
                apply_transition2_to_motionBG_segment(segment, soundSFX_dataset, transition_lightleaks_dataset)

            last_motionbg_segment = motionbg_segment

    return trimmed_segments

def apply_transition1_to_motionBG_segment(segment, soundSFX_dataset, transition_lightleaks_dataset):
    TRANSITIONS_TYPE_WITH_SFX = { "glitch": "Glitch_Transitions", "light_leak": "No_need", "Dissolve": "Warp_Transitions", "SlidingDoors": "Warp_Transitions", 
                    "LinearWipe": "Warp_Transitions", "CircularWipe": "Animating_Effects", "Pan": "Animating_Effects" }
    
    transition_type = random.choice(list(TRANSITIONS_TYPE_WITH_SFX.keys()))
    segment["transition1_sfx"] = True
    # Logic for transition1 effect
    if transition_type == "light_leak":
        transition_lightLeak_with_sfx = random.choice(transition_lightleaks_dataset["Transition_Light_Leaks"])
        segment["transition1_effect_with_sfx_uri"] = transition_lightLeak_with_sfx
    else:
        transition_sfx_uris = soundSFX_dataset.get(TRANSITIONS_TYPE_WITH_SFX[transition_type], {}).get("Blob_URL", [])
        segment["transition1_sfx_uri"] = random.choice(transition_sfx_uris) if transition_sfx_uris else ""

    segment["transition1Effect_type"] = transition_type
    segment["transition1SFX_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
    segment["transition1_start"] = segment["start"] - 0.10
    segment["transition1_end"] = segment["start"] + 0.15

def apply_transition2_to_motionBG_segment(segment, soundSFX_dataset, transition_lightleaks_dataset):
    TRANSITIONS_TYPE_WITH_SFX = { "glitch": "Glitch_Transitions", "light_leak": "No_need", "Dissolve": "Warp_Transitions", "SlidingDoors": "Warp_Transitions", 
                    "LinearWipe": "Warp_Transitions", "CircularWipe": "Animating_Effects", "Pan": "Animating_Effects" }
    transition_type = random.choice(list(TRANSITIONS_TYPE_WITH_SFX.keys()))
    segment["transition2_sfx"] = True
    # Logic for transition2 effect, similar to transition1
    if transition_type == "light_leak":
        transition_lightLeak_with_sfx = random.choice(transition_lightleaks_dataset["Transition_Light_Leaks"])
        segment["transition2_effect_with_sfx_uri"] = transition_lightLeak_with_sfx
    else:
        transition_sfx_uris = soundSFX_dataset.get(TRANSITIONS_TYPE_WITH_SFX[transition_type], {}).get("Blob_URL", [])
        segment["transition2_sfx_uri"] = random.choice(transition_sfx_uris) if transition_sfx_uris else ""

    segment["transition2Effect_type"] = transition_type
    segment["transition2SFX_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
    segment["transition2_start"] = segment["end"]
    segment["transition2_end"] = segment["end"] + 0.15

##############################################################################################
###### Function for applying Sound effects on Gifs in motionbg screen ########
def update_GIFsegments_with_AnimationSFX(trimmed_segments, soundSFX_dataset):
    # Animating Effects SFX URIs
    animating_effects_uris = soundSFX_dataset["Animating_Effects"]["Blob_URL"]
    current_motionbg_segment = None
    segment_indexes = []

    for i, segment in enumerate(trimmed_segments["Trimmed_segments"]):
        motionbg_segment = segment.get("motionbg_segment")

        # Detect a new motionbg_segment group or the last segment in the list
        if motionbg_segment != current_motionbg_segment or i == len(trimmed_segments["Trimmed_segments"]) - 1:
            # Skip the first and last segments of the previous group
            if len(segment_indexes) > 2:  # Ensure there are more than two segments, to skip first and last
                for index in segment_indexes[1:-1]:  # Skip the first and last index
                    apply_animation_sfx(trimmed_segments["Trimmed_segments"][index], animating_effects_uris)

            current_motionbg_segment = motionbg_segment
            segment_indexes = [i]  # Start a new group with the current segment
        else:
            segment_indexes.append(i)

    # Ensure the last motionbg_segment group is also processed
    if len(segment_indexes) > 2:  # Check again for the last group after the loop
        for index in segment_indexes[1:-1]:
            apply_animation_sfx(trimmed_segments["Trimmed_segments"][index], animating_effects_uris)

    return trimmed_segments

def apply_animation_sfx(segment, sfx_uris):
    # Apply animation SFX to a segment if 'gifs_on' is True
    if segment.get("gifs_on", False):
        segment["animation_sfx"] = True
        segment["animation_sfx_uri"] = random.choice(sfx_uris)
        segment["animation_sfx_start"] = segment["start"]
        segment["animation_sfx_end"] = segment["start"] + 0.10

##################### Apply background Music ########################################
def apply_background_music(segments, background_Music_dataset):
    # Flatten the list of Blob_URLs from all items in the dataset
    background_music_uris = background_Music_dataset.get("Forever_Green_Music", [{}])[0].get("Blob_URL", [])

    if background_music_uris:
        background_music_uri = random.choice(background_music_uris)
        # Update the segments with the background music URI
        for segment in segments["segments"]:
            segment["background_music_on"] = True
            segment["background_music_uri"] = background_music_uri
    else:
        # No background music available, update all segments accordingly
        for segment in segments["segments"]:
            segment["background_music_on"] = False
            segment["background_music_uri"] = ""

    return segments

def save_json_file(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    return 200

### MAin function
def main_apply_sound_effects(input_3words_json_path, main_json_file, output_json_path, embedding_model):
    try:
        client = QdrantClient("localhost", port=6333)
        collection_name = "aistudio_keywords_sfx"
        
        keywords_sfx_dataset_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/Keywords_soundhooks_SFX.json"
        
        # Load the JSON file
        segments_3word_data = load_json_file(input_3words_json_path)
        keyword_SFX_dataset = load_json_file(keywords_sfx_dataset_path)

        # Prepare data for embedding
        prepared_soundSFX_data = prepare_soundSFX_dataset_for_embedding(keyword_SFX_dataset)
        # Calculate dataset embeddings
        soundSFX_embeddings = calculate_dataset_embeddings(prepared_soundSFX_data, embedding_model, client, collection_name)
        # calculate_dataset_embeddings optional, because we have already done dataset embedding calculations in another file. 
        updated_segments_data = update_with_soundSFX(segments_3word_data, embedding_model, client, collection_name, desired_skip_segments=3)

        keyword_soundSFX = {"keyword_soundSFX" : updated_segments_data}
        
        # open json file
        # output_file_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_combined.json'
        soundSFX_output = load_json_file(output_json_path)

        # update the json file
        soundSFX_output.update(keyword_soundSFX)
        combined_data = soundSFX_output
        
        status = save_json_file(output_json_path, combined_data)
        
        ########################### applying transition hooks ##############################
        # main_file = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_combined.json"
        # output_file_transition = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words_test.json"
        transition_lightleaks_dataset_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/transitions_lightleaks_dataset.json"
        background_music_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/music_tracks_with_blob_urls.json"
        transitionSFX_dataset = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/transitions_hooks_sfx.json"
        jsonMainFile = load_json_file(main_json_file)
        transitionSFX_dataset_loaded = load_json_file(transitionSFX_dataset)
        transition_lightleaks_dataset = load_json_file(transition_lightleaks_dataset_path)
        background_music_dataset = load_json_file(background_music_path)

        transition_data = update_segments_with_BrollTransitions(jsonMainFile, transitionSFX_dataset_loaded, transition_lightleaks_dataset, allow_ending_transition=True)
        transition_data2 = update_trimmed_segments_with_MotionbgTransitions(transition_data, transitionSFX_dataset_loaded, transition_lightleaks_dataset)
        #### Animation SFX on GIFs in motionbg screen ####
        transition_data3 = update_GIFsegments_with_AnimationSFX(transition_data2, transitionSFX_dataset_loaded)

        #### Applying background music ####
        segment_data4 = apply_background_music(transition_data3, background_music_dataset)
        status = save_json_file(output_json_path, segment_data4)
        print("All files updated successfully")
        return (200, segment_data4)
    
    except Exception as e:
        print("Error in applying transition hooks sfx: ", e)
        return (500, None)

    
# def update_trimmed_segments_with_MotionbgTransitions(trimmed_segments, soundSFX_dataset, transition_lightleaks_dataset):
#     last_motionbg_segment = None
#     for segment in trimmed_segments["Trimmed_segments"]:
#         motionbg_segment = segment.get("motionbg_segment")

#         if motionbg_segment is not None and motionbg_segment != last_motionbg_segment:
#             transition_type = random.choice(list(TRANSITIONS_TYPE_WITH_SFX.keys()))

#             # Assign transition SFX only to the first segment of the changed motionbg_segment
#             if transition_type == "light_leak":
#                 transition_lightLeak_with_sfx = random.choice(transition_lightleaks_dataset["Transition_Light_Leaks"])
#                 segment["transition1_sfx"] = True
#                 segment["transition1_effect_with_sfx_uri"] = transition_lightLeak_with_sfx
#                 # segment["transition_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
#                 segment["transition1Effect_type"] = transition_type
#                 segment["transition1SFX_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
#                 segment["transition1_start"] = segment["start"] - 0.10
#                 segment["transition1_end"] = 0.15  # Assuming this is a constant value you wanted to set
#             else:
#                 transition_sfx_uris = soundSFX_dataset.get(TRANSITIONS_TYPE_WITH_SFX[transition_type], {}).get("Blob_URL", [])
#                 if transition_sfx_uris:
#                     segment["transition1_sfx"] = True
#                     segment["transition1_sfx_uri"] = random.choice(transition_sfx_uris)
#                     # segment["transition_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
#                     segment["transition1Effect_type"] = transition_type
#                     segment["transition1SFX_type"] = TRANSITIONS_TYPE_WITH_SFX[transition_type]
#                     segment["transition1_start"] = segment["start"] - 0.10
#                     segment["transition1_end"] = segment["start"] + 0.10   # Assuming this is a constant value you wanted to set
#                 else:
#                     segment["transition1_sfx"] = False
#                     segment["transition1_sfx_uri"] = ""

#         last_motionbg_segment = motionbg_segment

#     return trimmed_segments



# Function to find the closest B-roll footage based on cosine similarity
# def find_closest_overlays(inputText_embedding, prepared_data, embeddings):
#     max_similarity = -1
#     closest_match = None
#     for (key, text, urls), embedding in zip(prepared_data, embeddings):
#         similarity = util.pytorch_cos_sim(inputText_embedding, embedding)
#         if similarity > max_similarity:
#             max_similarity = similarity
#             # Choose between portrait and landscape based on your need here
#             # selected_url = portrait_url if is_portrait else landscape_url
#             selected_url_random = random.choice(urls) # custom 
#             closest_match = (key, selected_url_random, similarity.item())
#     return closest_match

# def update_with_overlays(inputData, model, prepared_overlays_data, overlays_embeddings):
#     for segment in inputData["segments"]:
#         # Determine if the segment's predicted emotion is neutral
        
#         # Convert segment's text to embeddings if emotion is neutral
#         inputText_embedding = input_text_embedding(segment["text"], model)
        
#         # Find the closest light leak match
#         closest_match = find_closest_overlays(inputText_embedding, prepared_overlays_data, overlays_embeddings)

#         # Update the segment based on whether a close match was found
#         if closest_match and closest_match[2] > 0.58:  # Assume closest_match[2] is the similarity score
#             segment["overlays_on"] = True
#             segment["overlay_confidence_score"] = closest_match[2]
#             segment["overlays_uri"] = closest_match[1]  # Assuming the URI is at position 1
#             segment["overlays_start_time"] = segment["start"]
#             segment["overlays_end_time"] = segment["end"]
#         else:
#             segment["overlays_on"] = False
#             segment["overlay_confidence_score"] = 0
#             segment["overlays_uri"] = ""  # No URI since no match was found
#             segment["overlays_start_time"] = None
#             segment["overlays_end_time"] = None
    
#     return inputData

##############################################################################################
################# test the functions ############################

# if __name__ == "__main__":
#     # Load the client
#     client = QdrantClient("localhost", port=6333)
#     collection_name = "aistudio_keywords_sfx"
        

#     ## load the data
#     inputData_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/data"
#     dataset_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data"
#     sound_dataset = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/Keywords_soundhooks_SFX.json"
#     transitionSFX_dataset = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/transitions_hooks_sfx.json"
#     file_name = "steve_3words.json"
#     file_path = os.path.join(inputData_folder, file_name)

#     # Load the JSON file
#     segments_data = load_json_file(file_path)
#     soundSFX_dataset = load_json_file(sound_dataset)

#     # Prepare data for embedding
#     prepared_soundSFX_data = prepare_soundSFX_dataset_for_embedding(soundSFX_dataset)

#     # loading embedding model
#     model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True, device="cpu")

#     # Calculate dataset embeddings
#     # soundSFX_embeddings = calculate_dataset_embeddings(prepared_soundSFX_data, model)
#     soundSFX_embeddings = calculate_dataset_embeddings(prepared_soundSFX_data, model, client, collection_name) # optional, 
#     # because we have already done dataset embedding calculations in another file. 

#     updated_segments_data = update_with_soundSFX(segments_data, model, client, collection_name, desired_skip_segments=3)

#     keyword_soundSFX = {"keyword_soundSFX" : updated_segments_data}

#     # open json file
#     # output_file_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words_test.json'
#     output_file_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_combined.json'
#     soundSFX_output = load_json_file(output_file_path)

#     # update the json file
#     soundSFX_output.update(keyword_soundSFX)
#     combined_data = soundSFX_output

#     # Write the updated data back to a JSON file
#     with open(output_file_path, 'w') as f:
#         json.dump(combined_data, f, indent=4)

#     print(f"Updated data has been written to {output_file_path}")

#     ########################### applying transition hooks ##############################
#     main_file = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_combined.json"
#     output_file_transition = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words_test.json"
#     transition_lightleaks_dataset_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/transitions_lightleaks_dataset.json"
#     background_music_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/music_tracks_with_blob_urls.json"
#     jsonMainFile = load_json_file(main_file)
#     transitionSFX_dataset_loaded = load_json_file(transitionSFX_dataset)
#     transition_lightleaks_dataset = load_json_file(transition_lightleaks_dataset_path)
#     background_music_dataset = load_json_file(background_music_path)

#     transition_data = update_segments_with_BrollTransitions(jsonMainFile, transitionSFX_dataset_loaded, transition_lightleaks_dataset, allow_ending_transition=True)
#     transition_data2 = update_trimmed_segments_with_MotionbgTransitions(transition_data, transitionSFX_dataset_loaded, transition_lightleaks_dataset)
#     #### Animation SFX on GIFs in motionbg screen ####
#     transition_data3 = update_GIFsegments_with_AnimationSFX(transition_data2, transitionSFX_dataset_loaded)

#     #### Applying background music ####
#     segment_data4 = apply_background_music(transition_data3, background_music_dataset)
#     with open(output_file_transition, 'w') as f:
#         json.dump(segment_data4, f, indent=4)

#     print("All files updated successfully")












# trigger on segments (3 words ) 
# trigger on transitions of scenes
# if any emoji are moving meaning gifs then we can trigger on that as well sound effect. 
# trigger on the gifs when we are in motion background screen. 1st element with sound, 2nd element with sound, 3rd with sound
# they all disappear with sound. 
# in the motion background screen, we remove gifs after 3 segments, for every segment we predict gif on diff positions
# for 3 segments and then after 3rd segment we remove all gifs with sound effect. 

# we will save 3 words segment hooks at the end of 8words json file. 

# finally we will apply music









