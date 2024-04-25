from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io
import os
import requests
import cv2
import numpy as np

app = Flask(__name__)

@app.route("/ocr", methods=["POST"])
def process_ocr():
    data = {"success": False, "error": ""}

    image_url = request.json.get('image_url')
    roi = request.json.get('roi')
    rotate = request.json.get('rotate', 0)

    if not image_url:
        data['error'] = '이미지 URL이 제공되지 않았습니다.'
        return jsonify(data), 400

    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_bytes = io.BytesIO(response.content)
        pil_image = Image.open(image_bytes)

        if rotate:
            pil_image = pil_image.rotate(-float(rotate), expand=True)

        if roi:
            roi_values = tuple(map(int, roi.split(',')))
            pil_image = pil_image.crop(roi_values)
        
        # PIL 이미지를 OpenCV 형식으로 변환
        open_cv_image = np.array(pil_image) 
        open_cv_image = open_cv_image[:, :, ::-1].copy() # RGB to BGR

        # 이미지 전처리 과정 추가
        # 여기에 이미지 전처리 단계를 추가합니다. (이전 답변에 사용된 과정 적용)
        # 예: 크기 조정, 그레이스케일 변환, 이진화, 노이즈 제거, 이진화, 노이즈 제거 등
        # 이 부분은 적절한 전처리 로직에 따라 채워져야 합니다.
        
        # OpenCV 전처리 코드 시작
        # 이미지를 그레이스케일로 변환
        gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        # 이미지 크기 조정
        gray_image = cv2.resize(gray_image, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
        
        # Adaptive Thresholding 적용
        binary_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # 경계선 강조와 노이즈 제거
        kernel = np.ones((1, 1), np.uint8)
        binary_image = cv2.dilate(binary_image, kernel, iterations=1)
        binary_image = cv2.erode(binary_image, kernel, iterations=1)
        
        # OpenCV 전처리 코드 끝

        # 다시 PIL 이미지로 변환
        pil_image = Image.fromarray(binary_image)

        # Tesseract를 사용하여 이미지에서 텍스트의 위치와 함께 정보 추출
        ocr_data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)

        # 인식된 텍스트의 bounding box를 원본 이미지에 그리기
        extracted_text = []  # 인식된 텍스트를 저장할 리스트
        n_boxes = len(ocr_data['text'])
        for i in range(n_boxes):
            if int(ocr_data['conf'][i]) > 60:  # Confidence level을 기준으로 필터링
                (x, y, w, h) = (ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i])
                cv2.rectangle(open_cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(open_cv_image, ocr_data['text'][i], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                extracted_text.append(ocr_data['text'][i])

        # OCR 결과를 포함한 이미지 저장
        save_dir = '/config/tesseract_ocr/result'
        file_name = 'overlay_image.jpg'
        save_path = os.path.join(save_dir, file_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        cv2.imwrite(save_path, open_cv_image)
        data['text'] = "\n".join(extracted_text)
        data['success'] = True
    except requests.RequestException as e:
        data['error'] = f'이미지 다운로드 실패: {str(e)}'
        return jsonify(data), 500
    except IOError:
        data['error'] = '이미지 파일 처리 중 오류가 발생했습니다.'
        return jsonify(data), 500
    except Exception as e:
        data['error'] = str(e)
        return jsonify(data), 500

    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)
