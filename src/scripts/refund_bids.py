from typing import Dict, Tuple
from brownie import accounts, chain
from dataclasses import dataclass

# ! 1. losing threshold to be set manually here
# ! 2. bids to be set manually here
# ! 3. set the account to rkl refunder account in main

# if the bid is below this value, it has lost the auction
# it is possible that there may be two bids for the same
# value and one lost. In this case, timestamp needs to be
# looked at. This will be dealt with, if it occurs
# * ^if equal bids and one lost
LOSING_THRESHOLD = 0.7306900000000001

# * this is where you place the bids json that comes out
# * of the transformer
BIDS = {
    "0x17a4e4aa1f87f677b6930f8c1bc6d3449181ad95": 0.25,
    "0x000000724350d0b24747bd816dc5031acb7efe0b": 0.418885345123424,
    "0x735fb1b51d03b1230321693aaf89e7d08476482e": 0.5,
    "0x2f90722088cf90e674708ea726a2ad2cd4cb8d50": 0.7306900000000001,
    "0x5e12b20feb5056660222f8a08382660548e12ef5": 0.81,
    "0x09125b0331354707d1238ae8044921de47dd4152": 0.9,
    "0x465dca9995d6c2a81a9be80fbced5a770dee3dae": 1.42069
}


def bids_ascending() -> Tuple[str, float]:
    pairs = zip(BIDS.keys(), BIDS.values())
    sorted_pairs = sorted(pairs, key=lambda x: x[1])
    bids = [Bid(address, total_amount, 0) for (address, total_amount) in sorted_pairs]
    return bids


@dataclass(frozen=True)
class Bid:
    address: str
    total_amount: float
    original_timestamp: int

    def is_losing_bid(self) -> bool:
        # ! take into account timestamp if required
        if self.total_amount < LOSING_THRESHOLD:
            return True
        return False

# todo: type for from_account
def refund_bid(bid: Bid, from_account) -> None:
    # two types of bids
    # - winning bid
    # - losing bid
    # We determine which one it is, by comparing the total bid
    # to a losing threshold
    # If winning bid, then refund the difference between the
    # lowest winning bid and this given bid
    # If losing bid, refund all

    refund_amount = 0.0

    # * < LOSING_THRESHOLD
    if bid.is_losing_bid():
        refund_amount = bid.total_amount
    # * == LOSING_THRESHOLD
    elif bid.total_amount == LOSING_THRESHOLD:
        # the bid that was the lowest winning one
        # does not get refunded
        return
    # * > LOSING_THRESHOLD
    else:
        refund_amount = bid.total_amount - LOSING_THRESHOLD

    # !!!!!!!! NOTICE THE SCALE: ETHER !!!!!!!!!!!!
    refund_amount = f'{refund_amount} ether'
    # 15% higher than the recommended priority fee
    priority_fee = int(1.15 * chain.priority_fee)
    print(f'Refunding {refund_amount}. Priority fee: {priority_fee} wei.')
    from_account.transfer(bid.address, refund_amount, priority_fee=priority_fee)


def main():
    """
    Off-chain script to refund bidders.
    """
    refunder = accounts.load("<refunder_account>")

    bids = bids_ascending()
    num_bids_to_refund = len(bids)

    for i, bid in enumerate(bids):
        print(f'refunding bid #{i + 1}/{num_bids_to_refund}.')
        print(f'bidder: {bid.address}, total_amount: {bid.total_amount} wei.')
        refund_bid(bid, refunder)


if __name__ == '__main__':
    main()
