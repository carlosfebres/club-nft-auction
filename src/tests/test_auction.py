import pytest
from brownie import Auction, AuctionFactory, accounts
import brownie

# 1. test can't bid if auction not started
# ✔️ 2. test correct state of the clones
# 3. test can't bid after auction ended
# 4. test can bid during active auction
# 5. test correct bids for diffs
# 6. test direct eth payments are rejected
# ✔️ 7. test auction can't be initialized more than once
# ✔️ 8. test auction can't be initialized by non-deployer
# 9. test can't bid if do not hold whitelisted collection
# 10. test can bid if I hold whitelisted collection
# 11. test anyone can bid if whitelisted collection is zero

# Consts

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
SENTINEL_TOKEN_ID = 0

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


# Tests
# 1.
def test_cant_bid_before_start(AuctionDeploy, A):
    auction = AuctionDeploy

    init_floor_price, init_timestamp, init_address = 1, 10, ZERO_ADDRESS
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    with brownie.reverts("typed error: 0x69b8d0fe"):
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
    init_floor_price, init_timestamp, init_address = 1, 10, A.alice
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

# 7.
def test_cant_doubly_initialize(AuctionDeploy, AuctionFactoryDeploy, A):
    auction = AuctionDeploy
    auction_factory = AuctionFactoryDeploy

    # we pretend that Alice is an NFT collection here
    init_floor_price, init_timestamp, init_address = 1, 10, A.alice
    auction_factory.setAuctionAddress(auction)
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    # AlreadyInitialized
    with brownie.reverts("typed error: 0x0dc149f0"):
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
    init_floor_price, init_timestamp, init_address = 1, 10, A.alice
    auction_factory.setAuctionAddress(auction)
    auction.initialize(
        init_floor_price,
        init_timestamp,
        init_address
    )
    # NotAdmin
    with brownie.reverts("typed error: 0x7bfa4b9f"):
        auction.initialize(
            init_floor_price,
            init_timestamp,
            init_address,
            {'from': A.alice}
        )
