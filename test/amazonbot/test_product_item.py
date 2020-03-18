import unittest

from amazonbot.items import ProductItem


class ProductItemTest(unittest.TestCase):
    def setUp(self):
        with open('../data/product-page.html', 'r') as html:
            self.product_item = ProductItem(html=html)

    def test_name(self):
        self.assertEqual("Nature's Bounty Magnesium 500 mg, 200 Tablets", self.product_item.parse_name())

    def test_print(self):
        print(self.product_item)


if __name__ == '__main__':
    unittest.main()
