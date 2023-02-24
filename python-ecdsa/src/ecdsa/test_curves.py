try:
    import unittest2 as unittest
except ImportError:
    import unittest

import base64
import pytest
from .curves import Curve, NIST256p, curves, UnknownCurveError, PRIME_FIELD_OID
from .ellipticcurve import CurveFp, PointJacobi, CurveEdTw
from . import der
from .util import number_to_string


class TestParameterEncoding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # minimal, but with cofactor (excludes seed when compared to
        # OpenSSL output)
        cls.base64_params = (
            "MIHgAgEBMCwGByqGSM49AQECIQD/////AAAAAQAAAAAAAAAAAAAAAP/////////"
            "//////zBEBCD/////AAAAAQAAAAAAAAAAAAAAAP///////////////AQgWsY12K"
            "o6k+ez671VdpiGvGUdBrDMU7D2O848PifSYEsEQQRrF9Hy4SxCR/i85uVjpEDyd"
            "wN9gS3rM6D0oTlF2JjClk/jQuL+Gn+bjufrSnwPnhYrzjNXazFezsu2QGg3v1H1"
            "AiEA/////wAAAAD//////////7zm+q2nF56E87nKwvxjJVECAQE="
        )

    def test_from_pem(self):
        pem_params = (
            "-----BEGIN EC PARAMETERS-----\n"
            "MIHgAgEBMCwGByqGSM49AQECIQD/////AAAAAQAAAAAAAAAAAAAAAP/////////\n"
            "//////zBEBCD/////AAAAAQAAAAAAAAAAAAAAAP///////////////AQgWsY12K\n"
            "o6k+ez671VdpiGvGUdBrDMU7D2O848PifSYEsEQQRrF9Hy4SxCR/i85uVjpEDyd\n"
            "wN9gS3rM6D0oTlF2JjClk/jQuL+Gn+bjufrSnwPnhYrzjNXazFezsu2QGg3v1H1\n"
            "AiEA/////wAAAAD//////////7zm+q2nF56E87nKwvxjJVECAQE=\n"
            "-----END EC PARAMETERS-----\n"
        )
        curve = Curve.from_pem(pem_params)

        self.assertIs(curve, NIST256p)

    def test_from_pem_with_explicit_when_explicit_disabled(self):
        pem_params = (
            "-----BEGIN EC PARAMETERS-----\n"
            "MIHgAgEBMCwGByqGSM49AQECIQD/////AAAAAQAAAAAAAAAAAAAAAP/////////\n"
            "//////zBEBCD/////AAAAAQAAAAAAAAAAAAAAAP///////////////AQgWsY12K\n"
            "o6k+ez671VdpiGvGUdBrDMU7D2O848PifSYEsEQQRrF9Hy4SxCR/i85uVjpEDyd\n"
            "wN9gS3rM6D0oTlF2JjClk/jQuL+Gn+bjufrSnwPnhYrzjNXazFezsu2QGg3v1H1\n"
            "AiEA/////wAAAAD//////////7zm+q2nF56E87nKwvxjJVECAQE=\n"
            "-----END EC PARAMETERS-----\n"
        )
        with self.assertRaises(der.UnexpectedDER) as e:
            Curve.from_pem(pem_params, ["named_curve"])

        self.assertIn("explicit curve parameters not", str(e.exception))

    def test_from_pem_with_named_curve_with_named_curve_disabled(self):
        pem_params = (
            "-----BEGIN EC PARAMETERS-----\n"
            "BggqhkjOPQMBBw==\n"
            "-----END EC PARAMETERS-----\n"
        )
        with self.assertRaises(der.UnexpectedDER) as e:
            Curve.from_pem(pem_params, ["explicit"])

        self.assertIn("named_curve curve parameters not", str(e.exception))

    def test_from_pem_with_wrong_header(self):
        pem_params = (
            "-----BEGIN PARAMETERS-----\n"
            "MIHgAgEBMCwGByqGSM49AQECIQD/////AAAAAQAAAAAAAAAAAAAAAP/////////\n"
            "//////zBEBCD/////AAAAAQAAAAAAAAAAAAAAAP///////////////AQgWsY12K\n"
            "o6k+ez671VdpiGvGUdBrDMU7D2O848PifSYEsEQQRrF9Hy4SxCR/i85uVjpEDyd\n"
            "wN9gS3rM6D0oTlF2JjClk/jQuL+Gn+bjufrSnwPnhYrzjNXazFezsu2QGg3v1H1\n"
            "AiEA/////wAAAAD//////////7zm+q2nF56E87nKwvxjJVECAQE=\n"
            "-----END PARAMETERS-----\n"
        )
        with self.assertRaises(der.UnexpectedDER) as e:
            Curve.from_pem(pem_params)

        self.assertIn("PARAMETERS PEM header", str(e.exception))

    def test_to_pem(self):
        pem_params = (
            b"-----BEGIN EC PARAMETERS-----\n"
            b"BggqhkjOPQMBBw==\n"
            b"-----END EC PARAMETERS-----\n"
        )
        encoding = NIST256p.to_pem()

        self.assertEqual(pem_params, encoding)

    def test_compare_with_different_object(self):
        self.assertNotEqual(NIST256p, 256)

    def test_named_curve_params_der(self):
        encoded = NIST256p.to_der()

        # just the encoding of the NIST256p OID (prime256v1)
        self.assertEqual(b"\x06\x08\x2a\x86\x48\xce\x3d\x03\x01\x07", encoded)

    def test_verify_that_default_is_named_curve_der(self):
        encoded_default = NIST256p.to_der()
        encoded_named = NIST256p.to_der("named_curve")

        self.assertEqual(encoded_default, encoded_named)

    def test_encoding_to_explicit_params(self):
        encoded = NIST256p.to_der("explicit")

        self.assertEqual(encoded, bytes(base64.b64decode(self.base64_params)))

    def test_encoding_to_unsupported_type(self):
        with self.assertRaises(ValueError) as e:
            NIST256p.to_der("unsupported")

        self.assertIn("Only 'named_curve'", str(e.exception))

    def test_encoding_to_explicit_compressed_params(self):
        encoded = NIST256p.to_der("explicit", "compressed")

        compressed_base_point = (
            "MIHAAgEBMCwGByqGSM49AQECIQD/////AAAAAQAAAAAAAAAAAAAAAP//////////"
            "/////zBEBCD/////AAAAAQAAAAAAAAAAAAAAAP///////////////AQgWsY12Ko6"
            "k+ez671VdpiGvGUdBrDMU7D2O848PifSYEsEIQNrF9Hy4SxCR/i85uVjpEDydwN9"
            "gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVR"
            "AgEB"
        )

        self.assertEqual(
            encoded, bytes(base64.b64decode(compressed_base_point))
        )

    def test_decoding_explicit_from_openssl(self):
        # generated with openssl 1.1.1k using
        # openssl ecparam -name P-256 -param_enc explicit -out /tmp/file.pem
        p256_explicit = (
            "MIH3AgEBMCwGByqGSM49AQECIQD/////AAAAAQAAAAAAAAAAAAAAAP//////////"
            "/////zBbBCD/////AAAAAQAAAAAAAAAAAAAAAP///////////////AQgWsY12Ko6"
            "k+ez671VdpiGvGUdBrDMU7D2O848PifSYEsDFQDEnTYIhucEk2pmeOETnSa3gZ9+"
            "kARBBGsX0fLhLEJH+Lzm5WOkQPJ3A32BLeszoPShOUXYmMKWT+NC4v4af5uO5+tK"
            "fA+eFivOM1drMV7Oy7ZAaDe/UfUCIQD/////AAAAAP//////////vOb6racXnoTz"
            "ucrC/GMlUQIBAQ=="
        )

        decoded = Curve.from_der(bytes(base64.b64decode(p256_explicit)))

        self.assertEqual(NIST256p, decoded)

    def test_decoding_well_known_from_explicit_params(self):
        curve = Curve.from_der(bytes(base64.b64decode(self.base64_params)))

        self.assertIs(curve, NIST256p)

    def test_decoding_with_incorrect_valid_encodings(self):
        with self.assertRaises(ValueError) as e:
            Curve.from_der(b"", ["explicitCA"])

        self.assertIn("Only named_curve", str(e.exception))

    def test_compare_curves_with_different_generators(self):
        curve_fp = CurveFp(23, 1, 7)
        base_a = PointJacobi(curve_fp, 13, 3, 1, 9, generator=True)
        base_b = PointJacobi(curve_fp, 1, 20, 1, 9, generator=True)

        curve_a = Curve("unknown", curve_fp, base_a, None)
        curve_b = Curve("unknown", curve_fp, base_b, None)

        self.assertNotEqual(curve_a, curve_b)

    def test_default_encode_for_custom_curve(self):
        curve_fp = CurveFp(23, 1, 7)
        base_point = PointJacobi(curve_fp, 13, 3, 1, 9, generator=True)

        curve = Curve("unknown", curve_fp, base_point, None)

        encoded = curve.to_der()

        decoded = Curve.from_der(encoded)

        self.assertEqual(curve, decoded)

        expected = "MCECAQEwDAYHKoZIzj0BAQIBFzAGBAEBBAEHBAMEDQMCAQk="

        self.assertEqual(encoded, bytes(base64.b64decode(expected)))

    def test_named_curve_encode_for_custom_curve(self):
        curve_fp = CurveFp(23, 1, 7)
        base_point = PointJacobi(curve_fp, 13, 3, 1, 9, generator=True)

        curve = Curve("unknown", curve_fp, base_point, None)

        with self.assertRaises(UnknownCurveError) as e:
            curve.to_der("named_curve")

        self.assertIn("Can't encode curve", str(e.exception))

    def test_try_decoding_binary_explicit(self):
        sect113r1_explicit = (
            "MIGRAgEBMBwGByqGSM49AQIwEQIBcQYJKoZIzj0BAgMCAgEJMDkEDwAwiCUMpufH"
            "/mSc6Fgg9wQPAOi+5NPiJgdEGIvg6ccjAxUAEOcjqxTWluZ2h1YVF1b+v4/LSakE"
            "HwQAnXNhbzX0qxQH1zViwQ8ApSgwJ3lY7oTRMV7TGIYCDwEAAAAAAAAA2czsijnl"
            "bwIBAg=="
        )

        with self.assertRaises(UnknownCurveError) as e:
            Curve.from_der(base64.b64decode(sect113r1_explicit))

        self.assertIn("Characteristic 2 curves unsupported", str(e.exception))

    def test_decode_malformed_named_curve(self):
        bad_der = der.encode_oid(*NIST256p.oid) + der.encode_integer(1)

        with self.assertRaises(der.UnexpectedDER) as e:
            Curve.from_der(bad_der)

        self.assertIn("Unexpected data after OID", str(e.exception))

    def test_decode_malformed_explicit_garbage_after_ECParam(self):
        bad_der = bytes(
            base64.b64decode(self.base64_params)
        ) + der.encode_integer(1)

        with self.assertRaises(der.UnexpectedDER) as e:
            Curve.from_der(bad_der)

        self.assertIn("Unexpected data after ECParameters", str(e.exception))

    def test_decode_malformed_unknown_version_number(self):
        bad_der = der.encode_sequence(der.encode_integer(2))

        with self.assertRaises(der.UnexpectedDER) as e:
            Curve.from_der(bad_der)

        self.assertIn("Unknown parameter encoding format", str(e.exception))

    def test_decode_malformed_unknown_field_type(self):
        curve_p = NIST256p.curve.p()
        bad_der = der.encode_sequence(
            der.encode_integer(1),
            der.encode_sequence(
                der.encode_oid(1, 2, 3), der.encode_integer(curve_p)
            ),
            der.encode_sequence(
                der.encode_octet_string(
                    number_to_string(NIST256p.curve.a() % curve_p, curve_p)
                ),
                der.encode_octet_string(
                    number_to_string(NIST256p.curve.b(), curve_p)
                ),
            ),
            der.encode_octet_string(
                NIST256p.generator.to_bytes("uncompressed")
            ),
            der.encode_integer(NIST256p.generator.order()),
        )

        with self.assertRaises(UnknownCurveError) as e:
            Curve.from_der(bad_der)

        self.assertIn("Unknown field type: (1, 2, 3)", str(e.exception))

    def test_decode_malformed_garbage_after_prime(self):
        curve_p = NIST256p.curve.p()
        bad_der = der.encode_sequence(
            der.encode_integer(1),
            der.encode_sequence(
                der.encode_oid(*PRIME_FIELD_OID),
                der.encode_integer(curve_p),
                der.encode_integer(1),
            ),
            der.encode_sequence(
                der.encode_octet_string(
                    number_to_string(NIST256p.curve.a() % curve_p, curve_p)
                ),
                der.encode_octet_string(
                    number_to_string(NIST256p.curve.b(), curve_p)
                ),
            ),
            der.encode_octet_string(
                NIST256p.generator.to_bytes("uncompressed")
            ),
            der.encode_integer(NIST256p.generator.order()),
        )

        with self.assertRaises(der.UnexpectedDER) as e:
            Curve.from_der(bad_der)

        self.assertIn("Prime-p element", str(e.exception))


@pytest.mark.parametrize("curve", curves, ids=[i.name for i in curves])
def test_curve_params_encode_decode_named(curve):
    ret = Curve.from_der(curve.to_der("named_curve"))

    assert curve == ret


@pytest.mark.parametrize("curve", curves, ids=[i.name for i in curves])
def test_curve_params_encode_decode_explicit(curve):
    if isinstance(curve.curve, CurveEdTw):
        with pytest.raises(UnknownCurveError):
            curve.to_der("explicit")
    else:
        ret = Curve.from_der(curve.to_der("explicit"))

        assert curve == ret


@pytest.mark.parametrize("curve", curves, ids=[i.name for i in curves])
def test_curve_params_encode_decode_default(curve):
    ret = Curve.from_der(curve.to_der())

    assert curve == ret


@pytest.mark.parametrize("curve", curves, ids=[i.name for i in curves])
def test_curve_params_encode_decode_explicit_compressed(curve):
    if isinstance(curve.curve, CurveEdTw):
        with pytest.raises(UnknownCurveError):
            curve.to_der("explicit", "compressed")
    else:
        ret = Curve.from_der(curve.to_der("explicit", "compressed"))

        assert curve == ret
