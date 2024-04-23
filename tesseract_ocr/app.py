from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io
import requests

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
