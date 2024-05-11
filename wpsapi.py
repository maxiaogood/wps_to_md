import os
import re
from bs4 import BeautifulSoup
import markdown
import pypandoc


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


# 解析标题
def analysis_title(title):
    if title.name == 'h1':
        title_str = str(title.text)
        return "# " + title_str
    elif title.name == 'h2':
        title_str = str(title.text)
        return "## " + title_str
    elif title.name == 'h3':
        title_str = str(title.text)
        return "### " + title_str
    elif title.name == 'h4':
        title_str = str(title.text)
        return "#### " + title_str
    elif title.name == 'h5':
        title_str = str(title.text)
        return "##### " + title_str
    return None

# 给每一行添加前缀
def add_prefix_to_each_line(s, prefix):
    lines = s.splitlines()
    new_lines = [prefix + line for line in lines]
    # 找到要删除的键
    keys_to_remove = [k for k, v in enumerate(new_lines) if v == prefix]
    # 删除这些键
    for index in reversed(keys_to_remove):
        del new_lines[index]
    return new_lines

# 解析引用
def analysis_quote(quote):
    if quote.name != 'blockquote':
        return None
    markdown_content = pypandoc.convert_text(quote, 'html', format='html')
    # print(markdown_content, type(markdown_content))
    quote_str = markdown_content.replace("<blockquote>", "")
    quote_str = quote_str.replace("</blockquote>", "")
    quote_str = quote_str.replace("<em> </em>", "")
    quote_str = quote_str.replace("<br />", "\r\n")
    quote_str = quote_str.replace("<br/>", "\r\n")
    quote_list = add_prefix_to_each_line(quote_str, "> ")
    return quote_list

# 解析高亮块
def analysis_highlight_block(highlight_block):
    if highlight_block.name != 'div':
        return None
    highlight_block_dict = highlight_block.attrs
    if 'class' not in highlight_block_dict:
        return None
    highlight_type = highlight_block_dict['class'][1]
    if highlight_type != 'highlight_block':
        return None
    highlight_block_all = highlight_block.find_all('div', class_='sub-doc-tile')
    highlight_list = []
    for son_tag in highlight_block_all:
        if son_tag.name != 'div':
            continue
        # if son_tag.text == 📌:
        #     continue
        highlight_list.append(son_tag.text)
    return highlight_list

# 解析代码块
def analysis_code_block(code_block):
    if code_block.name != 'nodeview':
        return None , None
    code_block_dict = code_block.attrs
    if 'data-node-type' not in code_block_dict:
        return None , None
    code_block_type = code_block_dict['data-node-type']
    if code_block_type != 'code_block':
        return None , None
    code_block_all = code_block.find('pre')
    code_block_dict = code_block_all.attrs
    if 'lang' not in code_block_dict:
        return None , None
    code_block_list = []
    for son_tag in code_block_all:
        if son_tag.name == 'div':
            code_block_type = son_tag.text
            continue
        if son_tag.name == 'code':
            code_block_list = son_tag.text.split('\n')
            continue
    return code_block_list, code_block_type

# 解析p标签
def analysis_p(pdata):
    if pdata.name != 'p':
        return None
    
    pdata_dict = pdata.attrs
    if 'class' not in pdata_dict:
        return None
    pdata_type = pdata_dict['class'][0]
    print(pdata_type)
    if pdata_type == 'outline-bullet-list-item': # 无序列表
        return "- " + pdata.text
    elif pdata_type == 'outline-order-list-item': # 有序列表
        return "1. " + pdata.text
    elif pdata_type == 'outline-todo-list-item': # 任务列表
        return "- [ ] " + pdata.text
    elif pdata_type == 'outline-done-list-item': # 已完成任务列表
        return "- [x] " + pdata.text
    return None

# 解析块数据
def analysis_block_tile(block_tile):
    for son_tag in block_tile.contents:
        # print("标签名：", son_tag.name)
        # print("属性：", son_tag.attrs)
        # print("文本内容：", son_tag.text)
        # title = analysis_title(son_tag)
        # if title:
        #     print(title)
        #     continue
        # quote_test = analysis_quote(son_tag)
        # if quote_test:
        #     print(quote_test)
        #     continue
        # highlight_test = analysis_highlight_block(son_tag)
        # if highlight_test:
        #     print(highlight_test)
        #     continue
        code_test_list, code_test_type = analysis_code_block(son_tag)
        if code_test_list:
            print(code_test_list,type(code_test_list))
            print(code_test_type,type(code_test_type))
        # p_test = analysis_p(son_tag)
        # if p_test:
        #     print(p_test)
        #     continue


# 将html文件转换为md文件
def convert_html_to_md(html_path, md_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        html_doc = file.read()
        soup = BeautifulSoup(html_doc, 'lxml')
        print(soup.title)
        script_blocks = soup.find_all('div', class_='block_tile')
        for script in script_blocks:
            #print(script, type(script))
            analysis_block_tile(script)
        return script_blocks

# </script><div class="ssr-editor">

def prosemirror_to_markdown(prosemirror_content):
    # 在这里实现将 ProseMirror 内容转换为 Markdown 的逻辑
    # 可以使用第三方库如 markdown 来处理转换过程
    # markdown_content = markdown.markdown(prosemirror_content)
    with open(prosemirror_content, 'r', encoding='utf-8') as file:
        html_doc = file.read()
        markdown_content = pypandoc.convert_text(html_doc, 'md', format='html')
        print(markdown_content, type(markdown_content))
    return markdown_content

if __name__ == "__main__":
    # url = "https://kdocs.cn/l/ckQ4sn6AvTXC"
    # html_path = "./tmp"
    # download_file(url, html_path)
    html_path = "./tmp/wpsapi测试文档.html"
    md_path = "./tmp/wpsapi测试文档.md"
    html_text = convert_html_to_md(html_path, md_path)
    # html_path = "./tmp/正文.html"
    # prosemirror_to_markdown(html_path)

    print("转换成功！")
