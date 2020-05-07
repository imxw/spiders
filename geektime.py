# coding: utf-8

import requests
import json
import pdfkit
import os
import arrow
import sys


def get_all_columns():
    '''
    获取所有专栏信息
    '''
    url = 'https://time.geekbang.org/serv/v1/my/products/all'
    ret = requests.post(url, headers=headers)
    ret_data = ret.json()
    code = ret_data.get('code', '')

    if code >= 0:
        info = ret_data['data']

        return [x['list'] for x in info if x['id'] == 1][0]
    else:
        return []

def get_all_article_title_ids(column_id):
    '''
    获取指定专栏所有文章id及标题
    '''
    if not column_id:
        print('请输入专栏id')
        sys.exit(1)
    
    url = 'https://time.geekbang.org/serv/v1/column/articles'

    payload = {
        "cid": column_id,
        "order": "earliest",
        "sample": False,
        "size": 200
    }
    ret = requests.post(url, json=payload, headers=headers)
    ret_data = ret.json()
    code = ret_data.get('code', '')

    if code >= 0:
        info = ret_data['data']
        # print(json.dumps(info, ensure_ascii=False, indent=2))

        title_ids = {x['article_title']:x['id'] for x in info['list']}

        return title_ids
    else:
        return {} 

def get_article_metas(article_id):
    '''
    获取文章内容及其他一些元数据
    '''
    
    url = 'https://time.geekbang.org/serv/v1/article'
    
    payload = {
        "id": str(article_id),
        "include_neighbors": False
    }

    ret = requests.post(url, headers=headers, json=payload)
    ret_data = ret.json()

    code = ret_data.get('code', '')

    if code >= 0:
        info = ret_data['data']
        # print(json.dumps(info, ensure_ascii=False, indent=2))
        # article_metas = {}
        keys = ['article_content', 'article_title', 'author_name', 'article_ctime', 'article_cover']

        article_metas = {key:info[key] for key in keys}

        return article_metas
    else:
        return {} 

def get_article_comments(article_id):
    '''
    获取文章注释信息
    '''
    
    url = 'https://time.geekbang.org/serv/v1/comments'
    
    payload = {
        "aid": str(article_id),
        "prev": 0
    }

    ret = requests.post(url, headers=headers, json=payload)
    ret_data = ret.json()

    code = ret_data.get('code', '')

    # if code >= 0:
    #     info = ret_data['data']
    #     # print(json.dumps(info, ensure_ascii=False, indent=2))
    #     article_metas = {}
    #     article_metas['article_content'] = info['article_content']
    #     article_metas['article_title'] = info['article_title']
    #     return article_metas
    # else:
    #     return {} 


if __name__ == "__main__":


    cookies = "" # 浏览器F12 -> Network -> 找到cookies

    headers = {
        'Cookie': cookies,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 DID:3441301122:DID',
        'Referer': 'https://time.geekbang.org', 
        'Origin': 'https://time.geekbang.org',
        'Host': 'time.geekbang.org',
        'Content-Type': 'application/json'    
    }

    columns = get_all_columns()

    if not columns:
        print('你未购买任何专栏')
        sys.exit(0)
    
    title_ids = {x['title']:x['extra']['column_sku'] for x in columns}


    output_root = "/tmp"


    for col_title, col_sku in title_ids.items():

        output_path = os.path.join(output_root, col_title)

        col_html_paths = []

        if not os.path.isdir(output_path):
            os.makedirs(output_path)
        article_title_ids = get_all_article_title_ids(col_sku)

        sorted_title_ids = sorted(article_title_ids.items(), key=lambda item: item[1])

        for item in sorted_title_ids:

            title, id = item
            article_metas = get_article_metas(id)
            head_html = "<h1>{}</h1>\n<p>{} {}</p>\n<img src={}>".format(article_metas['article_title'], arrow.get(article_metas['article_ctime']).format('YYYY-MM-DD'), article_metas['author_name'], article_metas['article_cover'])

            article_html = '\n'.join([head_html, article_metas['article_content']])

            file_path = os.path.join(output_path, '{}.html'.format(title))

            with open(file_path, 'w') as f:
                f.write(article_html)
            col_html_paths.append(file_path)
        
        # 批量转pdf并合并（保存在脚本所在路径）
        pdfkit.from_file(col_html_paths, '{}.pdf'.format(col_title), options={'encoding': 'utf-8'})
