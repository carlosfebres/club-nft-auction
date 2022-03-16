from brownie import ClubMintPass, accounts, chain


def main():

    deployer = accounts.load('<deployer>')
    priority_fee = int(1.15 * chain.priority_fee)
    print(f'Priority fee: {priority_fee} wei')
    from_deployer = {'from': deployer, 'priority_fee': priority_fee}

    ClubMintPass.deploy(from_deployer)


if __name__ == '__main__':
    main()
