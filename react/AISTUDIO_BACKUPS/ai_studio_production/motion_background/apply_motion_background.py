# "https://transpifyblob.blob.core.windows.net/aistudio-v2/Motion_Backgrounds/Love/portrait/portrait%20%28211%29.mp4?se=2200-07-11T16%3A51%3A04Z&sp=r&sv=2023-01-03&sr=b&sig=R6ZpOMRFlI3qlcXcCxWq/vzrJOJOrvjt%2BxEU7BXTuSY%3D" 

## This file will discard motion background where we have emotions like sadness, disappointment, amusement, excitement, joy, surprise predicted.
import json, os
import random
# from python import diarize_speakers
from motion_background import diarize_speakers

# from sentence_transformers import SentenceTransformer, util

def load_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def get_motion_background(motionbg_data):
    prepared_data = []
    for key, value in motionbg_data.items():
        bg_urls = value['Blob_URL']
        selected_url_random = random.choice(bg_urls)
        prepared_data.append(selected_url_random)
    return prepared_data



def write_json_with_speakers(input_json, audio_file, output_file):
    # audio_file = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_orig.mp4"
    # audio_file = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/tate_pier.mp4"
    output = diarize_speakers.diarize_speakers(audio_file, input_json, output_file)
    return output

# Working: This is for including last segment in motion background overlay
# def apply_motion_bg(segments, motion_bg_data, is_portrait=True):
#     # Determine orientation based on is_portrait flag
#     orientation = 'Portrait' if is_portrait else 'Landscape'

#     # Total number of segments
#     total_segments = len(segments)
#     print("total_segments: ", total_segments)

#     # Set all segments 'motion_bg' to False initially
#     for segment in segments:
#         segment['motion_bg'] = False
#         segment['motion_bg_uri'] = ''

#     # Select a random motion background URI from the appropriate category
#     random_motion_bg_uris = motion_bg_data[orientation]['Blob_URL'] if motion_bg_data[orientation]['Blob_URL'] else []
#     if not random_motion_bg_uris:
#         print("No motion background data found.")

    
#     all_segments_with_2_stops = {}
#     segment_group_id = 1
#     i = 0
#     while i < total_segments:
#         if segments[i]['text'].strip().endswith('.'):
#             # Start a new group for segments ending with a full stop
#             segment_group = [segments[i]["text"]]  # Start with the current segment
#             full_stops_found = 0  # We've found one full stop already

#             # Look ahead for the next two full stops
#             for j in range(i + 1, total_segments):
#                 segment_group.append(segments[j]["text"])  # Add segment to the group
#                 if segments[j]['text'].strip().endswith('.'):
#                     full_stops_found += 1
#                     if full_stops_found == 2:
#                         # Stop if two full stops are found
#                         break
            
#             # Store the group
#             all_segments_with_2_stops[str(segment_group_id)] = segment_group
#             segment_group_id += 1

#             # Move to the segment after this group
#             i = j + 1
#         else:
#             # Move to the next segment if this one doesn't end with a full stop
#             i += 1

#     return segments, all_segments_with_2_stops
    
# working v2: this is for exlcuding last segment in motion background overlay
def apply_motion_bg(segments, motion_bg_data, is_portrait=True):
    orientation = 'Portrait' if is_portrait else 'Landscape'
    total_segments = len(segments)
    print("total_segments: ", total_segments)

    for segment in segments:
        segment['motionbg'] = False
        segment['motionbg_uri'] = ''

    random_motion_bg_uris = motion_bg_data[orientation]['Blob_URL'] if motion_bg_data[orientation]['Blob_URL'] else []
    if not random_motion_bg_uris:
        print("No motion background data found.")

    all_segments_with_2_stops = {}
    segment_group_id = 1
    i = 0
    while i < total_segments - 1:  # Adjusted to stop 1 segment before the end
        if segments[i]['text'].strip().endswith('.'):
            segment_group = [segments[i]["text"]]
            full_stops_found = 1  # Start counting from the current segment

            for j in range(i + 1, total_segments):
                segment_group.append(segments[j]["text"])
                if segments[j]['text'].strip().endswith('.'):
                    full_stops_found += 1
                    if full_stops_found == 3:
                        break
            
            # Check if the group completes three sentences before adding
            if full_stops_found == 3:
                all_segments_with_2_stops[str(segment_group_id)] = segment_group
                segment_group_id += 1

            i = j + 1
        else:
            i += 1

    return segments, all_segments_with_2_stops
    

