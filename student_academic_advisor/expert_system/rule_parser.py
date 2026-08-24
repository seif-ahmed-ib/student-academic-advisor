"""Tokenizer and recursive-descent parser for rule-condition strings."""

from dataclasses import dataclass
from enum import Enum

from student_academic_advisor.expert_system.models import (
    ConditionKind,
    ConditionNode,
)


class ConditionSyntaxError(ValueError):
    """Raised when a condition does not follow the restricted syntax."""


class _TokenKind(str, Enum):
    IDENTIFIER = "IDENTIFIER"
    NOT = "NOT"
    AND = "AND"
    OR = "OR"
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    END = "END"


@dataclass(frozen=True)
class _Token:
    kind: _TokenKind
    text: str
    position: int


_KEYWORDS = {
    "NOT": _TokenKind.NOT,
    "AND": _TokenKind.AND,
    "OR": _TokenKind.OR,
}


def _is_identifier_start(character: str) -> bool:
    return character.isascii() and (character.isalpha() or character == "_")


def _is_identifier_part(character: str) -> bool:
    return character.isascii() and (character.isalnum() or character == "_")


def _tokenize(source: str) -> tuple[_Token, ...]:
    tokens: list[_Token] = []
    position = 0

    while position < len(source):
        character = source[position]

        if character.isspace():
            position += 1
            continue

        if character == "(":
            tokens.append(_Token(_TokenKind.LEFT_PAREN, character, position))
            position += 1
            continue

        if character == ")":
            tokens.append(_Token(_TokenKind.RIGHT_PAREN, character, position))
            position += 1
            continue

        if _is_identifier_start(character):
            start = position
            position += 1
            while position < len(source) and _is_identifier_part(source[position]):
                position += 1

            text = source[start:position]
            if text in ("IF", "THEN"):
                raise ConditionSyntaxError(
                    f"{text} is not allowed inside a condition at position {start}"
                )

            tokens.append(
                _Token(_KEYWORDS.get(text, _TokenKind.IDENTIFIER), text, start)
            )
            continue

        raise ConditionSyntaxError(
            f"unexpected character {character!r} at position {position}"
        )

    tokens.append(_Token(_TokenKind.END, "", len(source)))
    return tuple(tokens)


class _ConditionParser:
    def __init__(self, tokens: tuple[_Token, ...]) -> None:
        self._tokens = tokens
        self._index = 0

    @property
    def _current(self) -> _Token:
        return self._tokens[self._index]

    def _advance(self) -> _Token:
        token = self._current
        self._index += 1
        return token

    def parse(self) -> ConditionNode:
        condition = self._parse_or()
        if self._current.kind is not _TokenKind.END:
            raise ConditionSyntaxError(
                f"unexpected token {self._current.text!r} "
                f"at position {self._current.position}"
            )
        return condition

    def _parse_or(self) -> ConditionNode:
        operands = [self._parse_and()]
        while self._current.kind is _TokenKind.OR:
            self._advance()
            operands.append(self._parse_and())

        if len(operands) == 1:
            return operands[0]
        return ConditionNode(ConditionKind.OR, operands=tuple(operands))

    def _parse_and(self) -> ConditionNode:
        operands = [self._parse_not()]
        while self._current.kind is _TokenKind.AND:
            self._advance()
            operands.append(self._parse_not())

        if len(operands) == 1:
            return operands[0]
        return ConditionNode(ConditionKind.AND, operands=tuple(operands))

    def _parse_not(self) -> ConditionNode:
        if self._current.kind is _TokenKind.NOT:
            self._advance()
            return ConditionNode(
                ConditionKind.NOT,
                operands=(self._parse_not(),),
            )
        return self._parse_primary()

    def _parse_primary(self) -> ConditionNode:
        token = self._current

        if token.kind is _TokenKind.IDENTIFIER:
            self._advance()
            return ConditionNode(
                ConditionKind.FACT_REF,
                fact_attribute=token.text,
            )

        if token.kind is _TokenKind.LEFT_PAREN:
            opening = self._advance()
            nested = self._parse_or()
            if self._current.kind is not _TokenKind.RIGHT_PAREN:
                raise ConditionSyntaxError(
                    "expected ')' for '(' at position "
                    f"{opening.position}; found {self._current.text!r} "
                    f"at position {self._current.position}"
                )
            self._advance()
            return nested

        found = "end of condition" if token.kind is _TokenKind.END else repr(token.text)
        raise ConditionSyntaxError(
            "expected a fact identifier, NOT, or '('; "
            f"found {found} at position {token.position}"
        )


def parse_condition(source: str) -> ConditionNode:
    """Parse one restricted condition string into an immutable AST."""
    if not isinstance(source, str):
        raise TypeError(
            "condition source must be a string; "
            f"received {source!r} ({type(source).__name__})"
        )
    if not source.strip():
        raise ConditionSyntaxError("condition must not be empty")

    return _ConditionParser(_tokenize(source)).parse()
