import math

magnitudes = {
    'hundred': 100,
    'thousand': 1_000,
    'million': 10**6,
    'billion': 10**9,
    'trillion': 10**12,
    'quadrillion': 10**15,
    'quintillion': 10**18,
    'sextillion': 10**21,
    'septillion': 10**24,
    'octillion': 10**27,
    'nonillion': 10**30,
    'decillion': 10**33
}
# populate the magnitudes dict for magnitudes up to 1 decillion
# because if you're parsing numbers bigger than that then this library
# not having support is the least of your problems

decimal_words = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9
}

ordinal_magnitudes = {k + 'th': v for k, v in magnitudes.items()}

ordinal_words = {
    'zeroth': 0,
    'first': 1,
    'second': 2,
    'third': 3,
    'fourth': 4,
    'fifth': 5,
    'sixth': 6,
    'seventh': 7,
    'eighth': 8,
    'ninth': 9,
    'tenth': 10,
    'eleventh': 11,
    'twelfth': 12,
    'thirteenth': 13,
    'fourteenth': 14,
    'fifteenth': 15,
    'sixteenth': 16,
    'seventeenth': 17,
    'eighteenth': 18,
    'nineteenth': 19,
    'twentieth': 20,
    'thirtieth': 30,
    'fourtieth': 40,
    'fiftieth': 50,
    'sixtieth': 60,
    'seventieth': 70,
    'eightieth': 80,
    'ninetieth': 90,
    **ordinal_magnitudes
}

fraction_words = {
    'half': .5,
    'halves': .5,
    'quarter': .25,
    'quarters': .25
}
for k, v in ordinal_words.items():
    if v > 2:
        v = 1 / v
        fraction_words[k] = v
        fraction_words[k + 's'] = v
del(k)
del(v)

number_words = {
    **ordinal_words,
    **ordinal_magnitudes,
    **decimal_words,
    **fraction_words,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90,
    **magnitudes
}

# this comes in useful in num_to_word. Exclude plurals because they're a hassle to filter out later
number_words_backwards = {v: k for k, v in number_words.items() if not k.endswith('s')}
# comes in useful in both functions
_split_magnitudes = [
    i for i in list(magnitudes.keys()) + list(ordinal_magnitudes.keys()) if i not in ('hundred', 'hundredth')
]