def associate_speakers_times_emotions_with_sequences(segment_groups, original_segments):
    speaker_sequences = {}
    time_differences = {}
    predicted_emotions = {}

    for group_id, texts in segment_groups.items():
        # Find the start index of the group in the original segments
        start_index = next((i for i, segment in enumerate(original_segments) if texts[0].strip() in segment['text']), None)
        
        if start_index is not None and "speaker" in original_segments[start_index]:
            # Calculate the end index based on the number of texts in the group
            end_index = start_index + len(texts) - 1
            end_index = min(end_index, len(original_segments) - 1)

            speaker_sequence = []
            time_difference_sequence = []
            emotion_sequence = []

            # Iterate through the segments in the group
            for i in range(start_index, end_index + 1):
                if "speaker" in original_segments[i]:
                    speaker_sequence.append(original_segments[i]['speaker'])

                    # Calculate time differences except for the last element in the group
                    if i < end_index:
                        time_diff = original_segments[i + 1]['start'] - original_segments[i]['end']
                        time_difference_sequence.append(abs(time_diff))
                    else:
                        # For the last segment, use its start time as you mentioned
                        time_difference_sequence.append(original_segments[i]['start'])

                    # Capture predicted emotion for each segment
                    if "predicted_emotion" in original_segments[i]:
                        emotion_sequence.append(original_segments[i]['predicted_emotion'])
                else:
                    print(f"Speaker or emotion info missing for segment {i}")
                    continue

            if speaker_sequence:
                speaker_sequences[group_id] = speaker_sequence
                time_differences[group_id] = time_difference_sequence
                predicted_emotions[group_id] = emotion_sequence
        else:
            print(f"Start text from group {group_id} not found in original segments or speaker info missing")

    return speaker_sequences, time_differences, predicted_emotions


def check_conditions_for_motion_bg(speaker_sequences, predicted_emotions, time_differences, segment_groups):
    eligible_for_motion_bg = {}

    for group_id in speaker_sequences.keys():
        # Check if all speakers are the same in the sequence
        if all(speaker == speaker_sequences[group_id][0] for speaker in speaker_sequences[group_id]):
            # Check if the list does not contain certain emotions
            if not any(emotion in ["sadness", "disappointment", "amusement", "excitement", "joy", "surprise"] for emotion in predicted_emotions[group_id]):
                # Now checking the first element in the time differences list to see if it's greater than 0.5
                if group_id in time_differences and time_differences[group_id] and time_differences[group_id][0] > 0.5:
                    eligible_for_motion_bg[group_id] = segment_groups[group_id]
                else:
                    print(f"Group {group_id} does not meet the time difference condition or lacks time differences data.")
            else:
                print(f"Group {group_id} contains ineligible emotions.")
        else:
            print(f"Group {group_id} does not have consistent speaker.")

    # Check if any group is eligible for motion background
    if eligible_for_motion_bg:
        return eligible_for_motion_bg
    else:
        return "Cannot apply motion background to any list."

def update_segments_with_motion_bg(original_segments, eligible_groups, motion_bg_data, is_portrait=True):
    # Determine the orientation for URI selection
    orientation_key = 'Portrait' if is_portrait else 'Landscape'
    motion_bg_uris = motion_bg_data[orientation_key]['Blob_URL']
    
    for group_id, texts in eligible_groups.items():
        # Choose a random motion background URI for this group
        motion_bg_uri = random.choice(motion_bg_uris)
        
        # Find the start index of the first text in the original segments
        start_text = texts[0].strip()
        start_index = next((i for i, segment in enumerate(original_segments) if start_text in segment['text']), None)
        
        if start_index is not None:
            # Skip the first element by starting from start_index + 1
            for i in range(1, len(texts)):  # Start from 1 to skip the first text
                if start_index + i < len(original_segments):
                    original_segments[start_index + i]['motionbg'] = True
                    original_segments[start_index + i]['motionbg_start'] = original_segments[start_index + i]["start"]
                    original_segments[start_index + i]['motionbg_end'] = original_segments[start_index + i]["end"]
                    original_segments[start_index + i]['motionbg_uri'] = motion_bg_uri
        else:
            print(f"Text '{start_text}' not found in original segments for group {group_id}.")
    
    return original_segments

