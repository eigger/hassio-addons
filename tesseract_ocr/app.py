from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

@app.route("/ocr", methods=["POST"])
def process_ocr():
    data = {"success": False}

    if 'image' not in request.files:
        data['error'] = '이미지 파일이 제공되지 않았습니다.'
        return jsonify(data), 400

    image_file = request.files['image']
    if image_file.filename == '':
        data['error'] = '파일이 선택되지 않았습니다.'
        return jsonify(data), 400

    # ROI 및 회전 각도 값 받기
    roi = request.form.get('roi')
    rotate = request.form.get('rotate', type=float)  # 회전 각도를 float 형태로 받음

    if roi:
        try:
            roi = tuple(map(int, roi.split(',')))
        except ValueError:
            data['error'] = 'ROI 형식이 잘못되었습니다. "x,y,width,height" 형식이어야 합니다.'
            return jsonify(data), 400

    try:
        image_bytes = image_file.read()
        pil_image = Image.open(io.BytesIO(image_bytes))

        # 이미지 회전 처리
        if rotate:
            pil_image = pil_image.rotate(-rotate, expand=True)  # PIL은 시계 방향으로 회전하므로 각도를 반대로 적용

        # ROI가 제공되면 이미지 크롭
        if roi:
            pil_image = pil_image.crop((roi[0], roi[1], roi[0] + roi[2], roi[1] + roi[3]))

        text = pytesseract.image_to_string(pil_image)
        data['text'] = text
        data['success'] = True
    except IOError:
        data['error'] = '이미지 파일 처리 중 오류가 발생했습니다.'
        return jsonify(data), 500
    except Exception as e:
        data['error'] = str(e)
        return jsonify(data), 500

    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)
