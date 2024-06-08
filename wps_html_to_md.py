import os
import re
from bs4 import BeautifulSoup

# 获取html中的有效数据
def get_valid_data_from_html(html_path, html_need_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')  
        target_div = soup.find_all('div', class_='block_tile')  
        if target_div:  
            with open(html_need_path, 'w', encoding='utf-8') as file:  
                file.write(str(target_div))
                return target_div
        else:  
            print("未找到目标div元素。")
            return None

# 将html文件转换为md文件
def convert_html_to_md(html_path, md_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        html_doc = file.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        script_blocks = soup.find_all('div', class_='block_tile')
        for script in script_blocks:
            # print("标签名：", script.name)
            analysis_block_tile(script)
        return script_blocks

def analysis_block_tile(block_tile):
    for son_tag in block_tile.contents:
        if son_tag.name == None:
            continue
        print("## 标签名：", son_tag.name)
        print("属性：", son_tag.attrs)
        # print("文本内容：", son_tag.text)

if __name__ == "__main__":
    html_path = "./tmp/wpsapi测试文档.html"
    html_need_path = "./tmp/wpsapi测试文档need.html"
    md_path = "./tmp/wpsapi测试文档.md"
    # get_valid_data_from_html(html_path, html_need_path)

    convert_html_to_md(html_need_path, md_path)
    print("转换成功！")
