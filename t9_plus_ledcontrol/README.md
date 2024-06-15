# hassio-addons : TT9 Plus Mini PC LED Control
```
rest_command:
  led_control:
    url: "http://<your_flask_server_ip>:5090/led"
    method: "post"
    headers:
      Content-Type: "application/json"
    payload: '{"mode": "4", "brightness": "5", "speed":"5"}'
    content_type: "application/json"

```