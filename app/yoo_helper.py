import logging
import uuid
from datetime import datetime, timedelta
import aiohttp
from yoomoney import Client, Quickpay

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YooHelper:
    """Асинхронный класс для работы с ЮMoney"""

    def __init__(self, token: str, wallet: str, redirect_uri: str = ''):
        self.token = token
        self.wallet = wallet
        self.redirect_uri = redirect_uri
        try:
            self.client = Client(token) if token else None
        except Exception as e:
            logger.error(f"Failed to init YooMoney Client: {e}")
            self.client = None

    def create_payment(self, user_id: int, amount: float, description: str = "Оплата") -> dict | None:
        """Создает платежную ссылку"""
        try:
            payment_id = f"p_{user_id}_{uuid.uuid4().hex[:6]}"
            
            quickpay = Quickpay(
                receiver=self.wallet,
                quickpay_form="shop",
                targets=description,
                paymentType="AC",
                sum=amount,
                label=payment_id,
                successURL=self.redirect_uri
            )
            
            return {
                'payment_id': payment_id,
                'url': quickpay.redirected_url
            }
        except Exception as e:
            logger.error(f"Failed to create payment: {e}")
            return None

    async def check_payment(self, payment_id: str) -> dict:
        """Асинхронная проверка статуса платежа"""
        result = {'status': False, 'amount': 0, 'error': None}

        # Метод 1: Через Client API (синхронный, но быстрый)
        if self.client:
            try:
                history = self.client.operation_history(label=payment_id)
                if history.operations:
                    op = history.operations[0]
                    if op.status == 'success':
                        return {'status': True, 'amount': float(op.amount)}
            except Exception as e:
                logger.warning(f"Client API check failed: {e}")

        # Метод 2: Через aiohttp (асинхронный)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://yoomoney.ru/api/operation-history',
                    params={
                        'type': 'deposition',
                        'label': payment_id,
                        'from': (datetime.now() - timedelta(hours=24)).isoformat(),
                        'till': datetime.now().isoformat(),
                        'records': 5
                    },
                    headers={'Authorization': f'Bearer {self.token}'},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for op in data.get('operations', []):
                            if op.get('label') == payment_id and op.get('status') == 'success':
                                return {'status': True, 'amount': float(op.get('amount', 0))}
        except Exception as e:
            logger.warning(f"Async API check failed: {e}")
            result['error'] = str(e)

        return result