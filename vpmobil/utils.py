from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any, overload, Literal, Iterator, Callable, Mapping as _Mapping, Sequence as _Sequence
from dataclasses import dataclass
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
import re

type Mapping[KT, VT] = _Mapping[KT, VT]
"Mapping type von vpmobil-py (immutable Mapping, z.B. MappingProxyType)"
type Collection[T] = _Sequence[T]
"Collection type von vpmobil-py (immutable Sequenz, z.B. tuple)"

def prettyxml(object: ET.Element | ET.ElementTree) -> str:
    if isinstance(object, ET.ElementTree):
        element = object.getroot()
    elif isinstance(object, ET.Element):
        element = object
    else:
        raise TypeError
    
    string = ET.tostring(element, 'utf-8')
    reparsed = MD.parseString(string)
    return reparsed.toprettyxml(indent="\t")


def natural_sort_key(s: str) -> list[int | str]:
    """Sortierschlüssel für natürliche Sortierung von Strings mit Zahlen (z.B. '5a', '10a')."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', str(s))]

@overload
def find(element: ET.Element, path: str, mode: Literal["text"]) -> str | Literal[""]: ...
@overload
def find(element: ET.Element, path: str, mode: Literal["attrib"]) -> dict: ...
def find(element: ET.Element, path: str, mode: Literal["text", "attrib"]):
    target = element.find(path)
    if target is None:
        target = ET.Element(path.split('/')[-1])
    match mode:
        case "text":    return getattr(target, "text", "")
        case "attrib":  return getattr(target, "attrib", {})
        case _:         raise ValueError

    
def ElementBuilder(tag: str, text: str | Any | None = None, attrib: dict[str] = {}, *, children: list[ET.Element | None] = []) -> ET.Element:
    "Jedes None in `children` wird ignoriert und nicht angehangen"
    element = ET.Element(tag, attrib)
    if text:
        element.text = str(text)
    element.extend([c for c in children if c is not None])
    return element



def _default_adder[T](proxy: "SelectionProxy[T]", value: T) -> None:
    proxy.repository.append(value)


@dataclass(frozen=True, slots=True)
class SelectionProxy[T]:
    repository: list[T]
    selector: Callable[[T], bool]
    adder: Callable[[SelectionProxy[T], T], None] = field(default=_default_adder, repr=False, compare=False)

    @property
    def selection(self) -> tuple[T, ...]:
        return tuple(item for item in self.repository if self.selector(item))

    def __iter__(self) -> Iterator[T]:
        for item in self.repository:
            if self.selector(item):
                yield item

    def __len__(self) -> int:
        return sum(1 for item in self.repository if self.selector(item))

    def __contains__(self, item: object) -> bool:
        return any(item == candidate for candidate in self)

    def append(self, value: T) -> None:
        self.adder(self, value)

    def merge(self, value: T) -> None:
        self.append(value)

    def add(self, value: T) -> None:
        self.append(value)

    def delete(self, predicate: Callable[[T], bool]) -> int:
        if not callable(predicate):
            raise TypeError("predicate must be callable")

        removed = 0
        for index in range(len(self.repository) - 1, -1, -1):
            candidate = self.repository[index]
            if self.selector(candidate) and predicate(candidate):
                del self.repository[index]
                removed += 1
        return removed

    def clear(self) -> int:
        return self.delete(lambda _: True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self.selection)!r})"