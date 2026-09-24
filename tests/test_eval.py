import pytest

from ifstruct.eval import EvalResult, count_api_failures


def _result(seed, *, api_error):
    return EvalResult(
        seed=seed,
        model="m",
        passed=False,
        score=0.0,
        errors=[],
        details={"api_error": True} if api_error else {},
        prompt="",
        response="",
        latency_ms=0.0,
        output_format="json",
        entity_type="test__invoice",
        require_wrapper_key=False,
    )


def _results(n_errors, total=2000):
    return [_result(i, api_error=i < n_errors) for i in range(total)]


def test_no_api_errors():
    assert count_api_failures(_results(0)) == 0


def test_counts_only_api_errors():
    # Scoring failures without an api_error flag must not count.
    assert count_api_failures(_results(25)) == 25


# Real error counts from the 21 historical runs that tripped the old
# all-or-nothing check. At the 2% tolerance only the two worst still fail.
@pytest.mark.parametrize(
    "n_errors,fails",
    [(4, False), (25, False), (31, False), (40, False), (41, True), (55, True), (63, True)],
)
def test_tolerance_threshold(n_errors, fails):
    results = _results(n_errors)
    assert (count_api_failures(results) / len(results) > 0.02) is fails
