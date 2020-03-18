import unittest

from amazonbot.items import ProductItem


class ProductItemTest(unittest.TestCase):
    def setUp(self):
        self.asin = 'B00H5PJ0HW'
        with open('../data/product-page.html', 'r') as html:
            self.product_item = ProductItem(html=html, asin=self.asin)

    def test_name(self):
        self.assertEqual("Nature's Bounty Magnesium 500 mg, 200 Tablets", self.product_item.parse_name())

    def test_print(self):
        print(self.product_item)
        self.product_item.save()


if __name__ == '__main__':
    unittest.main()
