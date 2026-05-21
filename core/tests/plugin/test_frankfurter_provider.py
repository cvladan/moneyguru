# Copyright 2017 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from datetime import date

import pytest

from ...plugin.frankfurter_provider import FrankfurterProviderPlugin


@pytest.mark.needs_network
def test_frankfurter_provider_EUR():
    # A normal, well-supported currency: we should get one (date, rate) per business day in the
    # range, with positive CAD values.
    provider = FrankfurterProviderPlugin()
    rates = provider.get_currency_rates('EUR', date(2024, 1, 2), date(2024, 1, 8))
    assert rates, "expected some rates for EUR"
    for d, rate in rates:
        assert isinstance(d, date)
        assert rate is not None and rate > 0
    # Frankfurter only publishes on business days; the range above has 5.
    assert all(date(2024, 1, 2) <= d <= date(2024, 1, 8) for d, _ in rates)


@pytest.mark.needs_network
def test_frankfurter_provider_RSD():
    # RSD used to fail with the old Bank of Canada source. Frankfurter v2 supports it.
    provider = FrankfurterProviderPlugin()
    rates = provider.get_currency_rates('RSD', date(2024, 1, 2), date(2024, 1, 8))
    assert rates, "expected RSD to be supported by Frankfurter v2"
    assert all(rate is not None and rate > 0 for _, rate in rates)
