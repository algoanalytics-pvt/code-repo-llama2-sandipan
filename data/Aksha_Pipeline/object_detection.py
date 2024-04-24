from asyncio.log import logger
import cv2
import numpy as np 
import datetime as dt
import onnxruntime as ort
import random

#Load object detection model (yolo)
# def load_yolo():
# 	"""
#     Input   :   NA
#     Utility :   Load YOLO model for object detection from Model Folder (weights, cfg and label file).
#     Output  :   Object detector, Class lables, Colors for bounding boxes, Output layer.
#     Descriptioin :  YOLO is an algorithm that uses neural networks to provide real-time object detection. 
# 					This algorithm is popular because of its speed and accuracy. It has been used in various 
# 					applications to detect traffic signals, people, parking meters, and animals.
# 					In this application we are using customize version of YOLO by limiting its object detection 
# 					to specific classes.
# 					For more details visit:- https://arxiv.org/pdf/2004.10934.pdf
#     """
# 	# net = cv2.dnn.readNet("yolov4/yolov4-tiny_last.weights","yolov4/yolov4-tiny.cfg") #Uncomment this line for testing on development system
# 	net = cv2.dnn.readNet("yolov4-tiny_last.weights","yolov4-tiny.cfg") #Uncomment this line for running in production/docker network
# 	classes = []
# 	# with open("yolov4/coco.names", "r") as f:
# 	with open("coco.names", "r") as f:
	
# 		classes = [line.strip() for line in f.readlines()] 
	
# 	output_layers = [layer_name for layer_name in net.getUnconnectedOutLayersNames()]
# 	colors = np.random.uniform(0, 255, size=(len(classes), 3))
# 	return net, classes, colors, output_layers

# #Object detection function
# def detect_objects(img, net, outputLayers):
# 	"""
#     Input   :   Image, Loaded YOLO Model object, output layer (output of load_yolo function) 
#     Utility :   Load YOLO model for object detection from Model Folder (weights, cfg and label file).
#     Output  :   blob, detection outputs.
#     Descriptioin :  We pass the image for objet detection in the function with the Network and the Outputlayers 
# 					we got from load_yolo function.
#     """			
# 	blob = cv2.dnn.blobFromImage(img, scalefactor=0.00392, size=(320, 320), mean=(0, 0, 0), swapRB=True, crop=False)
# 	net.setInput(blob)
# 	outputs = net.forward(outputLayers)
# 	return blob, outputs

# #Getting box co-ordinates for detected objects on frame.
# def get_box_dimensions(outputs, height, width):
# 	"""
#     Input   :   Output from detect_object function, height and width of image) 
#     Utility :   Get detected objects box co-ordinates.
#     Output  :   bounding boxes, configurations, detected class label id.
#     Descriptioin :  This function is to get bounding box co-ordinate for detected objects inside frame.
#     """	
# 	boxes = []
# 	confs = []
# 	class_ids = [] 
# 	for output in outputs:
# 		for detect in output:
# 			scores = detect[5:]
# 			class_id = np.argmax(scores)
# 			conf = scores[class_id]
# 			if conf > 0.3:
# 				center_x = int(detect[0] * width)
# 				center_y = int(detect[1] * height)
# 				w = int(detect[2] * width)
# 				h = int(detect[3] * height)
# 				x = int(center_x - w/2)
# 				y = int(center_y - h / 2)
# 				boxes.append([x, y, w, h])
# 				confs.append(float(conf))
# 				class_ids.append(class_id)
# 	return boxes, confs, class_ids

#Draw bounding box around objects as per co-ordinates and lable the object			
def get_labels(boxes, confs, class_ids, classes):
# def get_labels(img,boxes, confs, colors, class_ids, classes): # Uncomment for drawing boxes with labels if needed
	"""
    Input   :   Output from get_box_dimension function boxes, confs, class_ids and labels classes list from load_yolo function ) 
    Utility :   Get object labels for box co-ordinates.
    Output  :   dist obj {"label": label, "x":x-value, "y":y-value, "w": width, "h": height, "confidence": ${object_accuracy}%}
    Descriptioin :  This function is to get respective lables for detected objects inside bounding box co-ordinate in the particular frame.
    """	 
	indexes = cv2.dnn.NMSBoxes(boxes, confs, 0.5, 0.4)
	#colors for labels 
	# colors = np.random.uniform(0, 255, size=(len(classes), 3))
	# font = cv2.FONT_HERSHEY_PLAIN
	all_results = []
	for i,j in zip(range(len(boxes)), confs):
		if i in indexes:
			x, y, w, h = boxes[i]
			label = str(classes[class_ids[i]])
			# color = colors[i]
			# cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
			# cv2.putText(img, label, (x, y - 5), font, 1, color, 1)
			result_meta = {"label": label, "x":x, "y":y, "w": w, "h": h, "confidence":j}
			all_results.append(result_meta)	
			

	# return all_results, img
	return all_results
	
