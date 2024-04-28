from src.utils.formatter import fformat, fill_keys

TEST_STRINGS = {
    'foo1': {
        'bar1': [
            '{key1} {key2}',
            '{key2} {key1}'
        ],
        'bar2': [
            'zoo1',
            'zoo2',
            'zoo3'
        ],
        'baR2': 'uppercase'
    },
    'foo': '{bar} {baza}'
}

TEST_DICTIONARY = {
    'test': ['test', 'tests'],
    'тест': ['тест', 'теста', 'тестов']
}


def _fformat(key_string: str, **kwargs) -> str:
    return fformat(key_string, __strings=TEST_STRINGS, __dictionary=TEST_DICTIONARY, **kwargs)


def _fill_keys(string: str, **kwargs) -> str:
    return fill_keys(string, __dictionary=TEST_DICTIONARY, **kwargs)


def test_simple():
    assert _fformat('') == ''
    assert _fformat('test') == 'test'
    assert _fformat('{}') == '{}'
    assert _fformat('{test}') == '{test}'
    assert _fformat('{test}', test='foo') == '{test}'


def test_key_finds():
    assert _fformat('foo1') == 'foo1'
    assert _fformat('foo') == '{bar} {baza}'
    assert _fformat('foo1.bar1') == 'foo1.bar1'

    assert _fformat('foo1.bar1.0') == '{key1} {key2}'
    assert _fformat('foo1.bar1.1') == '{key2} {key1}'
    assert _fformat('foo1.bar1.t') == '{key2} {key1}'
    assert _fformat('foo1.bar1.T') == '{key2} {key1}'
    assert _fformat('foo1.bar1.true') == '{key2} {key1}'
    assert _fformat('foo1.bar1.TruE') == '{key2} {key1}'

    assert _fformat('foo1.bar2.0') == 'zoo1'
    assert _fformat('foo1.bar2.2') == 'zoo3'
    assert _fformat('foo1.bar2.true') == 'foo1.bar2.true'

    assert _fformat('foo1.baR2') == 'uppercase'
    assert _fformat('foo1.baR2.0') == 'foo1.baR2.0'


def test_fill():
    assert _fill_keys('{{}}') == '{}'
    assert _fill_keys('{{{}}}') == '{{{}}}'
    assert _fill_keys('{{{test}}}') == '{{test}}'

    assert _fill_keys('{test}', test='value') == 'value'
    assert _fill_keys('{test}}}', test='value') == 'value}'
    assert _fill_keys('{{{test}', test='value') == '{value'
    assert _fill_keys('{{{test}}}', test='value') == '{value}'

    assert _fill_keys('{{{key1}}} {key2}{key3}', test='no', key1='val1', key3='val3') == '{val1} {key2}val3'


def test_fill_incline():
    assert _fill_keys('{key|test}') == '{key|test}'

    assert _fill_keys('{key|test}', key=1) == '1test'
    assert _fill_keys('{key||test}', key=1) == '1test'

    assert _fill_keys('{key| |test}', key=1) == '1 test'
    assert _fill_keys('{key| |test}', key='1') == '1 test'
    assert _fill_keys('{key| |test}', key=2) == '2 tests'
    assert _fill_keys('{key| |test}', key=0) == '0 tests'
    assert _fill_keys('{key| |test}', key=-1) == '-1 test'
    assert _fill_keys('{key| |test}', key=-2) == '-2 tests'

    assert _fill_keys('{key| |тест}', key=1) == '1 тест'
    assert _fill_keys('{key| |тест}', key=2) == '2 теста'
    assert _fill_keys('{key| |тест}', key=5) == '5 тестов'
    assert _fill_keys('{key| |тест}', key=12) == '12 тестов'
    assert _fill_keys('{key| |тест}', key=21) == '21 тест'
    assert _fill_keys('{key| |тест}', key=30) == '30 тестов'
    assert _fill_keys('{key| |тест}', key=44) == '44 теста'
    assert _fill_keys('{key| |тест}', key=0) == '0 тестов'
    assert _fill_keys('{key| |тест}', key=-1) == '-1 тест'
    assert _fill_keys('{key| |тест}', key=-2) == '-2 теста'
    assert _fill_keys('{key| |тест}', key=-5) == '-5 тестов'

    assert _fill_keys('{key| | |test}', key=1) == '1 | test'
    assert _fill_keys('{key| sep |test}', key=1) == '1 sep test'
    assert _fill_keys('{key| }}{{ |test}', key=1) == '1 }{ test'
    assert _fill_keys('{key| {{}} |test}', key=1) == '1 {} test'


def test_fill_depth():
    assert _fill_keys('{key| {key2} |test}', key=1, key2='val2') == '1 val2 test'
    assert _fill_keys('{key| {key2| {key3} {key4} |тест} |test}', key=1, key2=5, key3='val3', key4='val4') == '1 5 val3 val4 тестов test'
    assert _fill_keys('{key| {key2| {key3} {key4} |тест} |test}', key=5, key2=1, key3='val3', key4='val4') == '5 1 val3 val4 тест tests'
