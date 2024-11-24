
import json, os
import random
from effects_combined import face_detect_production
# import face_detect_production # use for local testing

# load json data
def load_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

#### original working code: here we are allowing next segment to have motionbg and overlays. And also broll ends with segment time. 
# def trigger_broll_with_conditions(segments, skip_segments=2):
#     # Set brolls_on = False initially for all segments
#     for segment in segments:
#         segment['brolls_on'] = False

#     i = 3  # Start checking from the 4th segment
#     while i < len(segments) - 1:  # Skip the last segment in the check
#         segment = segments[i]
#         prev_motion_bg = [segments[j].get('motionbg', False) for j in range(max(0, i-2), i)]

#         # Condition 1: Unsuitable emotion or current motionbg = True
#         if segment.get('motionbg', False) or segment['predicted_emotion'] in ["sadness", "disappointment", "amusement", "excitement", "joy", "surprise"]:
#             segment['brolls_on'] = False
#             i += 1  # Move to the next segment

#         # Condition 2: Suitable for broll based on motionbg and emotion criteria
#         elif not any(prev_motion_bg) and not segment.get('motionbg', False):
#             segment['brolls_on'] = True
#             # i += 3  # Skip next 2 segments after triggering broll
#             i += skip_segments + 1  # Skip the specified number of segments after triggering broll

#         else:
#             i += 1  # Move to the next segment if none of the conditions met

#     return segments

# updated and make sure all brolls are 3s.. and there is no effect after broll, meaning no overlay, no motionbg. This is test code. 
# above code is more perfect. 
def trigger_broll_with_conditions(segments, skip_segments=2):
    # Set brolls_on = False initially for all segments
    for segment in segments:
        segment['brolls_on'] = False

    i = 3  # Start checking from the 4th segment
    while i < len(segments) - 1:  # Skip the last segment in the check
        segment = segments[i]
        prev_motion_bg = [segments[j].get('motionbg', False) for j in range(max(0, i-2), i)]
        
        # Checking the next segment for overlays_on and motionbg
        next_segment = segments[i + 1]  # Reference to the next segment
        next_segment_overlays_or_motionbg = next_segment.get('overlays_on', False) or next_segment.get('motionbg', False)
        
        # Condition 1: Unsuitable emotion or next segment's overlays_on/motionbg = True
        if (segment['predicted_emotion'] in ["sadness", "disappointment", "amusement", "excitement", "joy", "surprise"] or
                next_segment_overlays_or_motionbg):
            segment['brolls_on'] = False
            i += 1  # Move to the next segment

        # Condition 2: Suitable for broll based on motionbg and emotion criteria
        elif not any(prev_motion_bg) and not segment.get('motionbg', False):
            segment['brolls_on'] = True
            # i += 3  # Skip next 2 segments after triggering broll
            i += skip_segments + 1  # Skip the specified number of segments after triggering broll

        else:
            i += 1  # Move to the next segment if none of the conditions met

    return segments
  
# ORiginal working code. 
# def trigger_overlays_final(segments, overlay_trigger_per_minute=2):
#     # Calculate the number of overlays to trigger based on video length
#     video_length = segments[-1]['end']
#     total_overlays_to_trigger = int((video_length / 60) * overlay_trigger_per_minute)
    
#     if total_overlays_to_trigger == 0:
#         # Set overlays_on to False for all segments initially
#         for segment in segments:
#             segment['overlays_on'] = False
        
#         return segments
    
#     else:
#         # Filter segments based on conditions
#         eligible_segments = [
#             segment for segment in segments
#             if segment['overlay_confidence_score'] > 0
#             and not segment.get('motionbg', False)
#             and segment['predicted_emotion'] not in ["sadness", "disappointment", "amusement", "excitement", "joy", "surprise"]
#             and not segment.get('brolls_on', False)
#         ]

