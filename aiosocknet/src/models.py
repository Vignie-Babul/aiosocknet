from __future__ import annotations


type JSONValue = (
	None
	| bool
	| int
	| float
	| str
	| list
	| tuple
	| dict[str, JSONValue]
)
