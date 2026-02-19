from app.services.money import calc_platform_fee_kobo, naira_to_kobo


def test_naira_to_kobo() -> None:
    assert naira_to_kobo(18000) == 1800000


def test_calc_platform_fee_kobo_exact() -> None:
    assert calc_platform_fee_kobo(1800000) == 27000


def test_calc_platform_fee_kobo_rounds_up_fractional() -> None:
    # 101 * 0.015 = 1.515 -> ceil -> 2
    assert calc_platform_fee_kobo(101) == 2