#         # Sort eligible segments by overlay_confidence_score, descending
#         eligible_segments.sort(key=lambda seg: seg['overlay_confidence_score'], reverse=True)

#         # Ensure we do not select more overlays than available eligible segments
#         overlays_to_trigger = min(total_overlays_to_trigger, len(eligible_segments))

#         # Select the top segments based on overlays_to_trigger
#         selected_segments = eligible_segments[:overlays_to_trigger]

#         # Set overlays_on to True for selected segments
#         for segment in selected_segments:
#             segment['overlays_on'] = True

#         return segments

def trigger_overlays_final(segments, overlay_trigger_per_minute=2):
    # Initialize variables to keep track of overlays count and the next time checkpoint
    current_time_checkpoint = 0
    overlays_count = 0
    video_length = segments[-1]['end'] if segments else 0
    
    # First, set overlays_on to False for all segments
    for segment in segments:
        segment['overlays_on'] = False
    
    # Filter eligible segments before sorting and applying logic
    eligible_segments = [
        segment for segment in segments
        if segment['overlay_confidence_score'] > 0
        and not segment.get('motionbg', False)
        and segment['predicted_emotion'] not in ["sadness", "disappointment", "amusement", "excitement", "joy", "surprise"]
        and not segment.get('brolls_on', False)
    ]
    # Sort eligible segments by overlay_confidence_score, descending
    eligible_segments.sort(key=lambda seg: seg['overlay_confidence_score'], reverse=True)

    for segment in eligible_segments:
        start_time = segment['start']
        
        # Check if current segment's start time has passed the next time checkpoint
        if start_time >= current_time_checkpoint:
            # Reset overlays count and update the next time checkpoint
            overlays_count = 0
            current_time_checkpoint += 60  # Move to the next 60 seconds window
        
        # Apply overlay if less than 2 overlays have been applied in the current window
        if overlays_count < overlay_trigger_per_minute:
            segment['overlays_on'] = True
            overlays_count += 1
        # Once two overlays are selected within 60 seconds, additional overlays won't be selected until the next window
        
        # Break the loop if the video length is covered
        if current_time_checkpoint >= video_length:
            break

    return segments




################ Zoom Feature #########

# Zoom effect types
# ZOOM_TYPES = [
#     "verySlowZoomIn", "verySlowZoomOut", "instantSharpZoomIn",
#     "instantSharpZoomOut", "instantZoomBlur", "instantZoomOutBlur",  "defaultZoomIn",
#     "defaultZoomOut"
# ]


# def combined_trigger_zoom_effects(segments, skip_after_zoom=2):
#     print("Combined trigger_zoom_effects")
#     apply_zoom_on_next_broll = True  # Flag to control zoom application on broll segments
#     last_motionbg_segment_index = None  # Track the index of the last segment with motionbg
#     skip_segments = 0  # Counter to manage when to skip checking for zoom conditions

    
#     # Define emotion to zoom effects mapping
#     EMOTION_ZOOM_EFFECTS = {
#         # Your emotion to zoom effects mapping
#     }
    
#     # Initialize the first segment with a random zoom effect if needed
#     segments[0].update({
#         "zoom_start": 0,
#         "zoom_end": 0.5,
#         "zoom_type": random.choice(["instantZoomBlur", "instantZoomOutBlur"]),
#         "zoom_on": True
#     })

#     i = 1  # Start from the first segment
#     while i < len(segments):
#         if skip_segments > 0:
#             skip_segments -= 1
#             i += 1
#             continue
    
#         segment = segments[i]
        
#         # Handle broll logic
#         if segment.get('brolls_on', False):
#             # if i + 1 < len(segments):  # Ensure there is a next segment to apply zoom
#             if apply_zoom_on_next_broll and i + 1 < len(segments):
#                 segments[i + 1].update({
#                     "zoom_start": segment['brolls_end_time'],
#                     "zoom_end": segments[i + 1]['end'],
#                     "zoom_type": random.choice(["verySlowZoomOut", "defaultZoomOut"]),
#                     "zoom_on": True
#                 })
#             apply_zoom_on_next_broll = not apply_zoom_on_next_broll  # Toggle the flag for the next broll segment

