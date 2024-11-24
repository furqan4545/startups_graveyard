import stable_whisper
from sentence_transformers import SentenceTransformer, util
import json, os
from Emotions_Filters import predict_emotions
from Emotions_Filters import apply_filters
from brolls import apply_brolls
from overlays import apply_overlays
from motion_background import apply_motion_background
from effects_combined import apply_zoom_broll_overlay_together
from motion_background import motionbg_template_with_speaker
from Sound_SFX import apply_SFX_hooks
import gc
import random


################# Predict Emotions  ##############
inputData_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/data"
dataset_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data"
file_name = "steve_orig.json"

file_path = os.path.join(inputData_folder, file_name)
output_3wordjson_path = os.path.join(inputData_folder, "steve_3words.json")
output_8wordjson_path = os.path.join(inputData_folder, "steve_8words.json")

status, text_with_emotions_3words, text_with_emotions_8words  = predict_emotions.main_predict_emotions(file_path, output_3wordjson_path, output_8wordjson_path)

if status != 200:
    print("Error in predicting emotions")
    exit()
    
############################################################################################################
################## Apply Filters ################

status, updated_data = apply_filters.main_apply_filters(input_json_path=output_8wordjson_path, output_json_path=output_8wordjson_path)
if status != 200:
    print("Error in applying filters")
    exit()

############################################################################################################
##################  Apply Brolls  ##################

## load the data
inputData_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/data"
dataset_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data"
broll_dataset = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/broll_dataset.json"
file_name = "steve_8words.json"
file_path = os.path.join(inputData_folder, file_name)
# loading embedding model
embedding_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True, device="cpu")
status, updated_segments_data = apply_brolls.main_apply_brolls(file_path, broll_dataset, embedding_model, file_path, is_portrait=False)
if status != 200:
    print("Error in applying filters")
    exit()

############################################################################################################
######################  Apply Overlays  ##################

overlay_dataset = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/overlays_dataset.json"
status, updated_segments_data = apply_overlays.main_apply_overlays(file_path, overlay_dataset, embedding_model, file_path)
if status != 200:
    print("Error in applying filters")
    exit()

############################################################################################################
##################  Apply motionbackground without filters  ##################
motionbg_dataset_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/viral_motion_backgrounds.json"
diarized_outputjson_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_diarized.json"
actual_input_json_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json"
output_json_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json"
video_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_orig.mp4"

status, updated_segments_data =apply_motion_background.main_apply_motionBG(actual_input_json_path, video_path,  
                                    diarized_outputjson_path, output_json_path, 
                                    motionbg_dataset_path, is_portrait=True)

if status != 200:
    print("Error in applying motion background")
    exit()
############################################################################################################
##################  Apply Zoom Broll Overlay All together Finalized  ##################
input_json_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json"
status, updated_segments = apply_zoom_broll_overlay_together.main_apply_zoom_brol_over(input_json_path, output_json_path, video_path)
if status != 200:
    print("Error in applying motion background")
    exit()
    
############################################################################################################
####################  Apply MotionBg Template 1 with segmented Speaker  ##################
input_json3words = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_3words.json"
input_json_8words = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json"
GIF_dataset_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data/GIFs_updated_dataset.json"
output_3words_json_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_3words.json"
# combined_output_json_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_combined.json"
combined_output_json_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json"

status, updated_data = motionbg_template_with_speaker.trigger_main_func_and_segmentation(input_json3words, 
                        input_json_8words, GIF_dataset_path, output_3words_json_path,
                        embedding_model, video_path, combined_output_json_path)

if status != 200:
    print("Error in applying motion background template with speaker")
    exit()

############################################################################################################
##################  Apply Keyword Based Sound SFX  ##################
input_3words_json_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_3words.json"
main_json_file = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json"
output_json_path = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json"

status, updated_segments = apply_SFX_hooks.main_apply_sound_effects( input_3words_json_path, main_json_file,
                                output_json_path, embedding_model )
if status != 200:
    print("Error in applying sound SFX")
    exit()


############################################################################################################
##################    ##################














