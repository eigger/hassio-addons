# hassio-addons : TT9 Plus Mini PC LED Control
```
sensor:
  - platform: rest
    name: OCR Text Extraction
    resource: http://<your_flask_server_ip>:5090/led
    method: POST
    headers:
      Content-Type: application/json
    payload: >-
      {
        "image_url": "http://url_to_your_image.jpg",
        "roi": "x,y,width,height",
        "rotate": "90"
      }
    value_template: >
      {% if value_json.success %}
        {{ value_json.text | replace('\n', ' ') }}
      {% else %}
        Error: {{ value_json.error }}
      {% endif %}
    scan_interval: 3600  # 센서가 매 시간마다 API를 호출

```