#         # Handling motionbg logic: apply zoom to the next segment after motionbg ends
#         if segment.get('motionbg', False):
#             last_motionbg_segment_index = i  # Record the index of the segment with motionbg
#         elif last_motionbg_segment_index is not None and (last_motionbg_segment_index + 1 == i):
#             # If the current segment is immediately after a segment with motionbg, apply zoom here
#             segment.update({
#                 "zoom_start": segments[last_motionbg_segment_index]['end'],
#                 "zoom_end": segment['end'],
#                 "zoom_type": "verySlowZoomOut",
#                 "zoom_on": True
#             })
#             last_motionbg_segment_index = None  # Reset after applying zoom

#         # # Skip segments if `brolls_on` or `motionbg` is True without applying any zoom effect
#         # if segment.get('brolls_on', False) or segment.get('motionbg', False):
#         #     i += skip_after_default  # Skip the next few segments as defined by `skip_after_default`
#         #     continue

#         # Apply zoom based on emotion if no broll or motionbg flags are active
#         if not segment.get('brolls_on', False) and not segment.get('motionbg', False) and segment['predicted_emotion'] in EMOTION_ZOOM_EFFECTS and not segment.get('zoom_on', False):
#             zoom_effect = random.choice(EMOTION_ZOOM_EFFECTS[segment['predicted_emotion']])
#             prev_segment = segments[i - 1]
#             zoom_start_time = prev_segment['brolls_end_time'] if prev_segment.get('brolls_on', False) else segment['start']
#             segment.update({
#                 # "zoom_start": segment['start'],
#                 "zoom_start": zoom_start_time,
#                 "zoom_end": segment['end'],
#                 "zoom_type": zoom_effect,
#                 "zoom_on": True
#             })
            
#             # Check and apply defaultZoomOut in the next segment if conditions allow
#             if i + 1 < len(segments):
#                 next_segment = segments[i + 1]
#                 prev_segment = segments[i]
#                 if not next_segment.get('brolls_on', False) and not next_segment.get('motionbg', False) and not next_segment.get('zoom_on', False):
#                     next_segment.update({
#                         "zoom_start": prev_segment['end'],
#                         "zoom_end": next_segment['end'],
#                         "zoom_type": "defaultZoomOut",
#                         "zoom_on": True
#                     })
#                     skip_segments = skip_after_zoom  # Ensure we skip after applying this pattern
#                 else:
#                     skip_segments = skip_after_zoom

#             # Skipping logic after applying an emotion-based zoom
#             # Adjust as necessary based on your logic

#         i += 1  # Proceed to the next segment

#     return segments


