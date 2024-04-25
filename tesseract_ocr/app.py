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
        
        # 원본 이미지 크기 저장
        original_size = open_cv_image.shape[:2][::-1]  # (width, height)
        
        # 이미지 전처리와 리사이즈
        gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        resized_gray = cv2.resize(gray_image, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
        binary_image = cv2.adaptiveThreshold(resized_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Tesseract를 사용하여 리사이즈된 이미지에서 텍스트 추출
        ocr_data = pytesseract.image_to_data(Image.fromarray(binary_image), output_type=pytesseract.Output.DICT)

        # 인식된 텍스트의 bounding box를 원본 이미지 크기에 맞게 조정하여 그리기
        scale_x = original_size[0] / binary_image.shape[1]
        scale_y = original_size[1] / binary_image.shape[0]

        extracted_text = []
        for i in range(len(ocr_data['text'])):
            if int(ocr_data['conf'][i]) > 60:
                x = int(ocr_data['left'][i] * scale_x)
                y = int(ocr_data['top'][i] * scale_y)
                w = int(ocr_data['width'][i] * scale_x)
                h = int(ocr_data['height'][i] * scale_y)
                cv2.rectangle(open_cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(open_cv_image, ocr_data['text'][i], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                extracted_text.append(ocr_data['text'][i])

        # OCR 결과를 포함한 이미지 저장
        save_dir = '/config/tesseract_ocr/result'
        result_path = os.path.join(save_dir, 'overlay_image.jpg')
        binary_path = os.path.join(save_dir, 'binary_image.jpg')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        cv2.imwrite(result_path, open_cv_image)
        cv2.imwrite(binary_path, binary_image)

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
