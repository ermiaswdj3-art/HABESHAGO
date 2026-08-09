"""
HABESHAGO Payment Provider Registry

Provides deterministic provider-adapter resolution for the
Payment Execution Platform.
"""

from app.payments.constants import (
    PaymentMethod,
    PaymentProvider,
)

from app.payments.exceptions import (
    PaymentProviderError,
)

from app.payments.provider_adapters import (
    CashPaymentAdapter,
    UnavailablePaymentAdapter,
)


_PROVIDER_REGISTRY = {
    PaymentProvider.CASH: (
        CashPaymentAdapter()
    ),

    PaymentProvider.TELEBIRR: (
        UnavailablePaymentAdapter(
            provider=PaymentProvider.TELEBIRR,
            payment_method=PaymentMethod.TELEBIRR,
        )
    ),

    PaymentProvider.CBE_BIRR: (
        UnavailablePaymentAdapter(
            provider=PaymentProvider.CBE_BIRR,
            payment_method=PaymentMethod.CBE_BIRR,
        )
    ),

    PaymentProvider.CHAPA: (
        UnavailablePaymentAdapter(
            provider=PaymentProvider.CHAPA,
            payment_method=PaymentMethod.CHAPA,
        )
    ),

    PaymentProvider.ARIFPAY: (
        UnavailablePaymentAdapter(
            provider=PaymentProvider.ARIFPAY,
            payment_method=PaymentMethod.ARIFPAY,
        )
    ),

    PaymentProvider.AWASH_BANK: (
        UnavailablePaymentAdapter(
            provider=PaymentProvider.AWASH_BANK,
            payment_method=PaymentMethod.AWASH_BANK,
        )
    ),

    PaymentProvider.AMHARA_BANK: (
        UnavailablePaymentAdapter(
            provider=PaymentProvider.AMHARA_BANK,
            payment_method=PaymentMethod.AMHARA_BANK,
        )
    ),

    PaymentProvider.BANK_OF_ABYSSINIA: (
        UnavailablePaymentAdapter(
            provider=(
                PaymentProvider.BANK_OF_ABYSSINIA
            ),
            payment_method=(
                PaymentMethod.BANK_OF_ABYSSINIA
            ),
        )
    ),

    PaymentProvider.DASHEN_BANK: (
        UnavailablePaymentAdapter(
            provider=PaymentProvider.DASHEN_BANK,
            payment_method=PaymentMethod.DASHEN_BANK,
        )
    ),
}


def get_payment_provider_adapter(
    provider: str,
):
    """
    Return the registered adapter for one provider.
    """

    adapter = _PROVIDER_REGISTRY.get(
        provider
    )

    if adapter is None:
        raise PaymentProviderError(
            (
                "No payment adapter is registered "
                f"for provider: {provider}"
            )
        )

    return adapter


def list_registered_payment_providers(
) -> tuple[str, ...]:
    """
    Return registered providers in deterministic order.
    """

    return tuple(
        sorted(
            _PROVIDER_REGISTRY.keys()
        )
    )