def draw_labels(orignal_img, object_labels, classes,live_path): # Uncomment for drawing boxes with labels if needed
	"""
    Input   :   Output from get_box_dimension function boxes, confs, class_ids and labels classes list from load_yolo function ) 
    Utility :   Get object labels for box co-ordinates.
    Output  :   dist obj {"label": label, "x":x-value, "y":y-value, "w": width, "h": height, "confidence": ${object_accuracy}%}
    Descriptioin :  This function is to get respective lables for detected objects inside bounding box co-ordinate in the particular frame.
    """	 
	img = orignal_img.copy()

	#colors for labels 
	colors = np.random.uniform(0, 255, size=(len(classes), 3))
	font = cv2.FONT_HERSHEY_PLAIN
	print("object labels are",object_labels)
	for i in object_labels:
		

		label = i["label"]
		x = i["x"]
		y = i["y"]
		w = i["w"]
		h = i["h"]
		print(f'type of x {type(x), x, label} ')
		try:
			print("issue color")
			# color = colors[classes.index(label)]
			color = (0,255,0)
			print("issue")
			cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
			print("issue")
			cv2.putText(img, label, (x, y - 5), font, 1, color, 2)
		except Exception as e:
			logger.info(msg=f"issue in draw labels {e}")
		
	try:
		points=np.array([[650,0],[650,50],[600,0]])
		cv2.fillPoly(img,pts=[points], color=(0,197,255))
		obd_result = img.copy()
		# cv2.imwrite(f'{live_path}/latest.jpg',img)
		logger.info(msg=f"Object Anomaly function processed sucessfully!")
		return obd_result
		
	except Exception as e:
			logger.info(msg=f"issue in put labels")
			return f'Object Anomaly processing got failed...'
		
#Part of YOLO V7 Model

def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
	# Resize and pad image while meeting stride-multiple constraints
	shape = im.shape[:2]  # current shape [height, width]
	if isinstance(new_shape, int):
		new_shape = (new_shape, new_shape)

	# Scale ratio (new / old)
	r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
	if not scaleup:  # only scale down, do not scale up (for better val mAP)
		r = min(r, 1.0)

	# Compute padding
	new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
	dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - \
			 new_unpad[1]  # wh padding

	if auto:  # minimum rectangle
		dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

	dw /= 2  # divide padding into 2 sides
	dh /= 2

	if shape[::-1] != new_unpad:  # resize
		im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
	top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
	left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
	im = cv2.copyMakeBorder(im, top, bottom, left, right,
							cv2.BORDER_CONSTANT, value=color)  # add border
	return im, r, (dw, dh)


def load_object_detection_model(RELATIVE_PATH_YOLO, RELATIVE_PATH_COCO, cuda=False):
	"""
	This method is used for loading the object detection model like yolov4/yolov7

	Args:
		cuda (bool, optional): To specify the execution provider, defaults to False.
	"""
	providers = ['CUDAExecutionProvider',
				'CPUExecutionProvider'] if cuda else ['CPUExecutionProvider']
	weights = RELATIVE_PATH_YOLO
	with open(RELATIVE_PATH_COCO, "r") as f:
		class_names = [line.strip() for line in f.readlines()]
	colors = {name: [random.randint(0, 255) for _ in range(3)] for i, name in enumerate(class_names)}

	object_detection_service = ort.InferenceSession(weights, providers=providers)
 
	return object_detection_service, class_names, colors


def object_detection(frame, object_detection_service, class_names, colors):
	""" this method uses the object detection model loaded previously to detect the objects in the current frame.

	Args:
		frame (numpy.ndarray): current frame
		object_detection_service (onnx model): Object detection model used for detecting objects in frame 

	Returns:
		_type_: _description_
	"""

	img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	image = img.copy()
	image, ratio, dwdh = letterbox(image, auto=False)
	image = image.transpose((2, 0, 1))
	image = np.expand_dims(image, 0)
	im = image.astype(np.float32)
	im /= 255
	outname = [i.name for i in object_detection_service.get_outputs()]
	inname = [i.name for i in object_detection_service.get_inputs()]
	inp = {inname[0]: im}
	outputs = object_detection_service.run(outname, inp)[0]
	confidence = []
	boxes = []
	classes = []
	for i, (batch_id, x0, y0, x1, y1, cls_id, score) in enumerate(outputs):
		if score > 0.4:
			box = np.array([x0, y0, x1, y1])
			box -= np.array(dwdh * 2)
			box /= ratio
			box = box.round().astype(np.int32).tolist()
			confidence.append(round(float(score), 3))
			new_box = [int(box[0]), int(box[1]), int(
				box[2] - box[0]), int(box[3] - box[1])]
			boxes.append(new_box)
			classes.append(int(cls_id))

	return boxes, confidence, classes, class_names
		

	
		

	

