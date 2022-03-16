from brownie import ClubMintPass, accounts, chain

# ! make sure these are only the winners of the auction
WINNERS = [
    "0x2f90722088cf90e674708ea726a2ad2cd4cb8d50",
    "0x5e12b20feb5056660222f8a08382660548e12ef5",
    "0x09125b0331354707d1238ae8044921de47dd4152",
    "0x465dca9995d6c2a81a9be80fbced5a770dee3dae"  
]


def main():

    deployer = accounts.load('<deployer>')
    club_mint_pass = ClubMintPass.at('<club_mint_pass_address>')
    priority_fee = int(1.15 * chain.priority_fee)
    print(f'Priority fee: {priority_fee} wei')
    from_deployer = {'from': deployer, 'priority_fee': priority_fee}

    club_mint_pass.batchMint(WINNERS, from_deployer)


if __name__ == '__main__':
    main()
