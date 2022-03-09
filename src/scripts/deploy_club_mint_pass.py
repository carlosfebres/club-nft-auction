from brownie import ClubMintPass, accounts


def main():

    deployer = accounts.load('<deployer_account_name>')
    from_deployer = {'from': deployer}

    ClubMintPass.deploy(from_deployer)


if __name__ == '__main__':
    main()
