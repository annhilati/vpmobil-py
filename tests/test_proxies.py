from vpmobil.utils import SelectionProxy

def test_SelectionProxy():

    repo: list[int] = [0, 1, 2, 3, 4, 5, 100, 200, 300, 400, 500]

    proxy = SelectionProxy(repo, lambda i: i < 100, lambda self, v: self.repository.append(v) if v not in self.repository else None)

    # selector funktioniert
    for n, i in enumerate(proxy):
        # Enumerierung funktioniert nur, weil das repo sortiert ist!
        assert n == i

    # __contains__ funktioniert
    assert 0 in proxy

    # 
    proxy.merge(6)
    assert 6 in proxy