class Word2Number():
    '''Class to group the internal functions used to convert words to numbers'''
    @staticmethod
    def split_by_magnitude(words: str):
        '''
        Splits strings by words of magnitude orders.

        Args:
            words (str): the string to split

        Returns:
            list: list of str

        Example:
            ```python
            print(Word2Number.split_by_magnitude('five million sixty five thousand two hundred and twenty three'))
            # ['five million', 'sixty five thousand', 'two hundred and twenty three']
            ```
        '''
        groups = []
        # split the number by magnitude, so 'four hundred thousand seven hundred and twelve'
        # gets split into ['four hundred thousand', 'seven hundred twelve']
        for m in reversed(_split_magnitudes):
            if m in words:
                # for each magnitude, if it's present in the phrase,
                # find it's right-most occurrence and everything after that
                # must be in the lower magnitude bracket
                pos = words.rindex(m)
                groups.append(words[: pos + len(m)].strip())
                words = words[pos + len(m):].strip()
        if words:
            # if there are numbers not grouped yet then them on the end
            # these are likely the ones that dont meet any magnitude bracket
            # (0-999)
            groups.append(words)

        return groups

    @staticmethod
    def group_by_magnitude_order(item: list):
        '''
        Groups a list of numbers according to changes in order of magnitude.
        They are grouped if the orders of magnitude stop descending.

        I use this to decide if a set of numbers should be a fraction or not because numbers
        are usually said in descending orders of magnitude (eg: one hundred and twenty three)
        whereas fractions will have equal or ascending orders of magnitude (eg: one thousandth).

        Args:
            item (list): this should be a list of integers or tuples. Tuples will be ignored
        '''
        result = []
        chunk = []
        last_order = None
        last_diff = 0
        for num in item:
            if type(num) == tuple:
                chunk.append(num)
            else:
                order = int(math.log10(num))
                if last_order is None:
                    last_order = order
                diff = order - last_order
                if diff > last_diff and chunk:
                    result.append(chunk)
                    chunk = []

                last_diff = diff
                last_order = order
                chunk.append(num)
        if chunk:
            result.append(chunk)

        return result

    @classmethod
    def process_chunk(cls, item: str, ordinals=False):
        '''
        Processes a 'chunk' and returns the number we think it is.
        Chunks should be of a single magnitude order (use `Word2Number.split_by_magnitude`)
        otherwise this will produce unexpected results.

        We calculate a total and a multiplier for the chunk. Regular number words are added
        to the total and magnitude words (thousand, million, ...) increase the multiplier.
        EG: "twenty three million" would have a total of 20 + 3
        and a multiplier of 1 million. Combined at the end they will make
        23 million.

        Args:
            item (str): the chunk to parse
            ordinals (bool): allow us to parse words like "third" as an ordinal (3rd) instead
                of as a fraction (1/3)
        '''
        multiplier = 1
        total = []
        latent_total = 0  # a total we add to the main total after the processing is done
        prefix = None  # the last non-number (invalid) word we have processed.
        # ^ See the fractions section for details on this
        previous = None  # the previous word we processed
        run_gbm = False  # see the fraction section for this ones usage
        fails = []  # invalid words we failed to parse

        if ' and ' in item:
            # items like 'ten and two thirds' should be interpreted as "10 + 2/3"
            it = []
            for i in item.split(' and '):
                # for each "and" statement
                tmp_total, tmp_multiplier = cls.process_chunk(i)
                tmp_result = (sum(tmp_total) or 1) * tmp_multiplier
                if type(tmp_result) == float:
                    # if it was a fraction we will add that up at the end
                    # eg: 'forty five and two thirds'. Process the 45
                    # then add 2/3 to it at the end
                    latent_total += tmp_result
                else:
                    # otherwise, we should process it with the rest of the phrase
                    # eg: 'four hundred and fifty six trillion' NEEDS to be
                    # processed as one item
                    it.append(i)

            # now, all processed items have been removed so we can
            # re-construct the items list and move on
            item = ' and '.join(it)

        item = item.split()
        for word in item:
            if word.isdigit():
                total.append(int(word))
            elif word in number_words:
                if word in _split_magnitudes:
                    # if the current word is a magnitude word then increase the multiplier
                    if word in magnitudes:
                        multiplier *= magnitudes[word]
                    else:
                        if not ordinals:
                            multiplier *= 1 / ordinal_magnitudes[word]
                        else:
                            run_gbm = True
                            total.append(ordinal_magnitudes[word])
                elif word == 'hundred' or (word == 'hundredth' and previous not in ('one', 'a')):
                    # for phrases like "one hundred 23 million"
                    # we don't want to increase the multiplier by 100, we want
                    # to add 100 to the total so we do that here
                    # but for phrases like 'one hundredth' we want to parse that
                    # as 1/100 (so not here)
                    if total:
                        # if total already contains some items then multiply all of them
                        # by 100
                        total = [sum(total) * 100]
                    else:
                        # if total doesn't contain any items then set
                        # it to 100
                        total = [100]
                elif word in fraction_words:
                    # the run_gbm bool controls whether we run our total through
                    # cls.group_by_magnitude_order to decide what to do about some fractions
                    run_gbm = True
                    if ordinals and word in ordinal_words:
                        # try to figure out what to do between cases such as:
                        # 'seventy fifth' (as in 75th) or 'seventy fifths' (as in 70*(1/5))
                        if previous:
                            # if this is not the first word in the sequence then treat as a fraction
                            # otherwise continue deciding
                            if word.endswith('s') or previous in ('one', 'a'):
                                # if the word ends with 's' then it's more likely to be
                                # pluralised fraction (eg: three quarters) and if the previous word is
                                # 'one' or 'a' then the phrase is probably 'one third' which is definitely
                                # a fraction
                                pass
                            else:
                                # if we have decided that it's probably not a fraction then process it as an ordinal
                                # and return to the beginning of the loop
                                total.append(ordinal_words[word])
                                continue

                    if word in ordinal_words:
                        # if the number could be a fraction or ordinal we attatch both
                        # and then decide which to use when we run the magnitude
                        # grouper
                        total.append((ordinal_words[word], fraction_words[word]))
                    else:
                        if prefix:
                            # eg: 'ten and a third' should be treated as 10+(2/3)
                            # so we append to total
                            total.append(fraction_words[word])
                        else:
                            # eg: 'two thirds'
                            multiplier *= fraction_words[word]
                            prefix = None
                else:
                    # otherwise they must be in the number dict
                    total.append(number_words[word])
            else:
                # dont parse words that arent numbers
                prefix = word
                fails.append(word)
            previous = word

        if run_gbm and (total and (len(total) > 1 or type(total[0]) == tuple)):
            # only run the gbm if we have the bool set and
            # 1. the first item in `total` is tuple (so its a fraction we need to decide on)
            # or 2. there are multiple items in `total`
            gbm = cls.group_by_magnitude_order(total)
            if len(gbm) == 1:
                t = []
                for i in total:
                    if type(i) == tuple:
                        multiplier *= i[1]
                    else:
                        t.append(i)
                total = t
            else:
                total = []
                for i in gbm[0]:
                    total.append(i[0] if type(i) == tuple else i)
                for group in gbm[1:]:
                    tmp = []
                    for i in group:
                        tmp.append(i[0] if type(i) == tuple else i)
                    multiplier *= 1 / sum(tmp)

        if latent_total:
            total.append(latent_total)

        if fails == item:
            # if every word was invalid
            raise ValueError('failed to parse. No valid number words detected')

        return total, multiplier


