# hassio-addons : Tesseract OCR
```
sensor:
  - platform: rest
    name: "OCR Text Extraction"
    resource: "http://localhost:5080/ocr"
    method: POST
    content_type: "multipart/form-data"
    payload: 'image=@/config/www/images/test.jpg;type=image/jpeg; roi=100,100,300,200; rotate=90'
    headers:
      Content-Type: application/json
    value_template: "{{ value_json.text }}"
    scan_interval: 3600  # 센서가 매 시간마다 API를 호출
```