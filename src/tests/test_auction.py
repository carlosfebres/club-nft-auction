import pytest
import time
from brownie import Auction, AuctionFactory, E721, accounts, chain, Wei
import brownie

# ✔️ 1. test can't bid if auction not started
# ✔️ 2. test correct state of the clones
# ✔️ 3. test can't bid after auction ended
# ✔️ 4. test can bid during active auction
# ✔️ 5. test correct bids for diffs
# ✔️ 6. test direct eth payments are rejected
# ✔️ 7. test auction can't be initialized more than once
# ✔️ 8. test auction can't be initialized by non-deployer
# ✔️ 9. test can't bid if do not hold whitelisted collection
# ✔️ 10. test can bid if I hold whitelisted collection
# ✔️ 11. test anyone can bid if whitelisted collection is zero
# (implicitly tested in the above tests)
# ✔️ 12. test withdraw of funds works
# ✔️ 13. test can't bid if diff less than minimum increment

# Consts

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
SENTINEL_TOKEN_ID = 0
FUTURE_TIMESTAMP = int(time.time()) + 1_000_000

# Errors

AuctionNotActive = 'typed error: 0x69b8d0fe'
AlreadyInitialized = 'typed error: 0x0dc149f0'
BidForbidden = 'typed error: 0xff005159'
NotAdmin = 'typed error: 0x7bfa4b9f'
RejectDirectPayments = 'typed error: 0x3c7b40ba'
LessThanMinIncrement = 'typed error: 0xf2148d68000000000000000000000000000000000000000000000000016345785d89ffff'

# Tests Set Up

class Accounts:
    def __init__(self, accounts):
        self.deployer = accounts[0]
        self.alice = accounts[1]
        self.bob = accounts[2]

# reset state before each test
@pytest.fixture(autouse=True)
def shared_setup(fn_isolation):
    pass

@pytest.fixture(scope="module")
def A():
    return Accounts(accounts)

@pytest.fixture(scope="module")
def AuctionDeploy(A):
    return Auction.deploy({'from': A.deployer})

@pytest.fixture(scope="module")
def AuctionFactoryDeploy(A):
    return AuctionFactory.deploy({'from': A.deployer})

@pytest.fixture(scope="module")
def E721Deploy(A):
    return E721.deploy({'from': A.deployer})


# Tests
# 1.
def test_cant_bid_before_start(AuctionDeploy, A):
    auction = AuctionDeploy

    init_floor_price, init_timestamp, init_address = 1, FUTURE_TIMESTAMP, ZERO_ADDRESS
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    with brownie.reverts(AuctionNotActive):
        auction.placeBid(
            SENTINEL_TOKEN_ID,
            {
                'from': A.alice,
                'value': f'{init_floor_price} ether'
            }
        )


# 2.
def test_correct_clone_state(AuctionDeploy, AuctionFactoryDeploy, A):
    auction = AuctionDeploy
    auction_factory = AuctionFactoryDeploy

    # we pretend that Alice is an NFT collection here
    init_floor_price, init_timestamp, init_address = 1, FUTURE_TIMESTAMP, A.alice
    auction_factory.setAuctionAddress(auction)
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    assert auction.floorPrice() == init_floor_price
    assert auction.auctionEndTimestamp() == init_timestamp
    assert auction.whitelistedCollection() == A.alice

    # make a clone and check it was initialized correctly
    init_floor_price_clone, init_timestamp_clone = 2, 20
    auction_clone_txn = auction_factory.createAuction(
        init_floor_price_clone,
        init_timestamp_clone,
        hex(0)
    )
    auction_clone = Auction.at(auction_clone_txn.return_value)
    assert auction_clone.floorPrice() == init_floor_price_clone
    assert auction_clone.auctionEndTimestamp() == init_timestamp_clone
    assert auction_clone.whitelistedCollection() == ZERO_ADDRESS

    # ensure that original auction state is correct
    assert auction.floorPrice() == init_floor_price
    assert auction.auctionEndTimestamp() == init_timestamp
    assert auction.whitelistedCollection() == A.alice


# 3., 4.
def test_cant_bid_after_end(AuctionDeploy, A):
    auction = AuctionDeploy

    now = int(time.time())
    init_floor_price, init_timestamp, init_address = 1, now, ZERO_ADDRESS
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    # txn.timestamp here will be equal to: `now`
    txn = auction.startAuction()
    chain.sleep(10)
    txn = auction.placeBid(
        SENTINEL_TOKEN_ID,
        {
            'from': A.alice,
            'value': f'{init_floor_price} ether'
        }
    )
    with brownie.reverts(AuctionNotActive):
        auction.placeBid(
            SENTINEL_TOKEN_ID,
            {
                'from': A.alice,
                'value': f'{init_floor_price} ether'
            }
        )


