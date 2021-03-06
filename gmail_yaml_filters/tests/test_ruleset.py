from gmail_yaml_filters.main import RuleSet
from gmail_yaml_filters.main import RuleAction
from gmail_yaml_filters.main import RuleCondition


def sample_rule(name):
    return {
        'from': '{}@msft.com'.format(name),
        'trash': True,
    }


def test_ruleset_from_dict():
    rules = RuleSet.from_object(sample_rule('bill'))
    assert len(rules) == 1
    assert sorted(rules)[0].flatten() == {
        'from': RuleCondition('from', 'bill@msft.com'),
        'shouldTrash': RuleAction('shouldTrash', 'true'),
    }


def test_ruleset_from_list():
    rules = sorted(RuleSet.from_object([sample_rule('bill'), sample_rule('steve')]))
    assert len(rules) == 2
    assert rules[0].flatten() == {
        'from': RuleCondition('from', 'bill@msft.com'),
        'shouldTrash': RuleAction('shouldTrash', 'true'),
    }
    assert rules[1].flatten() == {
        'from': RuleCondition('from', 'steve@msft.com'),
        'shouldTrash': RuleAction('shouldTrash', 'true'),
    }


def test_nested_conditions():
    ruleset = RuleSet.from_object({
        'from': 'steve@aapl.com',
        'archive': True,
        'more': {
            'subject': 'stop ignoring me',
            'archive': False,
        }
    })
    assert sorted(ruleset)[0].flatten() == {
        'from': RuleCondition('from', 'steve@aapl.com'),
        'subject': RuleCondition('subject', '"stop ignoring me"'),
        'shouldArchive': RuleAction('shouldArchive', 'false'),
    }
    assert sorted(ruleset)[1].flatten() == {
        'from': RuleCondition('from', 'steve@aapl.com'),
        'shouldArchive': RuleAction('shouldArchive', 'true'),
    }


def test_foreach():
    """
    Loop through each item in a list and create a rule from it.
    """
    ruleset = RuleSet.from_object({
        'for_each': ['steve', 'jony', 'tim'],
        'rule': {
            'from': '{item}@aapl.com',
            'star': True,
            'important': True,
            'more': [
                {'label': 'everyone', 'to': 'everyone@aapl.com'},
            ]
        }
    })
    assert sorted(rule.conditions for rule in ruleset) == [
        [RuleCondition(u'from', u'jony@aapl.com')],
        [RuleCondition(u'from', u'jony@aapl.com'), RuleCondition(u'to', u'everyone@aapl.com')],
        [RuleCondition(u'from', u'steve@aapl.com')],
        [RuleCondition(u'from', u'steve@aapl.com'), RuleCondition(u'to', u'everyone@aapl.com')],
        [RuleCondition(u'from', u'tim@aapl.com')],
        [RuleCondition(u'from', u'tim@aapl.com'), RuleCondition(u'to', u'everyone@aapl.com')],
    ]


def test_foreach_dict():
    """
    When the item in a for_each construct is a dict, format the rule
    using the dict's keys and values.
    """
    ruleset = RuleSet.from_object({
        'for_each': [
            {'team': 'retail', 'email': 'angela'},
            {'team': 'marketing', 'email': 'phil'},
            {'team': 'design', 'email': 'jony'},
        ],
        'rule': {
            'from': '{email}@aapl.com',
            'to': '{team}@aapl.com',
            'star': True,
        }
    })
    assert sorted(rule.conditions for rule in ruleset) == [
        [RuleCondition('from', 'angela@aapl.com'), RuleCondition('to', 'retail@aapl.com')],
        [RuleCondition('from', 'jony@aapl.com'), RuleCondition('to', 'design@aapl.com')],
        [RuleCondition('from', 'phil@aapl.com'), RuleCondition('to', 'marketing@aapl.com')],
    ]