def combined_trigger_zoom_effects(segments, skip_after_zoom=2):
    print("Combined trigger_zoom_effects")
    apply_zoom_on_next_broll = True  # Flag to control zoom application on broll segments
    last_motionbg_segment_index = None  # Track the index of the last segment with motionbg
    skip_segments = 0  # Counter to manage when to skip checking for zoom conditions
    
    # iterate over segments and make zoom_on = false for all segments
    for segment in segments:
        segment['zoom_on'] = False

    
    # Define emotion to zoom effects mapping
    EMOTION_ZOOM_EFFECTS = {
        "sadness": ["instantSharpZoomIn", "defaultZoomIn"],
        "anger": ["instantSharpZoomIn", "defaultZoomIn"],
        "disappointment": ["instantSharpZoomIn", "instantSharpZoomIn", "instantSharpZoomIn", "defaultZoomIn"],
        "remorse": ["instantSharpZoomIn", "defaultZoomIn"],
        "embarrassment": ["verySlowZoomIn", "defaultZoomIn"],
        "disgust": ["verySlowZoomIn", "defaultZoomIn"],
        "disapproval": ["instantSharpZoomIn", "defaultZoomIn"],
        "desire": ["verySlowZoomIn"],
        "joy": ["verySlowZoomIn", "defaultZoomIn"],
        "surprise": ["instantSharpZoomIn", "defaultZoomIn"],
        "gratitude": ["defaultZoomIn", "verySlowZoomIn"],
        "fear": ["defaultZoomIn", "verySlowZoomIn"],
        "excitement": ["defaultZoomIn", "verySlowZoomIn"],
        "amusement": ["defaultZoomIn", "verySlowZoomIn"],
        "curiosity": ["verySlowZoomIn", "defaultZoomIn"],
        "annoyance": ["instantSharpZoomIn", "defaultZoomIn"],
        "neutral": ["defaultZoomIn", "verySlowZoomIn", "verySlowZoomIn", "verySlowZoomIn"],
    }
    
    # Initialize the first segment with a random zoom effect if needed
    segments[0].update({
        "zoom_start": 0,
        "zoom_end": 0.5,
        "zoom_type": random.choice(["instantZoomBlur", "instantZoomOutBlur"]),
        "zoom_on": True
    })

    i = 1  # Start from the second segment
    while i < len(segments):
        if skip_segments > 0:
            skip_segments -= 1
            i += 1
            continue
    
        segment = segments[i]
        zoom_applied = False  # Flag to indicate whether a zoom effect was applied in this iteration
        
        # Handle broll logic
        if segment.get('brolls_on', False) and not segment.get('zoom_on', False):
            # only YHA PROBLEM HAI, BAKI SET HAI OKKKK.. this get true and then we apply zoom on emotion also get true which overrides it.
            # Check emotions too k emotion sad ya disappointment na ho, vrna instant zoom trigger hoga broll k bad. ya phr we can keep the logic same. 
            if apply_zoom_on_next_broll and i + 1 < len(segments):
                segments[i + 1].update({
                    "zoom_start": segment['brolls_end_time'],
                    "zoom_end": segments[i + 1]['end'],
                    "zoom_type": random.choice(["verySlowZoomOut", "defaultZoomOut"]),
                    "zoom_on": True
                })
            apply_zoom_on_next_broll = not apply_zoom_on_next_broll  # Toggle the flag for the next broll segment
            # skip_segments = skip_after_zoom
            zoom_applied = True 

        # Handling motionbg logic: apply zoom to the next segment after motionbg ends
        if segment.get('motionbg', False) and not segment.get('zoom_on', False):
            last_motionbg_segment_index = i  # Record the index of the segment with motionbg
        elif last_motionbg_segment_index is not None and (last_motionbg_segment_index + 1 == i):
            # If the current segment is immediately after a segment with motionbg, apply zoom here
            segment.update({
                "zoom_start": segments[last_motionbg_segment_index]['end'],
                "zoom_end": segment['end'],
                "zoom_type": "verySlowZoomOut",
                "zoom_on": True
            })
            last_motionbg_segment_index = None  # Reset after applying zoom
            # skip_segments = skip_after_zoom
            zoom_applied = True

        # Apply zoom based on emotion if no broll or motionbg flags are active
        if not segment.get('brolls_on', False) and not segment.get('motionbg', False) and segment['predicted_emotion'] in EMOTION_ZOOM_EFFECTS and not segment.get('zoom_on', False):
            zoom_effect = random.choice(EMOTION_ZOOM_EFFECTS[segment['predicted_emotion']])
            prev_segment = segments[i - 1]
            next_segment = segments[i+1]
            zoom_start_time = prev_segment['brolls_end_time'] if prev_segment.get('brolls_on', False) else segment['start']
            segment.update({
                # "zoom_start": segment['start'],
                "zoom_start": zoom_start_time,
                # "zoom_end": segment['end'],
                "zoom_end": next_segment['start'],
                "zoom_type": zoom_effect,
                "zoom_on": True
            })
            
            # Check and apply defaultZoomOut in the next segment if conditions allow
            # here we have slight problem which is, here we only skip 1 segment after applying zoom. so, lets see if it is good. 
            if i + 1 < len(segments):
                next_segment = segments[i + 1]
                prev_segment = segments[i]
                # check if segments[i+2] is available or not.
                # next_next_segment = None
                # if i+2 <= len(segments):
                #     next_next_segment = segments[i + 2] # test code.
                # else:
                #     next_next_segment = segments[i + 1]
                if not next_segment.get('brolls_on', False) and not next_segment.get('motionbg', False) and not next_segment.get('zoom_on', False):
                    next_segment.update({
                        # "zoom_start": prev_segment['end'],
                        "zoom_start": prev_segment['zoom_end'], # test
                        # "zoom_end": next_next_segment['end'],  # we can change it in a way that it ends on next segment start time.
                        "zoom_end": next_segment['end'],
                        "zoom_type": "defaultZoomOut",
                        "zoom_on": True
                    })
                    # skip_segments = skip_after_zoom  # Ensure we skip after applying this pattern
                    zoom_applied = True
                else:
                    # skip_segments = skip_after_zoom
                    zoom_applied = True

        if zoom_applied:
            # If a zoom was applied for any reason, ensure we skip the next two segments
            skip_segments = skip_after_zoom

        i += 1  # Proceed to the next segment

    return segments



