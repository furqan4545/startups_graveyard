import json, os
import random

def load_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def update_segments(data):
    sad_filters = ["grey", "halftone_grey"]
    sad_index = 0  # Index to keep track of the last assigned sad filter
    
    happy_filters = ["hue_filter"]
    surprise_filters = ["high_exposure"]
    
    for segment in data["segments"]:
        emotion = segment["predicted_emotion"].lower()
        
        # if emotion in ["sadness", "disappointment"]:
        #     segment["predicted_filter"] = random.choices(sad_filters, weights=[0.5, 0.5])[0]
        #     segment["filter_on"] = True
        if emotion in ["sadness", "disappointment"]:
            segment["predicted_filter"] = sad_filters[sad_index]
            segment["filter_on"] = True
            sad_index = (sad_index + 1) % len(sad_filters) 
        elif emotion in ["amusement", "joy"]:
            segment["predicted_filter"] = random.choice(happy_filters)
            segment["filter_on"] = True
        elif emotion in ["surprise", "excitement"]:
            segment["predicted_filter"] = random.choice(surprise_filters)
            segment["filter_on"] = True
        elif emotion not in ["sadness", "disappointment","amusement","excitement", "joy","surprise"]:
            segment["predicted_filter"] = None
            segment["filter_on"] = False
    
    return data


def save_json_file(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    return 200

def main_apply_filters(input_json_path="input_json_path", output_json_path="output_json_path"):
    try:
        loaded_data = load_json_file(input_json_path)
        updated_data = update_segments(loaded_data)
        status = save_json_file(output_json_path, updated_data)
        return (200, updated_data)
    except Exception as e:
        print("Error in main_apply_filters: ", e)
        return (500, None)
    
    

############## Test the functions ##############
# if __name__ == "__main__":      
#     inputData_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/data"
#     dataset_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data"
#     file_name = "steve_8words.json"
#     file_path = os.path.join(inputData_folder, file_name)

#     # Load the JSON file
#     data = load_json_file(file_path)

#     # Update the segments with predicted_filter and filter_on keys
#     updated_data = update_segments(data)

#     # Save the updated JSON file
#     output_file_path = os.path.join(inputData_folder, file_name)
#     save_json_file(output_file_path, updated_data)


