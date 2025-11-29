import logging
import contextvars

# Define global context variables for session_id and message_id
session_id_var = contextvars.ContextVar("session_id", default=None)
message_id_var = contextvars.ContextVar("message_id", default=None)

# Define the NOTICE log level globally
NOTICE_LEVEL = 25
if not hasattr(logging, "NOTICE"):
    logging.addLevelName(NOTICE_LEVEL, "NOTICE")
    logging.NOTICE = NOTICE_LEVEL  # Define logging.NOTICE

    # Extend Logger class to support `notice`
    def notice(self, message, *args, **kwargs):
        if self.isEnabledFor(NOTICE_LEVEL):
            self._log(NOTICE_LEVEL, message, args, **kwargs)

    logging.Logger.notice = notice  # Attach the method

class ContextLogger(logging.LoggerAdapter):
    """Custom LoggerAdapter to automatically inject session_id and message_id."""

    def __init__(self, logger):
        super().__init__(logger, {})

    def process(self, msg, kwargs):
        """Injects session_id and message_id only if they are available."""
        session_id = session_id_var.get()
        message_id = message_id_var.get()

        prefix = []
        if session_id:
            prefix.append(f"[session_id={session_id}]")
        if message_id:
            prefix.append(f"[message_id={message_id}]")

        msg = " ".join(prefix) + " - " + msg if prefix else msg
        return msg, kwargs

    def notice(self, msg, *args, **kwargs):
        """Enable NOTICE level in LoggerAdapter."""
        self.log(NOTICE_LEVEL, msg, *args, **kwargs)

# Function to configure logging 
def setup_logging():
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=NOTICE_LEVEL,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("app.log"),  # Log to a file
                logging.StreamHandler()  # Log to console
            ]
        )

# Function to get a logger (automatically includes session_id and message_id)
def get_logger(name):
    base_logger = logging.getLogger(name)
    return ContextLogger(base_logger)

# Function to set global session_id and message_id (call this at the beginning of a run)
def set_log_context(session_id, message_id):
    session_id_var.set(session_id)
    message_id_var.set(message_id)
