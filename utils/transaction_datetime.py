from datetime import datetime


DATE_LABEL_FORMAT = "%Y-%m-%d"
TIME_LABEL_FORMAT = "%I:%M %p"
DATABASE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_current_transaction_datetime_labels():
    now = datetime.now()
    return (
        now.strftime(DATE_LABEL_FORMAT),
        now.strftime(TIME_LABEL_FORMAT),
    )


def parse_date_label(date_text):
    return datetime.strptime(date_text, DATE_LABEL_FORMAT).date()


def parse_time_label(time_text):
    return datetime.strptime(time_text, TIME_LABEL_FORMAT).time()


def format_date_label(selected_date):
    return selected_date.strftime(DATE_LABEL_FORMAT)


def format_time_label(selected_time):
    return selected_time.strftime(TIME_LABEL_FORMAT)


def combine_date_time_labels(date_text, time_text):
    date_time = datetime.strptime(
        f"{date_text} {time_text}",
        f"{DATE_LABEL_FORMAT} {TIME_LABEL_FORMAT}",
    )

    return date_time.strftime(DATABASE_DATETIME_FORMAT)


def split_database_datetime(date_time_text):
    date_time = datetime.strptime(date_time_text, DATABASE_DATETIME_FORMAT)

    return (
        date_time.strftime(DATE_LABEL_FORMAT),
        date_time.strftime(TIME_LABEL_FORMAT),
    )