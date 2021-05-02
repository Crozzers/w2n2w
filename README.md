# w2n2w

Convert words to numbers and back again.  
Compatible with Python 3.6 and up.


## Why is this a thing?

There was one repo called [word2number](https://github.com/akshaynagpal/w2n) by [Akshay Nagpal](https://github.com/akshaynagpal) which converted words to numbers.
There was another repo called [num2word](https://github.com/MUKESHSIHAG/python_library_num2word) by [MUKESHSIHAG](https://github.com/MUKESHSIHAG) which converted numbers to words.  
To my knowledge there wasn't one that did both (also word2number appears un-maintained).  
So I forked and re-wrote word2number and here we are.


## What does it do?

Converts number words like "forty three" to integers/floats.

```python
import w2n2w
print(w2n2w.word_to_num('forty three'))
> 43
print(w2n2w.word_to_num('twenty-two point nine one'))
> 22.91
print(w2n2w.word_to_num('one hundred and twenty three million four hundred and fifty six thousand seven hundred and eighty nine'))
> 123456789
print(w2n2w.word_to_num('negative twelve'))
> -12
print(w2n2w.word_to_num('12 thousand and thirty 8'))
> 1238
print(w2n2w.word_to_num('seventy first'))
> 71
```

It can also convert numbers into words

```python
import w2n2w
print(w2n2w.num_to_word(1234))
> 'one thousand two hundred and thirty four'
print(w2n2w.num_to_word(123456789))
> 'one hundred and twenty three million four hundred and fifty six thousand seven hundred and eighty nine'
print(w2n2w.num_to_word(1.52))
> 'one point five two'
print(w2n2w.num_to_word(-0.999))
> 'negative zero point nine nine nine'
print(w2n2w.num_to_word(0))
> 'zero'
```

In theory this library can handle any real number (positive or negative) but for numbers greater than or equal to one undecillion (10^36) you will start to face issues, as these numbers are represented in terms of the highest order of magnitude this library knows.  
So 10^36 is represented as `10^33 * 1000` or 'one thousand decillion'.

## Things this library cannot do?

Fractions are a no-go and some other examples may produce unexpected behaviour.

```python
import w2n2w
print(w2n2w.word_to_num('one and one half'))
> ValueError: invalid number word "half"
print(w2n2w.word_to_num('one two three'))
> 6
print(w2n2w.word_to_num('one thousandth'))  # you might expect 0.001
> 1000
print(w2n2w.word_to_num('one third'))
> 4
```