def save_json_file(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    return 200

def main_apply_motionBG(input_json_path, video_file_path, diarized_output_path, output_json_path, 
                   motionbg_dataset_path, is_portrait=True):
    try:
        diarized_result = write_json_with_speakers(input_json_path, video_file_path, diarized_output_path)
        # Load the JSON file
        segments_data = load_json_file(diarized_output_path)
        motionbg_dataset = load_json_file(motionbg_dataset_path)
        
        # Set is_portrait to True if your video is in portrait mode, and False if it's in landscape mode
        updated_segments, segment_groups = apply_motion_bg(segments_data['segments'], motionbg_dataset, is_portrait)
        # updated_segments, segment_groups = apply_motion_bg(diarized_result['segments'], motionbg_dataset, is_portrait=True)
        
        # speaker_associations = associate_speakers_with_sequences(segment_groups, segments_data['segments'])
        speaker_sequences, time_differences, predicted_emotions = associate_speakers_times_emotions_with_sequences(segment_groups, segments_data['segments'])
        # print(speaker_associations)
        print("Speaker sequences:", speaker_sequences)
        print("Time differences:", time_differences)
        print("Predicted emotions:", predicted_emotions)    
        # Note: You should pass the dictionaries you obtained from your data processing steps.
        result = check_conditions_for_motion_bg(speaker_sequences, predicted_emotions, time_differences, segment_groups)
        print(result)
        
        eligible_groups = result
        updated_segments = update_segments_with_motion_bg(segments_data['segments'], eligible_groups, motionbg_dataset, is_portrait)
        # print(updated_segments)

        final_segments = {"segments": updated_segments}
        # output_json_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json'
        status = save_json_file(output_json_path, final_segments)
        return (200, final_segments)
    
    except Exception as e:
        print("Error in apply_motionBG: ", e)
        return (500, None)
    

############################################################################################################
########## Test the functions ##############

# if __name__ == "__main__":
#     ## load the data
#     inputData_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/data"
#     dataset_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data"
#     dataset = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/viral_motion_backgrounds.json"
#     outputfile_name = "steve_diarized.json"
#     inputfile_name = "steve_8words.json"
#     file_path = os.path.join(inputData_folder, inputfile_name)
#     output_file = os.path.join(inputData_folder, outputfile_name)

#     audio_file = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_orig.mp4"
#     # speaker diarization here. uncomment before running
#     result = write_json_with_speakers(file_path, audio_file, output_file)

#     # Load the JSON file
#     segments_data = load_json_file(output_file)
#     motionbg_dataset = load_json_file(dataset)

#     # Apply the function to predict motion background
#     # Set is_portrait to True if your video is in portrait mode, and False if it's in landscape mode
#     updated_segments, segment_groups = apply_motion_bg(segments_data['segments'], motionbg_dataset, is_portrait=False)

#     # speaker_associations = associate_speakers_with_sequences(segment_groups, segments_data['segments'])
#     speaker_sequences, time_differences, predicted_emotions = associate_speakers_times_emotions_with_sequences(segment_groups, segments_data['segments'])
#     # print(speaker_associations)
#     print("Speaker sequences:", speaker_sequences)
#     print("Time differences:", time_differences)
#     print("Predicted emotions:", predicted_emotions)

#     # print("Updated segments: ", updated_segments)
#     print("Segment groups: ", segment_groups)

#     # Note: You should pass the dictionaries you obtained from your data processing steps.
#     result = check_conditions_for_motion_bg(speaker_sequences, predicted_emotions, time_differences, segment_groups)
#     print(result)

#     eligible_groups = result
#     # Assuming `original_segments` is your list of segment dictionaries and `eligible_groups` is the dictionary returned by `check_conditions_for_motion_bg`
#     # Assuming `motion_bg_data` is loaded from your JSON file
#     # Update this call with actual data
#     updated_segments = update_segments_with_motion_bg(segments_data['segments'], eligible_groups, motionbg_dataset, is_portrait=True)
#     # print(updated_segments)

#     final_segments = {"segments": updated_segments}

#     output_file_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json'
#     status = save_json_file(output_file_path, final_segments)
















