from src.utils.validators import validate_string


def test_simple():
    assert validate_string('')
    assert validate_string('test')
    assert not validate_string('{}')
    assert validate_string('{test}')
    assert not validate_string('{тест}')
    assert not validate_string('{te-st}')
    assert validate_string('{test1} {test2}')
    assert validate_string('{test1}{test2}')
    assert validate_string('{az09_}')


def test_brackets():
    assert validate_string('{{}}')
    assert not validate_string('{{{}}}')
    assert validate_string('{{{test}}}')
    assert not validate_string('{ }{ { }')
    assert not validate_string('}{')
    assert validate_string('}}{{')


def test_incline():
    assert not validate_string('{test|12}')
    assert validate_string('{test|word}')
    assert not validate_string('{te\\|st|word}')
    assert not validate_string('{test|}')
    assert not validate_string('{|test}')
    assert validate_string('{test|test|test}')
    assert validate_string('{test|||word}')
    assert validate_string('{test|| |word}')
    assert validate_string('{test| ||word}')
    assert validate_string('{test| | |word}')


def test_depth():
    assert validate_string('{test1|{test2}|word}')
    assert validate_string('{test1|{test2|word}|word}')
    assert validate_string('{test1|{test2|word}{test3|word}|word}')
    assert validate_string('{test1|{test2|{test3|word}|word}|word}')
