

from transformers import AutoTokenizer, pipeline
from optimum.onnxruntime import ORTModelForSequenceClassification
import stable_whisper
import json, os

def main_predict_emotions(json_input_path, json_output_path_3words, json_output_path_8words): 
    try:
        text_with_emotions_3words = get_emotion_words(json_input_path, json_output_path_3words, max_words=3)
        text_with_emotions_8words = get_emotion_words(json_input_path, json_output_path_8words, max_words=8)
        return (200, text_with_emotions_3words, text_with_emotions_8words)
    except Exception as e:
        print(f"Error from emotions: {e}")
        return (500, None, None)
    
def words_per_screen(transcribed_output, max_words: int):
    # result = (
    #     transcribed_output
    #     .clamp_max()
    #     .split_by_punctuation([('.', ' '), '。', '?', '?', (',', ' '), '.'])
    #     .split_by_gap(.5)
    #     .merge_by_gap(float(f".{max_words}"), max_words=max_words)
    #     .split_by_punctuation([('.', ' '), '。', '?', '？'])
    #     # .split_by_length(max_words=max_words, force_len=True)
    #     .split_by_length(max_words=max_words)
    # ) 
    result = (
        transcribed_output
        .clamp_max()
        .split_by_punctuation([(',', ' '), '，'])
        .split_by_gap(.5)
        .merge_by_gap(.5, max_words=max_words)
        .split_by_punctuation([('.', ' '), '。', '?', '？'])
        .split_by_length(max_words=max_words)
    )
    return result  

