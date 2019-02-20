import pytest

import ssz

from eth2.beacon.types.attestation_data_and_custody_bits import (
    AttestationDataAndCustodyBit,
)
from eth2.beacon.types.slashable_attestations import (
    SlashableAttestation,
)


def test_defaults(sample_slashable_attestation_params):
    slashable_attestation = SlashableAttestation(**sample_slashable_attestation_params)

    assert (slashable_attestation.validator_indices ==
            sample_slashable_attestation_params['validator_indices'])
    assert (slashable_attestation.custody_bitfield ==
            sample_slashable_attestation_params['custody_bitfield'])
    assert slashable_attestation.data == sample_slashable_attestation_params['data']
    assert (
        slashable_attestation.aggregate_signature ==
        sample_slashable_attestation_params['aggregate_signature']
    )
    assert ssz.encode(slashable_attestation)


def test_hash(sample_slashable_attestation_params):
    slashable_attestation = SlashableAttestation(**sample_slashable_attestation_params)

    # NOTE: this hash was simply copied from the existing implementation
    # which should be the keccak-256 of the rlp serialization of `votes`.
    # Given that this value will change soon (cf. ssz tree hash), we just
    # do this to get the test passing for now and will need to update later
    # if we expect the hash computation is not working correctly
    hash_hex = "8cba2c190eae977ba16cbcc7ef1b95b32384fd12e86292ca8a91cc320eaeac9c"

    assert slashable_attestation.hash == bytes.fromhex(hash_hex)


def test_root(sample_slashable_attestation_params):
    slashable_attestation = SlashableAttestation(**sample_slashable_attestation_params)

    # NOTE: see note in `test_hash`, this test will need to be updated
    # once ssz tree hash lands...

    assert slashable_attestation.root == slashable_attestation.hash


@pytest.mark.parametrize(
    (
        'validator_indices',
        'are_validator_indices_ascending'
    ),
    [
        ((0, 1, 2), True),
        ((0, 2, 1), False),
    ],
)
def test_is_validator_indices_ascending(
        sample_slashable_attestation_params,
        validator_indices,
        are_validator_indices_ascending):
    slashable_attestation = SlashableAttestation(**sample_slashable_attestation_params).copy(
        validator_indices=validator_indices,
    )
    assert slashable_attestation.are_validator_indices_ascending == are_validator_indices_ascending


@pytest.mark.parametrize(
    (
        'validator_indices',
        'custody_bitfield',
        'custody_bit_indices'
    ),
    [
        ((0, 1, 2), b'\x80', ((1, 2), (0,))),
        ((0, 1, 2), b'\xC0', ((2,), (0, 1))),
    ],
)
def test_custody_bit_indices(
        sample_slashable_attestation_params,
        validator_indices,
        custody_bitfield,
        custody_bit_indices):
    slashable_attestation = SlashableAttestation(**sample_slashable_attestation_params).copy(
        validator_indices=validator_indices,
        custody_bitfield=custody_bitfield,
    )
    assert slashable_attestation.custody_bit_indices == custody_bit_indices


def test_messages(sample_slashable_attestation_params):
    slashable_attestation = SlashableAttestation(**sample_slashable_attestation_params)

    assert slashable_attestation.messages == (
        AttestationDataAndCustodyBit(slashable_attestation.data, False).root,
        AttestationDataAndCustodyBit(slashable_attestation.data, True).root,
    )
