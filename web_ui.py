import gradio as gr
from style_img_api import get_style_img_url_list, get_img_obj
from generator import Generator
import io
from PIL import Image
from utils import *


# 创建生成器实例
#提前加载模型，加快生成速度
generator = Generator()


# 定义一个函数来处理关键词搜索并返回图片URL列表
def search_style_images(style_keywords):
    style_img_url_list = get_style_img_url_list(style_keywords.split(","))

    # import pdb
    # pdb.set_trace()

    return gr.Dropdown(choices=style_img_url_list)

# 定义一个函数来处理图片上传和风格化图片生成
def generate_styled_image(style_img_url, content_img, style_keywords, neg_content_scale, steps):
    # 获取风格图片对象
    style_img_obj = get_img_obj(style_img_url)

    # 生成风格化图片
    styled_img = generator.generate(cv2_img_to_pil_image(content_img), style_img_obj, style_keywords.split(","), neg_content_scale, steps)


    return styled_img

# 内联CSS样式
inline_css = """
body {
    background-color: #f0f0f0;
    font-family: 'Arial', sans-serif;
}
gr|component {
    margin-bottom: 20px;
}
gr|textbox, gr|slider, gr|dropdown {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 10px;
    font-size: 16px;
}
gr|button {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
}
gr|button:hover {
    background-color: #0056b3;
}
"""

# 创建 Gradio 界面
with gr.Blocks(css=inline_css) as demo:
    # 用户输入风格关键词
    style_keywords = gr.Textbox(label="风格关键词（用英文逗号隔开）", placeholder="e.g., flower, nature")
    # 搜索按钮
    search_button = gr.Button("搜索风格图片")
    # 显示搜索结果图片URL列表
    style_img_urls = gr.Dropdown(label="选中的风格图片url", choices=[])
    with gr.Row():
        # 显示选中的图片
        selected_img = gr.Image(label="选中的风格图片")
        # 用户上传内容图片
        content_img = gr.Image(label="内容图片")
    # 对抗尺度（先变成不可视
    neg_content_scale = gr.Slider(0,1,0.8)
    # 迭代次数
    steps = gr.Slider(10,300,100)
    # 生成风格化图片按钮
    generate_button = gr.Button("生成风格化图片")
    # 显示生成的风格化图片
    styled_img = gr.Image(label="风格化图片")

    # 将搜索按钮点击事件与图片搜索函数关联
    search_button.click(search_style_images, inputs=[style_keywords], outputs=[style_img_urls])

    # 将下拉菜单的变化与显示选中图片函数关联
    style_img_urls.change(get_img_obj, inputs=[style_img_urls], outputs=[selected_img])

    # 将生成按钮点击事件与图片生成函数关联
    generate_button.click(generate_styled_image, inputs=[style_img_urls, content_img, style_keywords, neg_content_scale, steps], outputs=[styled_img])


demo.launch()



