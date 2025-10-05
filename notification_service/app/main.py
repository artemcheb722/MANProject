from services.rabbit.rabbitmq_service import rabbitmq_broker


def main():
    print(888888888888888888888888)
    with rabbitmq_broker.get_connection() as connection:
        with connection.channel() as channel:
            rabbitmq_broker.consume_message(channel)


if __name__ == "__main__":
    main()
