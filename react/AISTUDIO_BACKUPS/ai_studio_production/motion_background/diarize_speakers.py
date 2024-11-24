import whisperx
import gc 
import json


def diarize_speakers(audio_file, json_file, output_file, device = "cpu"):
    # 1. Load the audio file
    audio = whisperx.load_audio(audio_file)

    # 2. Diarize the speakers
    diarize_model = whisperx.DiarizationPipeline(use_auth_token="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", device=device)
    diarize_segments = diarize_model(audio)

    # 3. Assign speaker labels
    with open(json_file, "r") as f:
        result_pre = json.load(f)

    result = whisperx.assign_word_speakers(diarize_segments, result_pre)

    # 4. Save the result in json
    with open(output_file, "w") as f:
        json.dump(result, f)
        
    gc.collect()

    return result
  
  
# with open(json_file, "r") as f:
#     result_pre = json.load(f)

# # batch_size = 1 # reduce if low on GPU mem
# # compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)
# audio = whisperx.load_audio(audio_file)

# # 3. Assign speaker labels
# diarize_model = whisperx.DiarizationPipeline(use_auth_token="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", device=device)

# # add min/max number of speakers if known
# # diarize_segments = diarize_model(audio, num_speakers = 4)
# diarize_segments = diarize_model(audio)
# # diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)

# result = whisperx.assign_word_speakers(diarize_segments, result_pre)
# # print(diarize_segments)
# # print(result["segments"]) # segments are now assigned speaker IDs

# # save the result in json
# with open(json_file, "w") as f:
#   json.dump(result, f)


# audio_file = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/tate_pier.mp4"
# json_file = "/Users/top_g/Desktop/react/ai_studio_v3/public/data/tate_pier_diarized.json"

# result = diarize_speakers(audio_file, json_file)



