import cv2
import pickle
import face_recognition

# function to find the name of the person in the image by searching the "face_enc"
# give the image as an input
def find_person_name():
	data = pickle.loads(open('C:/Users/shri1/sih/sih-project-2022/sih-project-final/face_function/face_enc', "rb").read())
	vs = cv2.VideoCapture(0)
	result , image = vs.read()
	if result:
		cv2.imshow("person_image" ,image)
		cv2.imwrite("C:/Users/shri1/sih/sih-project-2022/sih-project-final/face_function/new_img.png", image)
		cv2.waitKey(0)
		cv2.destroyWindow("person_image")
	else:
		print("no img detected")

	# path = r"C:/Users/shri1/sih/sih-project-2022/sih-project-final/face_function/Images/Messi/Messi.jpg"
	frame = cv2.imread("C:/Users/shri1/sih/sih-project-2022/sih-project-final/face_function/new_img.png")
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	encodings = face_recognition.face_encodings(rgb)
	names = []
	for encoding in encodings:
		matches = face_recognition.compare_faces(data["encodings"],encoding)
		name = ""
		if True in matches:
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1
			name = max(counts, key=counts.get)
		print(name)
		return name

# find_person_name()
if __name__ == "__main__":
	value = find_person_name()
	print(value)

