from pytoniq import WalletV4R2, LiteBalancer, begin_cell
from config import WALLET_MNEMONIC, FRAGMENT_CONTRACT

async def send_stars_transaction(recipient_username: str, amount: int):
    provider = LiteBalancer.from_mainnet_config(trust_level=2)
    await provider.start_up()
    try:
        wallet = await WalletV4R2.from_mnemonic(provider=provider, mnemonics=WALLET_MNEMONIC.split())

       
        ton_to_send = int(amount * 0.015 * 10 ** 9)

        payload = (
            begin_cell()
            .store_uint(0, 32)
            .store_snake_string(f"gift:{recipient_username.replace('@', '')}:{amount}")
            .end_cell()
        )

        balance = await wallet.get_balance()
    
        if balance < ton_to_send + 50_000_000:
            return False, "E_LOW_BALANCE_BOT"

        await wallet.transfer(destination=FRAGMENT_CONTRACT, amount=ton_to_send, body=payload)
        return True, "Success"
    except Exception as e:
        return False, str(e)
    finally:
        await provider.close_all()
