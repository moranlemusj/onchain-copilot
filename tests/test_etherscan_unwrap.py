from copilot.providers.etherscan import unwrap_source


RAW_SOL = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Foo {
    function bar() public pure returns (uint256) { return 42; }
}
"""


def test_raw_solidity_passes_through():
    assert unwrap_source(RAW_SOL) == RAW_SOL


def test_double_braced_standard_json_input_is_unwrapped():
    wrapped = (
        '{{"language":"Solidity","sources":{'
        '"contracts/A.sol":{"content":"contract A { uint256 x; }"},'
        '"contracts/B.sol":{"content":"contract B { uint256 y; }"}'
        '},"settings":{}}}'
    )
    out = unwrap_source(wrapped)
    assert "contract A { uint256 x; }" in out
    assert "contract B { uint256 y; }" in out
    assert "// === contracts/A.sol ===" in out
    assert "// === contracts/B.sol ===" in out
    assert '"language"' not in out


def test_plain_json_with_sources_key_is_unwrapped():
    wrapped = (
        '{"language":"Solidity","sources":{'
        '"X.sol":{"content":"contract X {}"}'
        '},"settings":{}}'
    )
    out = unwrap_source(wrapped)
    assert "contract X {}" in out
    assert "// === X.sol ===" in out


def test_malformed_json_falls_back_to_raw():
    wrapped = "{{not valid json}}"
    assert unwrap_source(wrapped) == wrapped


def test_json_without_sources_key_passes_through():
    wrapped = '{"something":"else"}'
    assert unwrap_source(wrapped) == wrapped


def test_non_dict_sources_passes_through():
    wrapped = '{"sources":"not a dict"}'
    assert unwrap_source(wrapped) == wrapped
