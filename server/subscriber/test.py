from subscriber import Server


def print_data(data):
    print("Printing data: ")
    print(data)


def main():
    server = Server(callback=print_data)
    server.run()


if __name__ == '__main__':
    main()
