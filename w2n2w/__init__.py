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
    'third': 1 / 3,
    'quarter': .25,
    **{k: 1 / v for k, v in ordinal_words.items() if v > 4}
}
fraction_words = {
    **fraction_words,
    # add words like 'thirds' and 'quarters'
    **{k + 's': v for k, v in fraction_words.items() if v < .5}
}

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


def word_to_num(word):
    '''
    Converts a word, like "three" or "sixty seven" to a number.
    Can also handle decimals and negative numbers.

    Args:
        word (str): the word to convert

    Returns:
        int
        float: if the phrase contains the word 'point' or '.' it is treated as a decimal
    '''
    if type(word) != str:
        raise ValueError('word must be a string')

    if 'point' in word or '.' in word:
        # so it's a decimal number decice on the delimiter, whether its the word "point"
        # or a decimal point then split the word by that delimiter
        delim = 'point' if 'point' in word else '.'
        if word.count(delim) > 1:
            raise ValueError(f'too many occurences of "{delim}" to be a valid decimal')
        left, right = word.split(delim)
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

        return float(f'{left}.{r}')
    else:
        # replace hyphens, strip extra spaces and split
        words = word.replace('-', ' ').lower().strip()

        # decide whether this will be a negative number
        if words.startswith('minus'):
            minus = True
            words = words[6:].strip()
        elif words.startswith('negative'):
            minus = True
            words = words[8:].strip()
        else:
            minus = False

        if words.isdigit():
            # if the word is a digit (EG: '25') then just
            # convert straight away
            if minus:
                return 0 - int(words)
            else:
                return int(words)

        # if we have this pre-defined then return that straight away
        if words in ordinal_words:
            # check ordinals before all else because the fractions override the
            # ordinals in the number_words dict, so treat strings such as 'hundredth'
            # as an ordinal and 'one hundredth' as a fraction
            if minus:
                return 0 - ordinal_words[words]
            else:
                return ordinal_words[words]
        elif words in number_words:
            if minus:
                return 0 - number_words[words]
            else:
                return number_words[words]

        def process_item(item, fract_status=False):
            # now we calculate the value of each segment by calculating a total
            # and a multiplier. Regular number words increase the total and magnitude
            # words increase the multiplier.
            # EG: "twenty three million" would have a total of 20 + 3
            # and a multiplier of 1 million. Combined at the end they will make
            # 23 million.
            multiplier = 1
            total = []
            latent_total = 0  # a total we add to the main total after the processing is done
            prefix = None  # see the fractions section for how this is used
            previous = None  # the previous word we processed
            fails = 0  # how many words were deemed 'invalid'

            if ' and ' in item:
                # items like 'ten and two thirds' should be interpreted as "10 + 2/3"
                it = []
                for i in item.split(' and '):
                    # for each "and" statement
                    j, fract = process_item(i, fract_status=True)
                    if fract:
                        # if it was a fraction we will add that up at the end
                        # eg: 'forty five and two thirds'. Process the 45
                        # then add 2/3 to it at the end
                        latent_total += j
                    else:
                        # otherwise, we should process it with the rest of the phrase
                        # eg: 'four hundred and fifty six trillion' NEEDS to be
                        # processed as one item
                        it.append(i)

                # now, all processed items have been removed so we can
                # re-construct the items list and move on
                item = ' and '.join(it)

            if ' of ' in item:
                # items like 'two thirds of ten' should be interpreted as "2/3 * 10"
                item = item.split(' of ', 1)
                multiplier *= process_item(item[1])
                item = item[0]

            item = item.split()
            for word in item:
                if word in _split_magnitudes:
                    # if the current word is a magnitude word then increase the multiplier
                    if word in magnitudes:
                        multiplier *= magnitudes[word]
                    else:
                        multiplier *= ordinal_magnitudes[word]
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
                    if word in ordinal_words:
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
                    if prefix:
                        # eg: two and a third
                        # `prefix` differs from `previous` in that prefix only stores
                        # non-number words for cases like this
                        total.append(fraction_words[word])
                        prefix = None
                    else:
                        # eg: two thirds
                        multiplier *= fraction_words[word]
                else:
                    try:
                        # for words like "23" try to convert them directly
                        total.append(int(word))
                    except ValueError:
                        # otherwise they must be in the number dict
                        # if this fails then it was an invalid number
                        if word in number_words:
                            total.append(number_words[word])
                        else:
                            prefix = word
                            fails += 1
                previous = word

            total = sum(total) + latent_total

            if total:
                # if the total contains values, multiply them
                # by the multiplier
                total = total * multiplier
                if fract_status:
                    return total, type(total) == float
                else:
                    return total
            else:
                if fails == len(item):
                    # if every word in `item` was deemed not a number word
                    # then raise an exception
                    raise ValueError('No valid number words found')
                # otherwise just return the multiplier.
                # For items like "thousand"
                if fract_status:
                    return multiplier, False
                else:
                    return multiplier

        result = []
        # split the number by magnitude, so 'four hundred thousand seven hundred and twelve'
        # gets split into ['four hundred thousand', 'seven hundred twelve']
        for m in reversed(_split_magnitudes):
            if m in words:
                # for each magnitude, if it's present in the phrase,
                # find it's right-most occurrence and everything after that
                # must be in the lower magnitude bracket
                result.append(
                    process_item(
                        words[: words.rindex(m) + len(m)].strip()
                    )
                )
                words = words[words.rindex(m) + len(m):].strip()
        if words:
            # if there are numbers not grouped yet then them on the end
            # these are likely the ones that dont meet any magnitude bracket
            # (0-999)
            result.append(process_item(words))

        if not result:
            # if we found no valid material to parse
            raise ValueError('no valid number words detected')

        if minus:
            return 0 - sum(result)
        else:
            return sum(result)


def num_to_word(num, prefer_fraction_words=True):
    '''
    Converts a number into words. Can handle decimals and negatives

    Args:
        num (str, int or float): the number to convert
        prefer_fraction_words (bool): try to match decimals to fraction words.
            EG: 0.5 -> 'half' instead of 'zero point five'

    Returns:
        str
    '''
    num = float(num)
    if prefer_fraction_words:
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

    if not num.is_integer():
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
        split_magnitudes = [''] + _split_magnitudes
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
