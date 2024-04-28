from src.utils.phone_number import is_phone_number

__test_numbers = [
    '+79261234567',
    '89261234567',
    '79261234567',
    '+7 926 123 45 67',
    '8(926)123-45-67',
    '123-45-67',
    '9261234567',
    '79261234567',
    '(495)1234567',
    '(495) 123 45 67',
    '89261234567',
    '8-926-123-45-67',
    '8 927 1234 234',
    '8 927 12 12 888',
    '8 927 12 12 888',
    '8 927 123 8 123',
]

__wrong_numbers = [
    'test',
    '+7926123456',
    '8926123456',
    '+79261 test 234567'
]


def test_simple():
    assert is_phone_number('+79261234567')
    assert is_phone_number('89261234567')
    assert is_phone_number('79261234567')
    assert is_phone_number('+7 926 123 45 67')
    assert is_phone_number('8(926)123-45-67')
    # assert is_phone_number('123-45-67')
    assert is_phone_number('9261234567')
    assert is_phone_number('79261234567')
    assert is_phone_number('(495)1234567')
    assert is_phone_number('(495) 123 45 67')
    assert is_phone_number('89261234567')
    assert is_phone_number('8-926-123-45-67')
    assert is_phone_number('8 927 1234 234')
    assert is_phone_number('8 927 12 12 888')
    assert is_phone_number('8 927 12 12 888')
    assert is_phone_number('8 927 123 8 123')

    assert not is_phone_number('test')
    assert not is_phone_number('+7926126')
    assert not is_phone_number('892636')
    assert not is_phone_number('+79261 test 234567')
