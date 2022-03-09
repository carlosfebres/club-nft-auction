import logging

from db import DB
from transform.covalent import Covalent

# todo: needs to inherit an interface that implements flush
# todo: every instance should also take the address it transforms
# todo: as a constructor argument
class Transformer:
    def __init__(self, address: str):

        self._address = address

        self._transformed = {"_id": 1}

        self._db_name = "ethereum-indexer"
        self._collection_name = f"{address}-state"

        self._flush_state = False

        self._db = DB()

    # todo: txn dataclass
    def entrypoint(self, txn):
        """
        Main entrypoint for transforming the raw data. Responsible
        for routing the events into the correct handlers.

        Args:
            txn (_type_): _description_
        """

        # 1. check if there is state in the db
        # 2. if there is state in the db, update memory with it
        self.update_memory_state()

        # routes and performs any additional logic
        logging.info(f'Handling transaction at: {txn["block_height"]} block')

        log_events = txn["log_events"]
        # * ensures that events are supplied in the correct order
        log_events = sorted(log_events, key=lambda x: x["log_offset"])

        for event in log_events:

            # * means the event was emitted by a contract that is
            # * not of interest
            if event["sender_address"] != self._address.lower():
                continue

            # ! this is not good.
            # ! if this were to happen in an event that pertains to
            # ! our address, it would corrupt the state
            if event["decoded"] is None:
                logging.warning(f"No name for event: {event}")
                continue

            if event["decoded"]["name"] == "PlaceBid":
                decoded_params = Covalent.decode(event)
                bidder, price = (
                    decoded_params[0],
                    decoded_params[1],
                )
                self._on_place_bid(bidder, price)

            logging.info(event)

        self._flush_state = True

    # todo: should be part of the interface
    # todo: acts as the means to sync with db state
    def update_memory_state(self) -> None:
        """
        If the script was cancelled previously, this pulls the latest
        transformed state from the db.
        """

        state = self._db.get_any_item(self._db_name, self._collection_name)

        if state is None:
            return

        self._transformed = state

    # todo: should be part of the interface
    def flush(self) -> None:
        """
        Write the transformed state to the db.
        """

        if self._flush_state:
            # * write to the db
            self._db.put_item(self._transformed, self._db_name, self._collection_name)
            self._flush_state = False

    def _on_place_bid(self, bidder: str, price: float) -> None:
        # PlaceBid(address indexed bidder, uint256 indexed price)

        if bidder in self._transformed:
            self._transformed[bidder] += price
        else:
            self._transformed[bidder] = price