# 5.
def test_cant_bid_after_end(AuctionDeploy, A):
    auction = AuctionDeploy

    init_floor_price, init_timestamp, init_address = 1, FUTURE_TIMESTAMP, ZERO_ADDRESS
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    auction.startAuction()

    alice_bid = f'{init_floor_price} ether'
    auction.placeBid(
        SENTINEL_TOKEN_ID,
        {
            'from': A.alice,
            'value': Wei(alice_bid)
        }
    )
    assert auction.bids(A.alice) == Wei(alice_bid)

    auction.placeBid(
        SENTINEL_TOKEN_ID,
        {
            'from': A.alice,
            'value': Wei(alice_bid)
        }
    )
    assert auction.bids(A.alice) == (Wei(alice_bid) + Wei(alice_bid))


# 6.
def test_direct_payments_rejected(AuctionDeploy, A):
    auction = AuctionDeploy

    init_floor_price, init_timestamp, init_address = 1, FUTURE_TIMESTAMP, ZERO_ADDRESS
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    auction.startAuction()

    alice_bid = f'{init_floor_price} ether'
    with brownie.reverts(RejectDirectPayments):
        A.alice.transfer(auction, alice_bid)


# 7.
def test_cant_doubly_initialize(AuctionDeploy, AuctionFactoryDeploy, A):
    auction = AuctionDeploy
    auction_factory = AuctionFactoryDeploy

    # we pretend that Alice is an NFT collection here
    init_floor_price, init_timestamp, init_address = 1, FUTURE_TIMESTAMP, A.alice
    auction_factory.setAuctionAddress(auction)
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    with brownie.reverts(AlreadyInitialized):
        auction.initialize(
            init_floor_price,
            init_timestamp,
            init_address
        )

# 8.
def test_cant_initialize(AuctionDeploy, AuctionFactoryDeploy, A):
    auction = AuctionDeploy
    auction_factory = AuctionFactoryDeploy

    # we pretend that Alice is an NFT collection here
    init_floor_price, init_timestamp, init_address = 1, FUTURE_TIMESTAMP, A.alice
    auction_factory.setAuctionAddress(auction)
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    with brownie.reverts(NotAdmin):
        auction.initialize(
            init_floor_price,
            init_timestamp,
            init_address,
            {'from': A.alice}
        )


# 9.
def test_no_whitelisted_nft(AuctionDeploy, E721Deploy, A):
    auction = AuctionDeploy
    e721 = E721Deploy

    # mint first token to deployer
    e721.mint()
    minted_token_id = 1

    init_floor_price, init_timestamp, init_address = 1, FUTURE_TIMESTAMP, e721
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    auction.startAuction()

    with brownie.reverts(BidForbidden):
        auction.placeBid(
            minted_token_id,
            {
                'from': A.alice,
                'value': f'{init_floor_price} ether'
            }
        )

# 10.
def test_holds_whitelisted_nft(AuctionDeploy, E721Deploy, A):
    auction = AuctionDeploy
    e721 = E721Deploy

    # mint first token to deployer
    e721.mint({'from': A.alice})
    minted_token_id = 1

    init_floor_price, init_timestamp, init_address = 1, FUTURE_TIMESTAMP, e721
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    auction.startAuction()

    alice_bid = f'{init_floor_price} ether'
    auction.placeBid(
        minted_token_id,
        {
            'from': A.alice,
            'value': alice_bid
        }
    )

    assert auction.bids(A.alice) == alice_bid

# 12.
def test_withdraw_works(AuctionDeploy, A):
    auction = AuctionDeploy

    init_floor_price, init_timestamp, init_address = 1, FUTURE_TIMESTAMP, ZERO_ADDRESS
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    auction.startAuction()

    alice_bid = f'{init_floor_price} ether'
    auction.placeBid(
        SENTINEL_TOKEN_ID,
        {
            'from': A.alice,
            'value': Wei(alice_bid)
        }
    )
    
    balance_before = A.deployer.balance()
    auction.withdraw()
    expected_balance_after = balance_before + Wei(alice_bid)
    balance_after = A.deployer.balance()
    assert expected_balance_after == balance_after


# 13.
def test_fail_if_less_than_min(AuctionDeploy, A):
    auction = AuctionDeploy

    init_floor_price, init_timestamp, init_address = 1, FUTURE_TIMESTAMP, ZERO_ADDRESS
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    auction.startAuction()

    MINIMUM_BID_INCREMENT = auction.MINIMUM_BID_INCREMENT()
    alice_bid = f'{init_floor_price} ether'
    auction.placeBid(
        SENTINEL_TOKEN_ID,
        {
            'from': A.alice,
            'value': Wei(alice_bid)
        }
    )
    # ! this error will be different if min increment is something
    # ! other than 0.1 eth. You will need to change the error here
    with brownie.reverts(LessThanMinIncrement):
        auction.placeBid(
            SENTINEL_TOKEN_ID,
            {
                'from': A.alice,
                'value': MINIMUM_BID_INCREMENT - 1
            }
        )
