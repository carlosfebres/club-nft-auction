// SPDX-License-Identifier: MIT
pragma solidity =0.8.11;

interface IAuction {
    error NotAdmin();
    error AuctionNotActive();
    error AuctionIsActive();
    error NoEtherSent();
    error LessThanFloorPrice(uint256 actualSent);
    error LessThanMinIncrement(uint256 actualSent);
    error RejectDirectPayments();
    error TransferFailed();

    /// @notice Emitted when auction starts
    event StartAuction();
    /// @notice Emitted when auction ends
    event EndAuction();

    /// @notice Emitted when bid is placed
    /// @param bidder Address of the bidder
    /// @param price Amount the bidder has bid
    event PlaceBid(address indexed bidder, uint256 indexed price);
    /// @notice Emitted when lost bid was refunded
    /// @param bidder Address of the bidder that lost the auction
    /// @param refundAmount Amount the bidder is refunded
    event RefundBid(address indexed bidder, uint256 indexed refundAmount);

    /// @notice Starts the auction
    function startAuction() external;

    /// @notice Places the bid. Handles modifying the bid as well.
    /// If the same bidder calls this function again, then that alters
    /// their original bid
    function placeBid() external payable;

    /// @notice Refunds all the lost bids. Makes an assumption that
    /// the contract keeps track of all of the bids.
    /// @param losingThreshold Refund all the bids below this price
    /// @param fromIx Loop through all of the bidders starting at this index
    /// @param toIx Loop through all of the bidders ending at this index
    function refundBidders(
        uint256 losingThreshold,
        uint256 fromIx,
        uint256 toIx
    ) external;
}

/*
 * 88888888ba  88      a8P  88
 * 88      "8b 88    ,88'   88
 * 88      ,8P 88  ,88"     88
 * 88aaaaaa8P' 88,d88'      88
 * 88""""88'   8888"88,     88
 * 88    `8b   88P   Y8b    88
 * 88     `8b  88     "88,  88
 * 88      `8b 88       Y8b 88888888888
 *
 * IAuction.sol
 *
 * MIT License
 * ===========
 *
 * Copyright (c) 2022 Rumble League Studios Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 */