def load_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

    
def get_emotion_words(file_path, output_file_path, max_words=3):
    emotions_detail = {
        "desire": "expressing desire, showing hope, or expressing a wish",
        "disgust": "expressing strong dislike or disapproval or revulsion or repugnance",
        "fear": "expressing fear or anxiety or worry or concern or nervousness",
        "gratitude": "expressing gratitude or thankfulness or appreciation or thanks",
        "grief": "expressing grief or sadness or mourning or sorrow",
        "joy": "expressing joy, happiness, or delight",
        "love": "expressing love or affection or fondness or adoration or devotion",
        "surprise": "expressing surprise or amazement or astonishment or wonder",
        "anger": "expressing anger or rage or fury or wrath or indignation",
        "admiration": "expressing admiration or respect or esteem or regard or approval",
        "amusement": "expressing amusement or mirth or merriment or glee or joy or delight or pleasure or fun",
        "annoyance": "expressing annoyance or irritation or vexation or exasperation or displeasure or frustration",
        "approval": "expressing approval or acceptance or agreement or consent or assent or affirmation or endorsement or support",
        "caring": "expressing caring or concern or compassion or empathy or sympathy or understanding or kindness or helpfulness or support",
        "confusion": "expressing confusion or perplexity or bewilderment or puzzlement or uncertainty or doubt or hesitation or indecision or ambivalence",
        "curiosity": "expressing curiosity or inquisitiveness or interest or eagerness or enthusiasm or excitement or anticipation or expectation or hope or optimism",
        "disappointment": "expressing disappointment or discouragement or disillusionment or dissatisfaction or regret or sadness or sorrow or grief or mourning",
        "disapproval": "expressing disapproval or rejection or disfavor or dissent or opposition or resistance or refusal or denial or veto or prohibition or interdiction",
        "disgust": "expressing disgust or revulsion or repugnance or abhorrence or aversion or loathing or detestation or abomination or antipathy or animosity or hostility or enmity or hatred or malice or spite or rancor or resentment or bitterness or acrimony or venom or vitriol or malignity or malevolence",
        "embarrassment": "expressing embarrassment or self-consciousness or shame or humiliation or mortification or chagrin or discomfiture or confusion or awkwardness or unease or discomfort or distress or anxiety or worry or concern or nervousness",
        "excitement": "expressing excitement or enthusiasm or eagerness or anticipation or expectation or hope or optimism or merriment or having sense of accomplishment or achievement or success or victory or triumph or jubilation or exultation or elation or ecstasy",
        "nervousness": "expressing nervousness or having anxiety or worry or concern or apprehension or fear or dread or unease or discomfort or agitation or restlessness or impatience or not having confidence or lack of certainity, or lack of conviction or lack of faith",
        "optimism": "expressing optimism or hope or confidence or certainty or conviction or faith or trust or belief or assurance or sureness",
        "pride": "expressing pride or self-respect or self-esteem or self endeavor or sence of accompolishment or self confidence, or self assurance or self reliance or self sufficiency or self satisfaction or self contentment or self gratification",
        "realization": "expressing realization or understanding or comprehension or apprehension or perception or recognition or discernment or insight or enlightenment or awakening or revelation or discovery or invention or innovation or creation or origination or initiation",
        "relief": "expressing relief or relaxation or comfort or ease or rest or repose or respite or solace or satisfaction or contentment or fulfillment",
        "remorse": "expressing remorse, shame, shamefullness, guilt, contrition, penitence, repentance, regret, sorrow, grief, mourning, sadness, self-reproach, self-condemnation, self-accusation, self-criticism, self-blame, self-reproval, self-disapproval, self-censure, self-condemnation",
        "sadness": "expressing sadness or sorrow or grief or mourning or melancholy or despondency or dejection or depression or despair or hopelessness or unhappiness or wretchedness or misery or distress or agony or pain or suffering or torment or anguish or affliction or heartache or heartbreak or brokenheartedness or disconsolateness or desolation or devastation or loss or loneliness or isolation or abandonment or rejection or betrayal or disappointment or disillusionment or dissatisfaction",
        "neutral": "Nothing, neutral"
    }
    
    segments_with_emotions = []

    with open(file_path, "r") as file:
        data = json.load(file)

    st_result = stable_whisper.WhisperResult(file_path, force_order=True)
    # matches = st_result.find(r'[^.]+and[^.]+\.')
    st_result = words_per_screen(st_result, max_words=max_words)

    # segments = st_result["segments"]
    segments = st_result.segments
    text_list = [segment.text for segment in segments]
    # print(text_list)

    model_id = "SamLowe/roberta-base-go_emotions-onnx"
    file_name = "onnx/model_quantized.onnx"

    model = ORTModelForSequenceClassification.from_pretrained(model_id, file_name=file_name)
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    # sentences = ["ONNX is seriously fast for small batches. Impressive"]

    onnx_classifier = pipeline(
        task="text-classification",
        model=model,
        tokenizer=tokenizer,
        top_k=None,
        function_to_apply="sigmoid",  # optional as is the default for the task
    )

    model_outputs = onnx_classifier(text_list)
    # gives a list of outputs, each a list of dicts (one per label)
        
    # for text, output in zip(text_list, model_outputs):
    #     highest_label = max(output, key=lambda x: x['score'])['label']
    #     text_with_emotions[text] = highest_label
    #     print(f"{text}: {highest_label}")
    
    # return text_with_emotions
    for segment, output in zip(segments, model_outputs):
        highest_label = max(output, key=lambda x: x['score'])['label']
        # Add additional details to each segment
        segments_with_emotions.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
            "emotion_on": True,
            "predicted_emotion": highest_label,
            "emotion_detail": emotions_detail[highest_label]
        })
    
    data_to_write = {
        "segments": segments_with_emotions
    }

    # Write to the file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(data_to_write, f, ensure_ascii=False, indent=4)
    
    print(f"Emotions written to {output_file_path}")
    return data_to_write


########## Test the function ##
# if __name__ == "__main__":
    
#     inputData_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/data"
#     dataset_folder = "/Users/top_g/Desktop/react/ai_studio_v3/public/aistudio_json_data"
#     file_name = "steve_orig.json"

#     file_path = os.path.join(inputData_folder, file_name)
#     output_3wordjson_path = os.path.join(inputData_folder, "steve_3words.json")
#     output_8wordjson_path = os.path.join(inputData_folder, "steve_8words.json")

#     text_with_emotions_3words = get_emotion_words(file_path, output_3wordjson_path, max_words=3)
#     text_with_emotions_8words = get_emotion_words(file_path, output_8wordjson_path, max_words=8)