def save_json_file(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    return 200

############################
def main_apply_zoom_brol_over(input_json_path, json_output_path, video_file):
    try:
        # load data  
        segments_data = load_json_file(input_json_path)
        # And `broll_data` represents your available B-roll footage
        updated_segments = trigger_broll_with_conditions(segments_data["segments"], skip_segments=2)
        updated_segments2 = trigger_overlays_final(updated_segments, overlay_trigger_per_minute=2)
        # updated_segments3 = trigger_zoom_effects(segments_data["segments"], skip_after_zoom=2) # original working
        # updated_segments3 = trigger_zoom_effects(updated_segments2, skip_after_zoom=2) # test
        updated_segments3 = combined_trigger_zoom_effects(updated_segments2, skip_after_zoom=2)
        ##### apply face detection #### update here after lunch
        status, updated_segments4 = face_detect_production.detect_faces_with_checks(video_file, updated_segments3)
        if status != 200:
            print("Error in detect_faces")
            exit()
        final_segments = {"segments" : updated_segments4}
        
        status = save_json_file(json_output_path, final_segments)

        return (200, final_segments)
    
    except Exception as e:
        print("Error in main_apply_zoom_brol_over: ", e)
        return (500, None)


#################### Test the functions ####################
# if __name__ == "__main__":

#     ## load the data
#     inputData_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/data"

#     inputfile_name = "steve_8words.json"
#     # input_json = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json"
#     file_path = os.path.join(inputData_folder, inputfile_name)

#     video_file = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_orig.mp4"

#     # load data  
#     segments_data = load_json_file(file_path)

#     # Assuming `segments` is your list of dictionaries representing the video transcript segments
#     # And `broll_data` represents your available B-roll footage
#     updated_segments = trigger_broll_with_conditions(segments_data["segments"], skip_segments=2)

#     updated_segments2 = trigger_overlays_final(updated_segments, overlay_trigger_per_minute=2)

#     updated_segments3 = combined_trigger_zoom_effects(updated_segments2, skip_after_zoom=2)

#     ##### apply face detection #### update here after lunch
#     status, updated_segments4 = face_detect_production.detect_faces_with_checks(video_file, updated_segments3)
#     if status != 200:
#         print("Error in detect_faces")
#         exit()
#     ###############################

#     final_segments = {"segments" : updated_segments4}

#     # Write the updated data back to a JSON file
#     output_file_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words_test22.json'
    
#     status = save_json_file(output_file_path, final_segments)
    
    







  
  