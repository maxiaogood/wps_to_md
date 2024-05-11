import os
import re
from bs4 import BeautifulSoup

# 从文件中查找指定字符串所在的行
def find_otl_strings(file_path, target_string):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        otl_lines = [line for line in lines if re.search(target_string, line)]
        return str(otl_lines)

# 从字符串中提取出指定的数据
def extract_filename_from_string(pattern, text):
    result_data = re.search(pattern, text)
    if result_data:
        result = result_data.group(1)
    else:
        result = None
    return result

# 下载文件并重命名
def download_file(url, save_path):
    tmp_html= "/tmp/my_wps_to_md_tmp.html"
    command = f"wget {url} -O {tmp_html}"
    os.system(command)
    html_file_name_str = find_otl_strings(tmp_html, ".otl</title>")
    print(html_file_name_str, type(html_file_name_str))
    pattern = r'<title>(.*?)\.otl</title>'
    html_file_name = extract_filename_from_string(pattern, html_file_name_str)
    print(html_file_name, type(html_file_name))
    html_file_path = f"{save_path}/{html_file_name}.html"
    print(html_file_path, type(html_file_path))
    os.rename(tmp_html, html_file_path)

# 将html文件转换为md文件
def convert_html_to_md(html_path, md_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        html_doc = file.read()
        soup = BeautifulSoup(html_doc, 'lxml')
        print(soup.title)
        script_blocks = soup.find('div', class_='ssr-editor')
        for script in script_blocks:
            print(script)

# </script><div class="ssr-editor">

if __name__ == "__main__":
    # url = "https://kdocs.cn/l/ckQ4sn6AvTXC"
    # html_path = "./tmp"
    # download_file(url, html_path)
    html_path = "./tmp/wpsapi测试文档.html"
    md_path = "./tmp/wpsapi测试文档.md"
    convert_html_to_md(html_path, md_path)
    print("转换成功！")
