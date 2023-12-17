import asyncio

from telegraph.aio import Telegraph


def check_if_set_account() -> bool:
    """
    判断是否已经创建了用户
    :return: bool
    """
    pass




async def main():
    telegraph = Telegraph()
    print(await telegraph.create_account(short_name='xiaoqianhp'))

    response = await telegraph.create_page(
        'Hey',
        html_content='<p>Hello, world!</p>',
    )
    print(response['url'])


if __name__ == '__main__':
    asyncio.run(main())
