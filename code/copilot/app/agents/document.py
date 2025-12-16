from app.logs import setup_logging
from app.agents.root import RootAgent

logger = setup_logging(__name__)


class DocumentAgent(RootAgent):
    pass
