# страж для аргумента initial преобразователя Reduce
SENTINEL = object()


class Transducer:
    """Конвеер с оператором `>>` на преобразователях.

    Класс `Transducer` позволяет объединять `callable` объекты в цепочку
    преобразований с помощью оператора `>>`. `callable` конвертируются
    в звенья типа `Transducer`, которые объединяются в цепочки.

    Атрибуты:
        func (callable): `callable`, соответствующий первому звену цепочки
        label (str): вспомогательная строчка-бирка для `__repr__`
        chain (list): упорядоченная цепочка `callable` объектов
        chain_repr (list): бирки объектов цепочки

    """

    def __init__(self, func=lambda x: x, label='EmptyTransducer'):
        """Создается `Transduce` по `callable` и строчке-бирке.
        Без них создается пустой `Transduce`, возвращающий при вызове
        то же, что получил на вход."""
        self.func = func
        self.label = label
        self.chain = [self]
        self.chain_repr = [label]

    def __call__(self, s):
        """Объект `Transducer` является `callable` и возвращают результат
        вызова завеонутого в него `callable` от одного аргумента"""
        return self.func(s)

    def __rshift__(self, other):
        """Реализация работы оператора `>>` (левого)
        `Transducer >> not_callable` поднимает `TypeError`"""
        if not callable(other):
            raise TypeError
        return Transducer.concat(self, Transducer.from_callable(other))

    def __rrshift__(self, other):
        """Реализация работы оператора `>>` (правого)
        `Transducer >> not_callable` сворачивается, вычисляя результат"""
        if not callable(other):
            for func in self.chain:
                other = func(other)
            return other
        return Transducer.concat(Transducer.from_callable(other), self)

    @staticmethod
    def concat(Tr1, Tr2):
        """Вспомогательный метод для склеивания двух `Transducer`"""
        Tr = Transducer(Tr1.func, Tr1.label)
        Tr.chain = Tr1.chain + Tr2.chain
        Tr.chain_repr = Tr1.chain_repr + Tr2.chain_repr
        return Tr

    @staticmethod
    def from_callable(clb):
        """Вспомогательный метод, гарантирующий, что аргументами
        `concat` будут `Transducer` объекты"""
        if isinstance(clb, Transducer):
            return clb
        return Transducer(clb, str(clb))

    def __repr__(self):
        """Отображаем цепочку `Transduce` в порядке применения"""
        return 'input >> ' + ' >> '.join(self.chain_repr)


def Call(func):
    """Преобразователь, применяющий `func` к аргументу"""
    return Transducer(func, 'Call({})'.format(str(func)))


def Map(func):
    """Преобразователь, реализующий функциональность встроенной `map`"""

    def map_(s):
        return (func(x) for x in s)

    return Transducer(map_, 'Map({})'.format(str(func)))


def Filter(func=bool):
    """Преобразователь, реализующий функциональность встроенной `filter`"""

    def filter_(s):
        return (x for x in s if func(x))

    return Transducer(filter_, 'Filter({})'.format(str(func)))


def Reduce(func, initial=SENTINEL):
    """Преобразователь, реализующий функциональность `functools.reduce`"""
    default = (initial == SENTINEL)

    def reduce_(s):
        iter_s = iter(s)
        result = next(iter_s) if default else initial
        for x in iter_s:
            result = func(result, x)
        return result

    args_repr = str(func) if default else ', '.join((str(func), str(initial)))
    return Transducer(reduce_, args_repr)
