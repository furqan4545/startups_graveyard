# with speaker segmented
# TODO: write the code for emoji on and off .. same for Gif on and off for specific segment.. 

from sentence_transformers import SentenceTransformer, util
import torch
import json, os
import spacy
# from datetime import datetime, timedelta
import re
import gc
import random
from urllib.parse import urlparse
from scrapper import ai_scrapper

# Function to replace names in a text segment with 'PERSON'
def replace_names(nlp, text):
    doc = nlp(text)
    new_text = text
    orig_name = ''
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            new_text = new_text.replace(ent.text, 'PERSON')
        if ent.text is not None:
            orig_name = ent.text
    return new_text, orig_name

def load_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def input_text_embedding(text, model):
    return model.encode(text)
  
def prepare_GIFs_dataset_for_embedding(gif_data):
    prepared_data = []
    for key, value in gif_data.items():
        # combined_text = 'search_document: ' + ' '.join(value['Keywords']) + ' ' + value['Description']
        combined_text = 'search_document: ' + ' '.join(value['Keywords'])
        # combined_text = ' '.join(value['Keywords'])
        prepared_data.append((key, combined_text, value['Blob_URL'], value['Position']))
    return prepared_data
  
# Function to calculate embeddings for the prepared data
def calculate_dataset_embeddings(prepared_data, model):
    sentences = [data[1] for data in prepared_data]
    embeddings = model.encode(sentences)
    return embeddings

# Function to find the closest B-roll footage based on cosine similarity
def find_closest_gifs(target_embedding, prepared_data, embeddings):
    max_similarity = -1
    closest_match = None
    for (key, text, url, position), embedding in zip(prepared_data, embeddings):
        similarity = util.pytorch_cos_sim(target_embedding, embedding)
        if similarity > max_similarity:
            max_similarity = similarity
            # Choose between portrait and landscape based on your need here
            selected_url_random = random.choice(url) # custom 
            closest_match = (key, selected_url_random, similarity.item(), position)
    return closest_match

def update_with_gifs(inputData, model, prepared_gifs_data, gifs_embeddings):
    for segment in inputData["segments"]:
        # Determine if the segment's predicted emotion is neutral
        
        # Convert segment's text to embeddings if emotion is neutral
        target_embedding = input_text_embedding(segment["text"], model)
        
        # Find the closest light leak match
        closest_match = find_closest_gifs(target_embedding, prepared_gifs_data, gifs_embeddings)
        
        ######## Finding person image if detected in the segment
        try:
          # Load the spaCy model for English
            nlp = spacy.load('en_core_web_sm')  
            text = segment['text']
            processed_text, original_name = replace_names(nlp, text)
            query = original_name
            type = "person"
            if query != '':
                result = ai_scrapper.scrapper_pipeline(query, type, "furqan", "06206327ce")
                if result:
                    segment["Person_imguri"] = result["image_url"]
                    del result
                    del nlp
                    gc.collect()
            else:
                segment["Person_imguri"] = ""
        except Exception as e:
            print("Error:", str(e))
        
        ##############################
        
        # Update the segment based on whether a close match was found
        if closest_match and closest_match[2] > 0.6:  # Assume closest_match[2] is the similarity score
            segment["gifs_on"] = True
            segment["gifs_position"] = closest_match[3]
            segment["gifs_uri"] = closest_match[1]  # Assuming the URI is at position 1
            segment["gifs_start_time"] = segment["start"]
            segment["gifs_end_time"] = segment["end"]
        else:
            segment["gifs_on"] = False
            segment["gifs_position"] = None
            segment["gifs_uri"] = ""  # No URI since no match was found
            segment["gifs_start_time"] = None
            segment["gifs_end_time"] = None
    
    return inputData
  

def filter_3words_segments(segments_8words, segments_3words):
    segments_8words_filtered = [seg for seg in segments_8words if seg.get("motionbg")]

    # Use a set to track unique combinations of start and end times of segments already added
    added_segments = set()
    filtered_3words_segments = []
    
    # Initialize variables for tracking motionbg_uri changes and segment numbering
    last_motionbg_uri = None
    motionbg_segment_number = 0
  
    for seg_8 in segments_8words_filtered:
        motionbg_start = seg_8["motionbg_start"]
        motionbg_end = seg_8["motionbg_end"]
        motionbg_uri = seg_8.get("motionbg_uri", "")

        # Check if the motionbg_uri has changed since the last segment
        if motionbg_uri != last_motionbg_uri:
            # If so, increment the segment number and update last_motionbg_uri
            motionbg_segment_number += 1
            last_motionbg_uri = motionbg_uri

        for seg_3 in segments_3words:
            # Create a unique key for the segment based on its start and end times
            seg_key = (seg_3["start"], seg_3["end"])

            if seg_3["start"] <= motionbg_end and seg_3["end"] >= motionbg_start and seg_key not in added_segments:
                # Update the segment with the motionbg_uri and motionbg_segment number before appending
                seg_3_updated = seg_3.copy()  # Make a copy to avoid modifying the original list's items
                seg_3_updated["motionbg_uri"] = motionbg_uri  # Add or update the motionbg_uri field
                seg_3_updated["motionbg_segment"] = motionbg_segment_number  # Assign the motionbg_segment number
                
                filtered_3words_segments.append(seg_3_updated)
                added_segments.add(seg_key)  # Mark this segment as added

    return filtered_3words_segments

