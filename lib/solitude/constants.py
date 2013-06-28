# These come from solitude. Go there for detailed comments.
SOURCE_BANGO = 1

TYPE_PAYMENT = 0
TYPE_REFUND = 1
TYPE_REVERSAL = 2

STATUS_PENDING = 0
STATUS_COMPLETED = 1
STATUS_CHECKED = 2
STATUS_RECEIVED = 3
STATUS_FAILED = 4
STATUS_CANCELLED = 5

STATUS_ENDED = (STATUS_COMPLETED, STATUS_FAILED, STATUS_CANCELLED)
STATUS_RETRY_OK = (STATUS_FAILED, STATUS_CANCELLED)

ACCESS_PURCHASE = 1
ACCESS_SIMULATE = 2
