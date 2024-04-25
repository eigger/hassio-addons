from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io
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

        # Tesseract OCR 실행
        text = pytesseract.image_to_string(pil_image)
        data['text'] = text
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