def get_SpeakerSegmented_video(input_video_path, output_video_path, start_time, end_time):
    from video_segmentation import segmentation_parallel_production
    try:
        status = segmentation_parallel_production.process_video_background(input_video_path, output_video_path, start_time, end_time, processed_frames_dir='processed_frames', workers=4)
        if status != 200:
            print("Error processing video segment")
    except Exception as e:
        print("Error:", str(e))
        return 50
    return 200
  
def getStart_endTime_of_motionbg(filtered_segments):
    # Group segments by motionbg_segment number
    segment_groups = {}
    for segment in filtered_segments:
        segment_id = segment["motionbg_segment"]
        if segment_id not in segment_groups:
            segment_groups[segment_id] = []
        segment_groups[segment_id].append(segment)
    
    # Initialize timings dictionary
    timings = {}

    # Iterate through each group, setting start and end times
    for segment_id, segments in segment_groups.items():
        # Assuming segments are already in chronological order within each motionbg_segment
        timings[segment_id] = {
            "id": segment_id,
            "start": segments[0]["start"],  # First segment start time
            "end": segments[-1]["end"]     # Last segment end time
        }

    return timings
  
def main_workflow():
    ## load the data
    inputData_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/data"
    dataset_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data"
    dataset = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/GIFs_updated_dataset.json"
    input_video_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_orig.mp4"

    file_name = "steve_3words.json"
    file_path = os.path.join(inputData_folder, file_name)

    # Load the JSON file
    segments_data = load_json_file(file_path)
    gifs_dataset = load_json_file(dataset)

    # Prepare data for embedding
    prepared_gifs_data = prepare_GIFs_dataset_for_embedding(gifs_dataset)

    # loading embedding model
    model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True, device="cpu")

    # Calculate embeddings
    gifs_embeddings = calculate_dataset_embeddings(prepared_gifs_data, model)

    # Process segments (Change 'is_portrait' based on your video orientation)
    is_portrait = False  # or False for landscape
    updated_segments_data = update_with_gifs(segments_data, model, prepared_gifs_data, gifs_embeddings)

    # Write the updated data back to a JSON file
    output_file_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_3words.json'
    with open(output_file_path, 'w') as f:
      json.dump(updated_segments_data, f, indent=4)
    print(f"Updated data has been written to {output_file_path}")

    del model
    gc.collect()
    
    ###################################

    file_8words = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json"
    segment_8words = load_json_file(file_8words)

    # Now filter the 3words segments based on 8words criteria
    filtered_segments = filter_3words_segments(segment_8words["segments"], updated_segments_data["segments"])

    # del updated_segments_data
    # gc.collect()
    
    return filtered_segments, segment_8words
    

def trigger_segmentation(filtered_segments, segment_8words):
    input_video_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_orig.mp4"
    # Now segment out the video of speaker based on motionbg_segment id and time.

    # timings = getStart_endTime_of_motionbg(filtered_segments)
    # print("Timings:", timings)

    # for segment_id, segment_times in timings.items():
    #   start_time = segment_times['start']
    #   end_time = segment_times['end']
    #   output_video_path = f"/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_speaker_segmented{segment_id}.webm"
    #   res = get_SpeakerSegmented_video(input_video_path, output_video_path, start_time, end_time)
    #   if res == 200:
    #     print(f"Segment {segment_id} processed successfully")
    #   else:
    #     print(f"Error processing segment {segment_id}")

    # res = get_SpeakerSegmented_video(input_video_path, output_video_path, )

    # output_file_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words_test2.json'
    # with open(output_file_path, 'w') as f:
    #   json.dump(filtered_segments, f, indent=4)
      
    
    ########## Now combine both json files.. #####
    trim_segments = {"Trimmed_segments": filtered_segments}
    ### segment_8words["Trimmed_segments"] = filtered_segments
    
    # combined_data = segment_8words + trim_segments
    # combined_data = trim_segments
    segment_8words.update(trim_segments)
    combined_data = segment_8words
    
    combined_output_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_combined.json'
    # Write the combined data back to a new file (or overwrite an existing one)
    with open(combined_output_path, 'w') as f:
        json.dump(combined_data, f, indent=4)

    print(f"Combined data has been written to {combined_output_path}")
    
    
  
if __name__ == '__main__':
    filtered_segments, segment_8words = main_workflow()
    trigger_segmentation(filtered_segments, segment_8words)
    
    # after the video is segmented, we need to delete them later. 
    









