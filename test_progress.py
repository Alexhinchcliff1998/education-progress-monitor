import pytest
from progress import summarize,read
def test_statuses():
    results=[summarize(g,read('observations.csv')) for g in read('goals.csv')]
    assert [r['status'] for r in results]==['Target met','Progressing / review','Insufficient observations','Target met']
def test_duplicate():
    g=read('goals.csv')[0];row=read('observations.csv')[0]
    with pytest.raises(ValueError):summarize(g,[row,row])
