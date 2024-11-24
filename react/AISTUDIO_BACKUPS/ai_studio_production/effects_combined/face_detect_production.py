
import cv2
import mediapipe as mp
import numpy as np
import json


## Working code
# def detect_faces_with_checks(video_path, json_input_path, output_folder, json_output_path):
#     print("Starting advanced face detection...")
#     # Set up MediaPipe FaceDetector
#     mp_face_detection = mp.solutions.face_detection
#     mp_drawing = mp.solutions.drawing_utils
#     face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

#     # Load JSON data for segments
#     with open(json_input_path) as f:
#         segments_json = json.load(f)

#     # Open the video file
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         print("Error opening video file.")
#         return
#     fps = cap.get(cv2.CAP_PROP_FPS)

#     # Process each segment
#     for segment in segments_json['segments']:
#         start_time, end_time = segment['start'], segment['end']
#         start_frame, end_frame = int(start_time * fps), int(end_time * fps)
#         cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
#         consistent_single_face = True
#         orange_box_plotted = False
#         orange_box = None
#         segment["detection_on"] = True
#         segment["orange_box"] = False

#         for frame_counter in range(start_frame, end_frame + 1):
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = face_detection.process(rgb_frame)

#             # Adjusted check for NoneType or multiple detections
#             num_faces = 0 if results.detections is None else len(results.detections)
#             if num_faces != 1:
#                 print("I am here 1")
#                 consistent_single_face = False
#                 segment["detection_on"] = False
#                 segment["orange_box"] = False
#                 segment["face_count"] = num_faces
#                 break  # Exit loop if more than one face or no face detected

#             # Check 2: Plot orange box on the earliest possible frame
#             if not orange_box_plotted and frame_counter in [start_frame + 4, start_frame + 9, start_frame + 14]:
#                 detection = results.detections[0]
#                 bboxC = detection.location_data.relative_bounding_box
#                 ih, iw, _ = frame.shape
#                 x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                
#                 # Calculate center of the original box
#                 center_x = x + w / 2
#                 center_y = y + h / 2

#                 # New dimensions, 3 times larger
#                 new_w = w * 3
#                 new_h = h * 3

#                 # Calculate new top-left corner so the enlargement is centered
#                 new_x = center_x - new_w / 2
#                 new_y = center_y - new_h / 2
                
#                 orange_box = (int(new_x), int(new_y), int(new_w), int(new_h))
#                 orange_box_plotted = True
#                 segment["orange_box"] = True
#                 print("I am here 22")
#                 print(x, y, w, h)
#                 print(orange_box[0], orange_box[1], orange_box[2], orange_box[3])

#             # Check 3: Check for collision between white box and orange box
#             if orange_box_plotted:
#                 for detection in results.detections:
#                     bboxC = detection.location_data.relative_bounding_box
#                     x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

#                     # Check if any edge of the white box goes beyond the orange box
#                     if (x < orange_box[0] or x + w > orange_box[0] + orange_box[2] or
#                             y < orange_box[1] or y + h > orange_box[1] + orange_box[3]):
#                         # Here, we check:
#                         # - If the left edge of the white box is to the left of the orange box's left edge (x < orange_box[0])
#                         # - If the right edge of the white box is to the right of the orange box's right edge (x + w > orange_box[0] + orange_box[2])
#                         # - If the top edge of the white box is above the orange box's top edge (y < orange_box[1])
#                         # - If the bottom edge of the white box is below the orange box's bottom edge (y + h > orange_box[1] + orange_box[3])
#                         # Any of these conditions being true means an edge of the white box extends beyond the orange box
#                         print("Collision detected: White box edge goes beyond the orange box.")
#                         consistent_single_face = False
#                         break

#             if not consistent_single_face:
#                 break

#         ### test
#         # After all checks: If consistent single face was detected and no collision occurred
#         if consistent_single_face and orange_box_plotted:
#             segment["detection_on"] = True
#             segment["orange_box"] = True
#             # Log only the orange box as the detection for this segment
#             segment['detections'] = [{
#                 'frame_number': frame_counter,
#                 'bounding_box': {
#                     'xmin': orange_box[0], 
#                     'ymin': orange_box[1], 
#                     'width': orange_box[2], 
#                     'height': orange_box[3]
#                 }
#             }]
#         else:
#             segment["detection_on"] = False
#             segment["orange_box"] = False
        
#         ####
        
#         # # Update segment based on checks
#         # if not consistent_single_face:
#         #     segment["detection_on"] = False
#         #     segment["orange_box"] = False

#     cap.release()
    
#     # Write the updated JSON data to a new file
#     with open(json_output_path, 'w') as json_file:
#         json.dump(segments_json, json_file, indent=4)
#     print("Face detection and checks completed. JSON updated.")


