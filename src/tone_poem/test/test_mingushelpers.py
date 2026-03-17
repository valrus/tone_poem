from mingus.containers import NoteContainer

from .. import mingushelpers


def test_single_unison_match():
    nc1, nc2 = NoteContainer(["A-4"]), NoteContainer(["A-4"])
    assert mingushelpers.notes_match(nc1, nc2)


def test_single_octave_match():
    nc1, nc2 = NoteContainer(["A-4"]), NoteContainer(["A-5"])
    assert mingushelpers.notes_match(nc1, nc2)


def test_different_notes_nomatch():
    nc1, nc2 = NoteContainer(["A-4"]), NoteContainer(["B-4"])
    assert not (mingushelpers.notes_match(nc1, nc2))


def test_different_note_counts_nomarch():
    nc1, nc2 = NoteContainer(["A-4", "B-5"]), NoteContainer(["A-4"])
    assert not (mingushelpers.notes_match(nc1, nc2))


def test_empty_match():
    assert mingushelpers.notes_match(NoteContainer(), NoteContainer())


def test_multiple_octave_match():
    nc1, nc2 = NoteContainer(["A-3", "B-4"]), NoteContainer(["A-5", "B-5"])
    assert mingushelpers.notes_match(nc1, nc2)
