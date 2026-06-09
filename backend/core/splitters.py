from llama_index.core.node_parser import NodeParser, CodeSplitter
from tree_sitter_languages import get_parser
from dataclasses import dataclass
from enum import Enum


@dataclass
class SplitterConfig:
    splitter: NodeParser
    extensions: set[str]


class FileSplitter(Enum):
    CPP = SplitterConfig(
        splitter=CodeSplitter(
            language="cpp",
            parser=get_parser("cpp"),
            chunk_lines=40,
            chunk_lines_overlap=15,
            max_chars=1500,
        ),
        extensions={".cpp", ".hpp", ".c", ".h"},
    )
