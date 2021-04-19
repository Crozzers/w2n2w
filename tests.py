import unittest
import w2n2w


class TestWordToNumber(unittest.TestCase):
    def test_positives(self):
        self.assertEqual(w2n2w.word_to_num("two million three thousand nine hundred and eighty four"), 2003984)
        self.assertEqual(w2n2w.word_to_num("nineteen"), 19)
        self.assertEqual(w2n2w.word_to_num("two thousand and nineteen"), 2019)
        self.assertEqual(w2n2w.word_to_num("two million three thousand and nineteen"), 2003019)
        self.assertEqual(w2n2w.word_to_num('three billion'), 3000000000)
        self.assertEqual(w2n2w.word_to_num('three million'), 3000000)
        self.assertEqual(w2n2w.word_to_num('one hundred twenty three million four hundred fifty six thousand seven hundred and eighty nine'), 123456789)
        self.assertEqual(w2n2w.word_to_num('eleven'), 11)
        self.assertEqual(w2n2w.word_to_num('nineteen billion and nineteen'), 19000000019)
        self.assertEqual(w2n2w.word_to_num('one hundred and forty two'), 142)
        self.assertEqual(w2n2w.word_to_num('112'), 112)
        self.assertEqual(w2n2w.word_to_num('11211234'), 11211234)
        self.assertEqual(w2n2w.word_to_num('five'), 5)
        self.assertEqual(w2n2w.word_to_num('two million twenty three thousand and forty nine'), 2023049)
        self.assertEqual(w2n2w.word_to_num('two point three'), 2.3)
        self.assertEqual(w2n2w.word_to_num('two million twenty three thousand and forty nine point two three six nine'), 2023049.2369)
        self.assertEqual(w2n2w.word_to_num('one billion two million twenty three thousand and forty nine point two three six nine'), 1002023049.2369)
        self.assertEqual(w2n2w.word_to_num('point one'), 0.1)
        self.assertEqual(w2n2w.word_to_num('point'), 0)
        # self.assertEqual(w2n2w.word_to_num('point nineteen'), 0)  I don't if this behaviour makes sense or not
        self.assertEqual(w2n2w.word_to_num('one hundred thirty-five'), 135)
        self.assertEqual(w2n2w.word_to_num('hundred'), 100)
        self.assertEqual(w2n2w.word_to_num('thousand'), 1000)
        self.assertEqual(w2n2w.word_to_num('million'), 1000000)
        self.assertEqual(w2n2w.word_to_num('billion'), 1000000000)
        self.assertEqual(w2n2w.word_to_num('nine point nine nine nine'), 9.999)
        # self.assertEqual(w2n2w.word_to_num('seventh point nineteen'), 0)  I don't if this behaviour makes sense or not
        self.assertEqual(w2n2w.word_to_num('minus twenty-two point two six'), -22.26)
        self.assertEqual(w2n2w.word_to_num('negative ninety nine'), -99)
        self.assertEqual(w2n2w.word_to_num('negative zero'), 0)
        self.assertEqual(w2n2w.word_to_num('one octillion four hundred and sixty three trillion and nine'), 10**27 + (463 * 10**12) + 9)
        self.assertEqual(w2n2w.word_to_num('one million decillion'), 10**6 * 10**33)

    def test_negatives(self):
        self.assertRaises(ValueError, w2n2w.word_to_num, '-')
        self.assertRaises(ValueError, w2n2w.word_to_num, 'on')
        # self.assertRaises(ValueError, w2n2w.word_to_num, 'million four million')
        # I'm not sure what to do with this ^ so I'll come back to it
        self.assertRaises(ValueError, w2n2w.word_to_num, 'one billion point two million twenty three thousand and forty nine point two three six nine')
        self.assertRaises(ValueError, w2n2w.word_to_num, 112)


class TestNumberToWord(unittest.TestCase):
    def test_positives(self):
        self.assertEqual(w2n2w.num_to_word(2_003_984), "two million three thousand nine hundred and eighty four")
        self.assertEqual(w2n2w.num_to_word(19), "nineteen")
        self.assertEqual(w2n2w.num_to_word(2019), "two thousand and nineteen")
        self.assertEqual(w2n2w.num_to_word(2_003_019), "two million three thousand and nineteen")
        self.assertEqual(w2n2w.num_to_word(3_000_000_000), "three billion")
        self.assertEqual(w2n2w.num_to_word(3_000_000), "three million")
        self.assertEqual(w2n2w.num_to_word(123456789), "one hundred and twenty three million four hundred and fifty six thousand seven hundred and eighty nine")
        self.assertEqual(w2n2w.num_to_word(11), "eleven")
        self.assertEqual(w2n2w.num_to_word(19_000_000_019), "nineteen billion and nineteen")
        self.assertEqual(w2n2w.num_to_word(142), "one hundred and forty two")
        self.assertEqual(w2n2w.num_to_word(112), "one hundred and twelve")
        self.assertEqual(w2n2w.num_to_word(11_211_234), "eleven million two hundred and eleven thousand two hundred and thirty four")
        self.assertEqual(w2n2w.num_to_word(5), "five")
        self.assertEqual(w2n2w.num_to_word(2_023_049), "two million twenty three thousand and forty nine")
        self.assertEqual(w2n2w.num_to_word(2.3), "two point three")
        self.assertEqual(w2n2w.num_to_word(2023049.2369), "two million twenty three thousand and forty nine point two three six nine")
        self.assertEqual(w2n2w.num_to_word(1002023049.2369), "one billion two million twenty three thousand and forty nine point two three six nine")
        self.assertEqual(w2n2w.num_to_word(0.1), "zero point one")
        self.assertEqual(w2n2w.num_to_word(0), "zero")
        self.assertEqual(w2n2w.num_to_word(100), "hundred")
        self.assertEqual(w2n2w.num_to_word(1_000), "thousand")
        self.assertEqual(w2n2w.num_to_word(1_000_000), "million")
        self.assertEqual(w2n2w.num_to_word(1_000_000_000), "billion")
        self.assertEqual(w2n2w.num_to_word(1_000_000_000_000), "trillion")
        self.assertEqual(w2n2w.num_to_word(9.999), "nine point nine nine nine")
        self.assertEqual(w2n2w.num_to_word(-123), 'negative one hundred and twenty three')
        self.assertEqual(w2n2w.num_to_word(-29.666), 'negative twenty nine point six six six')
        self.assertEqual(w2n2w.num_to_word(-0), 'zero')

        self.assertEqual(10**27 + (463 * 10**12) + 9, w2n2w.word_to_num('one octillion four hundred and sixty three trillion and nine'))
        self.assertEqual(10**6 * 10**33, w2n2w.word_to_num('one million decillion'))

    def test_negatives(self):
        self.assertRaises(ValueError, w2n2w.num_to_word, 'not a num')
        self.assertRaises(ValueError, w2n2w.num_to_word, 'one hundred and six')
        self.assertRaises(ValueError, w2n2w.num_to_word, '100 6')

    def test_range(self):
        # only do 2 million because any more than that takes too long
        for i in range(-500_000, 1_500_000, 3):
            w = w2n2w.num_to_word(i)
            n = w2n2w.word_to_num(w)
            # if we can convert our number to words and those
            # words translate back into the same number then consider
            # it a success
            self.assertEqual(n, i)


if __name__ == '__main__':
    unittest.main()
