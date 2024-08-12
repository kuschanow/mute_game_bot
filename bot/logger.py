import logging

import seqlog
from django.conf import settings

if settings.SEQ_URL and settings.SEQ_KEY:
    seqlog.log_to_seq(
        server_url=settings.SEQ_URL,
        api_key=settings.SEQ_KEY,
        level=settings.SEQ_LEVEL,
        batch_size=settings.SEQ_BATCH,
        auto_flush_timeout=settings.SEQ_TIMEOUT,
        override_root_logger=True
    )

logger = logging.getLogger('bot')

