import unittest


class ProjectTest(unittest.TestCase):
    def test_user_set(self):
        from database import database
        from database import TelegraphUserInfo
        first = database.query(TelegraphUserInfo).first()
        print(first)

    def test_empty_str(self):
        if '':
            print("ok")


if __name__ == '__main__':
    pass
