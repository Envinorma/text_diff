#!/usr/bin/env python
# -*- coding: utf-8 -*-
import difflib
from dataclasses import dataclass
from enum import Enum
from typing import List, Union


@dataclass
class RemovedLine:
    content: str


@dataclass
class AddedLine:
    content: str


class EditOperation(Enum):
    MUTATION = '^'
    ADDITION = '+'
    DELETION = '-'
    UNCHANGED = ' '

    def __repr__(self) -> str:
        return self.value


@dataclass
class Mask:
    elements: List[EditOperation]

    def __str__(self):
        return '"' + ''.join([el.value for el in self.elements]) + '"'

    def __repr__(self):
        return str(self)


@dataclass
class ModifiedLine:
    content_before: str
    mask_before: Mask
    content_after: str
    mask_after: Mask


@dataclass
class UnchangedLine:
    content: str


DiffLine = Union[RemovedLine, AddedLine, ModifiedLine, UnchangedLine]


@dataclass
class TextDifferences:
    diff_lines: List[DiffLine]

    def nb_modifications(self) -> int:
        return len([line for line in self.diff_lines if not isinstance(line, UnchangedLine)])


def _extract_first_chars(strs: List[str]) -> str:
    return ''.join([x[:1] for x in strs])


def _parse_mask(mask_str: str) -> Mask:
    return Mask([EditOperation(x) for x in mask_str])


def _empty_mask(size: int) -> Mask:
    return Mask([EditOperation.UNCHANGED for _ in range(size)])


def _build_modified_line(difflines: List[str]) -> ModifiedLine:
    first_chars = _extract_first_chars(difflines)
    lines = [x[2:].strip('\n') for x in difflines]
    if first_chars == '-+?':
        return ModifiedLine(lines[0], _empty_mask(len(lines[0])), lines[1], _parse_mask(lines[2]))
    if first_chars == '+-?':
        return ModifiedLine(lines[1], _parse_mask(lines[2]), lines[0], _empty_mask(len(lines[0])))
    if first_chars.startswith('+?-'):
        deletion_mask = _parse_mask(lines[3]) if first_chars[-1] == '?' else _empty_mask(len(lines[1]))
        return ModifiedLine(lines[2], deletion_mask, lines[0], _parse_mask(lines[1]))
    if first_chars.startswith('-?+'):
        addition_mask = _parse_mask(lines[3]) if first_chars[-1] == '?' else _empty_mask(len(lines[1]))
        return ModifiedLine(lines[0], _parse_mask(lines[1]), lines[2], addition_mask)
    raise NotImplementedError(f'Unhandled modification for first_chars sequence {first_chars}')


def _apply_mask(line: str, mask: Mask) -> str:
    chars = []
    for char, operation in zip(line, mask.elements):
        if operation == EditOperation.UNCHANGED:
            chars.append(char)
    chars.extend(line[len(mask.elements) :])
    return ''.join(chars)


def _is_modified_line_consistent(line: ModifiedLine) -> bool:
    before = _apply_mask(line.content_before, line.mask_before)
    after = _apply_mask(line.content_after, line.mask_after)
    return before == after


def _build_difflines(difflines: List[str]) -> List[DiffLine]:
    """difflib output parser
    - if nothing at the beginning of the diffline: unchanged line
    - if three consecutive lines starting with -?+ or +?- and potentially followed by
      one line starting with '?' -> modified line
    - if three consecutive lines starting with -+? or +-? -> modified line
      (beware, if it actually is -+?-?, the +?-? has the priority)
    - otherwise, deletion if line starts with '-', addition if line starts with '+'
    """
    cursor = 0
    res: List[DiffLine] = []
    while True:
        if cursor >= len(difflines):
            break
        current_line = difflines[cursor]
        if current_line.startswith(' '):  # line is common to both texts
            res.append(UnchangedLine(current_line[2:]))
            cursor = cursor + 1
            continue
        first_chars = _extract_first_chars(difflines[cursor : cursor + 4])
        if first_chars[:4] in ('-?+?', '+?-?'):
            res.append(_build_modified_line(difflines[cursor : cursor + 4]))
            cursor += 4
            continue
        if first_chars[:3] in ('-?+', '+?-', '-+?', '+-?'):
            candidate = _build_modified_line(difflines[cursor : cursor + 3])
            if _is_modified_line_consistent(candidate):
                # above is a necessary check because it could be pattern '-' '+?-?' if starts with '-+?'
                res.append(candidate)
                cursor += 3
                continue
        if current_line[0] == '-':
            res.append(RemovedLine(current_line[2:]))
            cursor += 1
            continue
        if current_line[0] == '+':
            res.append(AddedLine(current_line[2:]))
            cursor += 1
            continue
        debug_start = cursor - 5 if cursor >= 5 else 0
        raise NotImplementedError(
            f'Unhandled difflines sequence ({first_chars}) :'
            f' {difflines[debug_start : cursor + 4]}\nDiff so far: {res[-3:]}'
        )
    return res


def _cleanup_text(lines: List[str]) -> List[str]:
    return [line.replace('\n', '').replace('\t', '  ') for line in lines]


def text_differences(original_text: List[str], new_text_version: List[str]) -> TextDifferences:
    """
    Builds text differences from input texts.

    Parameters
    ----------
    original_text: List[str]
        original text (as a list of lines)
    new_text_version: List[str]
        new text version (as a list of lines)

    Returns
    -------
    text_differences: TextDifferences
        TextDifferences object built on top of diffline output
    """
    diffs = list(difflib.Differ().compare(_cleanup_text(original_text), _cleanup_text(new_text_version)))
    return TextDifferences(_build_difflines(diffs))
