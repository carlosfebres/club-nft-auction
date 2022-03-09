// SPDX-License-Identifier: MIT
pragma solidity =0.8.12;

import "../../interfaces/INFTContract.sol";

library NFTCommon {

    /// @notice Determines if potentialOwner is in fact an owner of at least 1 qty of NFT token ID.
    /// @param nft NFT address
    /// @param potentialOwner suspected owner of the NFT token ID
    /// @param tokenID id of the token
    /// @return quantity of held token, possibly zero
    function quantityOf(
        INFTContract nft,
        address potentialOwner,
        uint256 tokenID
    ) internal view returns (uint256) {
        // assumes it's a 721 standard
        try nft.ownerOf(tokenID) returns (address owner) {
            if (owner == potentialOwner) {
                return 1;
            } else {
                return 0;
            }
        // it's actually a 1155
        } catch (bytes memory) {
            try nft.balanceOf(potentialOwner, tokenID) returns (
                uint256 amount
            ) {
                return amount;
            } catch (bytes memory) {
                return 0;
            }
        }
    }

}