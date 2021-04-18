magnitudes = {
    'hundred': 100,
    'thousand': 1_000,
    'million': 1_000_000,
    'billion': 1_000_000_000,
    'trillion': 1_000_000_000_000
}

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

number_words = {
    **decimal_words,
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


def word_to_num(word):
    '''
    Converts a word, like "three", "sixty seven" to a number.
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
        words = word.replace('-', ' ').replace(' and ', ' ').lower().strip()

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
        else:
            # check that all of the items in words is in fact a valid number/word
            for w in words.split():
                if w not in number_words and not w.isdigit():
                    raise ValueError(f'invalid number word "{w}"')

        split_magnitudes = [i for i in reversed(magnitudes.keys()) if i != 'hundred']
        step_1 = []

        # split the number by magnitude, so 'four hundred thousand seven hundred and twelve'
        # gets split into ['four hundred thousand', 'seven hundred twelve']
        for m in split_magnitudes:
            if m in words:
                # for each magnitude, if it's present in the phrase,
                # find it's right-most occurrence and everything after that
                # must be in the lower magnitude bracket
                step_1.append(words[:words.rindex(m) + len(m)].strip())
                words = words[words.rindex(m) + len(m):].strip()
        if words:
            # if there are numbers not grouped yet then them on the end
            # these are likely the ones that dont meet any magnitude bracket
            # (0-999)
            step_1.append(words)

        if not step_1:
            # if we couldn't find anything parseable in the input
            raise ValueError('could not find any valid material to parse')

        # now we calculate the value of each segment by calculating a total
        # and a multiplier. Regular number words increase the total and magnitude
        # words increase the multiplier.
        # EG: "twenty three million" would have a total of 20 + 3
        # and a multiplier of 1 million. Combined at the end they will make
        # 23 million.
        step_2 = []
        for item in step_1:
            multiplier = 1
            total = []
            for word in item.split():
                if word in split_magnitudes:
                    # if the current word is a magnitude word then increase the multiplier
                    multiplier *= magnitudes[word]
                elif word == 'hundred':
                    # for phrases like "one hundred 23 million"
                    # we don't want to increase the multiplier by 100, we want
                    # to add 100 to the total so we do that here
                    if total:
                        # if total already contains some items then multiply all of them
                        # by 100
                        total = [sum(total) * 100]
                    else:
                        # if total doesn't contain any items then set
                        # it to 100
                        total = [100]
                else:
                    try:
                        # for words like "23" try to convert them directly
                        total.append(int(word))
                    except ValueError:
                        # otherwise they must be in the number dict
                        # if this fails then it was an invalid number but that's
                        # not a problem we deal with
                        total.append(number_words[word])

            if total:
                # if the total contains values, multiply them
                # by the multiplier
                step_2.append(sum(total) * multiplier)
            else:
                # otherwise just return the multiplier.
                # For items like "thousand"
                step_2.append(multiplier)

        if minus:
            return 0 - sum(step_2)
        else:
            return sum(step_2)


def num_to_word(num):
    '''
    Converts a number into words. Can handle decimals and negatives

    Args:
        num (str, int or float): the number to convert

    Returns:
        str
    '''
    if isinstance(num, float):
        num = str(num).split('.')
        # parse the left like a regular number because it essentially is
        left = num_to_word(int(num[0]))

        # since decimals are in a nice easy format we just
        # have to concatenate a string of words
        dw_backwards = {v: k for k, v in decimal_words.items()}
        right = ' '.join([dw_backwards[int(i)] for i in num[1]])

        return f'{left} point {right}'
    else:
        if isinstance(num, int):
            num = str(num)

        num = num.strip()
        if num.startswith('-'):
            minus = True
            num = num.lstrip('-')
        else:
            minus = False

        # create a dict where the keys and values are swapped. This is
        # useful later
        nw_backwards = {v: k for k, v in number_words.items()}

        if int(num) in nw_backwards:
            # to handle simple cases like 0, 1, 2...
            if minus:
                return 'negative ' + nw_backwards[int(num)]
            else:
                return nw_backwards[int(num)]

        # split the number into 3 digit chunks
        num = num[::-1]
        chunks = []
        for i in range(0, len(num), 3):
            chunks.insert(0, num[i: i + 3][::-1])

        split_magnitudes = [''] + [i for i in magnitudes.keys() if i != 'hundred']
        parsed = []

        for index, chunk in enumerate(chunks[::-1]):
            # get the suffix for the chunk we are parsing
            addon = ''
            if split_magnitudes[index]:
                addon = ' ' + split_magnitudes[index]

            if int(chunk) == 0:
                continue
            elif int(chunk) in nw_backwards and chunk != '100':
                # the !='100' makes sure that we parse it as "one hundred" and not just "hundred"

                # if this chunk is in the reversed number_words dict's keys (so it's a number)
                # then slap that right in. No need to make any decisions ourselves
                parsed.insert(0, nw_backwards[int(chunk)] + addon)
            else:
                chunk = str(int(chunk))  # gets rid of leading zeroes
                tmp = ''
                if len(chunk) == 3:
                    # if it's a 3 digit chunk then take the first digit
                    # and put the "X hundred"
                    tmp += nw_backwards[int(chunk[0])] + ' hundred'
                    chunk = chunk[1:]
                if int(chunk) != 0:
                    # if the rest of the chunk is just zeroes then don't parse it
                    if len(chunk) == 2:
                        if int(chunk) in nw_backwards:
                            # if the chunk is directly mentioned in the dict, eg: 17
                            if tmp:
                                tmp += ' and '
                            tmp += nw_backwards[int(chunk)]
                        else:
                            # if the chunk isnt directly mentioned, eg: 25
                            # then we split the number into its digits, times the first by 10
                            # to get its word and combine with the second.
                            # eg: 25 -> (2*10) + 5 -> [20, 5] -> ['twenty', 'five']
                            if tmp:
                                tmp += ' and '
                            tmp += nw_backwards[int(chunk[0]) * 10] + ' ' + nw_backwards[int(chunk[1])]
                    else:
                        # by now the length of the chunk must be 1 digit long
                        # therefore it must be in the dict
                        if tmp:
                            tmp += ' and '
                        tmp += nw_backwards[int(chunk)]

                if tmp:
                    # if we parsed any values then insert them here
                    parsed.insert(0, tmp + addon)

        if len(parsed) >= 2 and ' and ' not in ' '.join(parsed):
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
