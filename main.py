import asyncio
import datetime
import logging
import os

from telegraph.aio import Telegraph
import pytz

from database import database
from database import TelegraphUserInfo
from database import TelegraphPageInfo

AccountName = '美图工坊'
AuthorUrl = 'https://t.me/beautyimg'
DefaultTimezone = pytz.timezone('Asia/Shanghai')  # Example: Eastern Time (ET)

logging.basicConfig(level=logging.INFO)


def check_if_set_account() -> bool:
    """
    判断是否已经创建了用户
    :return: bool
    """
    user = database.query(TelegraphUserInfo).first()
    return user is not None


async def create_telegraph_user(username: str, author_url: str) -> Telegraph:
    """
    创建telegraph用户 并保存到db
    :param author_url:
    :param username:
    :return:
    """
    telegraph = Telegraph()
    account_info = await telegraph.create_account(short_name=username, author_name=username, author_url=author_url)
    try:
        # 保存订单记录
        user_info = TelegraphUserInfo()
        user_info.author_url = account_info['author_url']
        user_info.short_name = account_info['short_name']
        user_info.author_name = account_info['author_name']
        user_info.auth_url = account_info['auth_url']
        user_info.access_token = account_info['access_token']

        user_info.created_time = datetime.datetime.now(tz=DefaultTimezone)
        user_info.update_time = datetime.datetime.now(tz=DefaultTimezone)
        # 在这里执行你的数据库操作
        # 例如，插入一条新记录
        database.add(user_info)
        # 手动提交事务
        database.commit()
        logging.info(f"Created user successfully: {account_info}")
    except Exception as e:
        # 如果出现异常，回滚事务
        database.rollback()
        logging.error(f"插入记录失败: {str(e)}")
    return telegraph


async def init_telegaph_account() -> Telegraph:
    account_info = None
    if_set_account = check_if_set_account()
    if not if_set_account:
        # create a new account
        user = await create_telegraph_user(AccountName, AuthorUrl)
        account_info = user
    else:
        exist_user = database.query(TelegraphUserInfo).first()

        account_info = Telegraph(exist_user.access_token)

    return account_info


def find_images(directory: str) -> [str]:
    """
    遍历目录查找图片文件
    :param directory:
    :return: 图片绝对路径 列表
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp4']  # 添加其他可能的图片格式
    image_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension.lower() in image_extensions:
                image_files.append(os.path.join(root, file))

    return image_files


def split_list(input_list, chunk_size):
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


async def post_gallery_page(folder: str) -> str:
    """
    上传图片集合生成telegraph page
    :param folder:
    :return:
    """
    # 判断是否已经存在上传过 如果上传过则提示已经上传过
    page = database.query(TelegraphPageInfo).filter_by(image_folder_name=os.path.basename(folder)).first()
    if page:
        logging.info(f"当前图片目录: {folder},已经上传过,上传时间为: {page.created_time}")
        return

    images = find_images(folder)
    telegraph_account = await init_telegaph_account()
    batch_images = split_list(images, 5)
    files = []
    for batch_image in batch_images:
        b_files = await telegraph_account.upload_file(batch_image)
        files.extend(b_files)

    images_src = [i['src'] for i in files]
    images_src_str = ','.join(images_src)

    # Get the current date and time
    current_datetime = datetime.datetime.now()

    # Extract the date part
    formatted_date = current_datetime.strftime("%Y-%m-%d")
    page_title = os.path.basename(folder + "|" + formatted_date)

    image_divs = []
    for index, image in enumerate(images_src, start=1):
        div = f'<img src="https://telegra.ph/{image}" alt="pic-{index}">'
        image_divs.append(div)

    all_image_divs = ''.join(image_divs)
    html_content = all_image_divs
    author_name = AccountName
    author_url = AuthorUrl

    page_resp = await telegraph_account.create_page(title=page_title, html_content=html_content,
                                                    author_name=author_name,
                                                    author_url=author_url)
    # await asyncio.sleep(1)
    # print(f"{page_resp}")
    # print(f"{page_resp['url']}")
    # save record to db
    try:
        # 保存上传记录
        page_info = TelegraphPageInfo()

        page_info.image_folder_name = os.path.basename(folder)
        page_info.images_src = images_src_str
        page_info.article_link = page_resp['url']
        page_info.article_title = page_title
        page_info.image_counts = len(images_src)

        page_info.created_time = datetime.datetime.now(tz=DefaultTimezone)
        page_info.update_time = datetime.datetime.now(tz=DefaultTimezone)

        database.add(page_info)
        database.commit()
        logging.info(f"Save page info: {page_resp['url']} to database successfully!")
        return page_resp['url']
    except Exception as e:
        database.rollback()
        logging.error("Exception on saving page info: %s", e)
    return ''


async def main():
    folder = '/Users/sunrise/CodeGround/PycharmProjects/telegraph-images-upload/data/[XIAOYU语画界] VOL.1145 林星阑 美腿比基尼'
    folder2 = '/Users/sunrise/CodeGround/PycharmProjects/telegraph-images-upload/data/[XiuRen秀人网] No.7655 唐安琪 丝袜短裙'
    folder3 = '/Users/sunrise/CodeGround/PycharmProjects/telegraph-images-upload/data/test'
    page_link1 = await post_gallery_page(folder)
    page_link2 = await post_gallery_page(folder2)
    page_link3 = await post_gallery_page(folder3)


if __name__ == '__main__':
    asyncio.run(main())
