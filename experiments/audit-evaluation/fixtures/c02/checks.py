def expect_cost(function, total, expected):
    actual = function(total)
    assert actual == expected
