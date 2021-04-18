# w2n2w

Convert words to numbers and back again.  
Compatible with Python 3.6 and up.


## Why is this a thing?

There was one repo called [word2number](https://github.com/akshaynagpal/w2n) by [Akshay Nagpal](https://github.com/akshaynagpal) which converted words to numbers.
There was another repo called [num2word](https://github.com/MUKESHSIHAG/python_library_num2word) by [MUKESHSIHAG](https://github.com/MUKESHSIHAG) which converted numbers to words.  
To my knowledge there wasn't one that did both (also word2number appears un-maintained).  
So I forked and re-wrote word2number and here we are.


## What does it do?

Converts number words like "forty three" to integers/floats. Can handle numbers less than 1 quadrillion (and greater than negative 1 quadrillion)

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

## Things this library cannot do?

Ordinals and fractions are a no-go.

```python
import w2n2w
print(w2n2w.word_to_num('first'))
> ValueError: invalid number word "first"
print(w2n2w.word_to_num('seventy second'))
> ValueError: invalid number word "second"
print(w2n2w.word_to_num('one and one half'))
> ValueError: invalid number word "half"
print(w2n2w.word_to_num('one two three'))
> 6
```