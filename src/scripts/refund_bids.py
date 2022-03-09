from brownie import accounts
from dataclasses import dataclass

# todo: losing threshold to be set manually here
# if the bid is below this value, it has lost the auction
# it is possible that there may be two bids for the same
# value and one lost. In this case, timestamp needs to be
# looked at. This will be dealt with, if it occurs
# todo: ^if equal bids and one lost
LOSING_THRESHOLD = 17e18


@dataclass(frozen=True)
class Bid:
    address: str
    total_amount: float
    original_timestamp: int

    @classmethod
    def from_json(cls):
        ...

    def is_losing_bid(self) -> bool:
        # todo: take into account timestamp
        # todo: if there are two or more bids
        # todo: but one or more is losing
        if self.total_amount < LOSING_THRESHOLD:
            return True
        return False


# todo: type for from_account
def refund_bid(bid: Bid, from_account):
    # two types of bids
    # - winning bid
    # - losing bid
    # We determine which one it is, by comparing the total bid
    # to a losing threshold
    # If winning bid, then refund the difference between the
    # lowest winning bid and this given bid
    # If losing bid, refund all

    refund_amount = 0.0

    if bid.is_losing_bid():
        refund_amount = bid.total_amount
    else:
        refund_amount = bid.total_amount - LOSING_THRESHOLD

    # todo: gas strategies never worked for me in brownie
    # todo: if possible, send the more expensive ones to
    # todo: clear quickly
    from_account.transfer(bid.address, refund_amount)


def main():
    """
    Off-chain script to refund bidders.
    """
    refunder = accounts.load("<refunder_account>")
    from_refunder = {'from': refunder}

    # todo: instantiate all bids from a file
    bids = []
    num_bids_to_refund = len(bids)

    for i, bid in enumerate(bids):
        print(f'refunding bid #{i + 1}/{num_bids_to_refund}')
        refund_bid(bid)


if __name__ == '__main__':
    main()