def word_to_num(words):
    '''
    Converts a word, like "three" or "sixty seven" to a number.
    Can also handle decimals and negative numbers.

    Args:
        words (str): the words to convert

    Returns:
        int
        float: if words contains "point" or "." it's treated as a decimal

    Raises:
        TypeError: if `words` is not a string
        ValueError: if `words` is invalid
    '''
    if type(words) != str:
        raise TypeError('word must be a string')

    # convert to lower case and strip whitespace
    words = words.lower().strip()
    # decide whether this will be a negative number
    if words.startswith('minus'):
        minus = True
        words = words[6:].strip()
    elif words.startswith('negative'):
        minus = True
        words = words[8:].strip()
    elif words.startswith('-'):
        minus = True
        words = words[1:]
    else:
        minus = False

    # replace hyphens, strip extra spaces
    words = words.replace('-', ' ').strip()

    # run some checks to see if we can get away with taking shortcuts instead
    # of doing any actual work :)
    if words.isdigit():
        words = int(words)
        return -words if minus else words
    elif words in ordinal_words:
        # we check ordinal words individually because words like 'third'
        # are overwritten by fraction words.
        words = ordinal_words[words]
        return -words if minus else words
    elif words in number_words:
        words = number_words[words]
        return -words if minus else words
    else:
        try:
            # words like '1.5' will fail the isdigit() check so try this
            words = float(words)
        except Exception:
            pass
        else:
            return -words if minus else words

    # make sure that the input value actually has some numbers for us
    if all(i not in number_words and i not in ordinal_words for i in words.split()):
        raise ValueError

    if 'point' in words or '.' in words:
        # so it's a decimal number decide on the delimiter, whether its the word "point"
        # or a decimal point then split the word by that delimiter
        delim = 'point' if 'point' in words else '.'
        if words.count(delim) > 1:
            raise ValueError(f'too many occurences of "{delim}" to be a valid decimal')
        left, right = words.split(delim)
        if not left:
            # EG: "point five"
            left = 0
        else:
            # the left is a regular number with regular rules so pass that to
            # word_to_num to sort out
            left = word_to_num(left)

        r = ''
        for i in right.split():
            if i.isdigit():
                r += i
            else:
                try:
                    # only sample from decimal_words because decimals should be in
                    # standard format, ie: noone should say "one point nineteen"
                    # it should be "one point one nine" and if we open the can
                    # of worms to parse that then we have to decide how to parse
                    # things like "one point twenty three". Is it 1.23 or 1.203?
                    r += str(decimal_words[i])
                except ValueError:
                    raise ValueError(f'invalid decimal word "{i}"')

        number = float(f'{left}.{r}')
        return -number if minus else number
    else:
        result = 0
        groups = Word2Number.split_by_magnitude(words)
        for chunk in groups:
            try:
                # only allow parsing of ordinals for the last item
                ordinals = chunk == groups[-1]
                if ' of ' in chunk:
                    # 'of' is treated as a multiplication
                    mults = []
                    # process each chunk
                    for i in chunk.split(' of '):
                        total, multiplier = Word2Number.process_chunk(i, ordinals=ordinals)
                        mults.append((sum(total) or 1) * multiplier)
                    # multiply all the chunks together at the end
                    num = mults[0]
                    for i in mults[1:]:
                        num *= i
                else:
                    # if there's not 'of' in the chunk then process normally
                    total, multiplier = Word2Number.process_chunk(chunk, ordinals=ordinals)
                    num = (sum(total) or 1) * multiplier

                result += num
            except ValueError:
                pass

        return -result if minus else result


