import requests
from bs4 import BeautifulSoup


def get_links_from_page(index):
    # 假设这是你的网页URL，这里需要替换为实际的URL
    url = 'https://www.edps.europa.eu/press-publications/press-news/news_en?page=' + str(index)

    try:
        # 发送HTTP请求获取网页内容
        response = requests.get(url)
        # 检查请求是否成功
        response.raise_for_status()

        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找类名为view-content的元素
        view_content = soup.find(class_='view-content')
        if view_content:
            # 查找类名为node__content clearfix的元素
            node_contents = view_content.find_all(class_='node__content clearfix')
            for node_content in node_contents:
                # 查找所有的a标签
                a_tags = node_content.find_all('a')
                for a_tag in a_tags:
                    # 获取a标签的href属性
                    link = a_tag.get('href')
                    if link:
                        if not link.startswith('http'):
                            link = 'https://www.edps.europa.eu' + link
                        print(f'insert into todo_url(url, source) value ("{link}", 6);')
        else:
            print("未找到类名为view-content的元素。")

    except requests.RequestException as e:
        print(f"请求发生错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")


if __name__ == '__main__':

    # for i in range(0, 57):
    get_links_from_page(31)


