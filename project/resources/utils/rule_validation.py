import re
from datetime import datetime

validations = {
    'string': lambda x: isinstance(x, str),
    'integer': lambda x: isinstance(x, int),
    'boolean': lambda x: isinstance(x, bool) or x.lower() in {'false', 'true'},
    'datetime': lambda x, dt_format=None: datetime.strptime(x, dt_format) if
    dt_format else datetime.fromisoformat(x),
    'required': lambda x: str(x),
    'max': lambda x, maximum: len(x) <= int(maximum),
    'min': lambda x, minimum: len(x) >= int(minimum),
    'pattern': lambda x, pattern: re.search(pattern, x),
    'fixed': lambda x: True
}

CODES = {
    'min:1': 'KEY000536',
    'min:10': 'KEY000541',
    'min:2': 'KEY000538',
    'min:20': 'KEY000540',
    'min:5': 'KEY000537',
    'min:7': 'KEY000539',
    'pattern:' r'^[^. |]+@([^. |]+\.)+[^. |]+$': 'KEY000418',
    'required': 'KEY000119',
}


class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors


def validate(obj, rules):
    to_validate = {k: [rule.split(':', 1) for rule in v] for k, v in
                   rules.items() if 'required' in v or obj.get(k) is not None}
    errors = []
    for key, rules in to_validate.items():
        for rule in rules:
            try:
                if not bool(validations[rule[0]](obj[key], *rule[1:])):
                    raise ValueError
            except ValueError:
                errors.append(
                    CODES.get(':'.join(rule), f'Validation <{" ".join(rule)}>' 
                                              f' failed for field <{key}>.'))

    if errors:
        raise ValidationError(errors)


def get_updatable(obj, rules):
    return filter(lambda x: 'fixed' not in rules.get(x[0], []), obj.items())
