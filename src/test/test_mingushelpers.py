import os
import unittest
import sys

sys.path.append(os.path.pardir)

from mingus.containers.Note import Note
from mingus.containers.NoteContainer import NoteContainer

import mingushelpers


class test_notes_match(unittest.TestCase):
    def test_single_unison_match(self):
        nc1, nc2 = NoteContainer(["A-4"]), NoteContainer(["A-4"])
        self.assertTrue(mingushelpers.notes_match(nc1, nc2))

    def test_single_octave_match(self):
        nc1, nc2 = NoteContainer(["A-4"]), NoteContainer(["A-5"])
        self.assertTrue(mingushelpers.notes_match(nc1, nc2))

    def test_different_notes_nomatch(self):
        nc1, nc2 = NoteContainer(["A-4"]), NoteContainer(["B-4"])
        self.assertFalse(mingushelpers.notes_match(nc1, nc2))

    def test_different_note_counts_nomarch(self):
        nc1, nc2 = NoteContainer(["A-4", "B-5"]), NoteContainer(["A-4"])
        self.assertFalse(mingushelpers.notes_match(nc1, nc2))

    def test_empty_match(self):
        self.assertTrue(mingushelpers.notes_match(NoteContainer(),
                                                  NoteContainer()))

    def test_multiple_octave_match(self):
        nc1, nc2 = NoteContainer(["A-3", "B-4"]), NoteContainer(["A-5", "B-5"])
        self.assertTrue(mingushelpers.notes_match(nc1, nc2))


if __name__ == '__main__':
    unittest.main()
