from __future__ import annotations
from typing import Iterable, Any, Callable, Iterator, TYPE_CHECKING, overload
from collections.abc import Sequence, Mapping
from vpmobil.utils import natural_sort_key

if TYPE_CHECKING:
    from vpmobil.models import Stunde, Kurs, Aufsicht, Klausur

class Repository[T](Sequence[T]):
    def __init__(
            self,
            items: list[T] = [],
            adder: Callable[[Repository[T], T], None] = lambda repo, item: repo._items.append(item),
            sorter: Callable[[list[T]], list[T]] = lambda x: x
        ):
        self._adder = adder
        self._sorter = sorter
        self._items: list[T] = []
        for item in items:
            self.add(item)

    def __repr__(self) -> str:
        return "Repository(" + ", ".join(item.__repr__() for item in self._sorter(self._items)) + ")"

    def __iter__(self) -> Iterator[T]:
        return iter(self._sorter(self._items))

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def add(self, item: T) -> None:
        self._adder(self, item)
        self._items = self._sorter(self._items)

    def extend(self, items: Iterable[T]) -> None:
        for item in items:
            self.add(item)

    @overload
    def remove(self, item: T, /) -> None: ...
    @overload
    def remove(self, selector: Callable[[T], bool], /) -> None: ...
    def remove(self, arg, /) -> None:
        if isinstance(arg, T):
            self._items.remove(arg)
        for item in self._items:
            if arg(item):
                self.remove(item)

    def clear(self) -> None:
        self._items.clear()
    
    def sort(self, *, key: Callable[[T], Any] | None = None, reverse: bool = False) -> None:
        self._items.sort(key=key, reverse=reverse)


def stunden_adder(repo: Repository['Stunde'], stunde: 'Stunde') -> None:
    # Merging Logik für Stunden
    existing_stunde = next((
        s for s in repo._items 
        if s.periode == stunde.periode and s.kursnummer == stunde.kursnummer and 
        (s.klassen == stunde.klassen or s.lehrer == stunde.lehrer or s.räume == stunde.räume)
    ), None)

    if existing_stunde:
        existing_stunde.klassen.extend(stunde.klassen)
        existing_stunde.lehrer.extend(stunde.lehrer)
        existing_stunde.räume.extend(stunde.räume)
    else:
        repo._items.append(stunde)


def kurs_adder(repo: Repository['Kurs'], kurs: 'Kurs') -> None:
    # Merging Logik für Kurse
    existing_kurs = next((k for k in repo._items if k.kursnummer == kurs.kursnummer), None)

    if existing_kurs:
        existing_kurs.klassen.extend(kurs.klassen)
    else:
        repo._items.append(kurs)


def aufsicht_adder(repo: Repository['Aufsicht'], aufsicht: 'Aufsicht') -> None:
    # Merging Logik für Aufsichten
    existing_aufsicht = next((
        a for a in repo._items 
        if a.beginn == aufsicht.beginn and a.ortinfo == aufsicht.ortinfo
    ), None)

    if existing_aufsicht:
        existing_aufsicht.lehrer.extend(aufsicht.lehrer)
    else:
        repo._items.append(aufsicht)


def uniqueness_adder[T](repo: Repository[T], string: T) -> None:
    if string in repo:
        return
    repo._items.append(string)


class SelectionProxy[T](Sequence[T]):
    """Ein dynamischer View auf ein Repository, basierend auf einer Filter-Bedingung."""
    def __init__(self, repository: Repository[T], selector: Callable[[T], bool]):
        self.repository = repository
        self.selector = selector

    def __iter__(self) -> Iterator[T]:
        return (item for item in self.repository if self.selector(item))

    def __len__(self) -> int:
        return sum(1 for item in self.repository if self.selector(item))

    def __getitem__(self, index):
        # Um list-like Indexierung zu unterstützen, iterieren wir und wählen das nth Element
        items = [item for item in self.repository if self.selector(item)]
        return items[index]

    def add(self, item: T) -> None:
        """Fügt ein Element in das unterliegende Repository hinzu."""
        self.repository.add(item)
    
    def __repr__(self) -> str:
        return f"SelectionProxy({list(self)!r})"

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


class GroupedSelectionProxy[T](Mapping[Any, SelectionProxy[T]]):
    """Ein Dictionary-ähnlicher View auf ein Repository, der die gefilterten Ergebnisse gruppiert."""
    def __init__(self, repository: Repository[T], selector: Callable[[T], bool], group_key: Callable[[T], Any]):
        self.repository = repository
        self.selector = selector
        self.group_key = group_key

    def _groups(self) -> dict[Any, list[T]]:
        groups = {}
        for item in self.repository:
            if self.selector(item):
                k = self.group_key(item)
                groups.setdefault(k, []).append(item)
        return groups

    def __getitem__(self, key: Any) -> SelectionProxy[T]:
        groups = self._groups()
        if key not in groups:
            raise KeyError(key)
        return SelectionProxy(
            self.repository, 
            lambda item: self.selector(item) and self.group_key(item) == key
        )

    def __iter__(self) -> Iterator[Any]:
        # Sortiere Schlüssel für reproduzierbare Iterationsreihenfolge
        return iter(sorted(self._groups().keys(), key=lambda x: natural_sort_key(str(x))))

    def __len__(self) -> int:
        return len(self._groups())

    def __repr__(self) -> str:
        return f"GroupedSelectionProxy({dict(self)!r})"

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self
