from brownie import Auction, AuctionFactory, accounts


def main():

    deployer = accounts.load('<deployer_account_name>')
    from_deployer = {'from': deployer}

    auction = Auction.deploy(from_deployer)
    auction_factory = AuctionFactory.deploy(from_deployer)

    auction_factory.setAuctionAddress(auction, from_deployer)

    # ! remember to initialize auction

if __name__ == '__main__':
    main()
