import requests
from config import USER_ID,USER_KEY
from PIL import Image
import io

def get_style_img_url_list(keyword_list, page=1, limit=10, type=1):
    print("using img api...")
    keywords = ' '.join(keyword_list)
    print("keywords:"+keywords)

    # 构造请求地址
    url = 'https://cn.apihz.cn/api/img/apihzimgbaidu.php'

    # 构造请求参数
    params = {
        'id': USER_ID,
        'key': USER_KEY,
        'words': keywords,
        'page': page,
        'limit': limit,
        'type': type
    }

    # 发送GET请求
    response = requests.get(url, params=params)

    # 检查请求是否成功
    if response.status_code == 200:
        # 解析返回的数据
        data = response.json()
        if data['code'] == 200:
            # 打印结果集
            print("result：")
            for img_url in data['res']:
                print(img_url)
            return data['res']
        else:
            # 打印错误信息
            print(f"错误：{data['msg']}")
            raise Exception(data['msg'])
    else:
        print(f"请求失败，状态码：{response.status_code}")
        raise Exception(response.status_code)

def get_img(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"请求失败，状态码：{response.status_code}")
        raise Exception(response.status_code)

def show_img(img_content):
    #本地显示
    img_bytes = io.BytesIO(img_content)
    img = Image.open(img_bytes)
    img.show()

def get_img_obj(url):
    response = requests.get(url)
    if response.status_code == 200:
        img_bytes = io.BytesIO(response.content)
        img = Image.open(img_bytes)
        return img
    else:
        print(f"请求失败，状态码：{response.status_code}")
        raise Exception(response.status_code)


if __name__ == '__main__':
    # 测试
    url_list = get_style_img_url_list(['女人', '美女', '帅哥'])
    show_img(get_img(url_list[0]))