import base64
import requests
import config


class FaceIndentify:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json; charset=UTF-8"
        }

    def img_to_BASE64(slef, path):
        with open(path, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            return base64_data

    def detect_face(self, img_path):
        # 人脸检测与属性分析
        img_BASE64 = self.img_to_BASE64(img_path)
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        post_data = {
            "image": img_BASE64,
            "image_type": "BASE64",
            "face_field": "gender,age,beauty,gender,race,expression",
            "face_type": "LIVE"
        }
        access_token = config.BAIDU_TOKEN
        # print("token:", access_token)
        request_url = request_url + "?access_token=" + access_token
        response = requests.post(url=request_url, data=post_data, headers=self.headers)
        json_result = response.json()
        if json_result['error_msg'] != 'pic not has face':
            result = {"status": "succeed"}
            result["age"] = json_result['result']['face_list'][0]['age']
            result["beauty"] = json_result['result']['face_list'][0]['beauty']
            result["gender"] = json_result['result']['face_list'][0]['gender']['type']
            result["expression"] = json_result['result']['face_list'][0]['expression']['type']
            return result
        return {"state": "error", "error_msg": "pic not has face"}
