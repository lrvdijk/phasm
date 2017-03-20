import enum
from typing import List, Tuple, NamedTuple

import parasail

from phasm.utils import round_up

dna_matrix = parasail.create_matrix("ACTG", 1, -3)


class Strand(enum.IntEnum):
    SAME = 0
    OPPOSITE = 1


class AlignmentType(enum.IntEnum):
    OVERLAP_AB = 0
    OVERLAP_BA = 1
    A_CONTAINED = 2
    B_CONTAINED = 3


_Read = NamedTuple(
    'Read',
    [('id', str), ('moviename', str), ('well', str), ('pulse_start', int),
     ('pulse_end', int), ('length', int)]
)


class Read(_Read):
    def __len__(self) -> int:
        return self.length

    def __str__(self) -> str:
        return self.id

    def __hash__(self) -> int:
        return hash(self.id)


_LocalAlignment = NamedTuple(
    '_LocalAlignment',
    [('a', Read), ('b', Read), ('strand', Strand), ('arange', Tuple[int, int]),
     ('brange', Tuple[int, int]), ('differences', int),
     ('tracepoints', List[Tuple[int, int]])]
)


class LocalAlignment(_LocalAlignment):
    def get_overlap_length(self) -> int:
        return max(self.arange[1] - self.arange[0],
                   self.brange[1] - self.brange[0])

    def get_error_rate(self) -> float:
        return self.differences / self.get_overlap_length()

    def get_overhang(self) -> int:
        return (min(self.arange[0], self.brange[0]) +
                min(len(self.a) - self.arange[1],
                    len(self.b) - self.brange[1]))

    def classify(self) -> AlignmentType:
        if (self.arange[0] <= self.brange[0] and len(self.a)-self.arange[1]
                <= len(self.b)-self.brange[1]):
            return AlignmentType.A_CONTAINED
        elif (self.arange[0] >= self.brange[0] and len(self.a)-self.arange[1]
              >= len(self.b)-self.brange[1]):
            return AlignmentType.B_CONTAINED
        elif self.arange[0] >= self.brange[0]:
            return AlignmentType.OVERLAP_AB
        else:
            return AlignmentType.OVERLAP_BA

    def get_alignment(self, trace_point_d: int=100):
        raise NotImplemented

        if not self.tracepoints:
            raise ValueError(
                "No tracepoints available for alignment '{}'".format(self))

        a_start = self.arange[0]
        a_end = round_up(self.arange[0], trace_point_d)

        alignment = []
        if a_start != 0:
            alignment.append("-" * a_start)

        for tp in self.tracepoints:
            b_start = self.brange[0]
            b_end = self.brange + tp[1]

            parasail.sw_table_striped_16(
                self.a.sequence[a_start:a_end], self.b.sequence[b_start:b_end],
                5, 2, dna_matrix
            )

    def __len__(self):
        return self.get_overlap_length()


class Pile:
    def __init__(self, a: Read):
        self.a = a
        self.alignments = []

    def add_alignment(self, alignment: LocalAlignment):
        assert alignment.a == self.a

        self.alignments.append(alignment)

    def perform_msa(self, trace_point_d=100):
        pass