def detect_faces_with_checks(video_path, json_data):
    try:
        print("Starting advanced face detection...")
        # Set up MediaPipe FaceDetector
        mp_face_detection = mp.solutions.face_detection
        mp_drawing = mp.solutions.drawing_utils
        face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

        # Load JSON data for segments
        # with open(json_input_path) as f:
        #     segments_json = json.load(f)
        segments_json = json_data
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error opening video file.")
            return
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Process each segment
        # for segment in segments_json['segments']:
        for segment in segments_json:
            start_time, end_time = segment['start'], segment['end']
            start_frame, end_frame = int(start_time * fps), int(end_time * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            consistent_single_face = True
            orange_box_plotted = False
            orange_box = None
            segment["detection_on"] = True
            segment["orange_box"] = False

            for frame_counter in range(start_frame, end_frame + 1):
                ret, frame = cap.read()
                if not ret:
                    break
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(rgb_frame)

                # Adjusted check for NoneType or multiple detections
                num_faces = 0 if results.detections is None else len(results.detections)
                if num_faces != 1:
                    print("I am here 1")
                    consistent_single_face = False
                    segment["detection_on"] = False
                    segment["orange_box"] = False
                    segment["face_count"] = num_faces
                    break  # Exit loop if more than one face or no face detected

                # Check 2: Plot orange box on the earliest possible frame... here the y is same both side.
                # if not orange_box_plotted and frame_counter in [start_frame + 4, start_frame + 9, start_frame + 14]:
                #     detection = results.detections[0]
                #     bboxC = detection.location_data.relative_bounding_box
                #     ih, iw, _ = frame.shape
                #     x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                    
                #     # Calculate center of the original box
                #     center_x = x + w / 2
                #     center_y = y + h / 2

                #     # New dimensions, 3 times larger
                #     new_w = w * 3
                #     new_h = h * 3

                #     # Calculate new top-left corner so the enlargement is centered
                #     new_x = center_x - new_w / 2
                #     new_y = center_y - new_h / 2
                    
                #     orange_box = (int(new_x), int(new_y), int(new_w), int(new_h))
                #     orange_box_plotted = True
                #     segment["orange_box"] = True
                #     print("I am here 22")
                #     print(x, y, w, h)
                #     print(orange_box[0], orange_box[1], orange_box[2], orange_box[3])

                ## working code.... # here the y is small for top but bottom is 3x
                if not orange_box_plotted and frame_counter in [start_frame + 4, start_frame + 9, start_frame + 14]:
                    detection = results.detections[0]
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

                    # Calculate center of the original box
                    center_x = x + w / 2
                    center_y = y + h / 2

                    # New dimensions: width x3
                    new_w = w * 3

                    # Adjusted scaling for height: different factors for top and bottom parts
                    scale_factor_up = 2  # Scale factor for the top part
                    scale_factor_down = 3  # Scale factor for the bottom part

                    # Calculate new height based on asymmetric scaling
                    new_h_up = (h / 2) * scale_factor_up  # Height above the center
                    new_h_down = (h / 2) * scale_factor_down  # Height below the center
                    new_h = new_h_up + new_h_down

                    # Calculate new top-left corner with adjusted scaling
                    new_x = center_x - new_w / 2
                    new_y = center_y - new_h_up  # Shift new_y up by the scaled-up portion only

                    orange_box = (int(new_x), int(new_y), int(new_w), int(new_h))
                    orange_box_plotted = True
                    segment["orange_box"] = True
                    print(x, y, w, h)
                    print(orange_box[0], orange_box[1], orange_box[2], orange_box[3])

                # Check 3: Check for collision between white box and orange box
                if orange_box_plotted:
                    for detection in results.detections:
                        bboxC = detection.location_data.relative_bounding_box
                        x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

                        # Check if any edge of the white box goes beyond the orange box
                        if (x < orange_box[0] or x + w > orange_box[0] + orange_box[2] or
                                y < orange_box[1] or y + h > orange_box[1] + orange_box[3]):
                            # Here, we check:
                            # - If the left edge of the white box is to the left of the orange box's left edge (x < orange_box[0])
                            # - If the right edge of the white box is to the right of the orange box's right edge (x + w > orange_box[0] + orange_box[2])
                            # - If the top edge of the white box is above the orange box's top edge (y < orange_box[1])
                            # - If the bottom edge of the white box is below the orange box's bottom edge (y + h > orange_box[1] + orange_box[3])
                            # Any of these conditions being true means an edge of the white box extends beyond the orange box
                            print("Collision detected: White box edge goes beyond the orange box.")
                            consistent_single_face = False
                            break

                        # Check 4:  if any of the value orange_box[0], orange_box[1], orange_box[2], orange_box[3] becomes negative
                        if any(coord < 0 for coord in orange_box):
                            print("Collision detected 22: White box edge goes beyond the orange box.")
                            consistent_single_face = False
                            break

                if not consistent_single_face:
                    break

            ### test
            # After all checks: If consistent single face was detected and no collision occurred
            if consistent_single_face and orange_box_plotted:
                segment["detection_on"] = True
                segment["orange_box"] = True
                # Log only the orange box as the detection for this segment
                segment['detections'] = [{
                    'frame_number': frame_counter,
                    'bounding_box': {
                        'xmin': orange_box[0], 
                        'ymin': orange_box[1], 
                        'width': orange_box[2], 
                        'height': orange_box[3]
                    }
                }]
            else:
                segment["detection_on"] = False
                segment["orange_box"] = False
            

        cap.release()
    
        return (200, segments_json)
    except Exception as e:
        print("Error in detect_faces_with_checks: ", e)
        return (412, None)
    # # Write the updated JSON data to a new file
    # with open(json_output_path, 'w') as json_file:
    #     json.dump(segments_json, json_file, indent=4)
    # print("Face detection and checks completed. JSON updated.")



# video_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_orig.mp4'
# output_folder = 'folder'
# json_input_path = '/Users/top_g/Desktop/react/ai_studio_v3/public/data/steve_8words.json'
# json_output_path = f'detection_results.json'


# # detect_faces(video_path, output_folder, json_output_path)
# status, updated_segments= detect_faces_with_checks(video_path, json_input_path, output_folder, json_output_path)



