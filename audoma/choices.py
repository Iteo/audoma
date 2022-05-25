from typing import (
    Any,
    List,
    Tuple,
    TypeVar,
)


_T = TypeVar("_T")


def make_choices(name: str, choices_tuple: Tuple[Any, str, str]) -> _T:
    from collections import namedtuple

    """Factory function for quickly making a namedtuple suitable for use in a
    Django model as a choices attribute on a field. It will preserve order.

    Usage::

        class MyModel(models.Model):
            COLORS = make_choices('COLORS', (
                (0, 'BLACK', 'Black'),
                (1, 'WHITE', 'White'),
            ))
            colors = models.PositiveIntegerField(choices=COLORS)

        >>> MyModel.COLORS.BLACK
        0
        >>> MyModel.COLORS.get_choices()
        [(0, 'Black'), (1, 'White')]

        class OtherModel(models.Model):
            GRADES = make_choices('GRADES', (
                ('FR', 'FR', 'Freshman'),
                ('SR', 'SR', 'Senior'),
            ))
            grade = models.CharField(max_length=2, choices=GRADES)

        >>> OtherModel.GRADES.FR
        'FR'
        >>> OtherModel.GRADES.get_choices()
        [('FR', 'Freshman'), ('SR', 'Senior')]

    """

    class Choices(namedtuple(name, [name_ for val, name_, desc in choices_tuple])):
        __slots__ = ()
        _choices = tuple([desc for val, name_, desc in choices_tuple])

        def get_display(self, val: Any) -> str:
            return self._choices[self.index(val)]

        def get_choices(self) -> List[Tuple[Any, str]]:
            return list(zip(tuple(self), self._choices))

        def get_api_choices(self) -> List[Tuple[str, str]]:
            return list(zip(tuple(self._asdict()), tuple(self._choices)))

        def get_value_by_name(self, name: str) -> Any:
            return getattr(self, name)

    return Choices._make([val for val, name_, desc in choices_tuple])