def num_to_word(num, prefer_fraction_words=True):
    '''
    Converts a number into words. Can handle decimals and negatives

    Args:
        num (str, int or float): the number to convert
        prefer_fraction_words (bool): try to match decimals to fraction words.
            EG: 0.5 -> 'half' instead of 'zero point five'

    Returns:
        str

    Raises:
        TypeError: if num isn't int or float
    '''
    if type(num) == str:
        try:
            # we try an int first because huge numbers don't play nicely with floats
            num = int(num)
        except Exception:
            num = float(num)

    if type(num) not in (int, float):
        raise TypeError('num must be int or float')

    if type(num) == float and prefer_fraction_words:
        if abs(num) in number_words_backwards:
            # if we already have the value computed (eg: a third)
            minus = num < 0
            num = abs(num)
            word = number_words_backwards[num]
            if num < 1 and word in fraction_words:
                # eg: 'tenth' -> 'one tenth'
                word = 'one ' + word

            if minus:
                return 'negative ' + word
            else:
                return word

    if type(num) == float and not num.is_integer():
        num = str(num).split('.')

        # parse the left like a regular number because it essentially is
        left = num_to_word(int(num[0]))

        # since decimals are in a nice easy format we just
        # have to concatenate a string of words
        dw_backwards = {v: k for k, v in decimal_words.items()}
        right = ' '.join([dw_backwards[int(i)] for i in num[1]])

        return f'{left} point {right}'
    else:
        num = str(int(num)).strip()
        if num.startswith('-'):
            minus = True
            num = num.lstrip('-')
        else:
            minus = False

        if int(num) in number_words_backwards:
            # to handle simple cases like 0, 1, 2...
            if minus:
                return 'negative ' + number_words_backwards[int(num)]
            else:
                return number_words_backwards[int(num)]

        # split the number into 3 digit chunks
        num = num[::-1]
        chunks = [num[i: i + 3][::-1] for i in range(0, len(num), 3)]
        split_magnitudes = [''] + [i for i in _split_magnitudes if i not in ordinal_magnitudes]
        parsed = []

        if len(chunks) > len(split_magnitudes):
            # if we have more chunks than we have magnitudes then we are going to have
            # to stack magnitudes, EG: 10**15 -> one thousand trillion
            # and 10**18 -> million trillion.
            # this is technically a valid number word? It's better than having an IndexError

            # use this alias for convenience
            lsm = len(split_magnitudes)
            for i in range(0, len(chunks), lsm - 1):
                # chunk the list into chunks that can be handled by our selection of magnitudes,
                # process each chunk and insert into the parsed list
                w = num_to_word(''.join(reversed(chunks[i: i + lsm - 1])))
                if w != 'zero':
                    # for big numbers like 10**25 there will be many trailing zeroes
                    # so dont add those
                    parsed.insert(0, w)
            # tag the correct number of magnitudes onto the first word in the list
            # this should be the largest magnitude word we have repeated for the
            # number of chunks we created
            parsed[0] = parsed[0] + ((' ' + split_magnitudes[-1]) * (i // (lsm - 1)))
        else:
            for index, chunk in enumerate(chunks):
                # get the suffix for the chunk we are parsing
                addon = ''
                if split_magnitudes[index]:
                    addon = ' ' + split_magnitudes[index]

                if int(chunk) == 0:
                    continue
                elif int(chunk) in number_words_backwards and chunk != '100':
                    # the !='100' makes sure that we parse it as "one hundred" and not just "hundred"

                    # if this chunk is in the reversed number_words dict's keys (so it's a number)
                    # then slap that right in. No need to make any decisions ourselves
                    parsed.insert(0, number_words_backwards[int(chunk)] + addon)
                else:
                    chunk = str(int(chunk))  # gets rid of leading zeroes
                    tmp = ''
                    if len(chunk) == 3:
                        # if it's a 3 digit chunk then take the first digit
                        # and put the "X hundred"
                        tmp += number_words_backwards[int(chunk[0])] + ' hundred'
                        chunk = chunk[1:]
                    if int(chunk) != 0:
                        # if the rest of the chunk is just zeroes then don't parse it
                        if len(chunk) == 2:
                            if int(chunk) in number_words_backwards:
                                # if the chunk is directly mentioned in the dict, eg: 17
                                if tmp:
                                    tmp += ' and '
                                tmp += number_words_backwards[int(chunk)]
                            else:
                                # if the chunk isnt directly mentioned, eg: 25
                                # then we split the number into its digits, times the first by 10
                                # to get its word and combine with the second.
                                # eg: 25 -> (2*10) + 5 -> [20, 5] -> ['twenty', 'five']
                                if tmp:
                                    tmp += ' and '
                                tmp += (
                                    number_words_backwards[int(chunk[0]) * 10]
                                    + ' '
                                    + number_words_backwards[int(chunk[1])]
                                )
                        else:
                            # by now the length of the chunk must be 1 digit long
                            # therefore it must be in the dict
                            if tmp:
                                tmp += ' and '
                            tmp += number_words_backwards[int(chunk)]

                    if tmp:
                        # if we parsed any values then insert them here
                        parsed.insert(0, tmp + addon)

        if parsed[0] in magnitudes:
            # if we parsed something like 100 and it came out as "hundred"
            parsed.insert(0, 'one')

        if len(parsed) >= 2 and ' and ' not in ' '.join(parsed) and parsed[-1] not in split_magnitudes:
            # makes sure that the last segment of the number is joined by an 'and'
            # if it isn't already. So ['one hundred thousand', 'thirty two']
            # should end up joined, but ['four hundred thousand', 'one hundred and two']
            # should not
            parsed = ' '.join(parsed[:-1]) + ' and ' + parsed[-1]
        else:
            parsed = ' '.join(parsed)

        if minus:
            parsed = 'negative ' + parsed
        return parsed
